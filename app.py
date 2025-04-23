from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Import your AI modules (ensure these files exist)
try:
    from brain_of_doctor import encode_image, analyze_image_with_query
    from voice_of_patient import transcribe_with_groq
    from voice_of_doctor import text_to_speech_with_elevenlabs
except ImportError as e:
    print(f"Import error: {e}")
    # Create dummy functions if imports fail
    def encode_image(*args, **kwargs): return None
    def analyze_image_with_query(*args, **kwargs): return "AI service not available"
    def transcribe_with_groq(*args, **kwargs): return "Transcription service not available"
    def text_to_speech_with_elevenlabs(*args, **kwargs): return "voice_response.mp3"

system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/save_recording', methods=['POST'])
def save_recording():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        filename = secure_filename(f"recording_{int(time.time())}.wav")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        return jsonify({
            "status": "success",
            "filename": filename,
            "audio_url": f"/get_audio/{filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process', methods=['POST'])
def process():
    try:
        # Get form data
        audio_filename = request.form.get('audio_filename')
        if not audio_filename:
            return jsonify({"error": "No audio provided"}), 400

        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
                image_file.save(image_path)

        # Process the request
        speech_to_text = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_path,
            stt_model="whisper-large-v3"
        )

        doctor_response = analyze_image_with_query(
            query=system_prompt + " " + speech_to_text,
            encoded_image=encode_image(image_path) if image_path else None,
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )

        voice_filename = f"response_{int(time.time())}.mp3"
        voice_path = text_to_speech_with_elevenlabs(
            input_text=doctor_response,
            output_filepath_mp3=os.path.join(app.config['UPLOAD_FOLDER'], voice_filename)
        )

        return jsonify({
            "status": "success",
            "speech_to_text": speech_to_text,
            "doctor_response": doctor_response,
            "voice_url": f"/get_audio/{voice_filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_audio/<filename>')
def get_audio(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return "Audio file not found", 404
        return send_file(filepath, mimetype="audio/mpeg")
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port, debug=True)