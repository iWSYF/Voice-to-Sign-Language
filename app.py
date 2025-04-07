from flask import Flask, render_template, request  
from vosk import Model, KaldiRecognizer 
import pyaudio
import json 
import os

app = Flask(__name__) 


model = None 
recognizer = None  
stream = None  
p = None  


stop_this_words = [
    "any", "much", "many", "a", "an", "the", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "he", "she", "it", "they",
    "and", "but", "or", "nor", "yet", "so", "i'm", "you're", "he's", "she's", "it's", "we're", "they're",
    "i've", "you've", "we've", "they've","i'll", "you'll", "he'll", "she'll", "we'll", "they'll",
    "i'd", "you'd", "he'd", "she'd", "we'd", "they'd","isn't", "aren't", "wasn't", "weren't",
    "hasn't", "haven't", "hadn't","might've", "must've", "could've", "should've", "would've" 
]

@app.route('/', methods=['GET', 'POST'])
def home():
    global recognizer, stream  
    text = ""  
    words = []  
    images_to_show = []

    if request.method == 'POST':
        for _ in range(0, int(44100 / 1024 * 5)):  # Recording for 5 seconds
            data = stream.read(1024) 
            if recognizer.AcceptWaveform(data):  
                result = json.loads(recognizer.Result())  
                text += result.get('text', '') + ' ' 

        final_result = json.loads(recognizer.FinalResult())  
        text += final_result.get('text', '') 

        words = text.strip().split()  
        filtered_words = [word for word in words if word.lower() not in stop_this_words]

        # 🔎 نبحث داخل مجلد ASL عن صور تطابق الكلمات
        asl_path = os.path.join(app.static_folder, "ASL")
        asl_images = os.listdir(asl_path)

        for word in filtered_words:
            for img in asl_images:
                img_name = os.path.splitext(img)[0].lower()
                if word.lower() == img_name:
                    images_to_show.append(f"ASL/{img}")

        print("Filtered words:", filtered_words)  
        print("Images to show:", images_to_show)

        return render_template('index.html', original_text=text.strip(), words=filtered_words, images=images_to_show)

    return render_template('index.html', original_text=None, words=None, images=None)

# for about.html page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    model = Model(r"C:\Users\Wail Mawa\Desktop\vosk-model-en-us-0.22")
      # Path to the Vosk model
      # C:\Users\PC\Downloads\vosk-model-small-en-us-0.15 - EYAD 
      # C:\Users\wsyf9\OneDrive\Desktop\vosk-model-en-us-0.42-gigaspeech - Wail
      # C:\Users\wsyf9\OneDrive\Desktop\vosk-model-en-us-0.22

      
    recognizer = KaldiRecognizer(model, 44100)  

    p = pyaudio.PyAudio()  
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)  

    app.run(debug=True, use_reloader=False) 