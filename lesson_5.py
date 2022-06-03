from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient

service = Service('./chromedriver')
options = Options()
options.add_argument('start-maximized')
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(10)
driver.get('https://account.mail.ru/login')

client = MongoClient('127.0.0.1', 27017)
db = client['emails']
emails_info = db.emails_info

email_links = set()


def login():
    authorisation = driver.find_element(By.NAME, 'username')
    authorisation.send_keys('study.ai_172@mail.ru')
    authorisation.send_keys(Keys.ENTER)

    authorisation = driver.find_element(By.NAME, 'password')
    authorisation.send_keys('NextPassword172#')
    authorisation.send_keys(Keys.ENTER)


def email_count():
    button = driver.find_element(By.CLASS_NAME, 'button2__explanation')
    button.click()
    emails = driver.find_element(By.XPATH, "//span[contains(@class,'button2_select-all')]//span[@class='button2__txt']")
    emails_amount = int(emails.text)
    return emails_amount


def email_to_db(emails_amount):
    while len(email_links) != emails_amount:
        emails = driver.find_elements(By.XPATH, "//a[contains(@class,'llc_active')]")
        for email in emails:
            email_links.add(email.get_attribute("href"))
        actions = ActionChains(driver)
        actions.move_to_element(emails[-1])
        actions.perform()

    for email_link in email_links:
        email_info = {}
        driver.get(email_link)
        email_info['from'] = driver.find_element(By.CLASS_NAME, 'letter-contact').get_attribute('title')
        email_info['date'] = driver.find_element(By.CLASS_NAME, 'letter__date').text
        email_info['subject'] = driver.find_element(By.CLASS_NAME, 'thread-subject').text
        email_info['message'] = driver.find_element(By.CLASS_NAME, 'letter__body').text
        emails_info.insert_one(email_info)


login()
email_to_db(email_count())
