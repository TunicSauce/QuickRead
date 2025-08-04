from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import PyPDF2
from docx import Document
from werkzeug.utils import secure_filename
import bleach

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt_tab')
    nltk.download('stopwords')

class TextSummarizer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text):
        text = bleach.clean(text, tags=[], strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def smart_summary(self, text, percentage=30):
        sentences = sent_tokenize(text)
        if len(sentences) <= 2:
            return text
        
        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        sentence_scores = np.sum(tfidf_matrix.toarray(), axis=1)
        
        num_sentences = max(1, int(len(sentences) * percentage / 100))
        top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
        top_indices.sort()
        
        return ' '.join([sentences[i] for i in top_indices])
    
    def bullet_summary(self, text):
        sentences = sent_tokenize(text)
        if len(sentences) <= 3:
            return '• ' + '\n• '.join(sentences)
        
        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        tfidf_matrix = vectorizer.fit_transform(sentences)
        sentence_scores = np.sum(tfidf_matrix.toarray(), axis=1)
        
        num_points = min(5, max(3, len(sentences) // 3))
        top_indices = sentence_scores.argsort()[-num_points:][::-1]
        top_indices.sort()
        
        key_points = [sentences[i] for i in top_indices]
        return '• ' + '\n• '.join(key_points)
    
    def detailed_summary(self, text, percentage=30):
        sentences = sent_tokenize(text)
        if len(sentences) <= 3:
            return text
        
        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        tfidf_matrix = vectorizer.fit_transform(sentences)
        sentence_scores = np.sum(tfidf_matrix.toarray(), axis=1)
        
        num_sentences = max(3, int(len(sentences) * percentage / 100))
        top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
        top_indices.sort()
        
        selected_sentences = [sentences[i] for i in top_indices]
        
        if len(selected_sentences) >= 3:
            intro = selected_sentences[0]
            body = ' '.join(selected_sentences[1:-1]) if len(selected_sentences) > 2 else ''
            conclusion = selected_sentences[-1]
            
            abstract = f"Overview: {intro}"
            if body:
                abstract += f" Key findings: {body}"
            abstract += f" Summary: {conclusion}"
            return abstract
        else:
            return ' '.join(selected_sentences)
    
    def quick_summary(self, text, percentage=30):
        sentences = sent_tokenize(text)
        if len(sentences) <= 2:
            return text
        
        weighted_scores = []
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            score = 0
            
            if re.search(r'\d+', sentence):
                score += 2
            
            capitalized_words = re.findall(r'\b[A-Z][a-z]+', sentence)
            score += len(capitalized_words) * 0.5
            
            factual_keywords = ['according', 'reported', 'announced', 'confirmed', 'stated', 'revealed']
            for keyword in factual_keywords:
                if keyword in sentence.lower():
                    score += 1
            
            vectorizer = TfidfVectorizer(stop_words='english')
            try:
                tfidf_score = vectorizer.fit_transform([sentence]).sum()
                score += tfidf_score
            except:
                pass
            
            weighted_scores.append(score)
        
        num_sentences = max(1, int(len(sentences) * percentage / 100))
        top_indices = np.argsort(weighted_scores)[-num_sentences:][::-1]
        top_indices.sort()
        
        return ' '.join([sentences[i] for i in top_indices])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    return text

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")
    return text

summarizer = TextSummarizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        style = data.get('style', 'smart')
        percentage = int(data.get('percentage', 30))
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) < 50:
            return jsonify({'error': 'Text too short for summarization'}), 400
        
        clean_text = summarizer.clean_text(text)
        
        if style == 'smart':
            summary = summarizer.smart_summary(clean_text, percentage)
        elif style == 'bullet':
            summary = summarizer.bullet_summary(clean_text)
        elif style == 'detailed':
            summary = summarizer.detailed_summary(clean_text, percentage)
        elif style == 'quick':
            summary = summarizer.quick_summary(clean_text, percentage)
        else:
            return jsonify({'error': 'Invalid summarization style'}), 400
        
        return jsonify({'summary': summary})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif file_ext == 'docx':
            text = extract_text_from_docx(file_path)
        
        os.remove(file_path)
        
        if not text.strip():
            return jsonify({'error': 'No text could be extracted from the file'}), 400
        
        return jsonify({'text': text})
    
    except Exception as e:
        try:
            if 'file_path' in locals():
                os.remove(file_path)
        except:
            pass
        
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)