import random, json
import numpy as np
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time, os
import settings
from settings import page_record_limit, num_pages


def load_job_info_using_location(search_location):
    '''
    Scrape from web or read from saved file
    Input: 
        search_location - search job in a certain city. Input from commond line.
    Output: 
        jobs_info - a list that has info of each job i.e. link, location, title, company, salary, desc
    '''
    exists = os.path.isfile(settings.job_info_file)
    if exists:
        with open(settings.job_info_file, 'r') as fp:
            jobs_info = json.load(fp)            
    else:
        jobs_info = scrape_from_location_from_web(search_location)
    return jobs_info
        
def scrape_from_location_from_web(search_location):
    '''
    Scrape jobs from indeed.co.in
    Input: 
        search_location - search job in a certain city. Input from commond line.
    Output: 
        jobs_info - a list that has info of each job i.e. link, location, title, company, salary, desc
    '''

    links_fetched = []
    start = time.time() # start time
    driver = webdriver.Chrome(settings.chrome_driver_location)
    job_locations = settings.indian_locations_to_search
    if (len(search_location) > 0):
        job_locations = [search_location]
        
    for location in job_locations:
        url = 'https://www.indeed.co.in/jobs?q=' + settings.keyword_to_search_for_scrape + '&l=' \
              + location + '&limit=' + str(page_record_limit) + '&fromage=' + str(settings.old_post_limit_days)
        driver.set_page_load_timeout(15)
        webdriver.DesiredCapabilities.CHROME["unexpectedAlertBehaviour"] = "accept"
        driver.get(url)
        time.sleep(3)
        for i in range(num_pages):            
            try:
                for job_each in driver.find_elements_by_xpath('//*[@data-tn-element="jobTitle"]'):
                    job_link = job_each.get_attribute('href')
                    links_fetched.append({'location':location, 'job_link':job_link})                
                print ('scraping {} page {}'.format(location, i+1))
                driver.find_element_by_link_text('Next »').click()
            except NoSuchElementException:
                print ("{} finished".format(location))
                break        
            time.sleep(3)
    with open(settings.job_link_metadata_file, 'w') as fp:
        json.dump(links_fetched, fp)
        
    jobs_info = []
    for single_link in links_fetched:
        m = random.randint(1,5)
        time.sleep(m) 
        link = single_link['job_link']
        driver.get(link)   
        location = single_link['location']
        title = driver.find_element_by_xpath('//*[@class="icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title"]').text
        company = driver.find_element_by_xpath('//*[@class="icl-u-lg-mr--sm icl-u-xs-mr--xs"]').text
        if (len(driver.find_elements_by_xpath('//*[@class="jobsearch-JobMetadataHeader-item "]'))==0):
            salary = np.nan 
        else:
            salary = driver.find_element_by_xpath('//*[@class="jobsearch-JobMetadataHeader-item "]').text
        desc = driver.find_element_by_xpath('//*[@class="jobsearch-JobComponent-description  icl-u-xs-mt--md  "]').text
        jobs_info.append({'link':link, 'location':location, 'title':title, 'company':company, 'salary':salary, 'desc':desc})
    with open(settings.job_info_file, 'w') as fp:
        json.dump(jobs_info, fp)
    driver.quit()
    end = time.time()
    scraping_time = (end - start) / 60.
    print('Took {0:.2f} minutes scraping {1:d} data scientist/engineer/analyst jobs'.format(scraping_time, len(jobs_info)))
    return jobs_info
