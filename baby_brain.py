import os
import asyncio
import edge_tts
import pygame
import time
import ollama

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


# 3. TEXT MODE MAIN LOOP 

speak("Hello My Majesty! I am your humble assistant, BABY. How may I serve you today?")

while True:
    # NEW: A simple text input box instead of listening to the microphone!
    user_text = input("\n[Chat] -> ")
    
    if user_text.strip() != "":
        if "stop" in user_text.lower() or "shut down" in user_text.lower():
            speak("Understood My Majesty. Dont forget about me, ok?")
            break
        else:
            smart_reply = think(user_text)
            speak(smart_reply)