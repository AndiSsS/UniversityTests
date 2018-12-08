authorize()

inneri = 0
for i in range(1,ITERATIONS+1):
	print('ITERATION:' + str(i))
	while True:
		inneri = inneri + 1
		print("INNERI:::::: " + str(inneri))

		question_name = get_question_name()
		value_to_verify = get_next_to_verify(question_name)
		question_number = get_question_number()
		points_number = get_points_number()
		points_for_test = get_points_for_test()

		print('points: ' + str(points_number))
		print('points for test: ' + str(points_for_test))

		if points_number >= POINTS:
			print("P N:" + str(points_number))
			# sys.exit(0) #########################
			skip_to_end()
			break
		elif question_number == 10:
			refresh_test()

		try:
			driver.implicitly_wait(0)
			driver.find_element_by_name('answer').send_keys([value.text + " " for value in last_question_parse_possibly_values()])
			driver.implicitly_wait(10)
			submit()
			driver.switch_to_alert().accept()
			print('FINDED')

			continue
		except Exception as e:
			print(str(e))
			pass

		if points_number + points_for_test > MAX_POINTS:
			submit()
			driver.switch_to_alert().accept()
			continue

		if(value_to_verify != False):
			print(value_to_verify+" value to verify exists")

			driver.find_element_by_name(value_to_verify).click()
			submit()
			try:
				alert_text = driver.switch_to_alert().text
			except:
				time.sleep(3)
				alert_text = driver.switch_to_alert().text
			if(alert_text == 'Неправильно!'):
				edit_value(value_to_verify, question_name, 'wrong')
			elif(alert_text == 'Правильно'):
				edit_value(value_to_verify, question_name, 'correct')
			else:
				edit_value(value_to_verify, question_name, 'correct', True)
			try:
				driver.switch_to_alert().accept()
			except:
				time.sleep(3)
				driver.switch_to_alert().accept()
		else:
			print('ended')

			correct_values = get_values(question_name, 'correct')
			for value in correct_values:
				driver.find_element_by_name(value).click()		
			submit()
			try:
				driver.switch_to_alert().accept()
			except:
				time.sleep(3)
				driver.switch_to_alert().accept()



