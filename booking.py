from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from datetime import datetime, date, timedelta
import re
import zoneinfo
import os
import notification

#Creates timezone aware date.
uk_timezone = zoneinfo.ZoneInfo("Europe/London")
now_in_uk = datetime.now(uk_timezone)
today = now_in_uk.date()
targetDate = today + timedelta(days=7)

defaultTimeout = 6000
username = os.environ.get('MY_USERNAMES')
password = os.environ.get('MY_PASSWORD')
if not username or not password:
    print("Error: Missing username or password environment variables.")
    exit(1)
bookingLink = f"https://bookings.better.org.uk/location/better-gym-connswater/fitness-classes1/{today}/by-time"

def error_exit(browser, status):
    browser.close()
    notification.send_notification(status, targetDate)
    exit(0)

def book_pilates():
    with sync_playwright() as p:
        #Set up
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        print(f"Attempting to open site {bookingLink}")
        page.goto(bookingLink, wait_until="networkidle")
        #Cookie block
        print("ACTION: Checking for cookies pop-up")
        try:
            page.locator("#onetrust-reject-all-handler").click(timeout=defaultTimeout)
            print("STATUS: Cookies rejected")
        except PlaywrightTimeoutError:
            print("STATUS: No cookies to reject")
            
        #log-in block
        try:
            print("ACTION: Attempting to log in")
            page.get_by_test_id("login").click()
            page.locator("#username").fill(username)
            page.locator("#password").fill(password)
            page.get_by_role("button", name="Log in").click(timeout=defaultTimeout)
            print("STATUS: Logged in")
        except:
            error_exit(browser, "Login Error")
        #Clearing Cart
        try:
            print("ACTION: Checking if Cart is empty")
            page.get_by_label(re.compile("Remove from cart")).click(timeout=defaultTimeout)
            success_message = page.get_by_text("Successfully removed item from the basket.")
            success_message.wait_for(state="visible")
            print("STATUS: Cart succesfully cleared")
        except:
            print("STATUS: Cart already empty")
            
        #Navigating to Pilates class
        try:
            print("ACTION: Navigating to Pilates class...")
            page.get_by_test_id(f"date-{targetDate}").click(timeout=defaultTimeout)
            page.get_by_label(re.compile("Pilates")).click(timeout=defaultTimeout)
            print("STATUS: Pilates class selected")
        except PlaywrightTimeoutError:
            error_exit(browser, "Navigation Error")
        
        #Main booking process
        try:
            print("ACTION: Adding to basket...")
            page.get_by_role("button", name="Book now").click(timeout=defaultTimeout)
            print("ACTION: Confirming booking...")
            page.get_by_role("button", name="Pay now").click(timeout=defaultTimeout)
            print("STATUS: Waiting for booking confirmation URL...")
            page.wait_for_url("**/booking-confirmed/**", timeout=15000)
            print(f"STATUS: Pilates booked for {targetDate} :)")
        except PlaywrightTimeoutError:
            error_exit(browser, "Booking Error")
        browser.close()
        notification.send_notification("Success", targetDate)

if __name__ == "__main__":
    book_pilates()
