from defs import *

inner_i = 0
for i in range(1, ITERATIONS+1):
	print('ITERATION\t' + str(i))

	authorize()

	while True:
		inner_i = inner_i + 1
		print("INNER_I\t" + str(inner_i))

		question_name = get_question_name()	
		question_number = get_question_number()
		points_number = get_points_number()
		points_for_test = get_points_for_test()
		text_input_elem = get_text_input_if_exists()
		# get next value to verify, create new row for question if not exist
		value_to_verify = get_next_to_verify(question_name)

		print('points: ' + str(points_number))
		print('points for test: ' + str(points_for_test))

		if points_number >= POINTS:
			print("P N:" + str(points_number))
			skip_to_end()
			break
		elif question_number == MAX_POINTS:
			refresh_test()

		if points_number + points_for_test > MAX_POINTS:
			submit()
			driver.switch_to_alert().accept()
			continue

		# check if this question requires manual text input
		if text_input_elem:
			if IS_SKIP_TEXT_INPUTS:
				submit()
				driver.switch_to.alert.accept()
				continue
			
			text_input_value = get_values(question_name, "correct", True)

			if text_input_value:
				text_input_elem.send_keys(text_input_value)
				submit()
				driver.switch_to.alert.accept()
				continue

			while True:
				text_input_value = text_input_elem.get_property('value')
				if text_input_value.find("-+-") != -1:
					text_input_elem.clear()
					text_input_elem.send_keys(text_input_value.replace('-+-', ''))
					submit()

					alert_text = driver.switch_to.alert.text
					if alert_text == STR_CORRECT_ANSWER:
						edit_value(text_input_value, question_name, 'correct')

					driver.switch_to.alert.accept()
					break
				time.sleep(0.1)
		else:
			if value_to_verify:
				print(value_to_verify + " value to verify exists")

				try:
					click_element(driver.find_element_by_name(value_to_verify))
				except:
					value_to_verify = "a1"
					click_element(driver.find_element_by_name(value_to_verify))

				submit()
				try:
					alert_text = driver.switch_to.alert.text
				except:
					submit()
					time.sleep(1)
					alert_text = driver.switch_to_alert().text
				if alert_text == STR_WRONG_ANSWER:
					edit_value(value_to_verify, question_name, 'wrong')
				elif alert_text == STR_CORRECT_ANSWER:
					edit_value(value_to_verify, question_name, 'correct')
				else:
					edit_value(value_to_verify, question_name, 'correct', True)
				try:
					driver.switch_to.alert.accept()
				except:
					driver.switch_to.alert.accept()
			else:
				print('ended')

				correct_values = get_values(question_name, 'correct')
				for value in correct_values:
					click_element(driver.find_element_by_name(value))
				submit()
				try:
					driver.switch_to.alert.accept()
				except:
					submit()
					time.sleep(1)
					driver.switch_to.alert.accept()
