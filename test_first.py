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

# ----------------------- FIXTURES -----------------------q

@pytest.fixture(scope="session")
def driver():
    """Setup and teardown of Chrome WebDriver for CI (headless)."""
    load_dotenv()
    options = Options()
    options.add_argument("--headless=new")
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


@pytest.fixture(scope="session")
def env():
    """Load environment variables once."""
    load_dotenv()
    return {
        "url": os.getenv("URL"),
        "email": os.getenv("EMAIL"),
        "password": os.getenv("PASSWORD"),
        "target_portal": os.getenv("TARGET_PORTAL"),
        "new_webcast_title": os.getenv("NEW_WEBCAST_TITLE"),
        "slide_path": os.getenv("SLIDE_PATH"),
        "video_path": os.getenv("VIDEO_PATH"),
    }

# ----------------------- TEST CASES -----------------------

def test_01_login(driver, env):
    driver.get(env["url"])
    driver.find_element(By.ID, 'email').send_keys(env["email"])
    driver.find_element(By.ID, 'password').send_keys(env["password"])
    driver.find_element(By.CLASS_NAME, 'login-button').click()

    wait = WebDriverWait(driver, 60)
    welcome_text = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'header-title'))
    ).text

    assert 'Welcome' in welcome_text, "Login failed — 'Welcome' not found."
    print(f"✅ Login successful: {welcome_text}")


def test_02_open_target_portal(driver, env):
    wait = WebDriverWait(driver, 30)
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search portal']")))
    search_box.click()
    search_box.send_keys(env["target_portal"])

    edit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Edit']")))
    driver.execute_script("arguments[0].click();", edit_btn)

    portal_title = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//p[@class='branding-information-text mt-1'])[1]"))
    ).text

    assert "Portal" in portal_title, "Portal title validation failed."
    print(f"✅ Opened portal: {portal_title}")


def test_03_create_new_webcast(driver, env):
    wait = WebDriverWait(driver, 30)

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

    # Fill in webcast title
    webcast_title = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='streamName']")))
    webcast_title.send_keys(env["new_webcast_title"])
    driver.find_element(By.XPATH, "//button[normalize-space()='Next']").click()

    # Select date, time, duration
    date_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Select date']")))
    date_field.click()
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[normalize-space()='25']"))).click()

    time_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Select time']")))
    time_field.click()
    wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@data-type='hour']//div[normalize-space()='03']"))).click()

    duration_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Select duration']")))
    duration_field.click()
    wait.until(EC.presence_of_element_located((By.XPATH, "(//div[normalize-space()='01'])[3]"))).click()

    # Next -> Next -> Create
    driver.find_element(By.XPATH, "//button[normalize-space()='Next']").click()
    driver.find_element(By.XPATH, "//button[normalize-space()='Next']").click()
    create_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class,'save-button')]")))
    driver.execute_script("arguments[0].click();", create_btn)

    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print(f"✅ Webcast '{env['new_webcast_title']}' created successfully.")


def test_04_upload_slide_and_video(driver, env):
    wait = WebDriverWait(driver, 30)

    # Slide upload
    content_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//button[normalize-space()='Content'])[1]")))
    driver.execute_script("arguments[0].click();", content_btn)

    slide_upload = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='file'])[1]")))
    driver.execute_script("arguments[0].style.display = 'block';", slide_upload)
    slide_upload.send_keys(env["slide_path"])
    driver.find_element(By.XPATH, "(//button[normalize-space()='Save'])[1]").click()
    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print(f"✅ Slide uploaded: {env['slide_path']}")

    # Video upload
    video_upload = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='file'])[2]")))
    driver.execute_script("arguments[0].style.display = 'block';", video_upload)
    video_upload.send_keys(env["video_path"])
    driver.find_element(By.XPATH, "//button[normalize-space()='Save']").click()
    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print(f"✅ Video uploaded: {env['video_path']}")


