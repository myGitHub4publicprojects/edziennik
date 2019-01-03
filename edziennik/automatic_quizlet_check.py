# -*- coding: utf-8 -*-
import time, sys, os

from django.conf import settings
from django.core.mail import send_mail

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait


def admin_email(mail_title, mail_body):
    send_mail(mail_title,
              mail_body,
              settings.EMAIL_HOST_USER,
              [settings.ADMIN_EMAIL],
              fail_silently=False)


def quizlet_check(username, password):


	# open browser
	driver = webdriver.Chrome()

	def quizlet_login(user_name, quizlet_password):
		'''log in to quizlet or throw error'''
		try:
			driver.get("https://quizlet.com/login")
			assert "Quizlet" in driver.title
			form1 = driver.find_element_by_class_name('LoginPromptModal-form')
			username = form1.find_element_by_name('username')
			password = form1.find_element_by_name('password')
			username.send_keys(user_name)
			password.send_keys(quizlet_password)
			submit = form1.find_element_by_class_name('UIButton-wrapper')
			submit.click()

			# confirm being on the right page
			element = wait(driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, "SiteHeader-username"))
				)

			# confirm succesfull login
			scraped_user = driver.find_element_by_class_name('SiteHeader-username').text
			assert scraped_user[:8] == user_name[:8]
		except Exception as e:
			exc_tb = sys.exc_info()[2]
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			message = 'Error: ' + repr(e) + 'w pliku:' + fname,'linia: ' + str(exc_tb.tb_lineno)
			print(message)
			admin_email('Quizlet check error', message)

	def get_groups(user_name):
		'''run this function after quizlet_login(),
		returns a list of all groups' urls,
		this function may not be needed if all groups' url are added by admin'''
		try:
			classes_url = 'https://quizlet.com/' + user_name + '/classes'
			driver.get(classes_url)
			wait(driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, "DashboardListItem"))
				)
			all_groups_urls = []
			divs = driver.find_elements_by_class_name('DashboardListItem')
			for div in divs:
				group_link = div.find_element_by_css_selector('a.UILink')
				all_groups_urls.append(group_link.get_attribute('href'))
			return all_groups_urls
		except Exception as e:
			exc_tb = sys.exc_info()[2]
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			message = 'Error: ' + repr(e) + 'w pliku:' + fname,'linia: ' + str(exc_tb.tb_lineno)
			print(message)
			admin_email('Quizlet check error', message)

	def get_set_urls(class_url):
		'''returns a list of urls, each url is for activity of students in a single set,
		during last week. Accepts str - url of a group - https://quizlet.com/class/2702900/'''
		driver.get(class_url)
		try:
			# wait until page is loaded, use ClassSetPreviewLink css class
			# only groups which have sets would have this element
			wait(driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, "ClassSetPreviewLink"))
				)
		except:
			print("No sets found in: ", class_url)
			pass
		# check if there are sets in this group
		group_sets = driver.find_elements_by_css_selector('div.PreviewCard-actions')

		if not group_sets:
			return []
		set_urls = []
		for single_set in group_sets:
			link = single_set.find_element_by_css_selector("a.UIButton.UIButton--borderless")
			single_set_url = link.get_attribute('href') + '/pastweek'
			set_urls.append(single_set_url)
		return set_urls


	def check_activity(single_set_url):
		'''Returns a list of students. Checks activity (completion of at least one activity)
		of students in a set during last week,	only students who compeleted at least one activity
		are added, if no students in a group returns an empty list.
		Accepts a string - url of the past week activity for whole group in a given set: 
		driver.get('https://quizlet.com/137287920/teacher/3652319/pastweek')'''
		try:	
			driver.get(single_set_url)
			wait(driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, "ClassProgressActivityRow"))
				)
			students = []
			# get list of rows
			rows = driver.find_elements_by_class_name('ClassProgressActivityRow')
			for row in rows:
				username = row.find_element_by_class_name('UserLink-username')
				activity = row.find_elements_by_css_selector('div.ClassProgressModeActivity.has-finished')
				if activity:
					students.append(username.text)
			return students
		except Exception as e:
			exc_tb = sys.exc_info()[2]
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			message = 'Error: ' + repr(e) + 'w pliku:' + fname,'linia: ' + str(exc_tb.tb_lineno)
			print(message)
			admin_email('Quizlet check error', message)
			
			# if no students added to the group:
			return []

	def get_all_active(username, password):
		'''returns a list of all active students in all groups, active is defined as those who completed at least
		one activity during past week in any of their sets.
		accepts str, str - username and password to Quizlet user who is an admin and teacher of all groups'''
		try:
			# login
			quizlet_login(username, password)
			# get urls of current groups
			groups = get_groups(username)
			# print('groups: ', groups)
			# get urls of activity in a single set
			all_sets_urls = []
			for group in groups:
				group_sets = get_set_urls(group)
				all_sets_urls += group_sets
				# time.sleep(5)

			# print('all_sets_urls', all_sets_urls)
			# get active students in all sets
			all_active_students = []
			for single_url in all_sets_urls:
				print('checking activity in this url: ', single_url)
				group_students = check_activity(single_url)
				all_active_students += group_students

			unique_students = list(set(all_active_students))
			email_body = ','.join(unique_students)
			admin_email('quizlet_done3', email_body)

			# close browser
			driver.close()

			return unique_students
		except Exception as e:
			exc_tb = sys.exc_info()[2]
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			message = 'Error: ' + repr(e) + 'w pliku:' + fname,'linia: ' + str(exc_tb.tb_lineno)
			print(message)
			admin_email('Quizlet check error', message)
	
	username = settings.QUIZLET_USERNAME
	password = settings.QUIZLET_PASSWORD
	get_all_active(username, password)