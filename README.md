# QuickRead

A powerful web-based text summarization application that transforms lengthy documents and articles into concise, meaningful summaries using advanced natural language processing techniques.

## Features

### 🎯 Multiple Summarization Styles
- **Smart Summary**: Intelligent sentence selection using TF-IDF scoring
- **Bullet Points**: Key highlights in an easy-to-scan format
- **Detailed Summary**: Comprehensive overview with structured sections
- **Quick Summary**: Essential facts and important information

### 📄 Document Processing
- Support for PDF and Microsoft Word documents
- Direct text input with real-time processing
- File size limit: 16MB
- Secure file handling with automatic cleanup

### 🎨 Modern Interface
- Clean, responsive design optimized for all devices
- Intuitive tabbed interface for text and document input
- Adjustable summary length (10-50% of original content)
- One-click copy to clipboard functionality
- Real-time loading indicators and error handling

### 🔒 Security & Reliability
- Input sanitization to prevent malicious content
- File type validation and size restrictions
- Secure temporary file management
- Cross-origin resource sharing (CORS) support

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Download the project files**
   ```bash
   cd QuickRead
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## How to Use

### Text Summarization
1. Select the "Summarize Text" tab
2. Paste or type your content into the text area
3. Choose your preferred summarization style
4. Adjust the summary length using the slider (except for Bullet Points)
5. Click "Generate Summary"
6. Copy your result with the copy button

### Document Summarization
1. Switch to the "Summarize Document" tab
2. Upload a PDF or Word document (drag & drop supported)
3. Select your summarization style and length
4. Click "Process Document"
5. Review and copy your generated summary

## Summarization Algorithms

### Smart Summary
Uses Term Frequency-Inverse Document Frequency (TF-IDF) analysis to identify and extract the most statistically significant sentences from your text.

### Bullet Points
Analyzes content structure to extract 3-5 key concepts and presents them as scannable bullet points, perfect for quick reviews.

### Detailed Summary
Creates a comprehensive overview with introduction, key findings, and conclusion sections for thorough understanding.

### Quick Summary
Prioritizes factual information, numerical data, and proper nouns to deliver the most essential facts and figures.

## Technical Stack

- **Backend**: Flask web framework with RESTful API design
- **NLP Processing**: NLTK for tokenization and text analysis
- **Machine Learning**: scikit-learn for TF-IDF vectorization
- **Document Parsing**: PyPDF2 for PDFs, python-docx for Word documents
- **Frontend**: HTML5, CSS3 (Tailwind), and vanilla JavaScript
- **Security**: bleach for input sanitization


## Project Structure

```
QuickRead/
├── app.py              # Flask application server
├── templates/
│   └── index.html      # Web interface
├── uploads/            # Temporary file storage (auto-created)
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Configuration

The application includes several configurable settings:

- **File Upload Limit**: 16MB maximum file size
- **Supported Formats**: PDF (.pdf) and Word (.docx) documents
- **Summary Length Range**: 10-50% of original content
- **Text Minimum**: 50 characters required for processing

## Requirements

- Text must be at least 50 characters for summarization
- PDF and DOCX files only, maximum 16MB
- NLTK language data downloads automatically on first run


## Performance Notes

- Processing time scales with document length
- PDF extraction may vary based on document complexity
- Large files (>5MB) may take longer to process
- Browser memory usage increases with very long summaries
