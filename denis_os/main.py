"""
DenisOS - Your Personal Digital Codex
An interactive notebook for life, work, and wisdom.
"Hello, Denis. My name is also Denis." - Your Codex
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from utils.config import load_config, get_config_value
from utils.data_manager import load_data, get_stats
from modules import finance, carpentry, philosophy


st.set_page_config(
    page_title="DenisOS",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    .codex-quote {
        font-style: italic;
        color: #555;
        border-left: 3px solid #667eea;
        padding-left: 1rem;
        margin: 1rem 0;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar():
    """Render the navigation sidebar."""
    with st.sidebar:
        st.markdown("# 📓 DenisOS")
        st.caption(f"v{get_config_value('app.version', '1.0.0')}")

        st.markdown("---")

        page = st.radio(
            "Navigate",
            options=["Home", "Finance", "Carpentry", "Philosophy", "Settings"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        stats = get_stats()
        st.markdown("**Codex Stats**")
        st.caption(f"📝 {stats['journal_entries']} journal entries")
        st.caption(f"💰 {stats['transactions']} transactions")
        st.caption(f"🪵 {stats['lumber_calcs']} lumber calcs")
        st.caption(f"💭 {stats['reflections']} reflections")

        st.markdown("---")
        st.caption(f"Last updated: {stats['last_modified'][:10] if stats['last_modified'] != 'Never' else 'Never'}")

        return page


def render_home():
    """Render the home dashboard."""
    user_name = get_config_value('user.name', 'Denis')

    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    st.markdown(f"# {greeting}, {user_name}")
    st.markdown(f"*{datetime.now().strftime('%A, %B %d, %Y')}*")

    st.markdown("---")

    st.markdown("""
    <div class="codex-quote">
    "Hello, Denis. I am your Codex - a repository of your thoughts, calculations,
    and wisdom. Unlike Tom Riddle's diary, I'm here to help you grow, not to steal your soul."
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 💰 Finance")
        data = load_data()
        transactions = data.get("finance", {}).get("transactions", [])
        today = datetime.now()
        this_month = [t for t in transactions
                      if t.get('date', '').startswith(today.strftime('%Y-%m'))]
        expenses = abs(sum(t['amount'] for t in this_month if t.get('amount', 0) < 0))
        st.metric("This Month's Expenses", f"${expenses:.2f}")

    with col2:
        st.markdown("#### 🪵 Carpentry")
        calcs = len(data.get("lumber_calculations", []))
        projects = len(data.get("projects", []))
        st.metric("Saved Calculations", calcs)
        st.metric("Projects", projects)

    with col3:
        st.markdown("#### 📖 Journal")
        entries = len(data.get("journal", []))
        reflections = len(data.get("reflections", []))
        st.metric("Journal Entries", entries)
        st.metric("Reflections", reflections)

    st.markdown("---")
    st.markdown("### Recent Activity")

    all_entries = []

    for entry in data.get("journal", [])[-5:]:
        all_entries.append({
            "type": "📝 Journal",
            "content": entry.get("content", "")[:100] + "...",
            "date": entry.get("created_at", "")
        })

    for txn in data.get("finance", {}).get("transactions", [])[-5:]:
        all_entries.append({
            "type": "💰 Finance",
            "content": f"{txn.get('description', 'Transaction')}: ${abs(txn.get('amount', 0)):.2f}",
            "date": txn.get("created_at", txn.get("date", ""))
        })

    all_entries = sorted(all_entries, key=lambda x: x.get('date', ''), reverse=True)[:5]

    if all_entries:
        for entry in all_entries:
            st.markdown(f"**{entry['type']}** - {entry['content']}")
            st.caption(entry['date'][:10] if entry['date'] else "")
    else:
        st.info("No recent activity. Start by adding a journal entry or tracking an expense!")


def render_settings():
    """Render settings page."""
    st.header("⚙️ Settings")

    config = load_config()

    st.subheader("User Preferences")

    col1, col2 = st.columns(2)

    with col1:
        new_name = st.text_input("Your Name", value=config.get("user", {}).get("name", "Denis"))
        new_currency = st.selectbox(
            "Currency",
            options=["CAD", "USD", "EUR", "GBP"],
            index=["CAD", "USD", "EUR", "GBP"].index(
                config.get("user", {}).get("currency", "CAD")
            )
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

    if st.button("Save Settings", type="primary"):
        from utils.config import save_config
        config["user"]["name"] = new_name
        config["user"]["currency"] = new_currency
        config["user"]["units"] = new_units
        config["user"]["timezone"] = new_timezone
        save_config(config)
        st.success("Settings saved!")
        st.rerun()

    st.markdown("---")

    st.subheader("About DenisOS")
    st.markdown("""
    **DenisOS** is your personal digital codex - a private space for tracking finances,
    calculating lumber needs, journaling, and collecting wisdom.

    Built with Python & Streamlit, Docker for deployment, and local JSON storage.

    *"The unexamined life is not worth living." - Socrates*
    """)

    st.markdown("---")

    st.subheader("Data Management")

    col1, col2 = st.columns(2)

    with col1:
        data = load_data()
        st.download_button(
            "📥 Export Data (JSON)",
            data=str(data),
            file_name=f"denis_os_backup_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

    with col2:
        st.warning("⚠️ Data reset is permanent")
        if st.button("Reset All Data", type="secondary"):
            st.session_state.confirm_reset = True

        if st.session_state.get("confirm_reset"):
            st.error("Are you sure? This cannot be undone!")
            if st.button("Yes, Reset Everything"):
                from utils.data_manager import get_data_path
                data_path = get_data_path()
                if data_path.exists():
                    data_path.unlink()
                st.session_state.confirm_reset = False
                st.success("Data reset complete")
                st.rerun()


def main():
    """Main application entry point."""
    page = render_sidebar()

    if page == "Home":
        render_home()
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
