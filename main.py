from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


try:
driver.get(full_url)
        driver.implicitly_wait(10)

        div_principal = driver.find_element(By.CLASS_NAME, 'baTaGaYf')
        html_div = div_principal.find_element(By.CSS_SELECTOR, 'div.bubble-element.HTML.baTaHaAaH')

        # Trocar para o iframe
        iframe = html_div.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)

        
# Função para encontrar elementos com retry
        def find_element_with_retry(by, value, retries=3):
            for _ in range(retries):
        def find_element_with_retry(by, value, retries=3, wait_time=1):
            for attempt in range(retries):
try:
return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
except StaleElementReferenceException:
                    time.sleep(1)  # Esperar antes de tentar novamente
            raise Exception(f"Não foi possível encontrar o elemento {value}")
                    if attempt < retries - 1:  # Se não for a última tentativa, espere e tente novamente
                        time.sleep(wait_time)
                    else:
                        raise Exception(f"Não foi possível encontrar o elemento {value} após {retries} tentativas.")
                except TimeoutException:
                    raise Exception(f"Tempo esgotado para encontrar o elemento {value}.")
        
        div_principal = find_element_with_retry(By.CLASS_NAME, 'baTaGaYf')
        html_div = find_element_with_retry(By.CSS_SELECTOR, 'div.bubble-element.HTML.baTaHaAaH')

        # Trocar para o iframe
        iframe = find_element_with_retry(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)

tradingview_div = find_element_with_retry(By.CSS_SELECTOR, 'div.tradingview-widget-container')
tradingview_iframe = find_element_with_retry(By.TAG_NAME, 'iframe', retries=5)

fundamental_sections = fundamentals_div.find_elements(By.CSS_SELECTOR, '.tv-widget-fundamentals__item--legacy-bg')

for section in fundamental_sections:
            title_element = section.find_element(By.CSS_SELECTOR, '.tv-widget-fundamentals__title')
            # Repetir a busca do título, pois o contexto do DOM pode mudar
            title_element = find_element_with_retry(By.CSS_SELECTOR, '.tv-widget-fundamentals__title')
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
