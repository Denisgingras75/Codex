"""
Philosophy & Reflection Module for DenisOS
Your digital journal and thinking companion - like Tom Riddle's diary, but it helps you grow
"""

import streamlit as st
from datetime import datetime
import random
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
        "How can you practice virtue in your work today?",
        "What fear is holding you back, and is it rational?",
        "If this were your last day, how would you spend it?",
    ],
    "practical": [
        "What's the ONE thing that would make today a success?",
        "What task have you been avoiding, and why?",
        "What did you learn from your last mistake?",
        "How can you help someone else today?",
        "What skill do you want to improve this week?",
        "What's draining your energy that you could eliminate?",
        "What would you attempt if you knew you couldn't fail?",
        "What's the best use of your time right now?",
    ],
    "craft": [
        "What does mastery look like in your current project?",
        "What technique could you practice to improve?",
        "Who do you admire in your craft, and why?",
        "What's the difference between good enough and excellent?",
        "What would you build if resources weren't a constraint?",
        "What have your hands taught you that your mind couldn't?",
        "How does your work serve others?",
        "What tradition in your craft is worth preserving?",
    ],
    "growth": [
        "What belief have you changed your mind about recently?",
        "What's uncomfortable that you should lean into?",
        "How are you different from a year ago?",
        "What would your future self thank you for doing today?",
        "What's a small habit that could compound over time?",
        "Where are you playing it too safe?",
        "What conversation are you avoiding?",
        "What does 'enough' look like for you?",
    ]
}

MOODS = ["😊 Great", "🙂 Good", "😐 Okay", "😔 Low", "😤 Frustrated", "🤔 Thoughtful", "💪 Motivated"]


def render():
    """Render the philosophy module UI."""
    st.header("📖 Journal & Reflections")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Write", "Daily Prompt", "Past Entries", "Wisdom"
    ])

    with tab1:
        _render_journal()

    with tab2:
        _render_daily_prompt()

    with tab3:
        _render_past_entries()

    with tab4:
        _render_wisdom()


def _render_journal():
    """Free-form journal entry."""
    st.subheader("What's on your mind?")

    col1, col2 = st.columns([3, 1])

    with col2:
        mood = st.selectbox("Current Mood", MOODS)
        tags_input = st.text_input("Tags", placeholder="work, family, goals")

    with col1:
        entry_text = st.text_area(
            "Write freely...",
            height=200,
            placeholder="This is your space. Write whatever comes to mind. "
                       "No one else will read this unless you share it.",
            key="journal_entry"
        )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Save Entry", type="primary", disabled=not entry_text.strip()):
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            entry_id = add_journal_entry(
                content=entry_text,
                mood=mood.split()[1] if mood else None,
                tags=tags
            )
            st.success("Entry saved to your codex")
            st.balloons()

    with col2:
        st.caption("Your entries are stored locally and never shared")


def _render_daily_prompt():
    """Daily reflection prompt."""
    st.subheader("Daily Reflection")

    category = st.selectbox(
        "Choose a theme",
        options=list(REFLECTION_PROMPTS.keys()),
        format_func=lambda x: x.title()
    )

    if "current_prompt" not in st.session_state:
        st.session_state.current_prompt = random.choice(REFLECTION_PROMPTS[category])

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"### *\"{st.session_state.current_prompt}\"*")
    with col2:
        if st.button("🔄 New"):
            st.session_state.current_prompt = random.choice(REFLECTION_PROMPTS[category])
            st.rerun()

    response = st.text_area(
        "Your reflection",
        height=150,
        placeholder="Take a moment to think before writing...",
        key="reflection_response"
    )

    if st.button("Save Reflection", type="primary", disabled=not response.strip()):
        add_reflection(
            prompt=st.session_state.current_prompt,
            response=response,
            category=category
        )
        st.success("Reflection saved")
        st.session_state.current_prompt = random.choice(REFLECTION_PROMPTS[category])
        st.rerun()


def _render_past_entries():
    """View past journal entries and reflections."""
    st.subheader("Your Codex")

    entry_type = st.radio("View", ["Journal Entries", "Reflections"], horizontal=True)

    data = load_data()

    if entry_type == "Journal Entries":
        entries = data.get("journal", [])
        entries = sorted(entries, key=lambda x: x.get('created_at', ''), reverse=True)

        if not entries:
            st.info("No journal entries yet. Start writing!")
            return

        for entry in entries[:20]:
            with st.expander(
                f"{entry.get('mood', '📝')} {entry.get('created_at', 'Unknown')[:10]}"
            ):
                st.write(entry.get('content', ''))
                if entry.get('tags'):
                    st.caption(f"Tags: {', '.join(entry['tags'])}")

                if st.button("Delete", key=f"del_j_{entry.get('id')}"):
                    data["journal"] = [e for e in data["journal"] if e.get('id') != entry.get('id')]
                    save_data(data)
                    st.rerun()

    else:
        reflections = data.get("reflections", [])
        reflections = sorted(reflections, key=lambda x: x.get('created_at', ''), reverse=True)

        if not reflections:
            st.info("No reflections yet. Try a daily prompt!")
            return

        for ref in reflections[:20]:
            with st.expander(f"💭 {ref.get('created_at', 'Unknown')[:10]} - {ref.get('category', 'general').title()}"):
                st.markdown(f"**Prompt:** *{ref.get('prompt', '')}*")
                st.write(ref.get('response', ''))

                if st.button("Delete", key=f"del_r_{ref.get('id')}"):
                    data["reflections"] = [e for e in data["reflections"] if e.get('id') != ref.get('id')]
                    save_data(data)
                    st.rerun()


def _render_wisdom():
    """Curated quotes and wisdom."""
    st.subheader("Collected Wisdom")

    wisdom = [
        ("Marcus Aurelius", "You have power over your mind, not outside events. Realize this, and you will find strength."),
        ("Seneca", "We suffer more often in imagination than in reality."),
        ("Epictetus", "It's not what happens to you, but how you react to it that matters."),
        ("Marcus Aurelius", "The object of life is not to be on the side of the majority, but to escape finding oneself in the ranks of the insane."),
        ("Lao Tzu", "A journey of a thousand miles begins with a single step."),
        ("Japanese Proverb", "Fall seven times, stand up eight."),
        ("Bruce Lee", "Adapt what is useful, reject what is useless, and add what is specifically your own."),
        ("Naval Ravikant", "Desire is a contract you make with yourself to be unhappy until you get what you want."),
        ("Miyamoto Musashi", "There is nothing outside of yourself that can ever enable you to get better, stronger, richer, quicker, or smarter. Everything is within."),
        ("Unknown Craftsman", "Measure twice, cut once."),
        ("Frank Lloyd Wright", "You can use an eraser on the drafting table or a sledgehammer on the construction site."),
        ("Abraham Lincoln", "Give me six hours to chop down a tree and I will spend the first four sharpening the axe."),
    ]

    if st.button("Show Random Wisdom"):
        author, quote = random.choice(wisdom)
        st.session_state.current_wisdom = (author, quote)

    if "current_wisdom" in st.session_state:
        author, quote = st.session_state.current_wisdom
        st.markdown(f"""
        > *"{quote}"*
        >
        > — **{author}**
        """)

    st.markdown("---")
    st.markdown("**All Collected Wisdom**")

    for author, quote in wisdom:
        st.markdown(f"**{author}:** *\"{quote}\"*")
        st.write("")
