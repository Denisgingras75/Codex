"""
Codex Advisor Module - Your AI-powered honest advisor
Uses Claude for brutally honest feedback, idea critique, and research.
"""

import streamlit as st
from datetime import datetime
import json
from pathlib import Path

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from utils.data_manager import load_data, save_data
from utils.config import get_config_value


SYSTEM_PROMPT = """You are the Codex - Denis's personal AI advisor living inside his digital notebook.

Your core traits:
1. BRUTAL HONESTY: You tell the truth even when it's uncomfortable. No sugarcoating. No false encouragement. If an idea is bad, say so directly and explain why.

2. CONSTRUCTIVE CRITICISM: When you criticize, you always offer concrete alternatives or improvements. You don't just tear down - you help rebuild better.

3. SOCRATIC METHOD: You ask probing questions to help Denis think deeper. You challenge assumptions.

4. PRACTICAL WISDOM: You combine philosophical insight with practical advice. Theory without action is useless.

5. RESEARCH-BACKED: When making claims, you explain your reasoning. You acknowledge uncertainty when it exists.

6. NO FLATTERY: Never say "great question" or "that's interesting" as filler. Get straight to substance.

7. REMEMBER CONTEXT: Denis is a carpenter/craftsman interested in finance, philosophy, and building things. Ground advice in his reality.

Your responses should be:
- Direct and concise (no fluff)
- Honest even if it stings
- Actionable with specific next steps
- Grounded in reality, not theory

You are not a yes-man. You are a trusted advisor who cares enough to tell hard truths.

When asked to research something, provide factual information with caveats about what you're uncertain about. Cite general sources when relevant (e.g., "According to standard financial advice..." or "Stoic philosophers like Marcus Aurelius argued...").

Start conversations with: "What's on your mind, Denis?" or similar. No flowery greetings."""


def get_client():
    """Get Anthropic client if API key is configured."""
    api_key = st.session_state.get("anthropic_api_key") or get_config_value("api.anthropic_key")
    if api_key and ANTHROPIC_AVAILABLE:
        return anthropic.Anthropic(api_key=api_key)
    return None


def get_conversation_history():
    """Load conversation history from data."""
    data = load_data()
    return data.get("codex_conversations", [])


def save_message(role: str, content: str):
    """Save a message to conversation history."""
    data = load_data()
    if "codex_conversations" not in data:
        data["codex_conversations"] = []

    data["codex_conversations"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

    # Keep last 100 messages
    data["codex_conversations"] = data["codex_conversations"][-100:]
    save_data(data)


def chat_with_codex(user_message: str, conversation_context: list) -> str:
    """Send message to Claude and get response."""
    client = get_client()
    if not client:
        return "API key not configured. Go to Settings to add your Anthropic API key."

    # Build messages for API
    messages = []
    for msg in conversation_context[-20:]:  # Last 20 messages for context
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        return response.content[0].text
    except anthropic.APIError as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def render():
    """Render the Codex Advisor page."""
    st.header("📓 The Codex")
    st.caption("Your brutally honest AI advisor")

    # API Key check
    if not ANTHROPIC_AVAILABLE:
        st.error("Anthropic library not installed. Run: pip install anthropic")
        return

    api_key = st.session_state.get("anthropic_api_key") or get_config_value("api.anthropic_key")

    if not api_key:
        st.warning("No API key configured")
        with st.expander("Configure API Key"):
            new_key = st.text_input("Anthropic API Key", type="password",
                                     help="Get your key at console.anthropic.com")
            if st.button("Save Key"):
                st.session_state.anthropic_api_key = new_key
                st.success("Key saved for this session!")
                st.rerun()
        st.info("Get an API key at [console.anthropic.com](https://console.anthropic.com)")
        return

    # Conversation modes
    mode = st.radio(
        "Mode",
        ["Chat", "Critique My Idea", "Research", "Decision Help"],
        horizontal=True
    )

    st.markdown("---")

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
        history = get_conversation_history()
        if history:
            st.session_state.messages = [
                {"role": m["role"], "content": m["content"]}
                for m in history[-10:]
            ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Mode-specific prompts
    placeholder_text = {
        "Chat": "What's on your mind?",
        "Critique My Idea": "Describe your idea - I'll give you honest feedback...",
        "Research": "What do you want me to research?",
        "Decision Help": "What decision are you facing? What are your options?"
    }

    # Chat input
    if prompt := st.chat_input(placeholder_text.get(mode, "Type here...")):
        # Add mode context to prompt
        if mode == "Critique My Idea":
            full_prompt = f"[IDEA CRITIQUE REQUEST]\n\nHere's my idea:\n{prompt}\n\nGive me your honest assessment. What's wrong with it? What could make it better? Don't hold back."
        elif mode == "Research":
            full_prompt = f"[RESEARCH REQUEST]\n\nTopic: {prompt}\n\nGive me a factual overview. Include what's well-established vs uncertain. Cite sources where relevant."
        elif mode == "Decision Help":
            full_prompt = f"[DECISION HELP]\n\nHere's my situation:\n{prompt}\n\nHelp me think through this. Ask me hard questions. Point out what I might be missing."
        else:
            full_prompt = prompt

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message("user", prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_codex(full_prompt, st.session_state.messages[:-1])
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message("assistant", response)

    # Sidebar actions
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Codex Actions**")

        if st.button("Clear Conversation"):
            st.session_state.messages = []
            data = load_data()
            data["codex_conversations"] = []
            save_data(data)
            st.rerun()

        if st.button("Export Chat"):
            chat_export = "\n\n".join([
                f"**{m['role'].upper()}**: {m['content']}"
                for m in st.session_state.messages
            ])
            st.download_button(
                "Download",
                chat_export,
                file_name=f"codex_chat_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )


def render_quick_ask():
    """Render a quick-ask widget for other pages."""
    with st.expander("💬 Quick Ask Codex"):
        quick_q = st.text_input("Quick question", key="quick_codex")
        if st.button("Ask", key="quick_ask_btn"):
            if quick_q:
                with st.spinner("..."):
                    response = chat_with_codex(quick_q, [])
                st.markdown(response)
