import time

from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)


def create_webdriver_options():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    return options


# Scraping 영업 요일/시간
def get_business_hours(m_article):
    try:
        # 영업정보 상세보기 버튼 클릭
        m_article.find_element(
            by=By.CSS_SELECTOR,
            value='div.cont_essential > div.details_placeinfo ' +
                  'div.location_detail.openhour_wrap > div.location_present '
                  'a.btn_more'
        ).click()

        operation_list = m_article.find_element(
            by=By.CSS_SELECTOR,
            value='div.details_placeinfo div.fold_floor > div.inner_floor'
        )
        opening_hours = operation_list.find_element(by=By.CSS_SELECTOR, value='ul:nth-child(2)').text
        closing_hours = operation_list.find_element(by=By.CSS_SELECTOR, value='ul:nth-child(4)').text

        return opening_hours, closing_hours
    except NoSuchElementException:
        try:
            opening_hours = m_article.find_element(
                by=By.CSS_SELECTOR,
                value='div.location_detail.openhour_wrap ' +
                      'ul.list_operation span.txt_operation'
            ).text
            return opening_hours, None
        except NoSuchElementException:
            return None, None


# Scraping homepage url
def get_homepage_url(m_article):
    try:
        return m_article.find_element(
            by=By.CSS_SELECTOR,
            value='div.cont_essential > div.details_placeinfo > div.placeinfo_default.placeinfo_homepage ' +
                  'a.link_homepage'
        ).text
    except NoSuchElementException:
        return None


@app.route('/api/scrap/places')
def get_kakao_place_info():  # put application's code here
    page_url = request.args.get("page_url")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=create_webdriver_options()
    )

    driver.get(url=page_url)
    driver.implicitly_wait(time_to_wait=0)

    time.sleep(2.5)

    m_article = driver.find_element(by=By.CSS_SELECTOR, value="#mArticle")

    opening_hours, closing_hours = get_business_hours(m_article)
    homepage_url = get_homepage_url(m_article)

    return jsonify({
        'opening_hours': opening_hours,
        'closing_hours': closing_hours,
        'homepage_url': homepage_url
    })


if __name__ == '__main__':
    app.run()
