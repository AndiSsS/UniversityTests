from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import sys, getopt
import selenium.common.exceptions
import time

driver = webdriver.Chrome('chromedriver.exe')
driver.get('http://localhost/tests/')

driver.implicitly_wait(0)

input_elem = driver.find_element_by_xpath('//input')

input_elem.send_keys('TEST')

print(input_elem.get_property('value'))
