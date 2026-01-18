"""
DenisOS - Your Personal Digital Codex
An interactive notebook for life, work, and wisdom.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from utils.config import load_config, get_config_value, set_config_value, save_config
from utils.data_manager import load_data, save_data, get_stats, get_data_path
from modules import finance, carpentry, philosophy, codex_advisor


st.set_page_config(
    page_title="DenisOS",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished dark theme
CUSTOM_CSS = """
<style>
    /* Main theme colors */
    :root {
        --accent: #6366f1;
        --accent-light: #818cf8;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --text-muted: #9ca3af;
    }

    /* Header styling */
    .main-title {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    /* Quote box */
    .codex-quote {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366f1;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        color: #d1d5db;
    }

    /* Card styling */
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.2s ease;
    }

    .stat-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
    }

    /* Section headers */
    .section-header {
        color: #f3f4f6;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3);
    }

    /* Button overrides */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }

    /* Input styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: 8px !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.95) 0%, rgba(31, 41, 55, 0.95) 100%);
    }

    [data-testid="stSidebar"] .stRadio > label {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(99, 102, 241, 0.1);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Activity item */
    .activity-item {
        padding: 0.75rem;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.02);
        margin-bottom: 0.5rem;
        border-left: 3px solid transparent;
    }

    .activity-item:hover {
        background: rgba(255, 255, 255, 0.05);
        border-left-color: #6366f1;
    }

    /* Settings section */
    .settings-section {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar():
    """Render the navigation sidebar."""
    with st.sidebar:
        st.markdown("## 📓 DenisOS")
        st.caption(f"v{get_config_value('app.version', '1.2.0')}")

        st.markdown("---")

        # Navigation with icons
        pages = {
            "Home": "🏠",
            "Codex": "🤖",
            "Finance": "💰",
            "Carpentry": "🪵",
            "Philosophy": "📖",
            "Settings": "⚙️"
        }

        page = st.radio(
            "Navigate",
            options=list(pages.keys()),
            format_func=lambda x: f"{pages[x]} {x}",
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Stats
        stats = get_stats()
        st.markdown("**Your Codex**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Journal", stats['journal_entries'], label_visibility="visible")
            st.metric("Calcs", stats['lumber_calcs'], label_visibility="visible")
        with col2:
            st.metric("Transactions", stats['transactions'], label_visibility="visible")
            st.metric("Reflections", stats['reflections'], label_visibility="visible")

        st.markdown("---")

        # Last updated
        if stats['last_modified'] != 'Never':
            st.caption(f"📅 {stats['last_modified'][:10]}")

        return page


def render_home():
    """Render the home dashboard."""
    config = load_config()
    user_name = config.get("user", {}).get("name", "Denis")

    # Time-based greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
        icon = "🌅"
    elif hour < 17:
        greeting = "Good afternoon"
        icon = "☀️"
    else:
        greeting = "Good evening"
        icon = "🌙"

    st.markdown(f'<h1 class="main-title">{icon} {greeting}, {user_name}</h1>', unsafe_allow_html=True)
    st.markdown(f"*{datetime.now().strftime('%A, %B %d, %Y')}*")

    # Codex quote
    st.markdown("""
    <div class="codex-quote">
    "Hello, Denis. I am your Codex - a repository of your thoughts, calculations,
    and wisdom. Unlike Tom Riddle's diary, I'm here to help you grow, not to steal your soul."
    </div>
    """, unsafe_allow_html=True)

    # Quick stats cards
    st.markdown('<p class="section-header">Quick Overview</p>', unsafe_allow_html=True)

    data = load_data()
    col1, col2, col3 = st.columns(3)

    with col1:
        transactions = data.get("finance", {}).get("transactions", [])
        today = datetime.now()
        this_month = [t for t in transactions
                      if t.get('date', '').startswith(today.strftime('%Y-%m'))]
        expenses = abs(sum(t['amount'] for t in this_month if t.get('amount', 0) < 0))
        income = sum(t['amount'] for t in this_month if t.get('amount', 0) > 0)

        st.markdown("**💰 Finance**")
        st.metric("This Month", f"${expenses:.2f}", delta=f"+${income:.2f}" if income > 0 else None)

    with col2:
        calcs = len(data.get("lumber_calculations", []))
        projects = len(data.get("projects", []))

        st.markdown("**🪵 Carpentry**")
        st.metric("Calculations", calcs)
        st.metric("Projects", projects)

    with col3:
        entries = len(data.get("journal", []))
        reflections = len(data.get("reflections", []))

        st.markdown("**📖 Journal**")
        st.metric("Entries", entries)
        st.metric("Reflections", reflections)

    # Recent Activity
    st.markdown('<p class="section-header">Recent Activity</p>', unsafe_allow_html=True)

    all_entries = []

    for entry in data.get("journal", [])[-5:]:
        content = entry.get("content", "")
        all_entries.append({
            "type": "📝",
            "label": "Journal",
            "content": content[:80] + "..." if len(content) > 80 else content,
            "date": entry.get("created_at", "")
        })

    for txn in data.get("finance", {}).get("transactions", [])[-5:]:
        all_entries.append({
            "type": "💰",
            "label": "Finance",
            "content": f"{txn.get('description', 'Transaction')}: ${abs(txn.get('amount', 0)):.2f}",
            "date": txn.get("created_at", txn.get("date", ""))
        })

    for calc in data.get("lumber_calculations", [])[-3:]:
        all_entries.append({
            "type": "🪵",
            "label": "Carpentry",
            "content": calc.get("name", "Calculation"),
            "date": calc.get("created_at", "")
        })

    all_entries = sorted(all_entries, key=lambda x: x.get('date', ''), reverse=True)[:6]

    if all_entries:
        for entry in all_entries:
            date_str = entry['date'][:10] if entry['date'] else ""
            st.markdown(f"""
            <div class="activity-item">
                <strong>{entry['type']} {entry['label']}</strong><br/>
                <span style="color: #9ca3af;">{entry['content']}</span>
                <span style="color: #6b7280; font-size: 0.8rem; float: right;">{date_str}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity. Start by adding a journal entry or tracking an expense!")


def render_settings():
    """Render settings page."""
    st.markdown('<h1 class="main-title">⚙️ Settings</h1>', unsafe_allow_html=True)

    config = load_config()

    # User Preferences
    st.markdown('<p class="section-header">User Preferences</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        new_name = st.text_input("Your Name", value=config.get("user", {}).get("name", "Denis"))
        new_currency = st.selectbox(
            "Currency",
            options=["CAD", "USD", "EUR", "GBP"],
            index=["CAD", "USD", "EUR", "GBP"].index(config.get("user", {}).get("currency", "CAD"))
        )

    with col2:
        new_units = st.selectbox(
            "Measurement Units",
            options=["imperial", "metric"],
            index=0 if config.get("user", {}).get("units", "imperial") == "imperial" else 1
        )
        new_timezone = st.text_input(
            "Timezone",
            value=config.get("user", {}).get("timezone", "America/Toronto")
        )

    if st.button("💾 Save Preferences", type="primary"):
        config["user"]["name"] = new_name
        config["user"]["currency"] = new_currency
        config["user"]["units"] = new_units
        config["user"]["timezone"] = new_timezone
        save_config(config)
        st.success("Preferences saved!")
        st.rerun()

    st.markdown("---")

    # API Configuration
    st.markdown('<p class="section-header">🤖 Codex AI (Claude)</p>', unsafe_allow_html=True)

    current_key = config.get("api", {}).get("anthropic_key", "")
    has_key = bool(current_key)

    if has_key:
        st.success("✓ API key configured")
        masked_key = current_key[:10] + "..." + current_key[-4:] if len(current_key) > 14 else "****"
        st.code(masked_key)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Change API Key"):
                st.session_state.show_api_input = True
        with col2:
            if st.button("🗑️ Remove API Key", type="secondary"):
                set_config_value("api.anthropic_key", "")
                if "anthropic_api_key" in st.session_state:
                    del st.session_state["anthropic_api_key"]
                st.success("API key removed!")
                st.rerun()

    if not has_key or st.session_state.get("show_api_input"):
        new_api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Get your key at console.anthropic.com"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save API Key", type="primary"):
                if new_api_key:
                    set_config_value("api.anthropic_key", new_api_key)
                    st.session_state.anthropic_api_key = new_api_key
                    st.session_state.show_api_input = False
                    st.success("API key saved!")
                    st.rerun()
                else:
                    st.error("Please enter an API key")
        with col2:
            if has_key and st.button("Cancel"):
                st.session_state.show_api_input = False
                st.rerun()

        st.info("🔗 Get an API key at [console.anthropic.com](https://console.anthropic.com)")

    st.markdown("---")

    # Data Management
    st.markdown('<p class="section-header">📦 Data Management</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        data = load_data()
        import json
        st.download_button(
            "📥 Export All Data",
            data=json.dumps(data, indent=2),
            file_name=f"denis_os_backup_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

    with col2:
        config_export = load_config()
        config_export["api"]["anthropic_key"] = "REDACTED"  # Don't export API key
        st.download_button(
            "📥 Export Config",
            data=json.dumps(config_export, indent=2),
            file_name="denis_os_config.json",
            mime="application/json"
        )

    with col3:
        st.markdown("")  # Spacer

    st.markdown("---")

    # Danger Zone
    st.markdown('<p class="section-header" style="color: #ef4444;">⚠️ Danger Zone</p>', unsafe_allow_html=True)

    with st.expander("Reset Options", expanded=False):
        st.warning("These actions cannot be undone!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Clear All Conversations"):
                data = load_data()
                data["codex_conversations"] = []
                save_data(data)
                if "messages" in st.session_state:
                    st.session_state.messages = []
                st.success("Conversations cleared!")
                st.rerun()

        with col2:
            if st.button("💣 Reset ALL Data", type="secondary"):
                st.session_state.confirm_full_reset = True

        if st.session_state.get("confirm_full_reset"):
            st.error("⚠️ This will delete ALL your data permanently!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete Everything", type="primary"):
                    data_path = get_data_path()
                    if data_path.exists():
                        data_path.unlink()
                    st.session_state.confirm_full_reset = False
                    st.success("All data reset!")
                    st.rerun()
            with col2:
                if st.button("Cancel"):
                    st.session_state.confirm_full_reset = False
                    st.rerun()

    st.markdown("---")

    # About
    st.markdown('<p class="section-header">About DenisOS</p>', unsafe_allow_html=True)
    st.markdown("""
    **DenisOS** is your personal digital codex - a private space for tracking finances,
    calculating lumber needs, journaling, and collecting wisdom.

    Built with Python, Streamlit, and Claude AI.

    *"The unexamined life is not worth living." - Socrates*
    """)


def main():
    """Main application entry point."""
    page = render_sidebar()

    if page == "Home":
        render_home()
    elif page == "Codex":
        codex_advisor.render()
    elif page == "Finance":
        finance.render()
    elif page == "Carpentry":
        carpentry.render()
    elif page == "Philosophy":
        philosophy.render()
    elif page == "Settings":
        render_settings()


if __name__ == "__main__":
    main()
