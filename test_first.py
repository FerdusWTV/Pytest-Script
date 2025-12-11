import os
import time
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------- FIXTURES ------------------------

@pytest.fixture(scope="session")
def driver():
    """Setup and teardown of Chrome WebDriver for CI (headless)."""
    load_dotenv()
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-allow-origins=*")

    driver_path = os.getenv("DRIVER")
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    yield driver
    driver.quit()


# @pytest.fixture(scope="session")
# def env():
#     """Load environment variables once."""
#     load_dotenv()
#     return {
#         "url": os.getenv("URL"),
#         "email": os.getenv("EMAIL"),
#         "password": os.getenv("PASSWORD"),
#         "target_portal": os.getenv("TARGET_PORTAL"),
#         "new_webcast_title": os.getenv("NEW_WEBCAST_TITLE"),
#         "slide_path": os.getenv("SLIDE_PATH"),
#         "video_path": os.getenv("VIDEO_PATH"),
#     }

# ----------------------- TEST CASES -----------------------

def test_01_login(driver, config):
    driver.get(config["url"])
    driver.find_element(By.ID, 'email').send_keys(config["email"])
    driver.find_element(By.ID, 'password').send_keys(config["password"])
    driver.find_element(By.CLASS_NAME, 'login-button').click()

    wait = WebDriverWait(driver, 60)
    welcome_text = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'header-title'))
    ).text

    assert 'Welcome' in welcome_text, "Login failed — 'Welcome' not found."
    print(f"✅ Login successful: {welcome_text}")


def test_02_open_target_portal(driver, config):
    wait = WebDriverWait(driver, 30)
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search portal']")))
    search_box.click()
    search_box.send_keys(config["target_portal"])

    edit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Edit']")))
    driver.execute_script("arguments[0].click();", edit_btn)

    portal_title = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//p[@class='branding-information-text mt-1'])[1]"))
    ).text

    assert "Portal" in portal_title, "Portal title validation failed."
    print(f"✅ Opened portal: {portal_title}")


def test_00_cleanup(driver, config):
    wait = WebDriverWait(driver, 30)

    time.sleep(2)
    session_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Sessions')]")))
    driver.execute_script("arguments[0].click();", session_btn)
    
    target_event = config["webcast_title"]

    def get_webcast_summaries():
        return wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "webcast-summary"))
        )

    try:
        webcast_summaries = get_webcast_summaries()
        print(f"Found {len(webcast_summaries)} webcast summaries.")
    except Exception as e:
        pytest.fail(f"Could not find any webcast summary. Error: {e}")

    for summary in webcast_summaries:
        try:
            name_elem = summary.find_element(
                By.XPATH,
                ".//div[contains(@class,'webcast-summary-event-name')]//div[contains(@class,'webcast-summary-background')]"
            )
            
            if target_event.casefold() in name_elem.text.strip().casefold():
                print(f"✅ Webcast '{target_event}' found.")

                # Delete
                delete_btn = WebDriverWait(summary, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, ".//div[contains(@class,'webcast-summary-delete')]//button")
                    ))
                
                delete_btn.click()
                print("Clicked the 'Delete' button.")
                
                dlt_confirm_btn = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//button[normalize-space()='Confirm']")
                    ))
                driver.execute_script("arguments[0].click();", dlt_confirm_btn)
                
                # Wait for popup and close/confirm it
                wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
                print("Popup detected after Delete.")
                time.sleep(2)
                
        except Exception:
            continue
    else:
        pytest.fail(f"Webcast '{target_event}' not found in summaries.")


    

#================ Audio&Slide ================
