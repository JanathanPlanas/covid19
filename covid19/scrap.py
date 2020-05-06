import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.firefox.options import Options

# Note: Install the gecko driver in arch with
# sudo pacman -S geckodriver

# https://mobileapps.saude.gov.br/esus-vepi/files/unAFkcaNDeXajurGB7LChj8SgQYS2ptm/1d2b944e065c7304b2754cc386635e38_Download_COVID19_20200430.csv
# https://mobileapps.saude.gov.br/esus-vepi/files/unAFkcaNDeXajurGB7LChj8SgQYS2ptm/b7ac2be9055d75727e05608cb181cc74_Download_COVID19_20200504.csv


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

# Sleep before closing the driver to allow time for the download. If we close
# the driver to quickly the window will be closed before the download is
# finished
sleep(3.0)

# Close the driver -> This closes the firefox window that was opened by selenium
driver.close()
