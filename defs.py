import getopt
import sys
import time
from selenium import webdriver

help_str = '-u <URL of test> [-i <number of iterations>] [-p <desired number of points>] [-m <max possible points ' \
           'for the test>] [-a] #not anonymous mode [-t] #not to skip text inputs'

URL = None
IS_ANONYMOUS = True
MAX_POINTS = 10
POINTS = 8.6
ITERATIONS = 1
IS_SKIP_TEXT_INPUTS = True

VALUES_VERIFY = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10']
VALUES_FILE_PATH = 'values.txt'
STR_CORRECT_ANSWER = 'Правильно!'
STR_WRONG_ANSWER = 'Неправильно!'

try:
    opts, args = getopt.getopt(sys.argv[1:], "u:p:i:m:a:t")
except getopt.GetoptError:
    print(help_str)
    sys.exit(2)
for opt, arg in opts:
    if opt in "-u":
        URL = arg
    elif opt in "-i":
        ITERATIONS = arg
    elif opt in "-p":
        POINTS = arg
    elif opt in "-m":
        MAX_POINTS = arg
    elif opt in "-a":
        IS_ANONYMOUS = False
    elif opt in "-t":
        IS_SKIP_TEXT_INPUTS = False

if 'URL' is None:
    print(help_str)
    sys.exit(2)

driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(0.2)
driver.get(URL)


def _create_line(question_name):
    values_file = open(VALUES_FILE_PATH, 'a+', encoding='utf-8')
    values_file.write(question_name + '-+--+-\n')


def _get_first_number_from_str(input_str):
    result = ""

    for s in input_str:
        if not s.isdigit():
            input_str = input_str[1:]
        else:
            break

    for s in input_str:
        if s.isdigit() or s == ".":
            result += s
        else:
            break
    return result


def authorize():
    if IS_ANONYMOUS:
        driver.find_element_by_name('skip').click()
        submit()
    else:
        driver.find_element_by_name('login').send_keys('123')
        driver.find_element_by_name('user_pwd').send_keys('123')
        submit()


def get_question_name():
    elems = driver.find_elements_by_xpath('//div[@class=\'b3\']/*[not(self::ol)]')
    result = ""
    for e in elems:
        result += e.get_attribute('innerHTML')
    return result.replace('\n', '')


def get_question_number():  # Питання N:-->2<--  Спроб : 6
    # Всього одержано балів : 0 з 1. Правильних відповідей: 0 Питання N:2 Спроб : 6
    text = driver.find_element_by_xpath('//div[@class=\'b2\']').text.split('N:')[1]
    # 2 Спроб : 6
    return int(_get_first_number_from_str(text))


def get_points_number():  # Всього одержано балів : -->0<-- з 1
    return float(_get_first_number_from_str(
        driver.find_element_by_xpath('//div[@class=\'b2\']').text.split('Всього одержано балів : ')[1]))


def get_points_for_test():  # Балів за це питання : -->1<-- Часу : 60
    return float(_get_first_number_from_str(
        driver.find_elements_by_xpath('//div[@class=\'b2\']')[1].text.split('Балів за це питання : ')[1]))


def get_question_correct(question_name):
    with open(VALUES_FILE_PATH, encoding='utf-8') as values_file:
        for line in values_file:
            line = line.split('-+-')
            if line[0] == question_name:
                return line[2]


def last_question_parse_possibly_values():
    return driver.find_elements_by_xpath('//tr/td/h3/strong')[6:]


def get_next_to_verify(question_name):
    with open(VALUES_FILE_PATH, encoding='utf-8') as values_file:
        for line in values_file:
            line = line.split('-+-')
            if line[0] == question_name:
                if line[1] == 'ended':
                    return False
                for value in VALUES_VERIFY:
                    if value not in line[1] and value not in line[2]:
                        return value
                edit_value('ended', question_name, 'wrong')
                return False
        _create_line(question_name)
        return VALUES_VERIFY[0]


def get_values(question_name, kind, get_only_first_value=False):
    with open(VALUES_FILE_PATH, 'r', encoding='utf-8') as values_file:
        for line in values_file:
            line = line.split('-+-')
            if kind == 'correct':
                if line[0] == question_name:
                    return [l.replace('\n', '') for l in line[2].split(',')] if not get_only_first_value \
                                                                                else line[2].replace('\n', '')
            elif kind == 'wrong':
                if line[0] == question_name:
                    return line[1].split(',') if not get_only_first_value else line[1]
        return False


def edit_value(value, question_name, kind, is_partial=False):
    with open(VALUES_FILE_PATH, encoding='utf-8') as values_file:
        lines = values_file.readlines()
        if kind == 'correct':
            for i, line in enumerate(lines):
                line = line.split('-+-')
                if line[0] == question_name:
                    with open(VALUES_FILE_PATH, 'w', encoding='utf-8') as values_file_w:
                        if not is_partial:
                            line[1] = 'ended'
                        else:
                            for value in VALUES_VERIFY:
                                if value not in line[1] and value not in line[2]:
                                    break
                                line[1] = 'ended'

                        line[2] = line[2].replace('\n', '')
                        line[2] += ',' + value + '\n' if line[2] != '' else value + '\n'
                        lines[i] = '-+-'.join(line)
                        values_file_w.writelines(lines)
                        return True
        elif kind == 'wrong':
            for i, line in enumerate(lines):
                line = line.split('-+-')
                if line[0] == question_name:
                    with open(VALUES_FILE_PATH, 'w', encoding='utf-8') as values_file_w:
                        line[1] += ',' + value if line[1] != '' else value
                        lines[i] = '-+-'.join(line)
                        values_file_w.writelines(lines)
                        return True

    _create_line(question_name)
    edit_value(value, question_name, kind)


def submit():
    click_element(driver.find_element_by_xpath('//input[@type="submit"]'))


def refresh_test():
    for cookie in driver.get_cookies():
        if cookie['name'] == 'sid':
            sid = cookie['value']
            if '_' not in sid:
                sid += '_1'
            else:
                sid = sid.split('_')
                sid[1] = str(int(sid[1]) + 1)
                sid = '_'.join(sid)
            driver.delete_cookie('sid')
            driver.add_cookie({'name': 'sid', 'value': sid, 'path': '/web_thesaurus'})
        # elif(cookie['name'] == 'check'):
        # 	driver.delete_cookie('check')
        # 	driver.add_cookie({'name':'check','value':'1','path':'/web_thesaurus'})
    for cookie in driver.get_cookies():
        print(cookie['name'] + '=>' + cookie['value'])


def skip_to_end():
    while True:
        try:
            driver.implicitly_wait(0.2)
            driver.find_element_by_name('results')
            print('finded results page')
            submit()
            break
        except:
            submit()
            try:
                driver.switch_to.alert.accept()
            except:
                continue


def click_element(elem):
    try:
        elem.click()
    except:
        try:
            time.sleep(2)
            print("SLEEP click_element 2")
            elem.click()
        except:
            time.sleep(3)
            print("SLEEP click_element second 3")
            elem.click()


def get_text_input_if_exists():
    driver.implicitly_wait(0.1)
    try:
        return driver.find_element_by_xpath("//*[@class='inp_answ']")
    except:
        return False
