import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from helper import click_menu, add_book_helper, add_author_helper

url = "http://localhost:8001/index.html"

@pytest.fixture(scope="session")
def driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--headless=new")
    drv = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    drv.implicitly_wait(3)
    yield drv
    drv.quit()


def test_01_page_loads(driver):
    """
    1. Сторінка відкривається, основні елементи інтерфейсу доступні.

    Feature: Відкриття головної сторінки
    Scenario: Користувач відкриває головну сторінку
        Given веб-браузер відкрито
        When користувач переходить на сторінку бібліотеки
        Then сторінка завантажується і відображаються заголовок, поле пошуку та меню
    """
    driver.get(url)
    assert "Библиотека" in driver.title
    assert driver.find_element(By.TAG_NAME, "h1").is_displayed()
    assert driver.find_element(By.ID, "mainInput").is_displayed()
    assert driver.find_element(By.CLASS_NAME, "menu-btn").is_displayed()


def test_02_switch_to_authors(driver):
    """
    2. Перемикання на авторів змінює заголовок таблиці.

    Feature: Перемикання на вкладку "Автори"
    Scenario: Користувач відкриває список авторів
        Given користувач знаходиться на сторінці "Книги"
        When користувач натискає кнопку "Автори"
        Then заголовок таблиці змінюється і містить колонку "Email"
    """
    driver.get(url)
    click_menu(driver, "Автори")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//th[contains(., 'Email')]")))
    headers = driver.find_element(By.ID, "tableHeader").text
    assert "Email" in headers


def test_03_add_author(driver):
    """
    3. Додавання автора.

    Feature: Додавання нового автора
    Scenario: Успішне додавання автора
        Given користувач відкрив вкладку "Автори"
        When користувач додає нового автора з унікальним ім'ям та email
        Then автор з’являється у таблиці авторів
    """
    driver.get(url)
    click_menu(driver, "Автори")

    unique_name = f"TestAuth_{int(time.time())}"
    add_author_helper(driver, unique_name, "User", f"{unique_name}@test.com")

    page_source = driver.find_element(By.ID, "tableBody").text
    assert unique_name in page_source


def test_04_add_book(driver):
    """
    4. Додавання книги.

    Feature: Додавання нової книги
    Scenario: Успішне додавання книги
        Given користувач знаходиться на вкладці "Книги"
        When користувач додає нову книгу з унікальною назвою
        Then книга з’являється у таблиці книг
    """
    driver.get(url)

    unique_title = f"TestBook_{int(time.time())}"
    add_book_helper(driver, unique_title, 2024)

    headers = driver.find_element(By.ID, "tableHeader").text
    if "Email" in headers:
        click_menu(driver, "Книги")
        time.sleep(0.5)

    page_source = driver.find_element(By.ID, "tableBody").text
    assert unique_title in page_source


def test_05_search_books(driver):
    """
    5. Пошук книги.

    Feature: Пошук книги
    Scenario: Користувач шукає існуючу книгу
        Given книга існує у бібліотеці
        When користувач вводить назву книги у поле пошуку
        Then таблиця відображає цю книгу
    """
    driver.get(url)

    target_book = f"FindMe_{int(time.time())}"
    add_book_helper(driver, target_book, 2025)

    inp = driver.find_element(By.ID, "mainInput")
    inp.clear()
    inp.send_keys(target_book)
    time.sleep(1)

    rows = driver.find_elements(By.CSS_SELECTOR, "#tableBody tr")
    assert len(rows) > 0
    assert target_book in rows[0].text


