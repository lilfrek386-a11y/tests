import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from helper import click_menu, add_author_helper

URL = "http://localhost:8001/index.html"


class TestLibraryUI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--headless=new")
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        cls.driver.implicitly_wait(3)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_01_page_loads(self):
        """1. Сторінка відкривається, основні елементи інтерфейсу доступні."""
        self.driver.get(URL)

        self.assertIn("Библиотека", self.driver.title)
        self.assertTrue(self.driver.find_element(By.TAG_NAME, "h1").is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, "mainInput").is_displayed())
        self.assertTrue(self.driver.find_element(By.CLASS_NAME, "menu-btn").is_displayed())

    def test_02_switch_to_authors(self):
        """2. Перемикання на авторів змінює заголовок таблиці."""
        self.driver.get(URL)

        click_menu(self.driver, "Автори")

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//th[contains(., 'Email')]"))
        )

        headers = self.driver.find_element(By.ID, "tableHeader").text
        self.assertIn("Email", headers)

    def test_03_add_author(self):
        """3. Додавання автора."""
        self.driver.get(URL)
        click_menu(self.driver, "Автори")

        unique_name = f"TestAuth_{int(time.time())}"

        add_author_helper(self.driver, unique_name, "User", f"{unique_name}@test.com")

        page_source = self.driver.find_element(By.ID, "tableBody").text

        self.assertIn(unique_name, page_source)


if __name__ =="__main__":
    unittest.main(verbosity=2)