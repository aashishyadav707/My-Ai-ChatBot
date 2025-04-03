import sys
sys.path.append('/Users/aashishnepal/Documents/ai-chatbot-project')
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.app import app  # If app.py is inside the app folder
import threading
import time
import os


class ChatbotUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure Flask to use a different port for testing
        cls.port = 5001  # Different from your development port
        cls.host = 'localhost'
        
        # Start Flask server
        cls.server = threading.Thread(
            target=app.run,
            kwargs={
                'host': cls.host,
                'port': cls.port,
                'debug': False,
                'use_reloader': False
            }
        )
        cls.server.daemon = True
        cls.server.start()
        
        # Give server time to start
        time.sleep(2)
        
        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Start Chrome browser
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.get(f'http://{cls.host}:{cls.port}/')

    def test_chat_interaction(self):
        try:
            # Wait for page to load completely
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
            # Find elements with more flexible waiting
            input_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'user-input')))
            
            send_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'send-button')))
            
            # Test sending a message
            input_box.send_keys('hello')
            send_button.click()
            
            # Wait for response with more specific condition
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'bot-message')]"))
            )
            
            # Verify messages
            messages = self.driver.find_elements(By.CLASS_NAME, 'message')
            self.assertGreater(len(messages), 1)
            
        except Exception as e:
            # Take screenshot on failure
            if not os.path.exists('test_failures'):
                os.makedirs('test_failures')
            self.driver.save_screenshot('test_failures/test_failure.png')
            raise  # Re-raise the exception to fail the test
        finally:
            # Clean up code can go here if needed
            pass

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == '__main__':
    unittest.main()