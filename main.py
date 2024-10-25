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
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException,
    StaleElementReferenceException
)
import re
import time

app = FastAPI()

# Função para criar o Selenium WebDriver
def create_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-logging")
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Função de scraping com Selenium
def scrape_data(url: str, cod: str):
    full_url = f"{url}?cod={cod}"
    driver = create_driver()
    output = {}

    try:
        driver.get(full_url)
        driver.implicitly_wait(10)

        # Função para encontrar elementos com retry
        def find_element_with_retry(by, value, retries=3):
            for attempt in range(retries):
                try:
                    return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
                except StaleElementReferenceException:
                    if attempt < retries - 1:  # Se não for a última tentativa, espere e tente novamente
                        time.sleep(1)  # Aguardar antes da próxima tentativa
                    else:
                        raise Exception(f"Não foi possível encontrar o elemento {value} após {retries} tentativas.")

        div_principal = find_element_with_retry(By.CLASS_NAME, 'baTaGaYf')
        html_div = find_element_with_retry(By.CSS_SELECTOR, 'div.bubble-element.HTML.baTaHaAaH')

        # Trocar para o iframe
        iframe = find_element_with_retry(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)

        tradingview_div = find_element_with_retry(By.CSS_SELECTOR, 'div.tradingview-widget-container')
        tradingview_iframe = find_element_with_retry(By.TAG_NAME, 'iframe', retries=5)

        driver.switch_to.frame(tradingview_iframe)
        fundamentals_div = find_element_with_retry(By.CSS_SELECTOR, 'div.tv-widget-fundamentals')

        fundamental_sections = fundamentals_div.find_elements(By.CSS_SELECTOR, '.tv-widget-fundamentals__item--legacy-bg')

        for section in fundamental_sections:
            title_element = find_element_with_retry(By.CSS_SELECTOR, '.tv-widget-fundamentals__title')  # Atualiza a busca
            title_text = title_element.text.strip()

            if title_text not in output:
                output[title_text] = []

            value_labels = section.find_elements(By.CSS_SELECTOR, '.tv-widget-fundamentals__label')
            value_elements = section.find_elements(By.CSS_SELECTOR, '.tv-widget-fundamentals__value')

            for label, value in zip(value_labels, value_elements):
                label_text = label.text.strip()
                value_text = value.text.strip()
                value_cleaned = re.sub(r'[\u202a\u202c\u202f]', '', value_text)
                value_cleaned = value_cleaned.replace("\u2212", "-").replace("\u2014", "-")

                output[title_text].append({
                    "label": label_text,
                    "valor": value_cleaned
                })

    except Exception as e:
        output["error"] = str(e)

    finally:
        driver.quit()

    return output

# Rota FastAPI para iniciar o scraping, com parâmetros URL e cod
@app.get("/scrape")
def scrape_endpoint(url: str, cod: str):
    data = scrape_data(url, cod)
    return data
