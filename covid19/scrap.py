import datetime
import glob
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

_data_filename = "dados.xlsx"
_data_filename_old = "dados_old.xlsx"


def _download_covid_data():
    """Download covid data from the internet"""
    URL = "https://covid.saude.gov.br/"

    # Create a profile and set some preferences to prevent download dialog
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)  # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    # The value is the folder where to download to. We are setting the download
    # folder as the current folder of the python interpreter by using 'os.getcwd'
    profile.set_preference('browser.download.dir', os.getcwd())
    profile.set_preference(
        'browser.helperApps.neverAsk.saveToDisk',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    options = Options()
    options.headless = True

    # Create a driver and load the webpage -> This blocks until the page
    # You need to install a driver. I'm using a driver for firefox
    # See here https://selenium-python.readthedocs.io/installation.html#drivers
    # In Arch Linux you can install driver for firefox with `sudo pacman -Sy geckodriver`
    driver = webdriver.Firefox(profile, options=options)
    driver.get(URL)

    # The webpage uses shadow-dom in several places, but we can get the download
    # button by get all "button"s from the page
    # buttons = driver.find_elements_by_class_name("button")

    # Everything in the app (except the navbar) is in a tag with name "ion-content"
    ion_content = driver.find_element_by_tag_name("ion-content")

    # The first "div" in the ion-content tag has the download button
    first_div = ion_content.find_element_by_tag_name("div")

    # There is a single "button" in this div, which is the download button
    download_button = first_div.find_element_by_class_name("button")

    # # The download button is the third one (index 2)
    # download_button = buttons[2]

    # When we run this script we should wait a bit before clicking the download
    # button. I'm waiting 2 seconds to be safe
    sleep(5.0)

    start = time()
    now = time()
    ONE_MINUTE = 60.0

    # Click the button
    download_button.click()

    # Read all ".xlsx" files in the current folder and check if the modification
    # time of any of them is greater than 'start'. The first ".xlsx" file with
    # modification time greater than 'start' is assumed to be the downloaded
    # file. If there is no file with modification date after 'start' then we
    # assume the file was not downloaded yet.
    while (now - start < ONE_MINUTE):
        files = glob.glob("*.xlsx")

        if len(files) == 0:
            logging.info("No files downloaded so far: sleeping for 1 second")
            sleep(1)
            now = time()
            continue

        # Sort files in descending order by timestamp
        files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
        most_current_timestamp = os.path.getmtime(files[0])
        if most_current_timestamp > start:
            # This will break the outer while loop
            os.rename(files[0], _data_filename)

            logging.info("The download was finished!")

            # This will break the while loop
            break
        else:
            logging.info(
                "The download was not finished yet: sleeping for 1 second")
            # If the for loop didn't break, sleep for one second
            now = time()
            sleep(1)
    else:
        # The while loop run until the end -> That means the file was not
        # downloaded within one minute
        raise TimeoutError("Could not download the file in under a minute")

    # Sleep before closing the driver to allow time for the download.
    # sleep(5.0)

    # Close the driver -> This closes the firefox window that was opened by selenium
    driver.close()


# def _conv_date(x):
#     """Convert a string in the `date` column into a `date` object"""
#     try:
#         return datetime.datetime.strptime(x.data, "%Y-%m-%d").date()
#     except TypeError:
#         return None


def _conv_date(x):
    """Convert a string in the `date` column into a `date` object"""
    try:
        return x.data.date()
    except TypeError:
        return None


def read_datafile_from_disc(filename=_data_filename):
    """
    Read the file with data from the disk.

    Note that one extra column is added: "diaDaSemana"

    Parameters
    ----------
    filename : str
        The name of the file with the data

    Returns
    -------
    pd.Dataframe
        A pandas Dataframe with the data
    """
    # data = pd.read_csv(filename, sep=';' , encoding='latin-1')
    data = pd.read_excel(filename)
    data["data"] = data.apply(_conv_date, axis=1)

    # xxxxxxxxxx Cleaning xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # Drop lines without a date (these are empty lines in the data)
    data = data[~data.data.isna()]
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    weekDays = ("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado",
                "Domingo")
    data["diaDaSemana"] = data.apply(lambda x: weekDays[x.data.weekday()],
                                     axis=1)

    return data


def get_covid_data():
    """
    Get the data from the disk if it exists or download it if it does not exist.

    If the data exists on disk, but the most recent date in the file is not
    today, then download new data.
    """
    download_log_file = "last_download_time.log"
    format_string = "%Y-%m-%d, %H:%M:%S"

    filepath = Path(_data_filename)
    if filepath.exists():
        data = read_datafile_from_disc()

        today = datetime.datetime.today().date()
        file_is_current = data.data.iloc[-1] == today

        if file_is_current:
            logging.info(
                "There is an existing file on disk and it is current: using it"
            )
            return data
        else:
            # If the file is not current check the log file to see if it was
            # downloaded lesss the one hour ago
            try:
                with open(download_log_file, mode="r") as f:
                    last_download_time = datetime.datetime.strptime(
                        f.read(), format_string)
                    now = datetime.datetime.now()
                    now - last_download_time
                    if (now - last_download_time) < datetime.timedelta(
                            minutes=60):
                        # The file is not current, but it was downloaded less
                        # than one hour ago. Let's use it
                        logging.info(
                            "The existing file on disk is not current, but it was downloaded less than one hour ago and we will use it"
                        )
                        return data
            except FileNotFoundError:
                pass

        # If we reach this point the file exists in the disk, but it is not
        # current and it was downloaded more then one hour ago -> Let's try
        # downloading a new file then
        del data

        logging.warning(
            "The existing file on disk is not current -> We will try downloading a new one"
        )

        # Backup current file
        filepath.rename(_data_filename_old)

    # A file does not exist on disk or the one that existed was old and was
    # renamed
    try:
        logging.info("Downloading data from the internet")
        # Download the file
        _download_covid_data()

        # Save the current time to a log file
        with open(download_log_file, mode="w") as f:
            now = datetime.datetime.now()
            f.write(now.strftime(format_string))

        # The data in the
        data = read_datafile_from_disc()
        return data

    except TimeoutError:
        logging.warning("Could not download data from internet")

        filepath = Path(_data_filename_old)
        if filepath.exists():
            # Could not download a new file. Let's use the old one in the disk
            logging.warning("Using an old data file")
            return read_datafile_from_disc(_data_filename_old)
        else:
            raise TimeoutError("Could not download data from the internet")
