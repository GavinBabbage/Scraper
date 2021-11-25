from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
import pandas as pd
from chromedriver_py import binary_path # this will get you the path variable
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time

#set the path to configure webdriver to use chrome browser
#chrome_options = Options()  
#chrome_options.add_argument("--headless") 
#driver = webdriver.Chrome(executable_path=binary_path,chrome_options=chrome_options)

driver = webdriver.Chrome(ChromeDriverManager().install())
#driver = webdriver.Chrome(executable_path=binary_path)
#r'C:\path\to\chromedriver.exe'
#driver = webdriver.Chrome(executable_path= r'C:/Program Files (x86)/Google/Chrome/Application/chrome'


#driver.get("<a href="https://www.flipkart.com/laptops/">https://www.flipkart.com/laptops/</a>~buyback-guarantee-on-laptops-/pr?sid=6bo%2Cb5g&uniq")
#this is where i added the website i want to scrape information from
#driver.get("https://www.glassdoor.com/Reviews/Nedbank-South-Africa-Reviews-EI_IE473362.0,7_IL.8,20_IN211.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false")
driver.get("https://www.glassdoor.com/Reviews/Standard-Bank-Group-Reviews-EI_IE8036.0,19_IN211.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME&filter.iso3Language=eng")

#driver.get("https://www.glassdoor.com/Reviews/Nedbank-Cape-Town-Reviews-EI_IE473362.0,7_IL.8,17_IM1026_P1.htm")
content = driver.page_source
pager = BeautifulSoup(content,features="html.parser")
soup = BeautifulSoup(content,features="html.parser")
arrow = driver.find_elements_by_class_name("pagination__ArrowStyle__nextArrow  ");
enabled = arrow[0].is_enabled()
sign = 0


# signin in to glassdoor
driver.get("https://www.glassdoor.com/Reviews/Standard-Bank-Group-Reviews-EI_IE8036.0,19_IN211.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME&filter.iso3Language=eng")
#driver.get("https://www.glassdoor.com/Reviews/Nedbank-South-Africa-Reviews-EI_IE473362.0,7_IL.8,20_IN211.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false")
driver.implicitly_wait(10)
driver.find_element_by_link_text("Sign In").click()
driver.implicitly_wait(20)
username = driver.find_element_by_id("userEmail")
driver.implicitly_wait(10)
password = driver.find_element_by_id("userPassword")
driver.implicitly_wait(10)
username.send_keys("")  #insert email for glassdoor
password.send_keys("")  #insert password
driver.implicitly_wait(20)
driver.find_element_by_name("submit").click()
driver.implicitly_wait(4)

#important arrays
overrating=[]
Reviewer=[]
Datearry = []
review=1
WorkLifeBalance =[]
CultureValues =[]
CareerOpportunities =[]
CompensationandBenefits =[]
SeniorManagement =[]
while(enabled):
	driver.get(driver.current_url)
	driver.implicitly_wait(10)
	content = driver.page_source
	soup = BeautifulSoup(content,features="html.parser")
	#looking through the page and finding the html attribute that is responsible for the revies 
	for a in soup.findAll('li', attrs={'class':'empReview cf'}):
		#obtaining attribute containing overall rating
		rate = a.find('div',attrs={'class':'v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__small'})
		date = a.find('time', attrs ={'class':'date subtle small'})
		s = date.text
		p = len(s)
		start = p - 4
		Datearry.append(s[start:p].strip())
		overrating.append(rate.text)
		Reviewer.append(review)
		review+=1

	#check if these fields are present in the subrating
	worklife=False
	culture = False
	career=False
	compensation=False
	senior=False
	#obtaining attribute containing sub rating
	for a in soup.findAll('li', attrs={'class':'empReview cf'}):
		#print("heeeeeeeey")
		worklife=True
		culture = True
		career=True
		compensation=True
		senior=True
		#for b in a.findAll('div', attrs={'class':'minor'}):
		for b in a.findAll('ul', attrs= {'class':'undecorated'}):
			for k in b.findAll('li'):
				c = k.find('div', attrs={'class':'minor'})
				#print(c.text)
				te= re.sub('[\W_]+', '', c.text)
				d = k.find('span',attrs={'class':'subRatings__SubRatingsStyles__gdBars gdBars gdRatings med'})
				if("WorkLifeBalance"==te):
					worklife=False
					WorkLifeBalance.append(d['title'])
				elif("CultureValues"==te):
					culture=False
					CultureValues.append(d['title'])
				elif("CareerOpportunities"==te):
					career=False
					CareerOpportunities.append(d['title'])
				elif("CompensationandBenefits"==te):
					compensation=False
					CompensationandBenefits.append(d['title'])
				elif("SeniorManagement"==te):
					senior=False
					SeniorManagement.append(d['title'])
				#print(d['title'])
		#checks if there is no subratings
		if(worklife):
				WorkLifeBalance.append(0)
		if(culture):
			CultureValues.append(0)
		if(career):
			CareerOpportunities.append(0)
		if(compensation):
			CompensationandBenefits.append(0)
		if(senior):
			SeniorManagement.append(0)
	arrow = driver.find_elements_by_class_name("pagination__ArrowStyle__nextArrow  ")
	try:
		enabled = arrow[0].is_enabled()
		arrow[0].click()
	except StaleElementReferenceException :
		print('StaleElementReferenceException while trying to type password, trying to find element again')
		driver.implicitly_wait(4)
		arrow = driver.find_elements_by_class_name("pagination__ArrowStyle__nextArrow  ")
		enabled = arrow[0].is_enabled()
		if(enabled):
			arrow[0].click()
			driver.implicitly_wait(4)
	except ElementClickInterceptedException:
		enabled = False




df = pd.DataFrame({'Reviewer':Reviewer,'overall rating':overrating,'WorkLifeBalanceSubRating':WorkLifeBalance,'CultureValuesSubRating':CultureValues,'CareerOpportunitiesSubRating':CareerOpportunities,'CompensationandBenefitsSubRating':CompensationandBenefits,'SeniorManagementSubRating':SeniorManagement,'Year':Datearry}) 
df.to_csv('reviews.csv', index=False, encoding='utf-8')
print("done and stored in csv file")
driver.quit()


# #whois -h whois.ripe.net -T route AS34086 -i origin | egrep "route: " | awk 'NR==1{$1=$1;print}'

# awk 'NR==1{$1=$1;print}'