"""
Multilingual RAG Planner Agent - Main Application
A Streamlit-based application for goal planning with multilingual support.
"""

import streamlit as st
from dotenv import load_dotenv
import os
from auth.auth_manager import AuthManager
from components.dashboard import Dashboard
from components.goal_planner import GoalPlanner
from components.task_manager import TaskManager
from utils.logger import setup_logger
from localization.translator import Translator

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger("main_app")

# Page configuration
st.set_page_config(
    page_title="Multilingual RAG Planner",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MainApp:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.translator = Translator()
        
    def run(self):
        """Main application runner"""
        # Initialize session state
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
        if "language" not in st.session_state:
            st.session_state.language = "en"
            
        # Language selector in sidebar
        self.render_language_selector()
        
        # Authentication check
        if not st.session_state.authenticated:
            self.render_auth_page()
        else:
            self.render_main_app()
    
    def render_language_selector(self):
        """Render language selector in sidebar"""
        with st.sidebar:
            st.title("🌐 Language")
            languages = {
                "en": "English",
                "es": "Español",
                "fr": "Français", 
                "de": "Deutsch",
                "it": "Italiano",
                "pt": "Português",
                "zh": "中文",
                "ja": "日本語",
                "ko": "한국어",
                "hi": "हिंदी",
                "ar": "العربية"
            }
            
            selected_lang = st.selectbox(
                "Select Language",
                options=list(languages.keys()),
                format_func=lambda x: languages[x],
                index=0 if st.session_state.language not in languages else list(languages.keys()).index(st.session_state.language)
            )
            
            if selected_lang != st.session_state.language:
                st.session_state.language = selected_lang
                st.rerun()
    
    def render_auth_page(self):
        """Render authentication page"""
        st.title("🎯 Multilingual RAG Planner")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Login to Your Account")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if self.auth_manager.login(email, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        with tab2:
            with st.form("signup_form"):
                st.subheader("Create New Account")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                full_name = st.text_input("Full Name")
                submit = st.form_submit_button("Sign Up")
                
                if submit:
                    if password != confirm_password:
                        st.error("Passwords don't match")
                    elif self.auth_manager.signup(email, password, full_name):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Failed to create account")
    
    def render_main_app(self):
        """Render main application interface"""
        # Header
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.title("🎯 Your Goal Planner")
        with col3:
            if st.button("Logout"):
                self.auth_manager.logout()
                st.rerun()
        
        # Sidebar navigation
        with st.sidebar:
            st.title("📋 Navigation")
            page = st.radio(
                "Go to:",
                ["Dashboard", "Goal Planner", "Task Manager", "Settings"]
            )
        
        # Main content based on selected page
        if page == "Dashboard":
            dashboard = Dashboard()
            dashboard.render()
        elif page == "Goal Planner":
            goal_planner = GoalPlanner()
            goal_planner.render()
        elif page == "Task Manager":
            task_manager = TaskManager()
            task_manager.render()
        elif page == "Settings":
            self.render_settings()
    
    def render_settings(self):
        """Render settings page"""
        st.header("⚙️ Settings")
        
        with st.expander("Profile Settings"):
            st.text_input("Full Name", value="")
            st.text_input("Email", disabled=True)
        
        with st.expander("Preferences"):
            st.slider("Daily Tasks Limit", 1, 20, 10)
            st.slider("Planning Horizon (days)", 7, 90, 30)
            st.multiselect("Notification Types", ["Email", "In-app", "SMS"])

if __name__ == "__main__":
    app = MainApp()
    app.run()