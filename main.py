from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from datetime import datetime, date, timedelta
import re
import zoneinfo
import os

# 1. Get the current time explicitly in the UK timezone
uk_timezone = zoneinfo.ZoneInfo("Europe/London")
now_in_uk = datetime.now(uk_timezone)
# 2. Extract just the local calendar date
today = now_in_uk.date()
# 3. Calculate your target date (7 days from your true local day)
targetDate = today + timedelta(days=7)
defaultTimeout = 6000
username = os.environ.get('MY_USERNAME')
password = os.environ.get('MY_PASSWORD')
if not username or not password:
    print("Error: Missing username or password environment variables.")
    exit(1)
bookingLink = f"https://bookings.better.org.uk/location/better-gym-connswater/fitness-classes1/{today}/by-time"

def book_pilates():
    with sync_playwright() as p:
        #Set up
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        print(f"Attempting to open site {bookingLink}")
        page.goto(bookingLink, wait_until="networkidle")
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
        page.get_by_test_id(f"date-{targetDate}").click(timeout=defaultTimeout)
        page.get_by_label(re.compile("Pilates")).click(timeout=defaultTimeout)
        print("Adding to basket...")
        page.get_by_role("button", name="Book now").click(timeout=defaultTimeout)
        print("Finalised add to basket...")
        try:
            print("Finalising booking...")
            page.get_by_role("button", name="Pay now").click(timeout=defaultTimeout)
            print("Waiting for booking confirmation URL...")
            page.wait_for_url("**/booking-confirmed/**", timeout=15000)
            print(f"Pilates booked for {targetDate}!!!!")
        except PlaywrightTimeoutError:
            print("Error finalising booking...")
            browser.close()
            return
        browser.close()

if __name__ == "__main__":
    book_pilates()
