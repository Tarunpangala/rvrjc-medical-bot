import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Supported Indian languages
LANGUAGES = {
    'English': 'en',
    'Hindi': 'hi',
    'Telugu': 'te',
    'Tamil': 'ta',
    'Bengali': 'bn',
    'Marathi': 'mr',
    'Gujarati': 'gu',
    'Kannada': 'kn',
    'Malayalam': 'ml',
    'Punjabi': 'pa'
}

# Initialize session state
if 'report_chat_history' not in st.session_state:
    st.session_state.report_chat_history = []
if 'skin_chat_history' not in st.session_state:
    st.session_state.skin_chat_history = []
if 'report_analysis' not in st.session_state:
    st.session_state.report_analysis = None
if 'skin_analysis' not in st.session_state:
    st.session_state.skin_analysis = None
if 'uploaded_report_image' not in st.session_state:
    st.session_state.uploaded_report_image = None
if 'uploaded_skin_image' not in st.session_state:
    st.session_state.uploaded_skin_image = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Page configuration
st.set_page_config(
    page_title="Medical Assistant Bot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme-Adaptive CSS with Complete Fixes
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Header - Gradient works in both themes */
    .main-header {
        font-size: clamp(1.8rem, 5vw, 3rem);
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
        animation: fadeIn 1s ease-in;
    }
    
    .sub-header {
        text-align: center;
        opacity: 0.8;
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        margin-bottom: 2rem;
    }
    
    /* Button Styling - Works perfectly in both themes */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 0.75rem 1.5rem;
        font-size: clamp(0.95rem, 2.5vw, 1.1rem);
        font-weight: 600;
        border: none !important;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Analysis Box - Theme adaptive */
    .analysis-box {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: clamp(1rem, 3vw, 2rem);
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin-top: 1.5rem;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.1);
        animation: slideIn 0.5s ease-out;
    }
    
    /* Chat Messages - Fully theme adaptive */
    .chat-message {
        padding: clamp(0.8rem, 2.5vw, 1.2rem);
        border-radius: 15px;
        margin-bottom: 1rem;
        animation: fadeInUp 0.3s ease-out;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.1);
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 100%;
    }
    
    .user-message {
        background: rgba(33, 150, 243, 0.1);
        border: 1px solid rgba(33, 150, 243, 0.25);
        margin-left: clamp(0.5rem, 5vw, 3rem);
        border-left: 4px solid #2196F3;
    }
    
    .assistant-message {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.25);
        margin-right: clamp(0.5rem, 5vw, 3rem);
        border-left: 4px solid #667eea;
    }
    
    /* Info Cards - Enhanced for both themes */
    .info-card {
        background: rgba(102, 126, 234, 0.06);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: clamp(1rem, 2.5vw, 1.5rem);
        border-radius: 12px;
        box-shadow: 0 3px 15px rgba(102, 126, 234, 0.08);
        margin-bottom: 1rem;
        border-top: 3px solid #667eea;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 25px rgba(102, 126, 234, 0.15);
    }
    
    .info-card h4 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .info-card p, .info-card ul {
        margin: 0.5rem 0;
        opacity: 0.9;
    }
    
    .info-card ul {
        padding-left: 1.2rem;
    }
    
    .info-card ul li {
        margin: 0.3rem 0;
    }
    
    /* Feature Cards */
    .feature-card {
        background: rgba(102, 126, 234, 0.06);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.05);
        transition: transform 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateX(5px);
    }
    
    .feature-card strong {
        display: block;
        margin-bottom: 0.25rem;
    }
    
    .feature-card small {
        opacity: 0.8;
    }
    
    /* Tab Styling - Improved for mobile */
    .stTabs [data-baseweb="tab-list"] {
        gap: clamp(4px, 2vw, 8px);
        background-color: rgba(102, 126, 234, 0.08);
        padding: 10px;
        border-radius: 10px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: clamp(8px, 2vw, 12px) clamp(12px, 3vw, 24px);
        font-weight: 600;
        font-size: clamp(0.85rem, 2.5vw, 1.05rem);
        white-space: nowrap;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.15);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Image Container */
    .image-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        margin: 1rem 0;
        border: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .image-container img {
        width: 100%;
        height: auto;
        display: block;
    }
    
    /* Sidebar Enhancements */
    [data-testid="stSidebar"] {
        background: rgba(102, 126, 234, 0.03);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        padding: 0.5rem 0;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1rem;
        background: rgba(102, 126, 234, 0.03);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(102, 126, 234, 0.5);
        background: rgba(102, 126, 234, 0.06);
    }
    
    /* Success/Warning/Error/Info Messages */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Mobile Optimizations */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 0.5rem 0;
        }
        
        .sub-header {
            font-size: 0.9rem;
            padding: 0 1rem;
        }
        
        .chat-message {
            margin-left: 0.5rem !important;
            margin-right: 0.5rem !important;
            font-size: 0.9rem;
        }
        
        .user-message {
            margin-left: 0.5rem;
        }
        
        .assistant-message {
            margin-right: 0.5rem;
        }
        
        .stButton > button {
            font-size: 1rem;
            padding: 0.6rem 1rem;
        }
        
        .analysis-box {
            padding: 1rem;
            font-size: 0.9rem;
        }
        
        .info-card {
            padding: 1rem;
        }
        
        .feature-card {
            padding: 0.8rem;
            font-size: 0.9rem;
        }
        
        /* Better spacing on mobile */
        .stTabs [data-baseweb="tab-list"] {
            padding: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            font-size: 0.9rem;
        }
        
        /* Reduce column gaps on mobile */
        [data-testid="column"] {
            padding: 0.5rem !important;
        }
    }
    
    /* Extra small devices */
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }
        
        .sub-header {
            font-size: 0.8rem;
        }
        
        .info-card h4 {
            font-size: 1rem;
        }
        
        .chat-message {
            padding: 0.6rem;
            font-size: 0.85rem;
        }
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideIn {
        from { 
            opacity: 0;
            transform: translateX(-20px);
        }
        to { 
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeInUp {
        from { 
            opacity: 0;
            transform: translateY(10px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(102, 126, 234, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }
    
    /* Loading Spinner Color */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Reduce animation on mobile for better performance */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
def save_user_data(user_id, name, age, gender, report_type, analysis, timestamp):
    """Save user data to JSON file"""
    data_file = 'user_medical_data.json'
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = []
    else:
        all_data = []
    
    user_entry = {
        'user_id': user_id,
        'name': name,
        'age': age,
        'gender': gender,
        'report_type': report_type,
        'analysis': analysis,
        'timestamp': timestamp
    }
    
    all_data.append(user_entry)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

def display_chat_history(chat_history):
    """Display chat messages"""
    for message in chat_history:
        if message['role'] == 'user':
            st.markdown(f'<div class="chat-message user-message">👤 <strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message">🤖 <strong>AI Assistant:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏥 Medical Assistant Bot</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">✨ Your Personal AI Health Companion | Powered by Google Gemini 2.0 Flash ✨</p>', unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings & Profile")
    
    selected_language = st.selectbox(
        "🌐 Select Language",
        options=list(LANGUAGES.keys()),
        index=0,
        help="Choose your preferred language for responses"
    )
    
    st.markdown("---")
    
    st.markdown("### 👤 Your Information")
    user_name = st.text_input("📝 Full Name", placeholder="Enter your name", help="Your name will be saved with your reports")
    
    col1, col2 = st.columns(2)
    with col1:
        user_age = st.number_input("🎂 Age", min_value=1, max_value=120, value=25)
    with col2:
        user_gender = st.selectbox("⚧ Gender", ["Male", "Female", "Other"])
    
    st.markdown("---")
    
    st.markdown("### 🎯 Features")
    st.markdown("""
    <div class="feature-card">
        💬 <strong>Medical Queries</strong><br>
        <small>Get instant medical information</small>
    </div>
    <div class="feature-card">
        📄 <strong>Report Analysis</strong><br>
        <small>Upload & analyze lab reports</small>
    </div>
    <div class="feature-card">
        🔍 <strong>Skin Detection</strong><br>
        <small>AI-powered skin condition analysis</small>
    </div>
    <div class="feature-card">
        🌐 <strong>10 Languages</strong><br>
        <small>Multilingual support</small>
    </div>
    <div class="feature-card">
        💾 <strong>Data Storage</strong><br>
        <small>Secure local storage</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.warning("⚠️ **Disclaimer:** This AI provides information only. Always consult healthcare professionals for medical advice.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if os.path.exists('user_medical_data.json'):
        with open('user_medical_data.json', 'r') as f:
            try:
                data = json.load(f)
                st.info(f"📊 **Total Analyses Saved:** {len(data)}")
            except:
                pass

# Main content tabs
tab1, tab2, tab3 = st.tabs(["💬 Medical Queries", "📄 Report Analysis", "🔍 Skin Detection"])

# Tab 1: Medical Query Summarization
with tab1:
    st.markdown("## 💬 Medical Query Assistant")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>🎯 How It Works</h4>
            <p>Ask any medical question and receive comprehensive, easy-to-understand answers in your preferred language.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>✅ What You'll Get</h4>
            <ul style='margin: 0; padding-left: 1.2rem;'>
                <li>Clear explanations</li>
                <li>Key information</li>
                <li>Medical recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    query = st.text_area(
        "🔍 Enter Your Medical Question:",
        placeholder="Example: What are the symptoms of diabetes? / मधुमेह के लक्षण क्या हैं?",
        height=150,
        help="Type your medical question in any language"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        summarize_btn = st.button("🔍 Get Answer", key="summarize", use_container_width=True)
    
    if summarize_btn:
        if query:
            if not user_name:
                st.warning("⚠️ Please enter your name in the sidebar to save your query.")
            
            with st.spinner("🤔 Analyzing your query... Please wait..."):
                try:
                    prompt = f"""You are an expert medical assistant. Analyze and summarize the following medical query 
                    and provide a comprehensive, accurate, and easy-to-understand response in {selected_language} language.
                    
                    Structure your response as follows:
                    1. **Understanding the Query**: Brief clarification of what's being asked
                    2. **Key Information**: Main facts and important points (3-5 bullet points)
                    3. **Detailed Explanation**: Comprehensive explanation in simple terms
                    4. **Important Considerations**: Things to keep in mind
                    5. **When to Seek Medical Help**: Red flags or situations requiring immediate attention
                    6. **Recommendation**: Always advise consulting healthcare professionals
                    
                    Query: {query}
                    
                    Provide the complete response in {selected_language} language with clear formatting."""
                    
                    response = model.generate_content(prompt)
                    
                    if user_name:
                        save_user_data(
                            user_id=st.session_state.user_id,
                            name=user_name,
                            age=user_age,
                            gender=user_gender,
                            report_type="Medical Query",
                            analysis=f"Query: {query}\n\nResponse: {response.text}",
                            timestamp=datetime.now().isoformat()
                        )
                    
                    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                    st.success("✅ Analysis Complete!")
                    st.markdown("### 📋 Medical Information:")
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if user_name:
                        st.info("💾 Your query has been saved successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Please check your GEMINI_API_KEY in the .env file")
        else:
            st.warning("⚠️ Please enter a medical question first!")

# Tab 2: Medical Report Analysis
with tab2:
    st.markdown("## 📄 Medical Report Analyzer")
    
    st.markdown("""
    <div class="info-card">
        <h4>📊 Comprehensive Report Analysis</h4>
        <p>Upload your medical reports (lab tests, X-rays, CT scans, MRI) and get detailed insights with interactive chat support.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📸 Upload Report")
        st.info("💡 **Best Results**: Upload clear, high-resolution images with good lighting")
        
        uploaded_file = st.file_uploader(
            "Choose a medical report image",
            type=['png', 'jpg', 'jpeg'],
            help="Supported formats: PNG, JPG, JPEG",
            key="report_uploader"
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(image, caption="📄 Your Medical Report", use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.session_state.uploaded_report_image = image
    
    with col2:
        if uploaded_file:
            st.markdown("### 🔬 Analysis")
            
            if not user_name:
                st.warning("⚠️ Please enter your name in the sidebar to save your analysis.")
            
            analyze_btn = st.button("📊 Analyze Report Now", key="analyze_report", use_container_width=True)
            
            if analyze_btn:
                with st.spinner("🔬 Analyzing your medical report... This may take a moment..."):
                    try:
                        prompt = f"""You are an expert medical report analyzer. Carefully examine this medical report image 
                        and provide a comprehensive, detailed analysis in {selected_language} language.
                        
                        Provide your analysis in the following structured format:
                        
                        ## 📋 Report Type Identification
                        - Identify what type of medical report this is
                        - Date of report (if visible)
                        - Issuing hospital/lab (if visible)
                        
                        ## 🔍 Detailed Findings
                        Extract and list ALL visible information:
                        - Test names with their values
                        - Normal reference ranges
                        - Units of measurement
                        - Any flags (High/Low/Critical)
                        
                        ## 📊 Parameter Analysis
                        For each test result:
                        - What the test measures
                        - Normal range explanation
                        - Current value interpretation
                        - Clinical significance
                        
                        ## 💡 Medical Interpretation
                        - Overall indication of results
                        - Patterns or correlations
                        - Possible health implications
                        - Body systems affected
                        
                        ## ⚠️ Areas of Concern
                        - Any abnormal values
                        - Severity assessment
                        - Potential health risks
                        
                        ## 🏥 Recommendations
                        - Follow-up tests needed
                        - Lifestyle modifications
                        - Dietary suggestions
                        - When to consult doctor
                        
                        ## ⚡ Summary
                        Brief overall summary with key takeaways
                        
                        Provide the complete analysis in {selected_language} language."""
                        
                        response = model.generate_content([prompt, st.session_state.uploaded_report_image])
                        st.session_state.report_analysis = response.text
                        
                        if user_name:
                            save_user_data(
                                user_id=st.session_state.user_id,
                                name=user_name,
                                age=user_age,
                                gender=user_gender,
                                report_type="Medical Report",
                                analysis=response.text,
                                timestamp=datetime.now().isoformat()
                            )
                        
                        st.success("✅ Analysis Complete!")
                        if user_name:
                            st.info("💾 Report analysis saved successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing report: {str(e)}")
                        st.info("💡 Please check your API key and try again")
        else:
            st.markdown("""
            <div class="info-card">
                <h4>📝 Instructions</h4>
                <ol style='margin: 0.5rem 0; padding-left: 1.5rem;'>
                    <li>Upload your medical report image</li>
                    <li>Click 'Analyze Report Now'</li>
                    <li>Review the detailed analysis</li>
                    <li>Ask follow-up questions in chat</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    if st.session_state.report_analysis:
        st.markdown("---")
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("### 📊 Analysis Results:")
        st.markdown(st.session_state.report_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💬 Ask Follow-up Questions")
        
        display_chat_history(st.session_state.report_chat_history)
        
        chat_input = st.text_input(
            "Ask a question about your report:",
            placeholder="e.g., What does high cholesterol mean?",
            key="report_chat_input"
        )
        
        if st.button("Send Question", key="send_report_question"):
            if chat_input:
                st.session_state.report_chat_history.append({
                    'role': 'user',
                    'content': chat_input
                })
                
                with st.spinner("🤔 Thinking..."):
                    try:
                        chat_prompt = f"""Based on this medical report analysis:
                        
                        {st.session_state.report_analysis}
                        
                        User question: {chat_input}
                        
                        Provide a helpful, detailed answer in {selected_language} language."""
                        
                        chat_response = model.generate_content(chat_prompt)
                        
                        st.session_state.report_chat_history.append({
                            'role': 'assistant',
                            'content': chat_response.text
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Tab 3: Skin Disease Detection
with tab3:
    st.markdown("## 🔍 Skin Disease Detection")
    
    st.markdown("""
    <div class="info-card">
        <h4>🏥 AI-Powered Skin Analysis</h4>
        <p>Upload an image of your skin concern and get instant AI-powered analysis with potential conditions and recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📸 Upload Skin Image")
        st.info("💡 **Tips**: Use clear, well-lit photos. Capture the affected area clearly.")
        
        uploaded_skin_file = st.file_uploader(
            "Choose a skin image",
            type=['png', 'jpg', 'jpeg'],
            help="Supported formats: PNG, JPG, JPEG",
            key="skin_uploader"
        )
        
        if uploaded_skin_file:
            skin_image = Image.open(uploaded_skin_file)
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(skin_image, caption="🔍 Skin Image for Analysis", use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.session_state.uploaded_skin_image = skin_image
    
    with col2:
        if uploaded_skin_file:
            st.markdown("### 🔬 Skin Analysis")
            
            if not user_name:
                st.warning("⚠️ Please enter your name in the sidebar to save your analysis.")
            
            analyze_skin_btn = st.button("🔍 Analyze Skin Condition", key="analyze_skin", use_container_width=True)
            
            if analyze_skin_btn:
                with st.spinner("🔬 Analyzing skin condition... Please wait..."):
                    try:
                        prompt = f"""You are an expert dermatology AI assistant. Analyze this skin image carefully 
                        and provide a comprehensive analysis in {selected_language} language.
                        
                        Provide your analysis in the following format:
                        
                        ## 👁️ Visual Observations
                        - Describe what you observe in the image
                        - Color, texture, pattern, size
                        - Location on body (if identifiable)
                        
                        ## 🔍 Possible Conditions
                        List 3-5 possible skin conditions with:
                        - Condition name
                        - Likelihood (High/Medium/Low)
                        - Brief description
                        - Common causes
                        
                        ## 📊 Detailed Analysis
                        For the most likely condition:
                        - Detailed explanation
                        - Typical symptoms
                        - Common triggers
                        - Natural progression
                        
                        ## ⚠️ Warning Signs
                        - When to seek immediate medical attention
                        - Red flags to watch for
                        - Complications to be aware of
                        
                        ## 🏥 Recommendations
                        - When to see a dermatologist
                        - General care tips
                        - Things to avoid
                        - Home care suggestions
                        
                        ## 💊 Possible Treatments
                        - Over-the-counter options
                        - Prescription treatments (mention doctor consultation needed)
                        - Lifestyle modifications
                        
                        ## ⚡ Important Disclaimer
                        Emphasize that this is AI analysis and professional dermatologist consultation is essential for accurate diagnosis.
                        
                        Provide the complete analysis in {selected_language} language."""
                        
                        response = model.generate_content([prompt, st.session_state.uploaded_skin_image])
                        st.session_state.skin_analysis = response.text
                        
                        if user_name:
                            save_user_data(
                                user_id=st.session_state.user_id,
                                name=user_name,
                                age=user_age,
                                gender=user_gender,
                                report_type="Skin Disease Detection",
                                analysis=response.text,
                                timestamp=datetime.now().isoformat()
                            )
                        
                        st.success("✅ Skin Analysis Complete!")
                        if user_name:
                            st.info("💾 Analysis saved successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing skin image: {str(e)}")
                        st.info("💡 Please check your API key and try again")
        else:
            st.markdown("""
            <div class="info-card">
                <h4>📝 How to Use</h4>
                <ol style='margin: 0.5rem 0; padding-left: 1.5rem;'>
                    <li>Take a clear photo of the skin area</li>
                    <li>Upload the image</li>
                    <li>Click 'Analyze Skin Condition'</li>
                    <li>Review AI analysis</li>
                    <li>Consult a dermatologist for confirmation</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    if st.session_state.skin_analysis:
        st.markdown("---")
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("### 🔍 Skin Analysis Results:")
        st.markdown(st.session_state.skin_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💬 Ask Questions About Your Skin Condition")
        
        display_chat_history(st.session_state.skin_chat_history)
        
        skin_chat_input = st.text_input(
            "Ask a question about the analysis:",
            placeholder="e.g., Is this condition contagious?",
            key="skin_chat_input"
        )
        
        if st.button("Send Question", key="send_skin_question"):
            if skin_chat_input:
                st.session_state.skin_chat_history.append({
                    'role': 'user',
                    'content': skin_chat_input
                })
                
                with st.spinner("🤔 Thinking..."):
                    try:
                        chat_prompt = f"""Based on this skin condition analysis:
                        
                        {st.session_state.skin_analysis}
                        
                        User question: {skin_chat_input}
                        
                        Provide a helpful, detailed answer in {selected_language} language. 
                        Always remind them to consult a dermatologist for professional advice."""
                        
                        chat_response = model.generate_content(chat_prompt)
                        
                        st.session_state.skin_chat_history.append({
                            'role': 'assistant',
                            'content': chat_response.text
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem 0; opacity: 0.7;'>
    <p><strong>🏥 Medical Assistant Bot</strong></p>
    <p>Powered by Google Gemini 2.0 Flash | Made with ❤️ for Healthcare</p>
    <p><small>⚠️ This tool provides information only. Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.</small></p>
</div>
""", unsafe_allow_html=True)
