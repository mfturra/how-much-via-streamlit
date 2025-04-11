from selenium import webdriver
from selenium.webdriver.safari.options import Options
from time import sleep

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

print("testing started")
options = webdriver.SafariOptions()
driver = webdriver.Safari(options=options)

driver.get("http://localhost:8501")
sleep(3)

# Get page title
title = driver.title

# Test if title is correct
assert "Swag Labs" in title
print("TEST 0: `title` test passed")

# Close the driver
driver.quit()