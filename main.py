from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException

app = FastAPI()

# Function to create the Selenium WebDriver
def create_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-logging")
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Scraping function with Selenium
def scrape_data(url: str, cod: str):
    # Construct full URL
    full_url = f"{url}?cod={cod}"
    driver = create_driver()  # Use the new create_driver function
    output = {}

    try:
        # Access the dynamic page
        driver.get(full_url)

        # Wait for the page to load
        driver.implicitly_wait(10)

        # Capture the main div with the desired class
        div_principal = driver.find_element(By.CLASS_NAME, 'baTaGaYf')

        # Find the new class inside the main div
        html_div = div_principal.find_element(By.CSS_SELECTOR, 'div.bubble-element.HTML.baTaHaAaH')

        # Switch to the iframe within html_div
        iframe = html_div.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)

        # Wait for the tradingview-widget-container div inside the iframe
        tradingview_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tradingview-widget-container'))
        )

        # Wait for the iframe within tradingview-widget-container
        tradingview_iframe = WebDriverWait(tradingview_div, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
        )
        driver.switch_to.frame(tradingview_iframe)

        # Wait for the div containing fundamentals
        fundamentals_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tv-widget-fundamentals'))
        )

        # Extract all sections within the fundamentals div
        fundamental_sections = fundamentals_div.find_elements(By.CSS_SELECTOR,
                                                              '.tv-widget-fundamentals__item--legacy-bg')

        for section in fundamental_sections:
            # Get the title of each section
            title_element = section.find_element(By.CSS_SELECTOR, '.tv-widget-fundamentals__title')
            title_text = title_element.text.strip()

            # Initialize the section in the output if it doesn't exist
            if title_text not in output:
                output[title_text] = []

            # Get all value elements in the section
            value_elements = section.find_elements(By.CSS_SELECTOR, '.tv-widget-fundamentals__value')

            # If there are value elements, collect them
            for value in value_elements:
                value_text = value.text.strip()
                output[title_text].append({
                    "nome": title_text,
                    "valor": value_text
                })

    except Exception as e:
        output["error"] = str(e)

    finally:
        # Close the browser
        driver.quit()

    return output


# FastAPI route to initiate scraping, with URL and cod parameters
@app.get("/scrape")
def scrape_endpoint(url: str, cod: str):
    data = scrape_data(url, cod)
    return data
