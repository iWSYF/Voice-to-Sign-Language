# Import necessary libraries
from flask import Flask, render_template, request  # Flask for web framework, render_template for HTML rendering, request for handling HTTP requests
from vosk import Model, KaldiRecognizer  # Vosk for speech recognition
import pyaudio  # PyAudio for microphone input
import json  # For parsing JSON responses

app = Flask(__name__)  # Create a Flask application instance

# Global variables (initialized here for use later)
model = None  # Vosk model variable (for speech recognition)
recognizer = None  # Recognizer for processing audio
stream = None  # Audio stream to capture input from microphone
p = None  # PyAudio instance to handle the microphone stream

# List of stop words to be filtered out from the recognized text
stop_this_words = [
    "any", "much", "many", "a", "an", "the", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "he", "she", "it", "they",
    "and", "but", "or", "nor", "yet", "so"
]

# Route for handling the main page, which can be accessed via both GET and POST methods
@app.route('/', methods=['GET', 'POST'])
def home():
    global recognizer, stream  # Use the global recognizer and stream initialized earlier
    text = ""  # Initialize the variable to store recognized text
    words = []  # Initialize an empty list to store the words

    # Check if the request method is POST (i.e., the user is submitting data)
    if request.method == 'POST':
        # Loop to capture 5 seconds of audio (44100 Hz sample rate with 1024 frames per buffer)
        for _ in range(0, int(44100 / 1024 * 5)):  # Recording for 5 seconds
            data = stream.read(1024)  # Read a chunk of audio data from the microphone
            if recognizer.AcceptWaveform(data):  # If the recognizer processes the audio chunk
                result = json.loads(recognizer.Result())  # Convert the result to a JSON object
                text += result.get('text', '') + ' '  # Add the recognized text to the text variable

        # After the recording, get the final result
        final_result = json.loads(recognizer.FinalResult())  # Convert the final result to JSON
        text += final_result.get('text', '')  # Append the final recognized text

        # Split the recognized text into individual words
        words = text.strip().split()  # Remove leading/trailing spaces and split into words

        # Filter out stop words from the recognized words
        filtered_words = [word for word in words if word.lower() not in stop_this_words]
        print("Filtered words:", filtered_words)  # Print the filtered words to the console for debugging

        # Return the filtered words and the original recognized text to be displayed in the HTML template
        return render_template('index.html', original_text=text.strip(), words=filtered_words)

    # If the request method is GET (i.e., when the page is first loaded), pass None to the template
    return render_template('index.html', original_text=None, words=None)

# for about.html page
@app.route('/about')
def about():
    return render_template('about.html')

# The main entry point of the script
if __name__ == '__main__':
    # Initialize the Vosk model for speech recognition
    model = Model(r"C:\Users\wsyf9\OneDrive\Desktop\vosk-model-en-us-0.42-gigaspeech")
      # Path to the Vosk model
      # C:\Users\PC\Downloads\vosk-model-small-en-us-0.15 - EYAD 
      # C:\Users\wsyf9\OneDrive\Desktop\vosk-model-en-us-0.42-gigaspeech - Wail
      
    recognizer = KaldiRecognizer(model, 44100)  # Initialize the recognizer with the model and sample rate (44100 Hz)

    # Initialize PyAudio for microphone input
    p = pyaudio.PyAudio()  # Create a PyAudio instance
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)  # Open the microphone stream
    stream.start_stream()  # Start capturing audio from the microphone

    # Start the Flask application in debug mode, with reloader disabled to prevent multiple initializations
    app.run(debug=True, use_reloader=False)  # Run the Flask web server (disabling reloader to prevent repeated initialization)
