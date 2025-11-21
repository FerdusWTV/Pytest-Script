import selenium
import pytest
import os
from dotenv import load_dotenv

# -----------------------------
# addoption for changing env in the terminal
# -----------------------------
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Environment to run tests against: dev or prod",
    )


# ----------------------- ENV ------------------------
@pytest.fixture(scope="session")
def config(request):
    load_dotenv()
    selected_env = request.config.getoption("--env")

    if selected_env == "prod":
        return {
            "url": os.getenv("URL_PROD"),
            "email": os.getenv("EMAIL_PROD"),
            "password": os.getenv("PASSWORD_PROD"),
            "target_portal": os.getenv("TARGET_PORTAL"),
            "new_webcast_title": os.getenv("NEW_WEBCAST_TITLE"),
            "slide_path": os.getenv("SLIDE_PATH"),
            "video_path": os.getenv("VIDEO_PATH"),
        }

    return {
        "url": os.getenv("URL"),
        "email": os.getenv("EMAIL"),
        "password": os.getenv("PASSWORD"),
        "target_portal": os.getenv("TARGET_PORTAL"),
        "new_webcast_title": os.getenv("NEW_WEBCAST_TITLE"),
        "slide_path": os.getenv("SLIDE_PATH"),
        "video_path": os.getenv("VIDEO_PATH"),
    }

# -----------------------------
# Show Selenium version in console
# -----------------------------
def pytest_report_header(config):
    return f"Selenium Version: {selenium.__version__}"


# -----------------------------
# Add Selenium version to HTML report Environment
# -----------------------------
def pytest_configure(config):
    if hasattr(config, "_metadata") and config._metadata is not None:
        config._metadata["Selenium Version"] = selenium.__version__


# -----------------------------
# Add Selenium version to HTML report summary
# -----------------------------
def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([f"Selenium Version: {selenium.__version__}"])

# -----------------------------
# Optional: Customize HTML report title
# -----------------------------
def pytest_html_report_title(report):
    report.title = "Automation Test Report"
