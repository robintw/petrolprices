import time
import os
from datetime import datetime

import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from sqlalchemy import create_engine

def get_petrol_prices(email, password, fuel_type):
    options = Options()
    options.add_argument("no-sandbox")
    options.add_argument("headless")
    options.add_argument("start-maximized")
    options.add_argument("window-size=1900,1080")

    driver = webdriver.Chrome(options=options)

    if fuel_type == 'unleaded':
        fuel_type_id = 2
    elif fuel_type == 'diesel':
        fuel_type_id = 5

    url = f"https://app.petrolprices.com/map?fuelType={fuel_type_id}&brandType=0&resultLimit=0&offset=0&sortType=price&lat=50.9317768&lng=-1.4436572&z=11&d=2"
    driver.get(url)

    email_field = driver.find_element_by_xpath('//*[@id="form-login"]/div[1]/input')
    email_field.clear()
    email_field.send_keys(email)   

    password_field = driver.find_element_by_xpath('//*[@id="passwordInput"]')
    password_field.clear()
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(1)
    try:
        password_field.send_keys(Keys.RETURN)
    except:
        pass

    driver.implicitly_wait(5)

    station_boxes = driver.find_elements_by_class_name('stationDiv')

    data = []

    for station_box in station_boxes:
        name = station_box.find_element_by_class_name('station-name').text[3:].strip()
        price = station_box.find_element_by_class_name('station-price').text[:-1].strip()

        if '-' in price:
            continue

        updated_date = station_box.find_element_by_xpath("div[@class='stationRightSide']/h5[1]").text.strip()

        data.append({'name': name,
                    'price': price,
                    'updated_date': datetime.strptime(updated_date, '%d/%m/%Y'),
                    'fuel_type': fuel_type})

    df = pd.DataFrame(data)

    return df


email = os.environ['PETROL_PRICES_EMAIL']
password = os.environ['PETROL_PRICES_PASSWORD']
mysql_username = os.environ['PETROL_PRICES_MYSQL_USERNAME']
mysql_password = os.environ['PETROL_PRICES_MYSQL_PASSWORD']


eng = create_engine(
    f'mysql://{mysql_username}:{mysql_password}@127.0.0.1/petrolprices')

df = get_petrol_prices(email, password, 'unleaded')
df.to_sql('petrolprices', eng, if_exists='append', index=False)

print(df)
