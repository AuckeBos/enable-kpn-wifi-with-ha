from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import find_dotenv, load_dotenv
import os


def load_env():
    """
    Load the environment variables from the .env file
    """
    load_dotenv(find_dotenv())


def get_browser(headless=True):
    """
    Get the browser to use
    """
    if not headless:
        driver = webdriver.Firefox()
    else:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
    return driver


def navigate(browser):
    """
    Navigate to the right page:
    - Go to login, set password and click login
    - Go to Settings page
    """
    browser.get(url)

    password = os.getenv("ADMIN_PASS")

    # Login page and login
    password_input = WebDriverWait(browser, 100).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    password_input.send_keys(password)

    button = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, "button-blue"))
    )
    button.click()

    # Go to settings page
    button = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, "my-sagemcom-box"))
    )

    browser.get("http://mijnmodem.kpn/2.0/gui/#/wifi/2.4GHz/priv/settings")


def find_element_robust(browser, element_id):
    """
    A helper function to find an element on the page.
    Used when untill doesn't work
    """
    while True:
        try:
            return browser.find_element(By.ID, element_id)
        except:
            pass


def wifi_is_enabled(driver) -> bool:
    """
    The wifi is enabled when the status indicator does not have the class "onoffswitch-disabled"
    """
    indicator = find_element_robust(driver, html_ids["status_indicator"])
    return indicator.get_attribute("class").find(disabled_class) == -1


def toggle_wifi(browser):
    """
    Toggle the wifi on or off. Find the switch, click it.
    Print the status change. Then wait for the status indicator to change.
    """
    was_enabled = wifi_is_enabled(browser)
    switch = find_element_robust(browser, html_ids["switch"])
    switch.click()
    # Wait max 10 seconds the status indicator to change
    indicator = find_element_robust(browser, "wifiGeneralTip1")
    end_time = time.time() + 10
    while time.time() < end_time:
        if (was_enabled and not wifi_is_enabled(browser)) or (
            not was_enabled and wifi_is_enabled(browser)
        ):
            return True
    return False


# Define the IDs of the elements to be scraped
html_ids = {"status_indicator": "wifiGeneralTip1", "switch": "enable-wifi-24"}

# Define the URL of the page to be scraped
url = "http://mijnmodem.kpn/2.0/gui/#/login/"
# This class is present on the status indicator when wifi is disabled
disabled_class = "onoffswitch-disabled"

if __name__ == "__main__":
    load_env()
    browser = get_browser()
    navigate(browser)
    # Safety check
    time.sleep(5)
    if toggle_wifi(browser):
        print(f"Wifi is now {'enabled' if wifi_is_enabled(browser) else 'disabled'}")
    else:
        print("Could not toggle wifi")

    browser.quit()
