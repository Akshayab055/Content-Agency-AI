"""
Main application entry point for Content Agency AI.
A professional content management system for social media agencies.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict

# Import modules
from config import APP_NAME, APP_VERSION
from models.database import init_database
from models.client_model import ClientModel
from models.content_model import ContentModel
from ui.auth_ui import AuthUI
from ui.client_ui import ClientUI
from ui.calendar_ui import CalendarUI
from ui.content_ui import ContentUI
from ui.dashboard_ui import DashboardUI


def initialize_session_state():
    """Initialize all session state variables."""
    defaults = {
        'user_id': None,
        'username': None,
        'clients': {},
        'current_client_id': None,
        'content_history': {},
        'calendar_posts': {},
        'calendar_days': {},
        'selected_calendar_post': None,
        'active_tab': "dashboard",
        'current_draft': "",
        'editable_text': "",
        'generated_image': None,
        'current_explanation': None,
        'current_context': None,
        'formality_level': 0.7,
        'humor_level': 0.3,
        'selected_topic': "",
        'selected_platform': "LinkedIn",
        'manual_topic': "",
        'last_generated_day': None,
        'show_success_popup': False,
        'success_message': "",
        'show_delete_confirmation': False,
        'client_to_delete': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def load_clients():
    """Load clients from database into session state."""
    if st.session_state.user_id and not st.session_state.clients:
        db_clients = ClientModel.get_clients(st.session_state.user_id)
        for client in db_clients:
            st.session_state.clients[client['basic_info']['company_name']] = client


def handle_client_selection():
    """Handle client selection from sidebar."""
    st.sidebar.title("Client Management")
    
    client_names = ["+ Add New Client"] + list(st.session_state.clients.keys())
    selected_client = st.sidebar.selectbox(
        "Select Client",
        client_names,
        key="client_selector"
    )
    
    if selected_client == "+ Add New Client":
        st.session_state.current_client_id = None
        st.session_state.active_tab = "onboarding"
    elif selected_client in st.session_state.clients:
        st.session_state.current_client_id = st.session_state.clients[selected_client]["client_id"]
    
    return selected_client


def render_delete_confirmation():
    """Render delete confirmation dialog."""
    if st.session_state.get('show_delete_confirmation', False):
        with st.sidebar:
            st.warning(f"Delete '{st.session_state.client_to_delete}'?")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✓ Confirm", key="confirm_delete", use_container_width=True):
                    client_to_delete = st.session_state.client_to_delete
                    if client_to_delete in st.session_state.clients:
                        client_id = st.session_state.clients[client_to_delete]["client_id"]
                        
                        # Delete from database
                        if ClientModel.delete_client(client_id):
                            del st.session_state.clients[client_to_delete]
                            
                            if st.session_state.current_client_id == client_id:
                                st.session_state.current_client_id = None
                                st.session_state.active_tab = "onboarding"
                            
                            st.session_state.success_message = f"Client '{client_to_delete}' deleted successfully!"
                            st.session_state.show_success_popup = True
                    
                    st.session_state.show_delete_confirmation = False
                    st.session_state.client_to_delete = None
                    st.rerun()
            
            with col2:
                if st.button("✗ Cancel", key="cancel_delete", use_container_width=True):
                    st.session_state.show_delete_confirmation = False
                    st.session_state.client_to_delete = None
                    st.rerun()


def render_navigation():
    """Render navigation sidebar."""
    nav_options = ["Dashboard", "Calendar", "Content Generator", "History", "Assets", "Edit Profile"]
    
    tab_index_map = {
        "dashboard": 0,
        "calendar": 1,
        "generator": 2,
        "history": 3,
        "assets": 4,
        "edit": 5
    }
    
    default_index = tab_index_map.get(st.session_state.active_tab, 0)
    selected_nav = st.sidebar.radio("Navigation", nav_options, index=default_index)
    
    # Map navigation to tabs
    nav_to_tab = {
        "Dashboard": "dashboard",
        "Calendar": "calendar",
        "Content Generator": "generator",
        "History": "history",
        "Assets": "assets",
        "Edit Profile": "edit"
    }
    
    st.session_state.active_tab = nav_to_tab.get(selected_nav, "dashboard")
    return st.session_state.active_tab


def render_success_popup():
    """Render success popup message."""
    if st.session_state.show_success_popup:
        st.success(st.session_state.success_message)
        st.session_state.show_success_popup = False


def render_active_client_info(selected_client: str):
    """Render active client info in sidebar."""
    if st.session_state.current_client_id and selected_client in st.session_state.clients:
        st.sidebar.success(f"Active Client: {selected_client}")
        
        # Delete button
        st.sidebar.markdown("---")
        if st.sidebar.button("Delete Client", key="delete_client_btn", use_container_width=True):
            st.session_state.show_delete_confirmation = True
            st.session_state.client_to_delete = selected_client
            st.rerun()


def render_content_history(client: Dict):
    """Render content history view."""
    st.header(f"Content History for {client['basic_info']['company_name']}")
    
    history = ContentModel.get_content_history(client['client_id'])
    
    if history:
        st.metric("Total Content Pieces", len(history))
        
        # Filter by type
        media_filter = st.multiselect(
            "Filter by type",
            ["text", "image"],
            default=["text", "image"]
        )
        
        for idx, item in enumerate(history[:20]):
            media_type = item.get('type', 'text')
            
            if media_type in media_filter:
                created_at = item.get('created_at', 'Unknown')
                platform = item.get('platform', 'Unknown')
                topic = item.get('topic', 'Unknown')
                
                with st.expander(f"{created_at} - {media_type.upper()} - {platform}"):
                    # Display image if available
                    if media_type == "image" and item.get('data', {}).get('media_data'):
                        import base64
                        from io import BytesIO
                        from PIL import Image
                        
                        img_data = base64.b64decode(item['data']['media_data'])
                        st.image(Image.open(BytesIO(img_data)), width=300)
                    
                    # Display text content
                    content_text = item.get('data', {}).get('content', '')
                    if content_text:
                        st.text_area("Content", content_text, height=150, disabled=True, key=f"history_{idx}")
                    
                    st.caption(f"Topic: {topic}")
    else:
        st.info("No content history yet. Generate and save content to see it here.")


def render_uploaded_assets(client: Dict):
    """Render uploaded assets view."""
    st.header(f"Uploaded Assets for {client['basic_info']['company_name']}")
    
    assets = client.get("assets", {})
    
    if not any([assets.get("logo"), assets.get("sample_posts"), assets.get("brand_guidelines")]):
        st.info("No assets uploaded yet.")
        return
    
    # Brand Guidelines
    if assets.get("brand_guidelines"):
        st.subheader("Brand Guidelines")
        guidelines = assets["brand_guidelines"]
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"**File:** {guidelines.get('name', 'Unknown')}")
        with col2:
            st.markdown(f"**Type:** {guidelines.get('type', 'Unknown')}")
        with col3:
            if guidelines.get('pdf_base64'):
                import base64
                pdf_bytes = base64.b64decode(guidelines['pdf_base64'])
                st.download_button("Download", pdf_bytes, file_name=guidelines['name'])
        
        st.markdown("---")
    
    # Logo
    if assets.get("logo"):
        st.subheader("Company Logo")
        logo = assets["logo"]
        
        if logo.get('image_base64'):
            import base64
            from io import BytesIO
            from PIL import Image
            
            img_data = base64.b64decode(logo['image_base64'])
            st.image(Image.open(BytesIO(img_data)), width=200)
            
            st.download_button(
                "Download Logo",
                img_data,
                file_name=logo.get('name', 'logo.png')
            )
        
        st.markdown("---")
    
    # Sample Posts
    if assets.get("sample_posts"):
        st.subheader(f"Sample Posts ({len(assets['sample_posts'])} files)")
        
        for idx, post in enumerate(assets["sample_posts"], 1):
            with st.expander(f"Sample {idx}: {post.get('name', 'Unknown')}"):
                if post.get('image_base64'):
                    import base64
                    from io import BytesIO
                    from PIL import Image
                    
                    img_data = base64.b64decode(post['image_base64'])
                    st.image(Image.open(BytesIO(img_data)), width=300)
                
                if post.get('content_preview'):
                    st.text_area("Preview", post['content_preview'], height=100, disabled=True)

def main():
    """Main application entry point."""
    # Page config
    st.set_page_config(
        page_title=APP_NAME,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize
    init_database()
    initialize_session_state()
    
    # Title
    st.title(APP_NAME)
    
    # Show success popup FIRST (before any other content)
    render_success_popup()
    
    # Authentication
    auth_ui = AuthUI()
    if not auth_ui.render():
        st.info("Please login or sign up to continue")
        return
    
    # Load clients
    load_clients()
    
    # Sidebar navigation
    render_delete_confirmation()
    selected_client = handle_client_selection()
    active_tab = render_navigation()
    render_active_client_info(selected_client)
    
    # Render main content
    if st.session_state.current_client_id is None:
        client_ui = ClientUI()
        client_ui.render_onboarding_form()
    else:
        client = st.session_state.clients[selected_client]
        
        if active_tab == "dashboard":
            DashboardUI.render(client)
        
        elif active_tab == "calendar":
            calendar_ui = CalendarUI()
            calendar_ui.render(client)
        
        elif active_tab == "generator":
            content_ui = ContentUI()
            content_ui.render(client)
        
        elif active_tab == "history":
            render_content_history(client)
        
        elif active_tab == "assets":
            render_uploaded_assets(client)
        
        elif active_tab == "edit":
            client_ui = ClientUI()
            client_ui.render_edit_form(client)
    
    # Sidebar footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"""
        **{APP_NAME}**  
        Version {APP_VERSION}
        
        **Active Clients:** {len(st.session_state.clients)}  
        **AI Model:** Groq
        **Image Model:** Cloudflare Stable Diffusion
        """
    )
    
if __name__ == "__main__":
    main()