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
    """Setup and teardown of Chrome WebDriver."""
    load_dotenv()
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-allow-origins=*")

    driver_path = os.getenv("DRIVER")
    if driver_path and os.path.exists(driver_path):
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    yield driver
    driver.quit()


# ----------------------- HELPER FUNCTIONS -----------------

def _navigate_and_create_webcast(driver, wait, title):
    """Navigate to Sessions page and create a new webcast with the given title."""
    time.sleep(2)
    session_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Sessions')]")))
    driver.execute_script("arguments[0].click();", session_btn)

    webcast_creation_btn = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='session-button-group-right']"))
    )
    webcast_creation_btn.click()

    new_webcast_btn = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//div[@class='stream-modal-container h-full'])[1]"))
    )
    driver.execute_script("arguments[0].click();", new_webcast_btn)

    # Step 1 — Title
    webcast_title_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='streamName']")))
    webcast_title_input.send_keys(title)
    time.sleep(3)

    next_btn_1 = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Next']")))
    driver.execute_script("arguments[0].click();", next_btn_1)

    # Step 2 — Date / Time / Duration
    webcast_date = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Select date']")))
    webcast_date.click()
    select_date = wait.until(EC.presence_of_element_located((By.XPATH, "//div[normalize-space()='25']")))
    driver.execute_script("arguments[0].click();", select_date)

    webcast_time = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Select time']")))
    webcast_time.click()
    select_time = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//ul[@data-type='hour']//div[@class='ant-picker-time-panel-cell-inner'][normalize-space()='03']")
    ))
    driver.execute_script("arguments[0].click();", select_time)

    webcast_duration = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Select duration']")))
    webcast_duration.click()
    select_duration = wait.until(EC.presence_of_element_located(
        (By.XPATH, "(//div[@class='ant-picker-time-panel-cell-inner'][normalize-space()='01'])[3]")
    ))
    driver.execute_script("arguments[0].click();", select_duration)

    next_btn_2 = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Next']")))
    driver.execute_script("arguments[0].click();", next_btn_2)

    # Step 3 — Signal
    signal = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='acquisitionSignal']")))
    driver.execute_script("arguments[0].style.display = 'block';", signal)
    driver.execute_script("arguments[0].click();", signal)

    next_btn_3 = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Next']")))
    driver.execute_script("arguments[0].click();", next_btn_3)

    # Create
    create_btn = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//button[@class='save-button d-flex flex-row justify-items-center']")
    ))
    driver.execute_script("arguments[0].click();", create_btn)

    time.sleep(3)
    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print(f"  ✅ Webcast '{title}' created.")


def _activate_and_manage_webcast(driver, wait, title):
    """Find webcast by title, activate it, then open its Manage page."""
    def get_summaries():
        return wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "webcast-summary")))

    try:
        summaries = get_summaries()
        print(f"  Found {len(summaries)} webcast summaries.")
    except Exception as e:
        pytest.fail(f"Could not find webcast summaries. Error: {e}")

    for summary in summaries:
        try:
            name_elem = summary.find_element(
                By.XPATH,
                ".//div[contains(@class,'webcast-summary-event-name')]//div[contains(@class,'webcast-summary-background')]"
            )
            if name_elem.text.strip().casefold() == title.casefold():
                print(f"  ✅ Found webcast '{title}'.")

                activate_btn = WebDriverWait(summary, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, ".//div[contains(@class,'webcast-summary-activate')]//button")
                    ))
                activate_btn.click()
                print("  Clicked 'Activate'.")

                wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
                time.sleep(2)

                # Re-fetch and click Manage
                for updated in get_summaries():
                    try:
                        updated_name = updated.find_element(
                            By.XPATH,
                            ".//div[contains(@class,'webcast-summary-event-name')]//div[contains(@class,'webcast-summary-background')]"
                        ).text.strip()
                        if updated_name.casefold() == title.casefold():
                            manage_btn = WebDriverWait(updated, 10).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, ".//div[contains(@class,'webcast-manage-column')]//button")
                                )
                            )
                            manage_btn.click()
                            print(f"  ✅ Manage page opened for '{title}'.")
                            return
                    except Exception:
                        continue
                pytest.fail(f"Failed to click 'Manage' for webcast '{title}'.")
        except Exception:
            continue

    pytest.fail(f"Webcast '{title}' not found in summaries.")


