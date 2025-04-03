import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from app.app import app, get_bot_response, analyze_sentiment

class ChatbotTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Assistant', response.data)

    def test_chat_response(self):
        test_cases = [
            ("hello", ["Hello there", "Hi!", "Hey"]),
            ("what's your name", ["I'm ChatBot", "You can call me ChatBot"]),
            ("tell me a joke", [
                "Why don't scientists trust atoms? Because they make up everything",
                "Did you hear about the mathematician who's afraid of negative numbers",
                "Why don't skeletons fight each other"
            ]),
        ]
        
        for input_text, possible_responses in test_cases:
            with self.subTest(input=input_text):
                response = get_bot_response(input_text)
                self.assertTrue(
                    any(possible.lower() in response.lower() 
                    for possible in possible_responses),
                    f"Failed for input: '{input_text}'. Response: '{response}'"
                )

    def test_sentiment_analysis(self):
        test_cases = [
            ("I love this!", "positive"),
            ("This is terrible", "negative"),
            ("What time is it?", "neutral"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = analyze_sentiment(text)
                self.assertEqual(result, expected)

    def test_api_endpoint(self):
        response = self.app.post('/get_response', data={'user_input': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.get_json())

if __name__ == '__main__':
    unittest.main()