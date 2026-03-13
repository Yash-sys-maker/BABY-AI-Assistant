import vosk
import sounddevice as sd
import queue
import json
import os
import asyncio
import edge_tts
import pygame
import time
import ollama

pygame.mixer.init()

# ==========================================
# 1. THE MOUTH (Edge-TTS with Barge-in)
# ==========================================
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
    
    with q.mutex:
        q.queue.clear()
        
    while pygame.mixer.music.get_busy():
        try:
            data = q.get_nowait()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                interrupt_text = result['text']
                
                if interrupt_text != "" and len(interrupt_text) > 3:
                    print(f"\n[INTERRUPTED!] Heard: {interrupt_text}")
                    pygame.mixer.music.stop() 
                    break 
        except queue.Empty:
            pass 
            
        time.sleep(0.01) 
        
    pygame.mixer.music.unload()
    try:
        os.remove(filename)
    except:
        pass

# ==========================================
# 2. THE BRAIN (Ollama with Memory)
# ==========================================
# ---> THIS IS THE MEMORY BANK THAT WAS MISSING! <---
chat_history = [
    {
        'role': 'system',
        'content': 'You are BABY, a highly intelligent and helpful personal AI assistant. Keep your spoken answers very concise, conversational, and short (1 to 2 sentences max).'
    }
]

def think(user_input):
    global chat_history
    print("...BABY is thinking...")
    
    chat_history.append({'role': 'user', 'content': user_input})
    
    response = ollama.chat(model='llama3.2', messages=chat_history)
    answer = response['message']['content']
    
    chat_history.append({'role': 'assistant', 'content': answer})
    
    if len(chat_history) > 11:
        chat_history = [chat_history[0]] + chat_history[-10:]
        
    return answer

# ==========================================
# 3. THE EARS (VOSK)
# ==========================================
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

model = vosk.Model("model")
rec = vosk.KaldiRecognizer(model, 16000)

# ==========================================
# 4. THE MAIN LOOP
# ==========================================
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    
    speak("Systems online. The brain is connected. I am ready.")
    
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            user_text = result['text']
            
            if user_text != "" and len(user_text) > 3:
                print(f"You said: {user_text}")
                
                if "stop" in user_text or "shut down" in user_text:
                    speak("Understood. Shutting down all systems.")
                    break
                
                else:
                    smart_reply = think(user_text)
                    speak(smart_reply)