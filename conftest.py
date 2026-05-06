import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selene import Browser, Config
from dotenv import load_dotenv
from utils import attach

load_dotenv()


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default="https://demoqa.com",
        help="Base URL"
    )
    parser.addoption(
        "--selenoid-url",
        action="store",
        default="https://selenoid.autotests.cloud/wd/hub",
        help="Selenoid"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox", "opera"],
        help="Browser"
    )
    parser.addoption(
        "--browser-version",
        action="store",
        default="128.0",
        help="Browser version"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run in headless mode"
    )
    parser.addoption(
        "--window-size",
        action="store",
        default="1920,1080",
        help="Window size (width,height)"
    )


@pytest.fixture(scope='session', autouse=True)
def load_env():
    pass


@pytest.fixture(scope='function')
def setup_browser(request):
    browser_version = request.config.getoption('--browser-version')
    browser_version = browser_version if browser_version != "" else "128.0"


    options = Options()
    selenoid_capabilities = {
        "browserName": "chrome",
        "browserVersion": browser_version,
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": True
        }
    }
    options.capabilities.update(selenoid_capabilities)

    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')
    selenoid_url = request.config.getoption('--selenoid-url')  # ← из CLI

    driver = webdriver.Remote(
        command_executor=selenoid_url.replace("://", f"://{login}:{password}@"),
        options=options
    )
    browser = Browser(Config(driver))

    yield browser

    attach.add_html(browser)
    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_video(browser)
    browser.quit()