def _upload_content(driver, wait, config):
    """Upload slide (Preview + Live) and video (Preview)."""
    # --- Open Webcast Details panel ---
    time.sleep(1)
    details_btn = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//input[@id='webcastType'])[1]"))
    )
    driver.execute_script("arguments[0].click();", details_btn)


    # --- Open Content panel ---
    time.sleep(1)
    content_btn = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//button[normalize-space()='Content'])[1]"))
    )
    driver.execute_script("arguments[0].click();", content_btn)
    content_btn.send_keys()

    # --- PREVIEW: Upload Slide ---
    slide_upload = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='file'])[1]")))
    driver.execute_script("arguments[0].style.display = 'block';", slide_upload)
    slide_upload.send_keys(config["slide_path"])

    time.sleep(1)
    preview_save_btn = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//button[normalize-space()='Save'])[1]"))
    )
    driver.execute_script("arguments[0].click();", preview_save_btn)
    time.sleep(5)
    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print(f"  ✅ Preview slide saved.")

    # --- Switch to LIVE ---
    status_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@title='Preview']")))
    status_dropdown.click()
    status_live = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Live')]")))
    driver.execute_script("arguments[0].click();", status_live)

    # --- LIVE: Upload Slide ---
    time.sleep(1)
    content_btn = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//button[normalize-space()='Content'])[1]"))
    )
    driver.execute_script("arguments[0].click();", content_btn)

    slide_upload = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='file'])[1]")))
    driver.execute_script("arguments[0].style.display = 'block';", slide_upload)
    slide_upload.send_keys(config["slide_path"])

    time.sleep(1)
    live_save_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Save']")))
    live_save_btn.click()
    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print(f"  ✅ Live slide saved.")

    # --- Switch back to PREVIEW ---
    status_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@title='Live']")))
    status_dropdown.click()
    status_preview = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Preview')]")))
    driver.execute_script("arguments[0].click();", status_preview)

    # --- PREVIEW: Upload Video ---
    video_upload = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='file'])[2]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", video_upload)
    driver.execute_script("arguments[0].style.display = 'block';", video_upload)
    video_upload.send_keys(config["video_path"])

    time.sleep(10)  # allow large video file to upload

    preview_save_btn = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//button[normalize-space()='Save'])[1]"))
    )
    driver.execute_script("arguments[0].click();", preview_save_btn)
    time.sleep(5)
    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print(f"  ✅ Preview video saved.")


def _configure_layout_and_go_back(driver, wait):
    """Configure webcast layout settings then click Back to return to Sessions."""
    layout_btn = wait.until(EC.presence_of_element_located(
        (By.XPATH, "(//button[normalize-space()='Webcast Layout'])[1]")
    ))
    driver.execute_script("arguments[0].click();", layout_btn)

    # Title
    preview_title = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Title']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", preview_title)
    preview_title.clear()
    preview_title.send_keys("Automated Preview Text Title!")

    # Description
    preview_desc = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Description']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", preview_desc)
    preview_desc.clear()
    preview_desc.send_keys("This is Automation test preview text for testing.")

    # Toggle switches: logo, Q&A, slider list
    switches = {
        "logo":        "(//button[@role='switch'])[2]",
        "qna":         "(//button[@role='switch'])[4]",
        "slider_list": "(//button[@role='switch'])[6]",
    }
    for key, xpath in switches.items():
        switch_btn = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", switch_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", switch_btn)

    # Save layout
    save_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Save']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
    driver.execute_script("arguments[0].click();", save_btn)
    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print(f"  ✅ Layout saved.")

    time.sleep(1)
    back_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Back']")))
    driver.execute_script("arguments[0].click();", back_btn)
    print(f"  ↩️  Clicked Back — returned to Sessions page.")
    time.sleep(2)





# ----------------------- TEST CASES -----------------------

def test_01_login(driver, config):
    driver.get(config["url_org"])
    driver.find_element(By.ID, 'email').send_keys(config["email_org"])
    driver.find_element(By.ID, 'password').send_keys(config["password_org"])
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


def test_03_create_all_webcasts(driver, config):
    """Create, activate, upload content, and configure layout for all 4 webcasts."""
    wait = WebDriverWait(driver, 30)
    titles = config["webcast_titles"]

    for i, title in enumerate(titles, start=1):
        print(f"\n{'='*60}")
        print(f"  WEBCAST {i}/{len(titles)}: '{title}'")
        print(f"{'='*60}")

        _navigate_and_create_webcast(driver, wait, title)
        _activate_and_manage_webcast(driver, wait, title)
        _upload_content(driver, wait, config)
        _configure_layout_and_go_back(driver, wait)

        print(f"  🎉 Webcast {i}/{len(titles)} '{title}' fully done!\n")

    print("✅ All webcasts created and configured successfully!")
