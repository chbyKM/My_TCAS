import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd


if __name__ == "__main__":
    url = "https://course.mytcas.com/"
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    
    search_bar = driver.find_element(By.ID, 'search')
    search_bar.send_keys('วิศวกรรม')

    universities = []
    uni_elements = driver.find_elements(By.XPATH, '//*[@id="results"]/ul/li/a/span/span')
    for elem in uni_elements:
        universities.append(elem.text)

    links = []
    link_elements = driver.find_elements(By.XPATH, '//*[@id="results"]/ul/li/a')
    for elem in link_elements:
        links.append(elem.get_attribute('href'))

    eng_programs_list = []
    for i in range(len(links)):
        driver.get(links[i])
        time.sleep(2)
        
        program = driver.find_element(By.XPATH, '//*[@id="root"]/main/div[2]/div/span/span/h1').text
        details = driver.find_elements(By.XPATH, '//*[@id="overview"]/dl/dt')
        sub_details = driver.find_elements(By.XPATH, '//*[@id="overview"]/dl/dd')
        
        all_detail = dict()
        for j in range(len(details)):
            all_detail[details[j].text] = sub_details[j].text
        
        eng_programs = {
            'name': program,
            'university': universities[i], 
        }
        eng_programs.update(all_detail)
        eng_programs_list.append(eng_programs)

    driver.quit()
    
    output_df = pd.DataFrame(eng_programs_list)
    output_df.to_csv('university.csv')
