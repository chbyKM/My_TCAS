import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import re

if __name__ == "__main__":
    file_path = r"university.csv"
    data = pd.read_csv(file_path)
    universities = set(data['university'].tolist())
    # print(universities)

    driver = webdriver.Chrome()
    university_locate = []

    for university in universities:  
        driver.get(f'https://www.google.com/maps/search/{university}')
        time.sleep(3)

        try:
            # Locate the meta tag with property "og:image"
            meta_tag = driver.find_element(By.XPATH, '//meta[@property="og:image"]')
            location_url = meta_tag.get_attribute('content')
            
            # Extract latitude and longitude from the URL
            pattern = r"center=([^%]+)%2C([^&]+)"
            matches = re.search(pattern, location_url)
            
            if matches:
                latitude = matches.group(1)
                longitude = matches.group(2)
            else:
                latitude = None
                longitude = None

            # Append the result to the list
            university_locate.append({
                'university': university,
                'latitude': latitude,
                'longitude': longitude
            })
        
        except Exception as e:
            print(f"Error processing university {university}: {e}")
            university_locate.append({
                'university': university,
                'latitude': None,
                'longitude': None
            })

    driver.quit()

    # Convert the result to a DataFrame and save to CSV
    result_df = pd.DataFrame(university_locate)
    result_df.to_csv('university_locations.csv', index=False)
    print(result_df)
