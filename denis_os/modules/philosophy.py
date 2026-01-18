"""
Philosophy & Reflection Module for DenisOS
Your digital journal and thinking companion
"""

import streamlit as st
from datetime import datetime
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_manager import (
    load_data, save_data, add_journal_entry,
    add_reflection, get_entries
)


REFLECTION_PROMPTS = {
    "stoic": [
        "What is within your control today, and what isn't?",
        "How would your ideal self handle today's challenges?",
        "What would you tell a friend facing your current situation?",
        "What obstacle can you view as an opportunity?",
        "What are you grateful for that you usually take for granted?",
    ],
    "practical": [
        "What's the ONE thing that would make today a success?",
        "What task have you been avoiding, and why?",
        "What did you learn from your last mistake?",
        "What skill do you want to improve this week?",
    ],
    "craft": [
        "What does mastery look like in your current project?",
        "What technique could you practice to improve?",
        "Who do you admire in your craft, and why?",
        "What would you build if resources weren't a constraint?",
    ],
    "growth": [
        "What belief have you changed your mind about recently?",
        "How are you different from a year ago?",
        "What would your future self thank you for doing today?",
        "Where are you playing it too safe?",
    ]
}

MOODS = ["Great", "Good", "Okay", "Low", "Frustrated", "Thoughtful", "Motivated", "Anxious", "Grateful"]
MOOD_ICONS = {
    "Great": "😊", "Good": "🙂", "Okay": "😐", "Low": "😔",
    "Frustrated": "😤", "Thoughtful": "🤔", "Motivated": "💪",
    "Anxious": "😰", "Grateful": "🙏"
}


def render():
    """Render the philosophy module UI."""
    st.markdown("## 📖 Journal & Reflections")

    # Quick action buttons at top
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 New Entry", type="primary", use_container_width=True):
            st.session_state.journal_mode = "write"
    with col2:
        if st.button("💭 Prompt", use_container_width=True):
            st.session_state.journal_mode = "prompt"
    with col3:
        if st.button("📚 History", use_container_width=True):
            st.session_state.journal_mode = "history"

    st.markdown("---")

    if "journal_mode" not in st.session_state:
        st.session_state.journal_mode = "write"

    mode = st.session_state.journal_mode

    if mode == "write":
        _render_journal()
    elif mode == "prompt":
        _render_daily_prompt()
    elif mode == "history":
        _render_past_entries()


