from utils.send_email_notification import send_email_notification
from utils.send_sms_notification import send_sms_notification
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
import time
from dotenv import load_dotenv

load_dotenv()

web_url = os.getenv("WEB_URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

def get_driver():
    service = Service('/usr/local/bin/chromedriver')
    return webdriver.Chrome(service=service)

def change_language(driver):
    try:
        lang_link = driver.find_element(By.XPATH, "//a[@href='/Language/ChangeLanguage?lang=2']")
        lang_link.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='active' and @href='/Language/ChangeLanguage?lang=2']"))
        )
        print("Changed language.")
    except NoSuchElementException as e:
        print("Language change link not found:", e)
        raise e
        
def login(driver):
    try:
        driver.get(web_url)
        time.sleep(5)
        change_language(driver)
        username_field = driver.find_element(By.XPATH, "//input[@id='login-email']")
        password_field = driver.find_element(By.XPATH, "//input[@id='login-password']")
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button = driver.find_element(By.XPATH, "//*[@id='login-form']/button")
        submit_button.click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("UserArea")
        )
        print("Successfully logged in and redirected to UserArea")
        
        # Change the language to English
        change_language(driver)

    except TimeoutException as e:
        print(f"Login failed or page did not redirect to UserArea in time: {e}")
        raise e

def navigate_to_booking_page(driver):
    try:
        book_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/Services' and @id='advanced' and @class='element  ']"))
        )
        book_link.click()
    except TimeoutException as e:
        print("Booking link not found:", e)
        raise e

def try_booking(driver):
    try:
        book_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/Services/Booking/692']/button[@class='button primary']"))
        )
        book_button.click()
    except TimeoutException as e:
        print("Book button not found:", e)
        raise e

def handle_no_spot(driver):
    try:
        no_spot_message = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Sorry, all appointments for this service are currently booked.')]"))
        )
        if no_spot_message:
            ok_button = driver.find_element(By.XPATH, "//div[@class='jconfirm-buttons']/button[@class='btn btn-blue']")
            ok_button.click()
            return False
    except TimeoutException:
        return True
    return True

def check_and_book(driver):
    while True:
        try:

            # Navigate to the booking page
            navigate_to_booking_page(driver)
            print("Opened Booking Page.")

            # Try booking
            try_booking(driver)
            print("Clicked on the Book button.")

            # If we reach the booking page with available slots
            # if "/Services/Booking/4996" in driver.current_url:
            if "/Services/Booking/692" in driver.current_url:    
                print("Spot available!")
                
                print("Sending Email Notification!")
                send_email_notification(
                    "Visa Appointment Available",
                    "A visa appointment slot is now available. Please check the consulate website https://prenotami.esteri.it/Services immediately."
                )
                
                print("Sending SMS Notification!")
                send_sms_notification(
                    "A visa appointment slot is now available. Please check the consulate website immediately."
                )
                break
            
            # Check for no available spots
            if not handle_no_spot(driver):
                print("No spots available, retrying in 30 minutes...")
                time.sleep(60)  # Wait for 30 minutes before retrying
                driver.refresh()
                continue

        except Exception as e:
            print(f"An error occurred: {e}")
            driver.quit()
            driver = get_driver()
            login(driver)
            continue

def main():
    global driver_path
    driver = get_driver()
    try:
        login(driver)
        check_and_book(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
