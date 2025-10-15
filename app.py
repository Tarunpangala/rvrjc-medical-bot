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

# Enhanced Custom CSS
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
        animation: fadeIn 1s ease-in;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Analysis Box */
    .analysis-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin-top: 1.5rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        animation: slideIn 0.5s ease-out;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        animation: fadeInUp 0.3s ease-out;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        margin-left: 3rem;
        border-left: 4px solid #2196F3;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
        margin-right: 3rem;
        border-left: 4px solid #667eea;
    }
    
    /* Info Cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-top: 3px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 25px rgba(0,0,0,0.15);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
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
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Image Container */
    .image-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
def save_user_data(user_id, name, age, gender, report_type, analysis, timestamp):
    """Save user data to JSON file"""
    data_file = 'user_medical_data.json'
    
    # Load existing data
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = []
    else:
        all_data = []
    
    # Create new entry
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
    
    # Save to file
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
st.markdown('<h1 class="main-header">Medical Assistant Bot</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">✨ Your Personal AI Health Companion | Powered by Google Gemini 2.0 Flash ✨</p>', unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings & Profile")
    
    # Language Selection
    selected_language = st.selectbox(
        "🌐 Select Language",
        options=list(LANGUAGES.keys()),
        index=0,
        help="Choose your preferred language for responses"
    )
    
    st.markdown("---")
    
    # User Information Section
    st.markdown("### 👤 Your Information")
    user_name = st.text_input("📝 Full Name", placeholder="Enter your name", help="Your name will be saved with your reports")
    
    col1, col2 = st.columns(2)
    with col1:
        user_age = st.number_input("🎂 Age", min_value=1, max_value=120, value=25)
    with col2:
        user_gender = st.selectbox("⚧ Gender", ["Male", "Female", "Other"])
    
    st.markdown("---")
    
    # Features Section
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
    
    # Disclaimer
    st.markdown("""
    <div style='background-color: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 4px solid #ffc107;'>
        ⚠️ <strong>Important Disclaimer</strong><br>
        <small>This AI assistant provides information only. Always consult healthcare professionals for medical advice.</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stats
    if os.path.exists('user_medical_data.json'):
        with open('user_medical_data.json', 'r') as f:
            try:
                data = json.load(f)
                st.markdown(f"""
                <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;'>
                    <h3 style='margin: 0;'>{len(data)}</h3>
                    <small>Total Analyses Saved</small>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass

# Main content tabs
tab1, tab2, tab3 = st.tabs(["💬 Medical Queries", "📄 Report Analysis", "🔍 Skin Disease Detection"])

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
        <div class="info-card" style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);">
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
    
    if summarize_btn and query:
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
                
                # Save user data for medical query
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

# Tab 2: Medical Report Analysis with Chat
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
            
            # Store the uploaded image in session state
            st.session_state.uploaded_report_image = Image.open(uploaded_file)
    
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
                        - Identify what type of medical report this is (Lab test, X-ray, CT scan, MRI, Prescription, etc.)
                        - Date of report (if visible)
                        - Issuing hospital/lab (if visible)
                        
                        ## 🔍 Detailed Findings
                        Extract and list ALL visible information:
                        - Test names with their values
                        - Normal reference ranges
                        - Units of measurement
                        - Any flags (High/Low/Critical)
                        
                        ## 📊 Parameter Analysis
                        For each test result, provide:
                        - What the test measures
                        - Normal range explanation
                        - Current value interpretation (Normal/Abnormal)
                        - Clinical significance
                        
                        ## 💡 Medical Interpretation
                        - What do these results indicate overall?
                        - Patterns or correlations between parameters
                        - Possible health implications
                        - Body systems affected
                        
                        ## ⚠️ Areas of Concern
                        - Any abnormal values requiring attention
                        - Severity of abnormalities (Mild/Moderate/Severe)
                        - Potential health risks
                        
                        ## 🏥 Recommendations
                        - Follow-up tests needed
                        - Lifestyle modifications
                        - Dietary suggestions
                        - When to consult doctor
                        
                        ## ⚡ Summary
                        Brief overall summary with key takeaways
                        
                        IMPORTANT: Be thorough and extract ALL visible information. Explain medical terms in simple language.
                        
                        Provide the complete analysis in {selected_language} language."""
                        
                        response = model.generate_content([prompt, st.session_state.uploaded_report_image])
                        
                        st.session_state.report_analysis = response.text
                        
                        # Save user data
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
        else:
            st.markdown("""
            <div class="info-card" style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); margin-top: 2rem;">
                <h4>📝 Instructions</h4>
                <ol style='margin: 0.5rem 0; padding-left: 1.5rem;'>
                    <li>Upload your medical report image</li>
                    <li>Click 'Analyze Report Now'</li>
                    <li>Review the detailed analysis</li>
                    <li>Ask follow-up questions in chat</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    # Display analysis
    if st.session_state.report_analysis:
        st.markdown("---")
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("### 📊 Detailed Analysis Report:")
        st.markdown(st.session_state.report_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.warning("⚠️ **Medical Disclaimer**: This AI analysis is for informational purposes only. Please consult your healthcare provider for medical advice.")
    
    # Chat section for medical report
    if st.session_state.uploaded_report_image and st.session_state.report_analysis:
        st.markdown("---")
        st.markdown("## 💬 Chat About Your Report")
        st.markdown("""
        <div class="info-card" style="background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);">
            <p style='margin: 0;'>💡 <strong>Ask questions like:</strong> "What does my cholesterol level mean?" or "Should I be worried about any values?"</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display chat history
        if st.session_state.report_chat_history:
            st.markdown("<br>", unsafe_allow_html=True)
            display_chat_history(st.session_state.report_chat_history)
        
        # Chat input
        st.markdown("<br>", unsafe_allow_html=True)
        chat_col1, chat_col2 = st.columns([5, 1])
        with chat_col1:
            report_question = st.text_input(
                "Type your question here:",
                key="report_chat_input",
                placeholder="e.g., What does my cholesterol level mean?",
                label_visibility="collapsed"
            )
        with chat_col2:
            send_btn = st.button("📤 Send", key="report_send", use_container_width=True)
        
        if send_btn and report_question:
            # Add user message to history
            st.session_state.report_chat_history.append({
                'role': 'user',
                'content': report_question
            })
            
            with st.spinner("💭 Thinking..."):
                try:
                    chat_prompt = f"""You are a medical assistant helping explain a medical report. 
                    Previous analysis: {st.session_state.report_analysis}
                    
                    User question: {report_question}
                    
                    Provide a clear, detailed answer in {selected_language} language. 
                    Reference specific values from the report when relevant.
                    Be helpful and educational, but always remind users to consult healthcare professionals."""
                    
                    chat_response = model.generate_content([chat_prompt, st.session_state.uploaded_report_image])
                    
                    # Add assistant message to history
                    st.session_state.report_chat_history.append({
                        'role': 'assistant',
                        'content': chat_response.text
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.report_chat_history:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Clear Chat History", key="clear_report_chat", use_container_width=True):
                    st.session_state.report_chat_history = []
                    st.rerun()

# Tab 3: Skin Disease Detection with Chat
with tab3:
    st.markdown("## 🔍 Skin Condition Analyzer")
    
    st.markdown("""
    <div class="info-card">
        <h4>🔬 AI-Powered Skin Analysis</h4>
        <p>Upload images of skin conditions for detailed AI analysis. Get insights on possible conditions and care recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📸 Upload Image")
        st.info("💡 **Photography Tips**: Use good lighting, focus clearly on the affected area, and take photos from multiple angles if possible")
        
        skin_image = st.file_uploader(
            "Choose a skin condition image",
            type=['png', 'jpg', 'jpeg'],
            key="skin_upload",
            help="Upload a clear photo of the skin condition"
        )
        
        if skin_image:
            image = Image.open(skin_image)
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(image, caption="🔍 Skin Condition Image", use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Store the uploaded image in session state
            st.session_state.uploaded_skin_image = Image.open(skin_image)
    
    with col2:
        if skin_image:
            st.markdown("### 🔬 Analysis")
            
            if not user_name:
                st.warning("⚠️ Please enter your name in the sidebar to save your analysis.")
            
            detect_btn = st.button("🔬 Analyze Skin Condition", key="detect", use_container_width=True)
            
            if detect_btn:
                with st.spinner("🔬 Analyzing skin condition... Please wait..."):
                    try:
                        prompt = f"""You are an expert dermatology assistant. Carefully analyze this skin condition image 
                        and provide a comprehensive, detailed assessment in {selected_language} language.
                        
                        Provide your analysis in the following structured format:
                        
                        ## 👁️ Visual Characteristics
                        - Color (redness, darkening, discoloration)
                        - Texture (smooth, rough, scaly, bumpy)
                        - Pattern (circular, linear, clustered, widespread)
                        - Size and shape
                        - Location on body (if identifiable)
                        - Any lesions, bumps, blisters, or rashes
                        
                        ## 🔍 Possible Conditions (Differential Diagnosis)
                        List 3-5 possible conditions with detailed explanations:
                        1. Most likely condition - explain why
                        2. Second possibility - reasoning
                        3. Other potential conditions
                        
                        ## 📊 Severity Assessment
                        - Mild / Moderate / Severe (with justification)
                        - Progression indicators
                        - Complications to watch for
                        
                        ## 💊 General Care Recommendations
                        - Immediate care steps
                        - Things to avoid
                        - Over-the-counter options
                        - Home remedies
                        
                        ## 🚨 When to Seek Immediate Medical Attention
                        - Red flags requiring urgent care
                        - Signs of infection
                        - Severe symptoms
                        
                        ## 🏥 Medical Consultation Recommendations
                        - Why professional diagnosis is essential
                        - What type of specialist to see
                        - What tests might be needed
                        
                        CRITICAL: Always emphasize this is NOT a definitive diagnosis.
                        
                        Provide the complete analysis in {selected_language} language."""
                        
                        response = model.generate_content([prompt, st.session_state.uploaded_skin_image])
                        
                        st.session_state.skin_analysis = response.text
                        
                        # Save user data
                        if user_name:
                            save_user_data(
                                user_id=st.session_state.user_id,
                                name=user_name,
                                age=user_age,
                                gender=user_gender,
                                report_type="Skin Condition",
                                analysis=response.text,
                                timestamp=datetime.now().isoformat()
                            )
                        
                        st.success("✅ Analysis Complete!")
                        if user_name:
                            st.info("💾 Skin analysis saved successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing skin condition: {str(e)}")
        else:
            st.markdown("""
            <div class="info-card" style="background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%); margin-top: 2rem;">
                <h4>📝 Instructions</h4>
                <ol style='margin: 0.5rem 0; padding-left: 1.5rem;'>
                    <li>Upload a clear photo of the skin condition</li>
                    <li>Click 'Analyze Skin Condition'</li>
                    <li>Review the detailed assessment</li>
                    <li>Ask questions about the analysis</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    # Display analysis
    if st.session_state.skin_analysis:
        st.markdown("---")
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("### 🔬 Detailed Dermatological Assessment:")
        st.markdown(st.session_state.skin_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.error("🚨 **CRITICAL REMINDER**: This AI analysis is NOT a medical diagnosis. Please consult a qualified dermatologist for proper diagnosis and treatment.")
    
    # Chat section for skin condition
    if st.session_state.uploaded_skin_image and st.session_state.skin_analysis:
        st.markdown("---")
        st.markdown("## 💬 Chat About Your Skin Condition")
        st.markdown("""
        <div class="info-card" style="background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);">
            <p style='margin: 0;'>💡 <strong>Ask questions like:</strong> "How long will this take to heal?" or "What products should I avoid?"</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display chat history
        if st.session_state.skin_chat_history:
            st.markdown("<br>", unsafe_allow_html=True)
            display_chat_history(st.session_state.skin_chat_history)
        
        # Chat input
        st.markdown("<br>", unsafe_allow_html=True)
        chat_col1, chat_col2 = st.columns([5, 1])
        with chat_col1:
            skin_question = st.text_input(
                "Type your question here:",
                key="skin_chat_input",
                placeholder="e.g., How long will this take to heal?",
                label_visibility="collapsed"
            )
        with chat_col2:
            send_btn2 = st.button("📤 Send", key="skin_send", use_container_width=True)
        
        if send_btn2 and skin_question:
            # Add user message to history
            st.session_state.skin_chat_history.append({
                'role': 'user',
                'content': skin_question
            })
            
            with st.spinner("💭 Thinking..."):
                try:
                    chat_prompt = f"""You are a dermatology assistant helping explain a skin condition analysis. 
                    Previous analysis: {st.session_state.skin_analysis}
                    
                    User question: {skin_question}
                    
                    Provide a clear, detailed answer in {selected_language} language. 
                    Reference specific observations from the analysis when relevant.
                    Be helpful and educational, but always remind users to consult a dermatologist."""
                    
                    chat_response = model.generate_content([chat_prompt, st.session_state.uploaded_skin_image])
                    
                    # Add assistant message to history
                    st.session_state.skin_chat_history.append({
                        'role': 'assistant',
                        'content': chat_response.text
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.skin_chat_history:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Clear Chat History", key="clear_skin_chat", use_container_width=True):
                    st.session_state.skin_chat_history = []
                    st.rerun()

# Enhanced Footer
st.markdown("---")
st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-top: 2rem;'>
        <div style='text-align: center; color: white;'>
            <h2 style='margin: 0; font-size: 1.8rem;'>🏥 Medical Assistant Bot</h2>
            <p style='font-size: 1.1rem; margin: 0.5rem 0;'>Powered by Google Gemini 2.0 Flash</p>
            <p style='font-size: 0.95rem; margin: 1rem 0;'>
                🌐 Supports 10 Languages: English • Hindi • Telugu • Tamil • Bengali • Marathi • Gujarati • Kannada • Malayalam • Punjabi
            </p>
            <div style='background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
                <p style='font-size: 0.9rem; margin: 0; font-weight: bold;'>⚠️ Medical Disclaimer</p>
                <p style='font-size: 0.85rem; margin: 0.5rem 0;'>
                    This tool is for informational and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.
                    Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
                </p>
            </div>
            <p style='font-size: 0.85rem; margin: 0.5rem 0;'>💾 All data is stored securely in <code>user_medical_data.json</code></p>
            <p style='font-size: 0.8rem; margin: 1rem 0; opacity: 0.9;'>
                Made with ❤️ for better healthcare accessibility
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)