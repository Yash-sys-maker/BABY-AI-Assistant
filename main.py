import pyttsx3

# 1. Initialize the 'Speaker' engine
engine = pyttsx3.init()

# 2. Set the speaking speed (150 is a good natural pace)
engine.setProperty('rate', 150)

# 3. Choose a voice (0 is usually a male voice, 1 is usually female)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) 

def speak(text):
    print(f"NOVA: {text}") # This lets you see what she says
    engine.say(text)
    engine.runAndWait()

# 4. Test it!
speak("Hello! I am Nova, your offline assistant. My systems are starting up.")