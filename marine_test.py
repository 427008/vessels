from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import os

logging.basicConfig(
    filename=r'{0}/Data/test_error.log'.format(os.getcwd()), level=logging.INFO, format='%(asctime)s %(message)s')

# if 'nt' in os.name:
#     path = r'C:\Selenium\ChromeDriver\chromedriver'
# else:

path = r'/usr/local/bin/chromedriver'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('no-sandbox')
chromeOptions.add_argument('headless')
driver = webdriver.Chrome(executable_path=path, chrome_options=chromeOptions)
logging.info(driver)

site = r'https://www.marinetraffic.com/en/data/'
params = r'?asset_type=vessels&columns=shipname,imo,time_of_latest_position,lat_of_latest_position,lon_of_latest_position&quicksearch|begins|quicksearch={}'
imo = '9738894'
url = site + params.format(imo)
logging.info(url)

driver.get(url)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[col-id="time_of_latest_position"] div.ag-cell-content'))
)

time_of_latest_position = element.text
lat_of_latest_position = driver.find_element(by=By.CSS_SELECTOR,
                                              value='div[col-id="lat_of_latest_position"] div.ag-cell-content div').text
lon_of_latest_position = driver.find_element(by=By.CSS_SELECTOR,
                                              value='div[col-id="lon_of_latest_position"] div.ag-cell-content div').text

logging.info((imo, time_of_latest_position, lat_of_latest_position, lon_of_latest_position))
