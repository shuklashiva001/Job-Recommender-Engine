
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import settings


df = pd.DataFrame(columns=["Link","Location","Title","Company","Description"])

driver = webdriver.Chrome(settings.chrome_driver_location)

job_search_words = settings.keyword_to_search_for_scrape

job_locations = settings.indian_locations_to_search
map = {}

for location in job_locations:
    try:
        i = 1
        for to in range(1,10):
            temp_link = url='https://www.naukri.com/'+ job_search_words + '-jobs-in-' + location + '-' + str(i)
            i = i + 1
            print(temp_link)
            driver.set_page_load_timeout(30)
            webdriver.DesiredCapabilities.CHROME["unexpectedAlertBehaviour"] = "accept"

            current_link = driver.current_url
            if current_link in map:
                break
            map[current_link] = "Found"

            driver.get(temp_link)
            driver.implicitly_wait(5)
            driver.set_page_load_timeout(30)
            webdriver.DesiredCapabilities.CHROME["unexpectedAlertBehaviour"] = "accept"

            # Collecting all jobs
            All_jobs = driver.find_elements_by_class_name('jobTuple')
            jobs_url = []

            # Iterating through all All_jobs And Collecting URL of All jobs in list
            for jobs in All_jobs:


                soup = BeautifulSoup((jobs.get_attribute('innerHTML')),'html.parser')
                href_tag = soup.find(href = True)
                try:
                    jobs_url.append(href_tag['href'])
                    driver.implicitly_wait(2)
                except Exception as e:
                    print(title,e,sep=" ")
            #print(jobs_url)
            # Iterating through all URL and scrapping data from it
            for url in jobs_url:

                driver.get(url)
                # Be kind and don't hit indeed server so hard
                driver.implicitly_wait(5)
                temp1 = driver.find_elements_by_class_name('leftSec')


                for temp in temp1:

                    result_html = temp.get_attribute('innerHTML')
                    soup = BeautifulSoup(result_html,'html.parser')

                    # Title
                    try:
                        title = soup.find('h1',class_='jd-header-title').text.replace("\n","")
                    except:
                        title = 'none'

                    # Company Name
                    try:
                        company_name = soup.find("a",class_='pad-rt-8').text.replace('\n','')
                    except:
                        company_name = 'none'

                    # Location
                    try:
                        location = soup.find("span",class_="location").text.replace("\n","")
                    except:
                        location = "none"


                    # Description
                    try:
                        desc = soup.find("section",class_="job-desc").text
                    except:
                        desc = "none"

                    # Appending data into data frames
                    df = df.append({'Link':url , 'Location':location , 'Title':title , 'Company':company_name , 'Description':desc},ignore_index = True)
    except Exception as e:
        print("page complete  ",e)

    # Storing data frames into csv file
df.to_csv("new_naukri-dot-com.csv",index=False)
