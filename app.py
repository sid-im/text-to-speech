from flask import Flask, request, render_template, send_file, redirect, url_for
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import PyPDF2

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    pdfReader = PyPDF2.PdfReader(filepath)
    text = ''
    for page in pdfReader.pages:
        text += page.extract_text()
    return text

def convert_text_to_speech(text, lang='kn'):
    translated_text = GoogleTranslator(source='auto', target=lang).translate(text)
    tts = gTTS(text=translated_text, lang=lang, lang_check=True)
    tts.save("tts.mp3")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Process text from file
            if file.filename.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif file.filename.endswith('.pdf'):
                text = extract_text_from_pdf(filepath)

            convert_text_to_speech(text)
            return redirect(url_for('download_file'))

        elif 'text' in request.form:
            text = request.form['text']
            convert_text_to_speech(text)
            return redirect(url_for('download_file'))
    
    return render_template('index.html')

@app.route('/download')
def download_file():
    return send_file('tts.mp3', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
