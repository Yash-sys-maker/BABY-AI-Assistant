import os
import asyncio
import edge_tts
import pygame
import time
import ollama
import webbrowser
import pywhatkit
pygame.mixer.init()


# 1. THE MOUTH 

async def generate_audio(text, filename):
    voice = "en-IN-NeerjaNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def speak(text):
    print(f"BABY: {text}")
    filename = f"temp_{int(time.time())}.mp3"
    
    asyncio.run(generate_audio(text, filename))
    
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    print("   -> [Press Ctrl+C to instantly stop her yapping] <-")
    
    # NEW: The Killswitch logic
    try:
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pygame.mixer.music.stop() # to stop her yapping immediately
        print("\n[skipped!]")
        time.sleep(0.2) 
        
    pygame.mixer.music.unload()
    try:
        os.remove(filename)
    except:
        pass

# 2. THE BRAIN 

chat_history = [
    {
        'role': 'system',
        'content': 'You are BABY, a highly intelligent personal AI assistant. Give very smart but VERY SHORT answers (1 to 2 sentences maximum). If the user needs more details, they will explicitly ask you to elaborate.'
    }
]
def think(user_input):
    global chat_history
    print(" Wait a sec Majesty, Let me Cook")
    
    chat_history.append({'role': 'user', 'content': user_input})
    
    response = ollama.chat(model='llama3.2', messages=chat_history)
    answer = response['message']['content']
    
    chat_history.append({'role': 'assistant', 'content': answer})
    
    if len(chat_history) > 11:
        chat_history = [chat_history[0]] + chat_history[-10:]
        
    return answer


# New : Accessing browser



def use_skills(text):
    text = text.lower() 
    
    # 1.  YouTube Playback
    if "play " in text and " on youtube" in text:
        song = text.replace("play ", "").replace(" on youtube", "").strip()
        pywhatkit.playonyt(song)
        return f"Playing {song} on YouTube right now."
        
    # 2.  YouTube Search
    elif "search " in text and " on youtube" in text:
        query = text.replace("search ", "").replace(" on youtube", "").strip()
        # URLs use "+" instead of spaces, so we format the query for the browser
        search_url = query.replace(" ", "+")
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_url}")
        return f"Searching YouTube for {query}."
        
    # 3.  Google Search
    elif "search " in text and " on google" in text:
        query = text.replace("search ", "").replace(" on google", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching Google for {query}."
        
    # 4. Basic Opens 
    elif "open youtube" in text:
        webbrowser.open("https://www.youtube.com")
        return "Opening the YouTube homepage."
        
    elif "open google" in text:
        webbrowser.open("https://www.google.com")
        return "Opening the Google homepage."
        
    elif "open github" in text:
        webbrowser.open("https://github.com")
        return "Opening your GitHub workspace."
        
    return None

# 3. TEXT MODE MAIN LOOP 


speak(" Hello Majesty! I am your BABY, your personal AI assistant. How can I help you today?")

while True:
    user_text = input("\n[STart your yapp] -> ")
    
    if user_text.strip() != "":
        if "stop" in user_text.lower() or "shut down" in user_text.lower():
            speak("Goodbye Majesty! If you need me again, just call me up. *wink*")
            break
        else:
         
            # First, checking if the user asked her to perform a physical physical
            skill_response = use_skills(user_text)
            
            if skill_response != None:
                # If she successfully used a skill, just speak the confirmation!
                speak(skill_response)
            else:
                # If it was just a normal question, send it to her LLaMA brain
                smart_reply = think(user_text)
                speak(smart_reply)