def test_06_sort_books(driver):
    """
    6. Сортування книг за роком.

    Feature: Сортування книг
    Scenario: Користувач сортує книги за роком видання
        Given існують книги з різними роками видання
        When користувач натискає на заголовок колонки "Рік"
        Then порядок книг змінюється після кліку
    """
    driver.get(url)

    add_book_helper(driver, "AAA_SortBook", 1000)
    add_book_helper(driver, "ZZZ_SortBook", 3000)

    driver.find_element(By.XPATH, "//th[contains(., 'Рік')]").click()
    time.sleep(0.5)
    first_row_text_asc = driver.find_element(By.CSS_SELECTOR, "#tableBody tr:first-child").text

    driver.find_element(By.XPATH, "//th[contains(., 'Рік')]").click()
    time.sleep(0.5)
    first_row_text_desc = driver.find_element(By.CSS_SELECTOR, "#tableBody tr:first-child").text

    assert first_row_text_asc != first_row_text_desc, "Порядок рядків не змінився після кліку на сортування!"


def test_07_delete_book(driver):
    """
    7. Видалення книги.

    Feature: Видалення книги
    Scenario: Користувач видаляє книгу
        Given книга існує у бібліотеці
        When користувач видаляє цю книгу
        Then книга більше не відображається у таблиці
    """
    driver.get(url)

    del_title = f"DeleteMe_{int(time.time())}"
    add_book_helper(driver, del_title, 2020)

    driver.find_element(By.ID, "mainInput").clear()
    driver.find_element(By.ID, "mainInput").send_keys(del_title)
    time.sleep(0.5)

    rows = driver.find_elements(By.CSS_SELECTOR, "#tableBody tr")
    if len(rows) == 0:
        pytest.fail("Книга для видалення не знайдена")

    rows[0].find_element(By.CLASS_NAME, "del-btn").click()
    WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
    time.sleep(1)

    driver.find_element(By.ID, "mainInput").clear()
    driver.find_element(By.ID, "mainInput").send_keys(del_title)
    time.sleep(0.5)

    rows_after = driver.find_elements(By.CSS_SELECTOR, "#tableBody tr")
    if len(rows_after) > 0:
        assert del_title not in rows_after[0].text


def test_08_edit_book(driver):
    """
    8. Редагування книги.

    Feature: Редагування книги
    Scenario: Користувач змінює назву книги
        Given книга існує у бібліотеці
        When користувач змінює назву книги
        Then нова назва відображається у таблиці
    """
    driver.get(url)

    old_title = f"EditMe_{int(time.time())}"
    new_title = f"Edited_{int(time.time())}"
    add_book_helper(driver, old_title, 2021)

    driver.find_element(By.ID, "mainInput").clear()
    driver.find_element(By.ID, "mainInput").send_keys(old_title)

    rows = driver.find_elements(By.CSS_SELECTOR, "#tableBody tr")
    if not rows: pytest.fail("Не знайшли книгу для редагування")

    rows[0].find_element(By.CLASS_NAME, "edit-btn").click()
    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, "bookModal")))

    title_field = driver.find_element(By.ID, "bookTitle")
    title_field.clear()
    title_field.send_keys(new_title)

    driver.find_element(By.CSS_SELECTOR, "#bookModal .save-btn").click()
    WebDriverWait(driver, 3).until(EC.invisibility_of_element_located((By.ID, "bookModal")))

    driver.find_element(By.ID, "mainInput").clear()
    driver.find_element(By.ID, "mainInput").send_keys(new_title)

    rows_new = driver.find_elements(By.CSS_SELECTOR, "#tableBody tr")
    assert len(rows_new) > 0
    assert new_title in rows_new[0].text

    rows_new[0].find_element(By.CLASS_NAME, "del-btn").click()
    WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()


def test_09_search_non_existent_book(driver):
    """
    9. Пошук неіснуючої книги.

    Feature: Пошук книги
    Scenario: Користувач шукає неіснуючу книгу
        Given у бібліотеці немає книги з такою назвою
        When користувач вводить назву у поле пошуку
        Then таблиця не відображає жодного результату
    """
    driver.get(url)

    driver.find_element(By.ID, "mainInput").send_keys("АбраКадабра12345")
    time.sleep(1)

    rows = driver.find_elements(By.CSS_SELECTOR, "#tableBody tr")
    assert len(rows) == 0, "Пошук мав повернути 0 результатів"
