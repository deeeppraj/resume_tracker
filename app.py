import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import logging
from typing import List, Tuple, Optional

from utils import resume_data, output_predict
from utils.parser import extract_skills_from_text
import nltk
import os

# Set NLTK data path to a known directory
nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

# Download required corpora
for res, path in [('punkt', 'tokenizers/punkt'), ('stopwords', 'corpora/stopwords')]:
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(res, download_dir=nltk_data_dir)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Resume Gap Detector", 
    layout="centered",
    page_icon="📄"
)

# Initialize session state
if 'go_to_course' not in st.session_state:
    st.session_state['go_to_course'] = False
if 'skills' not in st.session_state:
    st.session_state['skills'] = []
if 'predicted_role' not in st.session_state:
    st.session_state['predicted_role'] = ""
if 'confidence_score' not in st.session_state:
    st.session_state['confidence_score'] = 0
if 'processing_complete' not in st.session_state:
    st.session_state['processing_complete'] = False
if 'current_resume_name' not in st.session_state:
    st.session_state['current_resume_name'] = ""

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E86C1;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #2E86C1;
        color: white;
        padding: 0.6em 1.2em;
        border-radius: 8px;
        border: none;
        font-weight: 500;
        font-size: 16px;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1A5276;
        color: #fff;
        transform: translateY(-2px);
    }
    .skills-container {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .confidence-badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        margin: 0.25em;
        background-color: #2E86C1;
        color: white;
        border-radius: 12px;
        font-size: 0.875em;
    }
    .main .block-container {
        padding-bottom: 5rem;
    }
    .scroll-indicator {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #2E86C1;
        color: white;
        padding: 10px;
        border-radius: 50%;
        z-index: 1000;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

def display_file_info(resume) -> None:
    """Display file information in a formatted way"""
    name = resume.name
    size = round(resume.size / 1024, 2)
    file_type = resume.type
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 File Name", name)
    with col2:
        st.metric("📏 Size (KB)", size)
    with col3:
        st.metric("🔧 Type", file_type.split('/')[-1].upper())

def create_matplotlib_chart(labels: List[str], scores: List[float]) -> None:
    """Create a matplotlib chart (fallback for compatibility)"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create horizontal bar chart
    bars = ax.barh(labels[::-1], scores[::-1], color=['#2E86C1', '#5DADE2', '#85C1E9', '#AED6F1', '#D6EAF8'])
    
    # Customize chart
    ax.set_xlabel("Confidence (%)")
    ax.set_xlim(0, 100)
    ax.set_title("Job Role Predictions", fontsize=16, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, score) in enumerate(zip(bars, scores[::-1])):
        ax.text(score + 1, bar.get_y() + bar.get_height()/2, 
                f"{score}%", va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig)

def display_skills_with_badges(skills: List[str]) -> None:
    """Display skills as styled badges"""
    if skills:
        st.markdown("### 🎯 Extracted Skills")
        skills_html = ""
        for skill in sorted(skills):
            skills_html += f'<span class="confidence-badge">{skill}</span>'
        
        st.markdown(f'<div class="skills-container">{skills_html}</div>', 
                   unsafe_allow_html=True)
    else:
        st.info("🔍 No matching skills found in the resume.")

def validate_predictions(predictions: List[Tuple]) -> bool:
    """Validate prediction results"""
    if not predictions or len(predictions) == 0:
        return False
    
    for pred in predictions:
        if not isinstance(pred, tuple) or len(pred) != 2:
            return False
        
        label, score = pred
        if not isinstance(label, str) or not isinstance(score, (int, float)):
            return False
        
        if score < 0 or score > 1:
            return False
    
    return True

# Header
st.markdown('<h1 class="main-header">📄 Resume Gap Detector</h1>', 
            unsafe_allow_html=True)

# Sidebar upload section
with st.sidebar:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📁 Upload Resume")
    st.caption("Upload your PDF resume for analysis")
    
    resume = st.file_uploader(
        label='Choose a PDF file',
        accept_multiple_files=False,
        type=['pdf'],
        help="Only PDF files are supported"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if resume is None:
        st.info("📌 Waiting for a PDF resume to be uploaded.")

# Main content area
if resume is not None:
    try:
        # Check if this is a new resume or if processing is already complete
        is_new_resume = st.session_state.get('current_resume_name', '') != resume.name
        
        # If it's a new resume, reset processing state
        if is_new_resume:
            st.session_state['processing_complete'] = False
            st.session_state['current_resume_name'] = resume.name
            st.session_state['go_to_course'] = False
        
        # Display file information
        st.success("✅ Resume uploaded successfully!")
        display_file_info(resume)
        
        # Only run processing if not already completed for this resume
        if not st.session_state.get('processing_complete', False):
            # Extract text from resume
            with st.spinner("Extracting text from resume..."):
                extracted_text, is_valid = resume_data(resume)
            
            if not is_valid:
                st.error("❌ Failed to extract text from the PDF. Please ensure the file is not corrupted.")
                st.stop()
            
            # Show preview of extracted text
            with st.expander("📝 Preview Extracted Text"):
                st.text_area("Extracted Content", 
                            extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text, 
                            height=150, disabled=True)
            
            # Process resume with animated status
            status_placeholder = st.empty()
            with status_placeholder.status("Processing resume...", expanded=True) as status:
                st.write("• Extracting text from the uploaded document.")
                time.sleep(1.2)

                st.write("• Preprocessing the content for analysis.")
                time.sleep(1.2)

                st.write("• Running model inference to determine job role.")
                predictions = output_predict([[extracted_text]])
                time.sleep(1)

                st.write("• Finalizing results.")
                time.sleep(1.5)

                status.update(
                    label="Resume analysis completed successfully.",
                    state="complete",
                    expanded=False
                )
            
            status_placeholder.empty()
            
            # Validate predictions
            if not validate_predictions(predictions):
                st.error("❌ Invalid prediction results. Please try again.")
                st.stop()
            
            # Store results in session state
            st.session_state['extracted_text'] = extracted_text
            st.session_state['predictions'] = predictions
            st.session_state['processing_complete'] = True
            
            # Extract and store skills
            skills = extract_skills_from_text(resume)
            st.session_state['extracted_skills'] = skills
            
        else:
            # Use stored results from session state
            extracted_text = st.session_state.get('extracted_text', '')
            predictions = st.session_state.get('predictions', [])
            skills = st.session_state.get('extracted_skills', [])
            
            # Show that processing was already completed
            st.info("✅ Resume analysis already completed for this file.")
            
            # Show preview of extracted text
            with st.expander("📝 Preview Extracted Text"):
                st.text_area("Extracted Content", 
                            extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text, 
                            height=150, disabled=True)
        
        # Display skills (always show, regardless of processing state)
        display_skills_with_badges(skills)
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Job Role Analysis Results")
        
        # Prepare data
        labels = [label for label, _ in predictions]
        scores = [round(score * 100, 2) for _, score in predictions]
        
        # Create columns for table and chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Prediction Table")
            df_result = pd.DataFrame({
                "Job Role": labels,
                "Confidence (%)": scores
            })
            st.dataframe(df_result, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### 📊 Confidence Chart")
            create_matplotlib_chart(labels, scores)
        
        # Display top recommendation
        if labels and scores:
            st.info(f"🎯 **Top Recommendation**: {labels[0]} with {scores[0]}% confidence")
        
        # Action button section
        st.markdown("---")
        st.markdown("### 🚀 Next Steps")
        
        # Create centered button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🎯 Get My Personalized Course Plan", key="course_plan_btn"):
                # Store results in session state
                st.session_state["skills"] = skills if skills else ["python", "flask", "sql"]
                st.session_state["predicted_role"] = labels[0] if labels else "Data Engineer"
                st.session_state["confidence_score"] = scores[0] if scores else 0
                st.session_state["go_to_course"] = True
                
                with st.spinner("Preparing your personalized course plan..."):
                    time.sleep(2)
                
                st.success("🎉 Processing Complete!")
                st.balloons()
                
                # Show navigation message
                st.markdown("""
                    <div style="text-align: center; margin-top: 20px;">
                        <h4>🎯 Ready to explore your course recommendations!</h4>
                        <p>Click the button below to proceed to the course page.</p>
                    </div>
                """, unsafe_allow_html=True)
        
        # Show navigation button if processing is complete
        if st.session_state.get("go_to_course", False):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📚 Go to Course Recommendations", key="navigate_btn"):
                    st.session_state["go_to_course"] = False
                    try:
                        st.switch_page("pages/Course.py")
                    except Exception as e:
                        st.error(f"Navigation error: {str(e)}")
                        st.info("Please navigate to the Course page manually from the sidebar.")
        
        # Additional information section
        st.markdown("---")
        st.markdown("### 📚 About This Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            processing_status = "✅ Completed" if st.session_state.get('processing_complete', False) else "⏳ In Progress"
            st.markdown(f"""
            **Analysis Details:**
            - **Status:** {processing_status}
            - ✅ Text extraction completed
            - ✅ Skill matching performed
            - ✅ Job role prediction generated
            - ✅ Confidence scores calculated
            """)
        
        with col2:
            st.markdown(f"""
            **Results Summary:**
            - **Skills Found:** {len(skills) if skills else 0}
            - **Top Match:** {labels[0] if labels else 'N/A'}
            - **Confidence:** {scores[0] if scores else 0}%
            - **Predictions:** {len(predictions)} roles analyzed
            """)
        
        # Footer sectionz
        st.markdown("---")
        processing_time = "Already processed" if st.session_state.get('processing_complete', False) else "Just completed"
        st.markdown(f"""
            <div style="text-align: center; color: #666; margin-top: 2rem;">
                <p>Analysis {processing_time.lower()}! 🎉</p>
                <p><small>Resume Gap Detector v1.0 - Powered by AI</small></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Add some bottom padding to ensure everything is visible
        st.markdown("<br><br><br>", unsafe_allow_html=True)
            
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        st.error(f"❌ An error occurred while processing your resume: {str(e)}")
        st.info("Please try uploading a different PDF file or contact support if the issue persists.")

st.markdown("""
    <div class="scroll-indicator" onclick="window.scrollTo(0, 0);" title="Scroll to top">
        ↑
    </div>
""", unsafe_allow_html=True)