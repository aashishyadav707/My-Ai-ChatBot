from flask import Flask, render_template, request, jsonify
from nltk.chat.util import Chat, reflections
import random
from textblob import TextBlob
from datetime import datetime
import re

app = Flask(__name__)

# User memory (simple dictionary to store user info)
user_memory = {}

# Enhanced response patterns with more conversation topics
pairs = [
    [r"(hi|hello|hey|greetings|what's up)\b", 
     ["Hello there! How can I assist you today?", "Hi! What can I do for you?", "Hey! How can I help?"]],
    
    [r"my name is (.*)|i am (.*)|i'm (.*)", 
     ["Nice to meet you, %1! How can I help you today?", "Hello %1! What brings you here today?"]],
    
    [r"what('?s| is) your name\??", ["I'm ChatBot, your AI assistant!", "You can call me ChatBot!"]],
    
    [r"how (are you|do you feel)\??", ["I'm functioning well, thanks for asking! How about you?", "I'm here to help!"]],
    
    [r"thank(s| you)|thanks a lot|thx", ["You're welcome!", "Happy to help!", "No problem!"]],
    
    [r"(bye|goodbye|see ya|see you|quit)", ["Goodbye! Come back if you have more questions.", "See you later!", "Bye!"]],
    
    [r"tell me about yourself", 
     ["I'm an AI chatbot designed to have interesting conversations. I can discuss many topics, tell jokes, and ask thought-provoking questions!"]],
    
    [r"what can you do\??", 
     ["I can discuss various topics, ask you interesting questions, tell jokes, and have meaningful conversations. What would you like to talk about?"]],
    
    [r"tell me a joke", 
     ["Why don't scientists trust atoms? Because they make up everything!",
      "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
      "Why don't skeletons fight each other? They don't have the guts!"]],
    
    [r"give me advice", 
     ["Here's some general advice: Always be kind, stay curious, and never stop learning!",
      "My advice: Take breaks when you need them, your mental health is important.",
      "Remember: Small consistent actions lead to big results over time."]],
    
    [r"what do you think about (.*)\??", 
     ["I think %1 is an interesting topic! What specifically would you like to know?",
      "About %1, I believe there are many perspectives worth considering. What's your view?",
      "That's a complex subject. I'd love to hear your thoughts on %1 first."]],
    
    [r"(.*)", ["I'm not sure I understand. Could you rephrase that?", "Interesting! Can you tell me more?", "I'm still learning."]]
]

chatbot = Chat(pairs, reflections)

def analyze_sentiment(text):
    """Analyze sentiment of user input"""
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.3:
        return "positive"
    elif analysis.sentiment.polarity < -0.3:
        return "negative"
    return "neutral"

def get_random_question():
    """Return a random conversation starter"""
    questions = [
        "What's something interesting you learned recently?",
        "If you could visit any place in the world, where would you go?",
        "What's your favorite way to spend a free afternoon?",
        "Do you have any creative hobbies you enjoy?",
        "What's the most memorable meal you've ever had?"
    ]
    return random.choice(questions)

def get_bot_response(user_input):
    """Generate chatbot response with additional features"""
    try:
        user_input = user_input.lower()

        # Check for random question requests
        if "ask me something" in user_input or "ask me a question" in user_input:
            return get_random_question()

        # Check for time/date queries
        if "time" in user_input or "date" in user_input:
            return f"The current time is {datetime.now().strftime('%H:%M on %A, %B %d, %Y')}"

        # Get chatbot response
        response = chatbot.respond(user_input)
        
        # Fallback responses if no match is found
        if not response:
            sentiment = analyze_sentiment(user_input)
            fallback_responses = {
                "positive": ["You sound happy! Tell me more!", "Glad you're feeling good!", "Keep up the positivity!"],
                "negative": ["I'm sorry you're feeling that way. Can I assist?", "I'm here to help! What's wrong?", "Let me know how I can improve your day."],
                "neutral": ["Can you rephrase that?", "I'm not sure I understand. Could you explain?", "That's interesting! Tell me more."]
            }
            response = random.choice(fallback_responses[sentiment])

        # Check for user's name and personalize response
        name_match = re.search(r"my name is (\w+)|i am (\w+)|i'm (\w+)", user_input)
        if name_match:
            name = name_match.group(1) or name_match.group(2) or name_match.group(3)
            user_memory['name'] = name
            response = f"Nice to meet you, {name}! {response}"

        return response

    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "I encountered an error processing your request. Please try again."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form.get("user_input", "").strip()
    if not user_input:
        return jsonify({"response": "Please enter a message!"})

    bot_response = get_bot_response(user_input)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)