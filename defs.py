from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import sys, getopt
import selenium.common.exceptions
import time

try:
	opts, args = getopt.getopt(sys.argv[1:],"u:p:i:m:a")
except getopt.GetoptError:
	print (help_str)
	sys.exit(2)
for opt, arg in opts:
	if opt in ("-u"):
		URL = arg
	elif opt in ("-i"):
		ITERATIONS = arg
	elif opt in ("-p"):
		POINTS = arg
	elif opt in ("-m"):
		MAX_POINTS = arg
	elif opt in ("-a"):
		IS_ANONYMOUS = True

if 'URL' not in locals():
	print (help_str)
	sys.exit(2)

IS_ANONYMOUS = IS_ANONYMOUS if 'IS_ANONYMOUS' in locals() else False
MAX_POINTS = float(MAX_POINTS) if 'MAX_POINTS' in locals() else 10
POINTS = float(POINTS) if 'POINTS' in locals() else 8.6
ITERATIONS = int(ITERATIONS) if 'ITERATIONS' in locals() else 1
VALUES_VERIFY = ['a1','a2','a3','a4','a5','a6','a7','a8','a9','a10']
VALUES_FILE_PATH = 'values.txt'

driver = webdriver.Chrome('chromedriver.exe')
driver.get(URL)

def authorize():
	driver.implicitly_wait(10)
	# for cookie in driver.get_cookies():
	# 	if(cookie['name'] == 'PHPSESSID'):
	# 		print('FINDED PHPSESSID')
	# 		driver.delete_cookie('PHPSESSID')
	# 		driver.add_cookie({'name':'PHPSESSID','value':'r3okpl3hpe8nfegfq9j69k4a55','path':'/'})
	if IS_ANONYMOUS:
		driver.find_element_by_name('skip').click()
		submit()
	else:
		driver.find_element_by_name('login').send_keys('0117067')
		driver.find_element_by_name('user_pwd').send_keys('Killer1998')
		submit()
		
def get_question_name():
	elems_h2 = driver.find_elements_by_tag_name('h2')
	if(len(elems_h2) == 2):
		return elems_h2[0].text + elems_h2[1].text
	else:
		return elems_h2[1].text

def get_question_number():
	return int(driver.find_element_by_xpath('//font[@color="#0000ff"]').text)

def get_points_number():
	return float(driver.find_elements_by_xpath('//font[@color="#ff0000"]')[0].text)

def get_points_for_test():
	return float(driver.find_element_by_xpath('//div[@align="right"]').text.split(':')[1][1])

def get_question_correct(question_name):
	with open(VALUES_FILE_PATH, encoding='utf-8') as values_file:
		for line in values_file:
			line = line.split('-+-')
			if(line[0] == question_name):
				return line[2]

def last_question_parse_possibly_values():
	return driver.find_elements_by_xpath('//tr/td/h3/strong')[6:]

def get_next_to_verify(question_name):
	with open(VALUES_FILE_PATH, encoding='utf-8') as values_file:
		for line in values_file:
			line = line.split('-+-')
			if(line[0] == question_name):
				if(line[1] == 'ended'):
					return False
				for value in VALUES_VERIFY:
					if (value not in line[1] and value not in line[2]):
						return value
				edit_value('ended',question_name,'wrong')
				return False	
		create_line(question_name)
		return VALUES_VERIFY[0]

def get_values(question_name, kind):
	with open(VALUES_FILE_PATH, encoding='utf-8') as values_file:
		for line in values_file:
			line = line.replace('\n','').split('-+-')
			if(kind == 'correct'):
				if(line[0] == question_name):
					return line[2].split(',')
			elif(kind == 'wrong'):
				if(line[0] == question_name):
					return line[1].split(',')
		return False
		
def create_line(question_name):
	values_file = open(VALUES_FILE_PATH, 'a', encoding='utf-8')
	values_file.write(question_name + '-+--+-\n')

def edit_value(value, question_name, kind, is_partial=False):
	with open(VALUES_FILE_PATH, 'r', encoding='utf-8') as values_file:
		lines = values_file.readlines()
		if(kind == 'correct'):
			for i, line in enumerate(lines):
				line = line.split('-+-')
				if(line[0] == question_name):
					with open(VALUES_FILE_PATH, 'w', encoding='utf-8') as values_file_w:
						if not is_partial:
							line[1] = 'ended'
						else:
							for value in VALUES_VERIFY:
								if value not in line[1] and value not in line[2]:
									break
								line[1] = 'ended'

						line[2] = line[2].replace('\n','')
						line[2] += ','+value+'\n' if line[2] != '' else value+'\n'
						lines[i] = '-+-'.join(line)
						values_file_w.writelines(lines)
						return True		
		elif(kind == 'wrong'):
			for i, line in enumerate(lines):
				line = line.split('-+-')
				if(line[0] == question_name):
					with open(VALUES_FILE_PATH, 'w', encoding='utf-8') as values_file_w:
						line[1] += ','+value if line[1] != '' else value
						lines[i] = '-+-'.join(line)
						values_file_w.writelines(lines)
						return True

	create_line(question_name)
	edit_value(value, question_name, kind)

def submit():
	driver.find_element_by_xpath('//input[@type="image"]').click()
	print('submitted')

def refresh_test():
    for cookie in driver.get_cookies():
        if(cookie['name'] == 'sid'):
        	sid = cookie['value']
        	if not '_' in sid:
        		sid += '_1'
        	else:
        		sid = sid.split('_')
        		sid[1] = str(int(sid[1]) + 1)
        		sid = '_'.join(sid)
        	driver.delete_cookie('sid')
        	driver.add_cookie({'name':'sid','value':sid,'path':'/web_thesaurus'})
        # elif(cookie['name'] == 'check'):
        # 	driver.delete_cookie('check')
        # 	driver.add_cookie({'name':'check','value':'1','path':'/web_thesaurus'})
    for cookie in driver.get_cookies():
    	print(cookie['name']+'=>'+cookie['value'])

def skip_to_end():
	while True:
		try:
			print('try')
			driver.implicitly_wait(0)
			driver.find_element_by_name('results')
			driver.implicitly_wait(10)
			time.sleep(1)
			print('finded results page')
			submit()
			time.sleep(100)
			authorize()
			break
		except BaseException as e:
			submit()
			try:
				driver.switch_to_alert().accept()
			except:
				continue	