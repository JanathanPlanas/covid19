import datetime
import logging
import os
from pathlib import Path
from time import sleep, time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

# Note: Install the gecko driver in arch with
# sudo pacman -S geckodriver

# https://mobileapps.saude.gov.br/esus-vepi/files/unAFkcaNDeXajurGB7LChj8SgQYS2ptm/1d2b944e065c7304b2754cc386635e38_Download_COVID19_20200430.csv
# https://mobileapps.saude.gov.br/esus-vepi/files/unAFkcaNDeXajurGB7LChj8SgQYS2ptm/b7ac2be9055d75727e05608cb181cc74_Download_COVID19_20200504.csv


def _download_covid_data():
    """Download covid data from the internet"""
    URL = "https://covid.saude.gov.br/"

    # Create a profile and set some preferences to prevent download dialog
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    # The value is the folder where to download to. We are setting the download
    # folder as the current folder of the python interpreter by using 'os.getcwd'
    profile.set_preference('browser.download.dir', os.getcwd())
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    options = Options()
    options.headless = True

    # Create a driver and load the webpage -> This blocks until the page
    # You need to install a driver. I'm using a driver for firefox
    # See here https://selenium-python.readthedocs.io/installation.html#drivers
    driver = webdriver.Firefox(profile, options = options)
    driver.get(URL)

    # The webpage uses shadow-dom in several places, but we can get the download
    # button by get all "button"s from the page
    buttons = driver.find_elements_by_class_name("button")

    # The download button is the third one (index 2)
    download_button = buttons[2]

    # When we run this script we should wait a bit before clicking the download
    # button. I'm waiting 2 seconds to be safe
    sleep(2.0)

    # Click the button
    download_button.click()

    start = time()
    now = time()
    ONE_MINUTE = 60.0
    filepath = Path("arquivo_geral.csv")
    # If we close the driver to quickly the window will be closed before the
    # download is finished. We will check that the file was downloaded and if
    # not sleep for one second.
    while now - start < ONE_MINUTE:
        if filepath.exists():
            logging.info(f"The file was downloaded in {now - start} seconds")
            break
        else:
            sleep(1)
    else:
        # The while loop run until the end and entered the if
        # print("Timeout: the file was not downloaded")
        raise TimeoutError("Could not download the file in under a minute")

    # Sleep before closing the driver to allow time for the download.
    # sleep(5.0)

    # Close the driver -> This closes the firefox window that was opened by selenium
    driver.close()


def _conv_date(x):
    """Convert a string in the `date` column into a `date` object"""
    return datetime.datetime.strptime(x.data, "%Y-%m-%d").date()

def _read_datafile_from_disc(filename="arquivo_geral.csv"):
    data = pd.read_csv(filename, sep=';' , encoding='latin-1')
    data["data"] = data.apply(_conv_date, axis=1)

    return data


def get_covid_data():
    """
    Get the data from the disk if it exists or download it if it does not exist.

    If the data exists on disk, but the most recent date in the file is not
    today, then download new data.
    """
    filepath = Path("arquivo_geral.csv")
    if filepath.exists():
        data = _read_datafile_from_disc()

        today = datetime.datetime.today().date()
        file_is_current = data.data.iloc[-1] == today

        if file_is_current:
            logging.info("There is an existing file on disk with is current: using it")
            return data

        # data is not current
        del data

        logging.warning("The existing file on disk is not current -> We will try downloading a new one")

        # Backup current file
        filepath.rename("arquivo_geral_old.csv")


    # A file does not exist on disk or the one that existed was old and was
    # renamed
    try:
        logging.info("Downloading data from the internet")
        # Download the file
        _download_covid_data()

        # The data in the
        return _read_datafile_from_disc()

    except TimeoutError:
        logging.warn("Could not download data from internet -> An old file will be used instead")

        # Could not download a new file. Let's use the old one in the disk
        return _read_datafile_from_disc("arquivo_geral_old.csv")
