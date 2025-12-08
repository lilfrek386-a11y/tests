import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def click_menu(drv, text):
    menu_btn = drv.find_element(By.CLASS_NAME, "menu-btn")
    menu_btn.click()
    WebDriverWait(drv, 2).until(lambda d: "active" in drv.find_element(By.ID, "dropdown").get_attribute("class"))

    xpath = f"//div[contains(@class,'dropdown-item') and contains(., '{text}')]"
    item = WebDriverWait(drv, 2).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    item.click()


def add_author_helper(drv, first, last, email):
    click_menu(drv, "Додати автора")
    WebDriverWait(drv, 3).until(EC.visibility_of_element_located((By.ID, "authorModal")))
    time.sleep(0.3)

    drv.find_element(By.ID, "authFirstName").send_keys(first)
    drv.find_element(By.ID, "authLastName").send_keys(last)
    drv.find_element(By.ID, "authAge").send_keys("30")
    drv.find_element(By.ID, "authEmail").send_keys(email)

    drv.find_element(By.CSS_SELECTOR, "#authorModal .save-btn").click()
    WebDriverWait(drv, 3).until(EC.invisibility_of_element_located((By.ID, "authorModal")))
    time.sleep(0.5)


def add_book_helper(drv, title, year):
    click_menu(drv, "Додати книгу")
    WebDriverWait(drv, 3).until(EC.visibility_of_element_located((By.ID, "bookModal")))
    time.sleep(0.3)

    drv.find_element(By.ID, "bookTitle").send_keys(title)
    drv.find_element(By.ID, "bookYear").send_keys(str(year))

    try:
        select = drv.find_element(By.ID, "bookAuthorSelect")
        options = select.find_elements(By.TAG_NAME, "option")
        if options:
            options[0].click()
    except:
        pass

    drv.find_element(By.CSS_SELECTOR, "#bookModal .save-btn").click()
    WebDriverWait(drv, 3).until(EC.invisibility_of_element_located((By.ID, "bookModal")))
    time.sleep(0.5)
