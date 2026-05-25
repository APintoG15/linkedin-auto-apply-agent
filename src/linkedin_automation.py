from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class LinkedInAutomation:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None
    
    def initialize_driver(self):
        print("Initializing Chrome driver...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ Chrome driver initialized")
        return True
    
    def login_to_linkedin(self):
        print("Logging in to LinkedIn...")
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        self.driver.find_element(By.ID, "username").send_keys(self.email)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.XPATH, "//button[@aria-label='Sign in']").click()
        print("✓ Logged in")
        time.sleep(5)
        return True
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()