import os
import time
from datetime import datetime, timedelta
import logging
from dateutil import parser
from dateutil.parser import UnknownTimezoneWarning
import warnings
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


def _split_pair(s, splitter):
    if isinstance(s, str):
        t = s.split(splitter)
        if len(t) == 2:
            return t[0], t[1]
    return None, None


def _is_float(s=None):
    if s is not None:
        l = list(s)
        if len(l) > 1 and l[0] == '-':
            s = s[1:]
        return s.replace('.', '', 1).isdigit()
    else:
        return False


def _get_text_from_element(element):
    if isinstance(element, WebElement):
        return element.text
    else:
        return None


def _date_parse(s):
    """ Converts a string to a timestamp int """
    old_time = (datetime.now() + timedelta(days=-365)).timestamp()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UnknownTimezoneWarning)
        for x in [s, s.replace('.5', '', 1)]:
            try:
                t = parser.parse(x, fuzzy=True)
                if t.timestamp() < old_time:
                    raise ValueError
                break
            except (ValueError, OverflowError):
                t = datetime.fromtimestamp(old_time)
    return int(t.timestamp())


def get_driver(path=None):
    if path is None:
        if 'nt' in os.name:
            path = r'C:\Selenium\ChromeDriver\chromedriver'
        else:
            path = r'/usr/local/bin/chromedriver'
    options=webdriver.ChromeOptions()
    options.add_argument("headless")
    return webdriver.Chrome(executable_path=path,
                            chrome_options=options)


def get_from_marine(future, driver, imo):
    ship_name, time_of_latest_position, lat, lon = None, None, None, None
    retry, dwt = 0, 0
    area = ''
    ret = 'not_found'
    params = '?asset_type=vessels&columns=time_of_latest_position,area,lat_of_latest_position,lon_of_latest_position,dwt&quicksearch|begins|quicksearch={}'.format(imo)
    url = r'https://www.marinetraffic.com/en/data/' + params

    for _ in range(3):
        try:
            driver.get(url)
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                'div[col-id="time_of_latest_position"] div.ag-cell-content'))
            )
            time_of_latest_position = _get_text_from_element(element)
            if time_of_latest_position is not None:
                lat = _get_text_from_element(driver.find_element(
                    by=By.CSS_SELECTOR, value='div[col-id="lat_of_latest_position"] div.ag-cell-content div'))
                lon = _get_text_from_element(driver.find_element(
                    by=By.CSS_SELECTOR, value='div[col-id="lon_of_latest_position"] div.ag-cell-content div'))

                area = _get_text_from_element(driver.find_element(
                    by=By.CSS_SELECTOR, value='div[col-id="area"] div.ag-cell-content a'))
                dwt_s = _get_text_from_element(driver.find_element(
                    by=By.CSS_SELECTOR, value='div[col-id="dwt"] div.ag-cell-content div'))

                if area is None:
                    area = ''
                if isinstance(dwt_s, str) and dwt_s.isdigit():
                    dwt = int(dwt_s)
                break
        except (TimeoutException, NoSuchElementException):
            pass
        except Exception as err:
            logging.error(err)
            ret = 'error'
            break
        time.sleep(5)

    if None not in [time_of_latest_position, lat, lon]:
        future.set_result([(imo, lat, lon, time_of_latest_position, area, _date_parse(time_of_latest_position)),
                           (area, dwt)])
    else:
        future.set_result([(ret, ),
                           None])
