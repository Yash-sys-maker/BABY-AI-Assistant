import pyttsx3

# 1. Initialize the 'Speaker' engine
engine = pyttsx3.init()

# 2. Setting the speaking speed 
engine.setProperty('rate', 150)

# 3. Choosing a voice 
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) 

def speak(text):
    print(f"NOVA: {text}") # This lets me see what she says
    engine.say(text)
    engine.runAndWait()


speak("Hello! I am Nova, your offline assistant. My systems are starting up.")
