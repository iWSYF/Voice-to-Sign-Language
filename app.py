from flask import Flask, render_template, request  
from vosk import Model, KaldiRecognizer 
import pyaudio
import json 
import os

# Initialize the Flask application
app = Flask(__name__) 

# Global variables for model, recognizer, audio stream, and PyAudio instance
model = None 
recognizer = None  
stream = None  
p = None  

# List of stop words to exclude from the recognized text
stop_this_words = [
    "any", "much", "many", "a", "an", "the", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "he", "she", "it", "they",
    "and", "but", "or", "nor", "yet", "so", "i'm", "you're", "he's", "she's", "it's", "we're", "they're",
    "i've", "you've", "we've", "they've","i'll", "you'll", "he'll", "she'll", "we'll", "they'll",
    "i'd", "you'd", "he'd", "she'd", "we'd", "they'd","isn't", "aren't", "wasn't", "weren't",
    "hasn't", "haven't", "hadn't","might've", "must've", "could've", "should've", "would've"
]

# Main route for the homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    global recognizer, stream  
    text = ""  # To store the recognized text
    words = []  # To store individual words
    images_to_show = []  # To store matching images

    if request.method == 'POST':
        # Record audio for 5 seconds by reading multiple audio chunks
        for _ in range(0, int(44100 / 1024 * 5)):  # Record for 5 seconds
            data = stream.read(1024) 
            if recognizer.AcceptWaveform(data):  
                result = json.loads(recognizer.Result())  # Parse the recognition result
                text += result.get('text', '') + ' '  # Append recognized text

        # Get the final result after recording
        final_result = json.loads(recognizer.FinalResult())  
        text += final_result.get('text', '') 

        # Split the recognized text into individual words
        words = text.strip().split()  
        # Filter out common stop words
        filtered_words = [word for word in words if word.lower() not in stop_this_words]

        # 🔎 Search inside the ASL folder for images matching the filtered words
        asl_path = os.path.join(app.static_folder, "ASL")
        asl_images = os.listdir(asl_path)  # List all images in ASL folder

        # Match filtered words with ASL image names
        for word in filtered_words:
            for img in asl_images:
                img_name = os.path.splitext(img)[0].lower()  # Get image name without extension
                if word.lower() == img_name:
                    images_to_show.append(f"ASL/{img}")  # Add matching image path

        # Debug prints to verify recognized words and selected images
        print("Filtered words:", filtered_words)  
        print("Images to show:", images_to_show)

        # Render the results on the HTML page
        return render_template('index.html', original_text=text.strip(), words=filtered_words, images=images_to_show)

    return render_template('index.html', original_text=None, words=None, images=None)

# Route for the about page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    # Load the Vosk speech recognition model
    model = Model(r"C:\Users\Wail Mawa\Desktop\vosk-model-en-us-0.22")
      # Example paths for other models
      # C:\Users\PC\Downloads\vosk-model-small-en-us-0.15 - EYAD 
      # C:\Users\wsyf9\OneDrive\Desktop\vosk-model-en-us-0.42-gigaspeech - Wail
      # C:\Users\wsyf9\OneDrive\Desktop\vosk-model-en-us-0.22

    # Create a recognizer with the model and sample rate
    recognizer = KaldiRecognizer(model, 44100)  

    # Initialize PyAudio and open an input audio stream
    p = pyaudio.PyAudio()  
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)  

    # Run the Flask app
    app.run(debug=True, use_reloader=False)
