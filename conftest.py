import selenium

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