def test_05_activate_and_manage_webcast(driver, env):
    wait = WebDriverWait(driver, 30)
    target_event_name = env["new_webcast_title"]

    def get_webcast_summaries():
        return wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "webcast-summary")))

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
            if name_elem.text.strip().casefold() == target_event_name.casefold():
                print(f"✅ Webcast '{target_event_name}' found.")

                # Activate
                activate_btn = WebDriverWait(summary, 10).until(
                    EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class,'webcast-summary-activate')]//button"))
                )
                activate_btn.click()
                wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
                time.sleep(2)

                # Re-check and click Manage
                for updated_summary in get_webcast_summaries():
                    try:
                        updated_name = updated_summary.find_element(
                            By.XPATH, ".//div[contains(@class,'webcast-summary-event-name')]//div[contains(@class,'webcast-summary-background')]"
                        ).text.strip()
                        if updated_name.casefold() == target_event_name.casefold():
                            manage_btn = WebDriverWait(updated_summary, 10).until(
                                EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class,'webcast-manage-column')]//button"))
                            )
                            manage_btn.click()
                            print(f"🎯 Webcast '{target_event_name}' Manage page opened successfully.")
                            return
                    except Exception:
                        continue
                pytest.fail(f"Failed to click 'Manage' for webcast '{target_event_name}'.")
        except Exception:
            continue

    pytest.fail(f"Webcast '{target_event_name}' not found in summaries.")


def test_06_configure_webcast_layout(driver, env):
    """Configure webcast layout settings and verify UI elements."""
    wait = WebDriverWait(driver, 30)

    # Open Layout
    layout_btn = wait.until(EC.presence_of_element_located(
        (By.XPATH, "(//button[normalize-space()='Webcast Layout'])[1]")
    ))
    driver.execute_script("arguments[0].click();", layout_btn)

    # Update Preview Title
    preview_title = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Title']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", preview_title)
    preview_title.clear()
    preview_title.send_keys("Automated Preview Text Title!")

    # Update Preview Description
    preview_desc = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Description']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", preview_desc)
    preview_desc.clear()
    preview_desc.send_keys("This is Automation test preview text for testing.")

    # Enable Logo, Q&A, Slider list
    switches = {
        "logo": "(//button[@role='switch'])[2]",
        "qna": "(//button[@role='switch'])[4]",
        "slider_list": "(//button[@role='switch'])[6]"
    }
    for key, xpath in switches.items():
        switch_btn = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", switch_btn)
        driver.execute_script("arguments[0].click();", switch_btn)
        time.sleep(0.5)

    # Save layout
    save_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Save']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
    driver.execute_script("arguments[0].click();", save_btn)
    wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
    print("✅ Webcast layout configured successfully.")


def test_07_toggle_webcast_status(driver, env):
    """Toggle webcast status between Preview and Live, upload content for each status."""
    wait = WebDriverWait(driver, 30)

    status_map = [("Preview", env["slide_path"]), ("Live", env["slide_path"])]

    for status_name, slide_file in status_map:
        # Click status dropdown
        status_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, f"//span[@title='{status_name}']")))
        status_dropdown.click()

        # Toggle to opposite status
        new_status = "Live" if status_name == "Preview" else "Preview"
        new_status_elem = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(),'{new_status}')]")))
        time.sleep(1)
        new_status_elem.click()
        print(f"✅ Webcast status changed to {new_status}")

        # Upload slide
        content_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//button[normalize-space()='Content'])[1]")))
        driver.execute_script("arguments[0].click();", content_btn)

        slide_upload = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='file'])[1]")))
        driver.execute_script("arguments[0].style.display = 'block';", slide_upload)
        slide_upload.send_keys(slide_file)

        save_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//button[normalize-space()='Save'])[1]")))
        driver.execute_script("arguments[0].click();", save_btn)
        wait.until(EC.presence_of_element_located((By.ID, "swal2-html-container")))
        print(f"✅ Slide uploaded for status {new_status}: {slide_file}")
