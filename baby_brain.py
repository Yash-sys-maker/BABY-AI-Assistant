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
    
    # Empty the ear queue right before she talks so old noise doesn't trigger an interrupt
    with q.mutex:
        q.queue.clear()
        
    # THE NEW BARGE-IN LOOP
    while pygame.mixer.music.get_busy():
        try:
            # While audio is playing, instantly check if you are talking
            data = q.get_nowait()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                interrupt_text = result['text']
                
                # If she hears you say a real word, she kills her own audio
                if interrupt_text != "" and len(interrupt_text) > 3:
                    print(f"\n[INTERRUPTED!] Heard: {interrupt_text}")
                    pygame.mixer.music.stop() # Instantly shut her mouth
                    break # Break out of the loop and go back to listening
        except queue.Empty:
            pass # If you aren't talking, just keep playing the audio
            
        time.sleep(0.01) # Check your mic 100 times a second
        
    pygame.mixer.music.unload()
    try:
        os.remove(filename)
    except:
        pass

# ==========================================
# 2. THE BRAIN (Ollama)
# ==========================================
def think(user_input):
    print("...BABY is thinking...")
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': 'You are BABY, a highly intelligent and helpful personal AI assistant. Keep your spoken answers very concise, conversational, and short (1 to 2 sentences max).'
        },
        {
            'role': 'user',
            'content': user_input
        }
    ])
    return response['message']['content']

# ==========================================
# 3. THE EARS (VOSK)
# ==========================================
q = queue.Queue()

def callback(indata, frames, time, status):
    # Ears are now ALWAYS ON. No more blocking.
    q.put(bytes(indata))

# ---> THE MISSING EARS ARE BACK <---
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
            
            # Noise filter. Ignore empty text and tiny 1-letter fan noises
            if user_text != "" and len(user_text) > 3:
                print(f"You said: {user_text}")
                
                if "stop" in user_text or "shut down" in user_text:
                    speak("Understood. Shutting down all systems.")
                    break
                
                else:
                    smart_reply = think(user_text)
                    speak(smart_reply)