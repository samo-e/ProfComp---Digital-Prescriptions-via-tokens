from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up the Chrome WebDriver
driver = webdriver.Chrome()  # Or use webdriver.Firefox() if you prefer

try:
    # Open the login page
    driver.get('http://127.0.0.1:5000/login')

    # Fill in the email
    email_input = driver.find_element(By.ID, 'email')
    email_input.send_keys('student3@gmail.com')  # Replace with your test email

    # Fill in the password
    password_input = driver.find_element(By.ID, 'password')
    password_input.send_keys('12345678')      # Replace with your test password

    # Select the role
    role_select = driver.find_element(By.ID, 'roleSelect')
    for option in role_select.find_elements(By.TAG_NAME, 'option'):
        if option.text.lower() == 'student':
            option.click()
            break

    # Submit the form
    password_input.send_keys(Keys.RETURN)

    # Wait for a bit to see the result
    time.sleep(3)

    # Optionally, check for a success message or redirect
    print(driver.current_url)
    print(driver.page_source)

finally:
    pass  # Do not quit the driver, so the browser stays open
    # driver.quit()