# Resume Gap Detector 📄

A comprehensive AI-powered web application that analyzes resumes to predict suitable job roles and recommends personalized courses to bridge skill gaps.

## 🚀 Features

### Core Functionality
- **PDF Resume Upload & Analysis** - Upload PDF resumes for automated text extraction and processing
- **AI-Powered Job Role Prediction** - Advanced ML models predict the most suitable job roles with confidence scores
- **Skill Extraction & Matching** - Automatically extracts and matches skills from resume content
- **Personalized Course Recommendations** - Suggests relevant courses based on identified skill gaps
- **Interactive Visualizations** - Dynamic charts and graphs showing prediction results
- **Session Persistence** - Maintains user data across browser sessions for up to 1 hour

### User Experience
- **Modern UI/UX** - Clean, responsive design with smooth animations and transitions
- **Real-time Processing** - Live status updates during resume analysis
- **Multi-page Navigation** - Seamless navigation between resume analysis and course recommendations
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile devices

## 🛠️ Technology Stack

### Frontend
- **Streamlit** - Main web framework for UI components
- **HTML/CSS** - Custom styling with modern design principles
- **Matplotlib** - Data visualization and chart generation
- **Pandas** - Data manipulation and analysis

### Backend
- **Python 3.7+** - Core programming language
- **Machine Learning Models** - Custom trained models for job role prediction
- **Text Processing** - Advanced NLP for skill extraction and resume parsing
- **File Processing** - PDF text extraction and validation
- **Session Management** - Temporary data storage with automatic cleanup

### Data Storage
- **JSON** - Session data persistence
- **CSV** - Course database storage
- **Temporary Files** - Session-based file management

## 📁 Project Structure

```
resume-gap-detector/
├── app.py                      # Main application file
├── pages/
│   └── Course.py              # Course recommendations page
├── utils/
│   ├── __init__.py
│   ├── parser.py              # Resume parsing and skill extraction
│   ├── course.py              # Course recommendation logic
│   └── resume_data.py         # Resume text extraction utilities
├── data/
│   └── processed_courses.csv  # Course database
├── temp_data/                 # Temporary session storage
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip package manager
- At least 2GB RAM for model processing

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/resume-gap-detector.git
   cd resume-gap-detector
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare data files**
   - Ensure `processed_courses.csv` is in the `data/` directory
   - Verify course data contains required columns: `title`, `Instructor`, `Organization`, `Level`, `enrolled`, `rating`, `URL`

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`

## 📋 Requirements

### Python Dependencies
```text
streamlit>=1.28.0
pandas>=1.5.0
matplotlib>=3.5.0
numpy>=1.21.0
scikit-learn>=1.0.0
PyPDF2>=2.0.0
python-docx>=0.8.11
```

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: 500MB free space
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

## 🎯 Usage Guide

### Step 1: Upload Resume
1. Navigate to the main application page
2. Use the sidebar file uploader to select a PDF resume
3. Wait for the upload confirmation

### Step 2: Resume Analysis
1. The application automatically extracts text from your resume
2. Skills are identified and matched against the database
3. AI models predict suitable job roles with confidence scores
4. Results are displayed in both tabular and chart formats

### Step 3: Course Recommendations
1. Click "Get My Personalized Course Plan"
2. Navigate to the Course Recommendations page
3. View personalized course suggestions for each predicted role
4. Browse course details including instructor, rating, and enrollment
5. Click course links to access external learning platforms

### Step 4: Session Management
- Your data is automatically saved for 1 hour
- You can reload the page without losing progress
- Use the session information panel to manage your data

## 🔍 Features Deep Dive

### Resume Processing
- **Text Extraction**: Advanced PDF parsing with error handling
- **Skill Identification**: NLP-based skill matching from comprehensive database
- **Data Validation**: Ensures resume quality and completeness
- **Preview Mode**: Shows extracted text for verification

### Job Role Prediction
- **ML Models**: Trained classification models for accurate predictions
- **Confidence Scoring**: Provides reliability metrics for each prediction
- **Multi-Role Analysis**: Analyzes multiple potential career paths
- **Interactive Charts**: Visual representation of prediction results

### Course Recommendations
- **Skill Gap Analysis**: Identifies missing skills for target roles
- **Personalized Matching**: Courses matched to individual skill gaps
- **Quality Filtering**: Curated courses from reputable platforms
- **Responsive Cards**: Modern card-based course display

### Session Persistence
- **Temporary Storage**: Secure temporary file storage
- **Auto-Cleanup**: Automatic removal of expired sessions
- **Session Recovery**: Restore progress after browser refresh
- **Data Security**: Local storage with automatic expiration

## 🎨 UI/UX Features

### Design Elements
- **Modern Styling**: Clean, professional interface
- **Responsive Layout**: Works on all screen sizes
- **Interactive Elements**: Hover effects and smooth transitions
- **Color Scheme**: Professional blue theme with accessibility compliance

### User Experience
- **Progress Indicators**: Real-time processing status
- **Loading Animations**: Smooth loading states
- **Error Handling**: User-friendly error messages
- **Success Feedback**: Confirmation messages and celebrations

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom session timeout (default: 3600 seconds)
export SESSION_TIMEOUT=7200

# Optional: Set custom temporary directory
export TEMP_DIR="custom_temp_data"
```

### Course Database Configuration
The application expects a CSV file with the following columns:
- `title`: Course title
- `Instructor`: Course instructor name
- `Organization`: Educational platform/organization
- `Level`: Course difficulty level
- `enrolled`: Number of enrolled students
- `rating`: Course rating (0-5 scale)
- `URL`: Direct link to course

## 🐛 Troubleshooting

### Common Issues

**1. PDF Upload Fails**
- Ensure PDF is not password-protected
- Check file size (recommended < 10MB)
- Verify PDF contains extractable text

**2. No Skills Detected**
- Resume may lack recognizable skill keywords
- Try using a more detailed resume
- Ensure resume is in standard format

**3. Course Recommendations Not Loading**
- Check if `processed_courses.csv` exists
- Verify course data format
- Ensure network connectivity for external links

**4. Session Data Lost**
- Sessions expire after 1 hour
- Browser storage may be disabled
- Try refreshing the page

### Performance Optimization
- Use recent PDF files for better text extraction
- Limit resume size to under 5MB
- Close unused browser tabs for better performance

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make your changes
5. Run tests and linting
6. Submit a pull request

### Code Style
- Follow PEP 8 Python style guide
- Use meaningful variable names
- Add docstrings for functions
- Include error handling

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run linting
flake8 app.py pages/ utils/

# Check formatting
black --check app.py pages/ utils/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit Team** - For the excellent web framework
- **Course Providers** - Educational platforms providing course data
- **Open Source Community** - Various libraries and tools used
- **Beta Testers** - Users who provided valuable feedback

## 📞 Support

### Getting Help
- 📧 Email: work.deepraj@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/deeeppraj/resume_tracker/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/deeeppraj/resume_tracker/discussions)

### FAQ
**Q: What file formats are supported?**
A: Currently only PDF files are supported for resume upload.

**Q: How accurate are the job role predictions?**
A: Accuracy depends on resume quality and completeness. The system provides confidence scores to help evaluate predictions.

**Q: Can I use this for commercial purposes?**
A: Yes, under the MIT license terms. Please see the LICENSE file for details.

**Q: How long is my data stored?**
A: Session data is automatically deleted after 1 hour for privacy and security(stil under process tho)

---

**Made with ❤️ by [Deepraj Bhattacharjee]**

*Last updated: July 2025*