from flask import Flask, render_template, request, send_file
import pyttsx3
from PyPDF2 import PdfReader

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error='No selected file')

    if not allowed_file(file.filename):
        return render_template('index.html', error='Invalid file type. Supported types: pdf, txt')

    # Save the uploaded file
    file_path = 'uploads/' + file.filename
    file.save(file_path)

    # Extract text from the file
    if file.filename.lower().endswith('.pdf'):
        pdf_reader = PdfReader(open(file_path, 'rb'))
        full_text = ""
        for page_num in range(len(pdf_reader.pages)):
            text = pdf_reader.pages[page_num].extract_text()
            clean_text = text.strip().replace('\n', ' ')
            full_text += clean_text
    elif file.filename.lower().endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            full_text = txt_file.read()

    # Save text to a text file
    text_file_path = 'static/' + file.filename.rsplit('.', 1)[0] + '.txt'
    with open(text_file_path, 'w', encoding='utf-8') as text_file:
        text_file.write(full_text)

    # Convert text to audio
    speaker = pyttsx3.init()
    speaker.setProperty('rate', 150)
    speaker.save_to_file(full_text, 'static/' + file.filename.rsplit('.', 1)[0] + '.mp3')
    speaker.runAndWait()
    speaker.stop()

    return render_template('result.html', text_file=text_file_path, audio_file=file.filename.rsplit('.', 1)[0] + '.mp3')

@app.route('/download/<filename>')
def download(filename):
    return send_file('static/' + filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
