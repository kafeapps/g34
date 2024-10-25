from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
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
def scrape_data(url: str, cod: str) -> Dict:
    full_url = f"{url}?cod={cod}"
    driver = create_driver()
    output = {}
    max_retries = 3
    attempt = 0

    while attempt < max_retries:
        try:
            driver.get(full_url)
            driver.implicitly_wait(10)

            # Trocar para o iframe
            iframe = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
            driver.switch_to.frame(iframe)

            # Encontrar a div que contém os fundamentos
            fundamentals_div = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tv-widget-fundamentals')))

            # Obter todas as seções de fundamentos
            fundamental_sections = fundamentals_div.find_elements(By.CSS_SELECTOR, '.tv-widget-fundamentals__item--legacy-bg')

            # Iterar sobre cada seção de fundamentos
            for section in fundamental_sections:
                # Obter o título da seção
                title_element = section.find_element(By.CSS_SELECTOR, '.tv-widget-fundamentals__title')
                title_text = title_element.text.strip()

                # Inicializar lista para armazenar os valores da seção
                if title_text not in output:
                    output[title_text] = []

                # Obter todas as linhas de valores dentro da seção
                value_rows = section.find_elements(By.CSS_SELECTOR, '.tv-widget-fundamentals__row')

                for row in value_rows:
                    label_element = row.find_element(By.CSS_SELECTOR, '.tv-widget-fundamentals__label')
                    value_element = row.find_element(By.CSS_SELECTOR, '.tv-widget-fundamentals__value')

                    label_text = label_element.text.strip()
                    value_text = value_element.text.strip()

                    # Limpar valores
                    value_cleaned = re.sub(r'[\u202a\u202c\u202f]', '', value_text)
                    value_cleaned = value_cleaned.replace("\u2212", "-").replace("\u2014", "-")

                    # Adicionar a label e valor ao output
                    output[title_text].append({
                        "label": label_text,
                        "valor": value_cleaned
                    })

            break  # Se o código for executado com sucesso, sai do loop

        except (Exception) as e:
            attempt += 1
            output["error"] = str(e)
            time.sleep(2)  # Aguardar antes da próxima tentativa

    driver.quit()
    return output

# Rota FastAPI para iniciar o scraping, com parâmetros URL e cod
@app.get("/scrape")
def scrape_endpoint(url: str, cod: str):
    data = scrape_data(url, cod)
    return data
