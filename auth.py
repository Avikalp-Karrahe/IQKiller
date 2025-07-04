import os
import hashlib
import time
from typing import Optional, Dict, Any
from functools import wraps
import gradio as gr
from datetime import datetime, timedelta
import requests

# Configuration
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# Simple session storage (in production, use Redis or database)
active_sessions = {}

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Google OAuth token and get user info
    
    Args:
        token: Google OAuth token
    
    Returns:
        User info dict or None if invalid
    """
    try:
        response = requests.get(
            f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def create_login_interface():
    """Create the login interface with Google OAuth and development mode"""
    
    def handle_auth_choice(auth_method: str):
        """Handle authentication method selection"""
        if auth_method == "development":
            return (
                "✅ Development mode enabled - no authentication required",
                "dev_session",
                True,
                gr.update(visible=False),  # Hide Google auth
                gr.update(visible=False)   # Hide token input
            )
        elif auth_method == "google":
            google_auth_url = "https://accounts.google.com/oauth/authorize"
            client_id = GOOGLE_CLIENT_ID or "your-google-client-id"
            redirect_uri = "http://localhost:7862/auth/callback"
            scope = "openid email profile"
            
            auth_url = f"{google_auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code"
            
            return (
                f"🔗 Click here to sign in with Google: [Open Google Auth]({auth_url})",
                "",
                False,
                gr.update(visible=True),   # Show Google auth
                gr.update(visible=True)    # Show token input
            )
    
    def verify_google_auth(token: str):
        """Verify Google authentication token"""
        if not token:
            return "❌ Please enter your Google auth token", "", False
        
        user_info = verify_google_token(token)
        if user_info:
            session_id = f"google_{user_info.get('id', 'unknown')}_{int(time.time())}"
            active_sessions[session_id] = {
                "user_info": user_info,
                "auth_time": time.time(),
                "auth_method": "google"
            }
            return (
                f"✅ Welcome, {user_info.get('name', 'Google User')}!",
                session_id,
                True
            )
        else:
            return "❌ Invalid Google token", "", False

    with gr.Blocks(title="IQKiller - Login") as login_interface:
        gr.Markdown("""
        # 🚀 IQKiller AI Job Analysis Platform
        
        Choose your authentication method:
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                pass  # Spacing
            with gr.Column(scale=2):
                auth_method = gr.Radio(
                    choices=[
                        ("🛠️ Development Mode (No Auth)", "development"),
                        ("🔐 Google OAuth", "google")
                    ],
                    label="Authentication Method",
                    value="development" if DEVELOPMENT_MODE else "google"
                )
                
                auth_button = gr.Button("Select Authentication", variant="primary")
                
                # Google OAuth section (initially hidden)
                with gr.Group(visible=False) as google_auth_section:
                    gr.Markdown("""
                    ### Google OAuth Instructions:
                    1. Click the Google Auth link above
                    2. Sign in with your Google account  
                    3. Copy the authorization code from the redirect URL
                    4. Paste it below and click "Verify"
                    """)
                    
                    google_token_input = gr.Textbox(
                        label="Google Auth Code",
                        placeholder="Paste your Google authorization code here",
                        lines=2
                    )
                    google_verify_button = gr.Button("Verify Google Auth", variant="secondary")
                
                # Status and hidden outputs
                login_status = gr.Textbox(label="Status", interactive=False)
                session_id = gr.Textbox(label="Session ID", visible=False)
                is_authenticated = gr.Checkbox(label="Authenticated", visible=False)
                
            with gr.Column(scale=1):
                pass  # Spacing
        
        # Event handlers
        auth_button.click(
            fn=handle_auth_choice,
            inputs=[auth_method],
            outputs=[login_status, session_id, is_authenticated, google_auth_section, google_token_input]
        )
        
        google_verify_button.click(
            fn=verify_google_auth,
            inputs=[google_token_input],
            outputs=[login_status, session_id, is_authenticated]
        )
    
    return login_interface

def create_authenticated_wrapper(app_function):
    """
    Create an authentication wrapper for the main application
    
    Args:
        app_function: Function that returns the main Gradio app
    
    Returns:
        Wrapped application with authentication
    """
    
    # If in development mode, just return the app directly without any auth
    if DEVELOPMENT_MODE:
        return app_function
    
    def verify_session(session_id: str):
        """Verify session and return user info"""
        if DEVELOPMENT_MODE and session_id == "dev_session":
            return True, "Development mode - no authentication required"
        
        if session_id in active_sessions:
            session = active_sessions[session_id]
            # Check if session is still valid (24 hours)
            if time.time() - session["auth_time"] < 86400:  # 24 hours
                user_info = session.get("user_info", {})
                username = user_info.get("name", "User")
                return True, f"Authenticated as {username}"
            else:
                # Session expired
                del active_sessions[session_id]
                return False, "Session expired"
        
        return False, "Invalid session"
    
    def create_main_app_with_auth():
        """Create the main application with authentication check"""
        
        with gr.Blocks(title="IQKiller - Job Analysis Platform") as main_app:
            # Authentication state
            session_id = gr.State("")
            auth_status = gr.State(False)
            
            with gr.Row():
                with gr.Column(scale=4):
                    gr.Markdown("# 🚀 IQKiller - AI Job Analysis Platform")
                with gr.Column(scale=1):
                    auth_display = gr.Textbox(
                        label="Auth Status",
                        value="Google OAuth Required",
                        interactive=False
                    )
            
            # Authentication section
            with gr.Row():
                session_input = gr.Textbox(
                    label="Google Session ID",
                    placeholder="Enter your session ID from Google login",
                    lines=1
                )
                verify_button = gr.Button("Verify Session", variant="secondary")
            
            # Login redirect
            gr.Markdown("""
            ### 🔐 Authentication Required
            
            Please visit the [Login Page](/) to authenticate with Google OAuth before accessing the main application.
            """)
            
            def handle_session_verification(session_id_input):
                """Handle session verification"""
                is_valid, message = verify_session(session_id_input)
                if is_valid:
                    # Create the main app
                    main_app_interface = app_function()
                    return (
                        gr.update(value=message, label="✅ Authentication Status"),
                        True,
                        session_id_input,
                        gr.update(visible=False),  # Hide auth section
                        gr.update(visible=True)    # Show main app
                    )
                else:
                    return (
                        gr.update(value=f"❌ {message}", label="❌ Authentication Status"),
                        False,
                        "",
                        gr.update(visible=True),   # Show auth section
                        gr.update(visible=False)   # Hide main app
                    )
            
            # Main application (initially hidden)
            with gr.Column(visible=False) as main_app_section:
                app_function()
            
            # Verification event
            verify_button.click(
                fn=handle_session_verification,
                inputs=[session_input],
                outputs=[auth_display, auth_status, session_id, session_input, main_app_section]
            )
            
        return main_app
    
    return create_main_app_with_auth

def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "authentication": "google_oauth" if not DEVELOPMENT_MODE else "development_mode"
    } 