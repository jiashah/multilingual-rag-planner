"""
Authentication Manager using Supabase Auth
Handles user login, signup, and session management
"""

import streamlit as st
from database.supabase_client import supabase_client
from utils.logger import setup_logger
from typing import Optional, Dict, Any

logger = setup_logger("auth_manager")

class AuthManager:
    def __init__(self):
        self.client = supabase_client.client
    
    def login(self, email: str, password: str) -> bool:
        """
        Authenticate user with email and password
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Store user session in Streamlit session state
                st.session_state.authenticated = True
                st.session_state.user_id = response.user.id
                st.session_state.user_email = response.user.email
                st.session_state.access_token = response.session.access_token
                
                logger.info(f"User {email} logged in successfully")
                return True
            
        except Exception as e:
            logger.error(f"Login failed for {email}: {e}")
            return False
        
        return False
    
    def signup(self, email: str, password: str, full_name: str) -> bool:
        """
        Register a new user
        
        Args:
            email (str): User email
            password (str): User password
            full_name (str): User full name
            
        Returns:
            bool: True if signup successful, False otherwise
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name
                    }
                }
            })
            
            if response.user:
                logger.info(f"User {email} registered successfully")
                return True
                
        except Exception as e:
            logger.error(f"Signup failed for {email}: {e}")
            return False
        
        return False
    
    def logout(self) -> bool:
        """
        Log out the current user
        
        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            self.client.auth.sign_out()
            
            # Clear Streamlit session state
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.session_state.access_token = None
            
            logger.info("User logged out successfully")
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user information
        
        Returns:
            Dict containing user information or None if not authenticated
        """
        try:
            user = self.client.auth.get_user()
            if user and user.user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "created_at": user.user.created_at,
                    "user_metadata": user.user.user_metadata
                }
        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
        
        return None
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return st.session_state.get("authenticated", False)
    
    def reset_password(self, email: str) -> bool:
        """
        Send password reset email
        
        Args:
            email (str): User email
            
        Returns:
            bool: True if reset email sent successfully, False otherwise
        """
        try:
            self.client.auth.reset_password_email(email)
            logger.info(f"Password reset email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Password reset failed for {email}: {e}")
            return False
    
    def update_password(self, new_password: str) -> bool:
        """
        Update user password (requires authenticated session)
        
        Args:
            new_password (str): New password
            
        Returns:
            bool: True if password updated successfully, False otherwise
        """
        try:
            if not self.is_authenticated():
                return False
            
            self.client.auth.update_user({"password": new_password})
            logger.info("Password updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Password update failed: {e}")
            return False
    
    def update_profile(self, **kwargs) -> bool:
        """
        Update user profile information
        
        Args:
            **kwargs: Profile fields to update
            
        Returns:
            bool: True if profile updated successfully, False otherwise
        """
        try:
            if not self.is_authenticated():
                return False
            
            # Update auth user metadata
            if any(key in kwargs for key in ["full_name", "avatar_url"]):
                auth_data = {k: v for k, v in kwargs.items() if k in ["full_name", "avatar_url"]}
                self.client.auth.update_user({"data": auth_data})
            
            # Update user profile table
            user_id = st.session_state.user_id
            profile_data = {k: v for k, v in kwargs.items() 
                          if k in ["full_name", "preferred_language", "timezone", 
                                 "daily_task_limit", "planning_horizon_days"]}
            
            if profile_data:
                self.client.table("user_profiles").update(profile_data).eq("id", user_id).execute()
            
            logger.info("Profile updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            return False
    
    def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get user profile information from database
        
        Returns:
            Dict containing user profile or None if not found
        """
        try:
            if not self.is_authenticated():
                return None
            
            user_id = st.session_state.user_id
            response = self.client.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if response.data:
                return response.data[0]
                
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
        
        return None
    
    def check_session_validity(self) -> bool:
        """
        Check if current session is still valid
        
        Returns:
            bool: True if session is valid, False otherwise
        """
        try:
            user = self.client.auth.get_user()
            return bool(user and user.user)
        except:
            return False