import vosk
import sys
import sounddevice as sd
import queue

# This is a 'queue' to hold the audio data
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

# 1. Load the model from your D: drive folder
model = vosk.Model("model")
rec = vosk.KaldiRecognizer(model, 16000)

# 2. Start the microphone
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("BABY is listening... Say something!")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            # This prints what BABY heard
            print(rec.Result())
        else:
            print(rec.PartialResult())