def _render_journal():
    """Free-form journal entry."""
    st.markdown("### What's on your mind?")

    title = st.text_input(
        "Title (optional)",
        placeholder="Give this entry a name...",
        key="journal_title"
    )

    entry_text = st.text_area(
        "Write freely...",
        height=250,
        placeholder="This is your space. Write whatever comes to mind.\n\nTip: Use #tags inline (e.g., #work #idea)",
        key="journal_entry"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        mood = st.selectbox(
            "Mood",
            options=MOODS,
            format_func=lambda x: f"{MOOD_ICONS.get(x, '📝')} {x}"
        )

    with col2:
        tags_input = st.text_input(
            "Tags",
            placeholder="work, project, idea"
        )

    with col3:
        link_to_codex = st.checkbox(
            "🤖 Link to Codex",
            help="Let the AI reference this entry"
        )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Save", type="primary", disabled=not entry_text.strip()):
            inline_tags = re.findall(r'#(\w+)', entry_text)
            manual_tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            all_tags = list(set(inline_tags + manual_tags))
            if link_to_codex:
                all_tags.append("codex-linked")

            add_journal_entry(
                content=entry_text,
                mood=mood,
                tags=all_tags,
                title=title if title else None
            )
            st.success("Saved!")
            st.balloons()

    with col2:
        st.caption("Stored locally, never shared")


def _render_daily_prompt():
    """Daily reflection prompt."""
    st.markdown("### Daily Reflection")

    category = st.selectbox(
        "Theme",
        options=list(REFLECTION_PROMPTS.keys()),
        format_func=lambda x: x.title()
    )

    if "current_prompt" not in st.session_state or st.session_state.get("prompt_cat") != category:
        st.session_state.current_prompt = random.choice(REFLECTION_PROMPTS[category])
        st.session_state.prompt_cat = category

    st.markdown(f"""
    <div style="background: rgba(99, 102, 241, 0.1); padding: 1rem; border-radius: 8px; border-left: 3px solid #6366f1; margin: 1rem 0;">
        <p style="font-size: 1.1rem; font-style: italic; margin: 0;">"{st.session_state.current_prompt}"</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 New Prompt"):
        st.session_state.current_prompt = random.choice(REFLECTION_PROMPTS[category])
        st.rerun()

    response = st.text_area(
        "Your reflection",
        height=180,
        placeholder="Take a moment to think...",
        key="reflection_response"
    )

    link_to_codex = st.checkbox("🤖 Link to Codex", key="ref_codex")

    if st.button("💾 Save Reflection", type="primary", disabled=not response.strip()):
        tags = ["reflection", category]
        if link_to_codex:
            tags.append("codex-linked")

        add_reflection(
            prompt=st.session_state.current_prompt,
            response=response,
            category=category,
            tags=tags
        )
        st.success("Saved!")
        st.session_state.current_prompt = random.choice(REFLECTION_PROMPTS[category])
        st.rerun()


def _render_past_entries():
    """View past entries."""
    st.markdown("### Your Codex History")

    data = load_data()

    col1, col2 = st.columns(2)
    with col1:
        entry_type = st.selectbox("Type", ["Journal", "Reflections", "All"])
    with col2:
        all_tags = set()
        for e in data.get("journal", []):
            all_tags.update(e.get("tags", []))
        for r in data.get("reflections", []):
            all_tags.update(r.get("tags", []))
        tag_filter = st.selectbox("Tag", ["All"] + sorted([t for t in all_tags if t != "codex-linked"]))

    st.markdown("---")

    if entry_type in ["Journal", "All"]:
        entries = sorted(data.get("journal", []), key=lambda x: x.get('created_at', ''), reverse=True)
        if tag_filter != "All":
            entries = [e for e in entries if tag_filter in e.get("tags", [])]

        for entry in entries[:15]:
            mood_icon = MOOD_ICONS.get(entry.get('mood', ''), '📝')
            title = entry.get('title') or entry.get('content', '')[:40] + "..."
            date = entry.get('created_at', '')[:10]
            linked = "🤖" if "codex-linked" in entry.get("tags", []) else ""

            with st.expander(f"{mood_icon} {title} — {date} {linked}"):
                st.write(entry.get('content', ''))
                tags = [f"`#{t}`" for t in entry.get("tags", []) if t != "codex-linked"]
                if tags:
                    st.markdown(" ".join(tags))
                if st.button("🗑️", key=f"del_j_{entry.get('id')}"):
                    data["journal"] = [e for e in data["journal"] if e.get('id') != entry.get('id')]
                    save_data(data)
                    st.rerun()

    if entry_type in ["Reflections", "All"]:
        refs = sorted(data.get("reflections", []), key=lambda x: x.get('created_at', ''), reverse=True)
        if tag_filter != "All":
            refs = [r for r in refs if tag_filter in r.get("tags", [])]

        for ref in refs[:15]:
            date = ref.get('created_at', '')[:10]
            cat = ref.get('category', 'general').title()
            linked = "🤖" if "codex-linked" in ref.get("tags", []) else ""

            with st.expander(f"💭 {cat} — {date} {linked}"):
                st.markdown(f"*{ref.get('prompt', '')}*")
                st.markdown("---")
                st.write(ref.get('response', ''))
                if st.button("🗑️", key=f"del_r_{ref.get('id')}"):
                    data["reflections"] = [e for e in data["reflections"] if e.get('id') != ref.get('id')]
                    save_data(data)
                    st.rerun()


def get_codex_linked_entries():
    """Get all entries tagged for Codex access."""
    data = load_data()
    linked = []

    for entry in data.get("journal", []):
        if "codex-linked" in entry.get("tags", []):
            linked.append({
                "type": "journal",
                "title": entry.get("title", "Untitled"),
                "content": entry.get("content", ""),
                "date": entry.get("created_at", ""),
                "mood": entry.get("mood", "")
            })

    for ref in data.get("reflections", []):
        if "codex-linked" in ref.get("tags", []):
            linked.append({
                "type": "reflection",
                "prompt": ref.get("prompt", ""),
                "content": ref.get("response", ""),
                "date": ref.get("created_at", "")
            })

    return sorted(linked, key=lambda x: x.get("date", ""), reverse=True)
