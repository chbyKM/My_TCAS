import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
import json
import csv
import pandas as pd

if __name__ == "__main__":
    url = "https://course.mytcas.com/"
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    search_bar = driver.find_element(By.ID, 'search')
    search_bar.send_keys('วิศวกรรม')

    universities = []
    uni = driver.find_elements(By.XPATH, '//*[@id="results"]/ul/li/a/span/span')
    for i in uni:
        universities.append(i.text)

    links = []
    link = driver.find_elements(By.XPATH, '//*[@id="results"]/ul/li/a')
    for i in link:
        links.append(i.get_attribute('href'))

    # driver.close()
    # for i in range(len(universities)):
    #     print(universities[i], '-',links[i] )


    eng_programs = dict()
    for i in range(len(universities)):
        driver.get(links[i])
        time.sleep(2)
        program = driver.find_element(By.XPATH, '//*[@id="root"]/main/div[2]/div/span/span/h1').text
        details = driver.find_elements(By.XPATH, '//*[@id="overview"]/dl/dt')
        sub_details = driver.find_elements(By.XPATH, '//*[@id="overview"]/dl/dd')
        detail = dict()
        for j in range(len(details)):
            detail[details[j].text] = sub_details[j].text
        eng_programs[f"eng_program{i}"] = {
            "name": program,
            "university": universities[i],
            "details": detail,
        }
    driver.close()

df = pd.DataFrame.from_dict(eng_programs)
df.to_csv(r'university.csv', index=False, header=True)

