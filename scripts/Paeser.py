import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver


def clean_strange_symbols(str_) -> float:
    str_ = str_.replace('\u2006', ' ')
    first_point = str_ .find('.')
    if first_point != -1:
        str_ = str_[:first_point + 2]
    str_  = re.sub(r"[^\d.-]", "", str_.replace(",", "."))
    
    return float(str_)

def parsing_yandex_market(req, driver, df, n_scroll = 10):
    search_input = driver.find_element(By.ID, "header-search")
    search_input.click()
    search_input.clear()
    search_input.send_keys(req)
    search_input.send_keys(Keys.RETURN)
    for _ in range(n_scroll):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver.execute_script("window.scrollBy(0, -200)")
        time.sleep(1.2)
    
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, "html.parser")
    items = soup.find_all('div', class_="_1H-VK")

    for item in items:
        try:
            # Название товара
            title = item.find('div', class_='cia-cs _1pFpJ').text.strip()
            
            # Цена
            price = clean_strange_symbols(item.find('span', class_='ds-valueLine DPiFo').text.strip())
            
            # Рейтинг
            rating = item.find('span', class_='ds-text ds-text_weight_bold ds-text_color_text-rating ds-text_proportional ds-text_typography_text ds-rating__value ds-text_text_tight ds-text_text_bold').text.strip()
            reviews = clean_strange_symbols(item.find('span', class_='ds-text ds-text_lineClamp_1 ds-text_weight_reg ds-text_color_text-secondary ds-text_proportional ds-text_typography_text ds-text_text_tight ds-text_text_reg ds-text_lineClamp').text.strip())

            # Ссылка на товар
            link = item.find('a', href=lambda href: href and href.startswith('/'))['href']
            full_link = f"https://market.yandex.ru{link}" if link.startswith('/') else link
            
        except:
            continue
        
        df.loc[len(df)] = [title, price, rating, reviews, full_link, req]
        
    return df


def create_driver():
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("start-maximized")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)

    return driver
