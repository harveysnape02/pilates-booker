from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from datetime import datetime, date, timedelta
import re
import os

#Setting variables for script
today = date.today()
targetDate = today + timedelta(days=3)
defaultTimeout = 6000
username = os.environ.get('MY_USERNAME')
password = os.environ.get('MY_PASSWORD')
bookingLink = f"https://bookings.better.org.uk/location/better-gym-connswater/fitness-classes1/{targetDate}/by-time"

def book_pilates():
    with sync_playwright() as p:
        #Set up
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        print(f"Attempting to open site {bookingLink}")
        page.goto(bookingLink, wait_until="networkidle")
        page.wait_for_timeout(defaultTimeout)
        current_url = page.url
        
        #Checks to see if classes have been released yet
        if str(bookingLink) not in current_url:
            print(f"Redirected, darn. We landed on: {current_url}")
            print(f"Classes for {targetDate} have not been released yet.")
            browser.close()
            return
        print(f"Succefully opened booking site for classes on {targetDate}")
        
        #Cookie block
        print("Checking for cookies pop-up")
        try:
            page.locator("#onetrust-reject-all-handler").click(timeout=defaultTimeout)
            print("Cookies rejected")
        except PlaywrightTimeoutError:
            print("No cookies to reject")
            
        #log-in block
        try:
            page.get_by_test_id("login").click()
            page.locator("#username").fill(username)
            page.locator("#password").fill(password)
            page.get_by_role("button", name="Log in").click(timeout=defaultTimeout)
            print("Logged in")
        except:
            print("Issue entering log in details")
            browser.close()
            return
            
        #Clearing Cart
        try:
            print("Checking if Cart is empty")
            page.get_by_label(re.compile("Remove from cart")).click(timeout=defaultTimeout)
            success_message = page.get_by_text("Successfully removed item from the basket.")
            success_message.wait_for(state="visible")
            print("Cart succesfully cleared")
        except:
            print("Cart already empty")
            
        #Main booking process
        page.get_by_label(re.compile("Pilates")).click(timeout=defaultTimeout)
        print("Adding to basket...")
        page.get_by_role("button", name="Book now").click(timeout=defaultTimeout)
        print("Finalised add to basket...")
        try:
            print("Finalising booking...")
            page.locator(".PayNowButton__PayText-sc-2le0ue-2").click(timeout=defaultTimeout)
            print(f"Pilates booked for {targetDate}!!!!")
        except PlaywrightTimeoutError:
            print("Error finalising booking...")
            browser.close()
            return
        browser.close()

if __name__ == "__main__":
    book_pilates()
