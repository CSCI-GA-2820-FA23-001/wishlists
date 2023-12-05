"""
Environment for Behave Testing
"""
from os import getenv
from selenium import webdriver

WAIT_SECONDS = int(getenv("WAIT_SECONDS", "60"))
BASE_URL = getenv("BASE_URL", "http://localhost:8080")
DRIVER = getenv("DRIVER", "chrome").lower()
API_KEY = getenv("API_KEY", "")


def before_all(context):
    """Executed once before all tests"""
    context.BASE_URL = BASE_URL
    context.WAIT_SECONDS = WAIT_SECONDS
    context.API_KEY = API_KEY
    # Select either Chrome or Firefox
    if "firefox" in DRIVER:
        context.driver = get_firefox()
    else:
        context.driver = get_chrome()
    context.driver.implicitly_wait(context.WAIT_SECONDS)
    context.config.setup_logging()


def after_all(context):
    """Executed after all tests"""
    context.driver.quit()


######################################################################
# Utility functions to create web drivers
######################################################################


def get_chrome():
    """Creates a headless Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)


def get_firefox():
    """Creates a headless Firefox driver"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)
