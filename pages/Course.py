# Course.py
import streamlit as st
import pandas as pd
import os
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta

# Assuming utils.parser and utils.course are correctly in your project structure
try:
    from utils.parser import missingskills
    from utils.course import get_course_recomend
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure utils.parser and utils.course modules are available")
    st.stop()

# Configuration for persistence
TEMP_DIR = "temp_data"
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Page config
st.set_page_config(page_title="🚀 Course Recommendations", layout="wide")
st.title('Course Predictions')

# --- Custom CSS for Styling ---
st.markdown("""
<style>
.card {
    border: 1px solid #d1d5db;
    border-radius: 12px;
    padding: 16px;
    background-color: #ffffff;
    min-height: 320px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s ease-in-out;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}
.organization-tag {
    background-color: #e0f2fe;
    color: #0369a1;
    display: inline-block;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-top: 6px;
}
.card-title {
    margin: 0 0 10px 0;
    font-size: 1.1rem;
    font-weight: 700;
    color: #1f2937 !important;
    line-height: 1.3;
    display: block;
}
.card-details p {
    margin: 8px 0;
    font-size: 0.9rem;
    color: #4b5563;
    font-weight: 500;
}
.card-details ul {
    list-style-type: none;
    padding: 0;
    margin: 6px 0;
}
.card-details li {
    margin: 5px 0;
    font-size: 0.85rem;
    color: #4b5563;
    font-weight: 500;
    position: relative;
    padding-left: 14px;
}
.card-details li:before {
    content: "•";
    color: #3b82f6;
    font-weight: bold;
    position: absolute;
    left: 0;
}
.card-details strong {
    font-weight: 600;
    color: #374151;
}
.view-course-btn a {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white !important;
    padding: 10px 16px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 600;
    display: block;
    text-align: center;
    transition: background 0.3s ease;
}
.view-course-btn a:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    text-decoration: none;
}
.missing-skills-container {
    background-color: #f3f4f6;
    border-left: 4px solid #3b82f6;
    padding: 15px;
    margin: 20px 0;
    border-radius: 8px;
}
.missing-skills-title {
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 10px;
}
.skill-tag {
    background-color: #dbeafe;
    color: #1e40af;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    margin-right: 8px;
    margin-bottom: 4px;
    display: inline-block;
}
.error-message {
    background-color: #fee2e2;
    border: 1px solid #fecaca;
    color: #dc2626;
    padding: 12px;
    border-radius: 8px;
    margin: 10px 0;
}
.warning-message {
    background-color: #fef3c7;
    border: 1px solid #fde68a;
    color: #d97706;
    padding: 12px;
    border-radius: 8px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# --- Persistence Functions ---
def ensure_temp_directory():
    """Create temp directory if it doesn't exist."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def get_session_id():
    """Generate or retrieve a session ID for the current user."""
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state['session_id'] = str(uuid.uuid4())
    return st.session_state['session_id']

def save_session_data(predictions, skills):
    """Save session data to a temporary file."""
    try:
        ensure_temp_directory()
        session_id = get_session_id()
        
        data = {
            'predictions': predictions,
            'skills': skills,
            'timestamp': datetime.now().isoformat()
        }
        
        filepath = os.path.join(TEMP_DIR, f"session_{session_id}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        return True
    except Exception as e:
        st.error(f"Error saving session data: {e}")
        return False

def load_session_data():
    """Load session data from temporary file."""
    try:
        session_id = get_session_id()
        filepath = os.path.join(TEMP_DIR, f"session_{session_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Check if data is not too old
        timestamp = datetime.fromisoformat(data['timestamp'])
        if datetime.now() - timestamp > timedelta(seconds=SESSION_TIMEOUT):
            # Data is too old, remove it
            os.remove(filepath)
            return None
        
        return data
    except Exception as e:
        st.error(f"Error loading session data: {e}")
        return None

def cleanup_old_sessions():
    """Remove old session files."""
    try:
        if not os.path.exists(TEMP_DIR):
            return
        
        current_time = datetime.now()
        for filename in os.listdir(TEMP_DIR):
            if filename.startswith("session_") and filename.endswith(".json"):
                filepath = os.path.join(TEMP_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    if current_time - timestamp > timedelta(seconds=SESSION_TIMEOUT):
                        os.remove(filepath)
                except:
                    # If we can't read the file, remove it
                    os.remove(filepath)
    except Exception as e:
        pass  # Silently handle cleanup errors

def get_url_params():
    """Get URL parameters for session restoration."""
    try:
        query_params = st.query_params
        return query_params.get('session_id', [None])[0] if 'session_id' in query_params else None
    except:
        return None

def set_url_params(session_id):
    """Set URL parameters for session restoration."""
    try:
        st.query_params['session_id'] = session_id
    except:
        pass  # Ignore if URL params can't be set

def restore_session_state():
    """Restore session state from saved data."""
    if 'predictions' not in st.session_state or 'skills' not in st.session_state:
        saved_data = load_session_data()
        if saved_data:
            st.session_state['predictions'] = saved_data['predictions']
            st.session_state['skills'] = saved_data['skills']
            return True
    return False

@st.cache_data(show_spinner=False)
def load_course_data():
    """Loads the processed course data from a CSV file."""
    # Check multiple possible locations for the CSV file
    possible_paths = [
        'processed_courses.csv',
        'data/processed_courses.csv',
        '../data/processed_courses.csv'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                return pd.read_csv(path)
            except Exception as e:
                st.error(f"Error loading CSV from {path}: {e}")
                continue
    
    # If no file found, create an empty DataFrame with expected columns
    st.error("processed_courses.csv not found in any expected location")
    return pd.DataFrame(columns=['title', 'Instructor', 'Organization', 'Level', 'enrolled', 'rating', 'URL'])

@st.cache_data(show_spinner=False)
def get_course_data_cached(indices):
    """Retrieves course data for given indices from the cached dataframe."""
    try:
        # Load course data once
        course_data = load_course_data()
        
        if course_data.empty:
            return []
                
        # Filter out invalid indices
        valid_indices = [i for i in indices if 0 <= i < len(course_data)]
        if len(valid_indices) != len(indices):
            st.warning(f"Some course indices were out of range. Using {len(valid_indices)} valid recommendations.")
                
        return [course_data.iloc[i].to_dict() for i in valid_indices]
    except Exception as e:
        st.error(f"Error retrieving course data: {e}")
        return []

@st.cache_data(show_spinner="Fetching fresh recommendations...")
def get_recommendations_cached(missing_skills):
    """Gets course recommendations based on missing skills, with caching."""
    try:
        return get_course_recomend(missing_skills)
    except Exception as e:
        st.error(f"Error getting course recommendations: {e}")
        return []

def clean_data_value(value, default='N/A'):
    """Clean data values, handling 'not found' strings and None values."""
    if value is None or pd.isna(value):
        return default
    
    value_str = str(value).strip()
    if value_str.lower() in ['not found', 'n/a', '', 'none', 'nan']:
        return default
    
    return value_str

def format_enrolled_count(enrolled):
    """Format enrollment count for display."""
    cleaned = clean_data_value(enrolled)
    if cleaned == 'N/A':
        return 'N/A'
    
    try:
        # Try to parse as number and format
        num = float(cleaned.replace(',', ''))
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return f"{int(num):,}"
    except (ValueError, AttributeError):
        return cleaned

def format_rating(rating):
    """Format rating for display."""
    cleaned = clean_data_value(rating)
    if cleaned == 'N/A':
        return 'N/A'
    
    try:
        rating_float = float(cleaned)
        return f"⭐ {rating_float:.1f}"
    except (ValueError, TypeError):
        return cleaned

def validate_url(url):
    """Validate and clean URL."""
    if not url or pd.isna(url):
        return '#'
    
    url_str = str(url).strip()
    if url_str.lower() in ['not found', 'n/a', '', 'none', 'nan']:
        return '#'
    
    if not url_str.startswith(('http://', 'https://')):
        return '#'
    
    return url_str

# --- Main Application Logic ---
def main():
    # Clean up old sessions on app start
    cleanup_old_sessions()
    
    # Try to restore session state from saved data
    restored = restore_session_state()
    
    if restored:
        st.success("✅ Session restored successfully!")
    
    # Check if necessary data is in session state
    if 'predictions' not in st.session_state or 'skills' not in st.session_state:
        st.markdown("""
        <div class="warning-message">
            <strong>⚠️ No Resume Data Found</strong><br>
            It looks like you've navigated directly to this page or the session data has expired. 
            Please go back to the main application page to upload your resume and get job predictions first.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🏠 Go to Resume Analysis", type="primary"):
                try:
                    st.switch_page("app.py")
                except Exception as e:
                    st.error(f"Navigation error: {str(e)}")
                    st.info("Please navigate to the main application page manually.")
        return

    try:
        # Get predictions and skills from session state
        predictions = st.session_state['predictions']
        skills = st.session_state['skills']
        
        # Save current session data for persistence
        session_id = get_session_id()
        save_session_data(predictions, skills)
        set_url_params(session_id)
        
        # Add session info for user
        with st.expander("ℹ️ Session Information"):
            st.info(f"Session ID: {session_id[:8]}...")
            st.info("Your session data is temporarily saved. You can reload this page within 1 hour.")
            if st.button("Clear Session Data"):
                try:
                    filepath = os.path.join(TEMP_DIR, f"session_{session_id}.json")
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    st.session_state.clear()
                    st.success("Session data cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing session: {e}")
        
        # Validate data
        if not predictions or not skills:
            st.error("Invalid session data. Please return to the main page and upload your resume again.")
            return
        
        # Process predictions (limit to top 5)
        labels = [predictions[i][0] for i in range(min(5, len(predictions)))]
        skills_set = set(skill.lower().strip() for skill in skills if skill.strip())
        
        # Get missing skills
        missing = missingskills(labels=labels, skills=skills_set)
        
        if not missing:
            st.success("🎉 Congratulations! You already have all the skills needed for the predicted job roles.")
            return
        
        # Display recommendations for each missing role
        for role_data in missing:
            if len(role_data) < 2:
                continue
                
            label, missing_skill_list = role_data[0], role_data[1]
            
            # Skip if no missing skills
            if not missing_skill_list:
                continue
            
            with st.spinner(f"⌛ Curating recommendations for the **{label}** role..."):
                recommendations = get_recommendations_cached(missing_skill_list)
                course_cards_data = get_course_data_cached(recommendations)
            
            # Display section header
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"## 🚀 Recommended Skill Upgrades for **{label}**")
            st.markdown("---")
            
            # Display course cards
            if course_cards_data:
                # Use responsive columns (max 4 on desktop for smaller cards)
                num_cols = min(len(course_cards_data), 4)
                cols = st.columns(num_cols)
                
                for i, course in enumerate(course_cards_data):
                    # Safely get and clean course details
                    title = clean_data_value(course.get('title', 'N/A'), 'Untitled Course')
                    instructor = clean_data_value(course.get('Instructor', 'N/A'))
                    organization = clean_data_value(course.get('Organization', 'N/A'))
                    level = clean_data_value(course.get('Level', 'N/A'))
                    
                    enrolled_display = format_enrolled_count(course.get('enrolled', 'N/A'))
                    rating_display = format_rating(course.get('rating', 'N/A'))
                    course_url = validate_url(course.get('URL', '#'))
                    
                    # Create course card
                    with cols[i % num_cols]:
                        st.markdown(
                            f"""
                            <div class="card">
                                <div>
                                    <h4 class="card-title">{title}</h4>
                                    <div class="organization-tag">{organization}</div>
                                    <div class="card-details">
                                        <ul>
                                            <li><strong>Instructor:</strong> {instructor}</li>
                                            <li><strong>Level:</strong> {level}</li>
                                            <li><strong>Enrolled:</strong> {enrolled_display}</li>
                                            <li><strong>Rating:</strong> {rating_display}</li>
                                        </ul>
                                    </div>
                                </div>
                                <div class="view-course-btn">
                                    <a href="{course_url}" target="_blank" {'style="pointer-events: none; opacity: 0.6;"' if course_url == '#' else ''}>
                                        {'Course Link Unavailable' if course_url == '#' else 'Go to Course'}
                                    </a>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.markdown(f"""
                <div class="warning-message">
                    <strong>⚠️ No Courses Found</strong><br>
                    Could not find course recommendations for the required skills for the <strong>{label}</strong> role.
                    This might be due to:
                    <ul>
                        <li>Limited course data available</li>
                        <li>Very specific skill requirements</li>
                        <li>Technical issues with the recommendation system</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    except Exception as e:
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ Error Processing Recommendations</strong><br>
            An error occurred while processing your course recommendations: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        
        # Add debug info in development
        if st.checkbox("Show debug information"):
            st.exception(e)

if __name__ == "__main__":
    main()