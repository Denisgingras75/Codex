"""
Codex Advisor Module - Your AI-powered honest advisor
Uses Claude for brutally honest feedback, idea critique, and research.
"""

import streamlit as st
from datetime import datetime

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from utils.data_manager import load_data, save_data
from utils.config import get_config_value, set_config_value


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

Start conversations naturally. No flowery greetings."""


CUSTOM_CSS = """
<style>
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }

    .mode-selector {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .codex-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2rem;
        font-weight: 700;
    }

    .api-setup-box {
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
"""


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
        return "⚠️ API key not configured. Go to **Settings** to add your Anthropic API key."

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
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        return response.content[0].text
    except anthropic.AuthenticationError:
        return "⚠️ Invalid API key. Please check your key in **Settings**."
    except anthropic.RateLimitError:
        return "⚠️ Rate limit exceeded. Please wait a moment and try again."
    except anthropic.APIError as e:
        return f"⚠️ API Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def render():
    """Render the Codex Advisor page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.markdown('<h1 class="codex-header">🤖 The Codex</h1>', unsafe_allow_html=True)
    st.caption("Your brutally honest AI advisor • Powered by Claude")

    # API Key check
    if not ANTHROPIC_AVAILABLE:
        st.error("⚠️ Anthropic library not installed. This shouldn't happen in Docker.")
        return

    api_key = st.session_state.get("anthropic_api_key") or get_config_value("api.anthropic_key")

    if not api_key:
        st.markdown("""
        <div class="api-setup-box">
            <h3>🔑 Setup Required</h3>
            <p>To use the Codex, you need an Anthropic API key.</p>
        </div>
        """, unsafe_allow_html=True)

        new_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-api03-...",
            help="Get your key at console.anthropic.com"
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🔑 Save & Start", type="primary"):
                if new_key:
                    set_config_value("api.anthropic_key", new_key)
                    st.session_state.anthropic_api_key = new_key
                    st.success("API key saved!")
                    st.rerun()
                else:
                    st.error("Please enter an API key")

        st.markdown("---")
        st.info("🔗 [Get an API key at console.anthropic.com](https://console.anthropic.com)")
        return

    # Mode selector
    st.markdown("---")

    mode_icons = {
        "Chat": "💬",
        "Critique My Idea": "🎯",
        "Research": "🔍",
        "Decision Help": "⚖️"
    }

    mode = st.radio(
        "Mode",
        list(mode_icons.keys()),
        horizontal=True,
        format_func=lambda x: f"{mode_icons[x]} {x}"
    )

    # Mode descriptions
    mode_hints = {
        "Chat": "Free conversation - ask anything",
        "Critique My Idea": "Get brutal, honest feedback on your ideas",
        "Research": "Get factual information with sources",
        "Decision Help": "Work through tough decisions together"
    }
    st.caption(mode_hints[mode])

    st.markdown("---")

    # Handle pending journal context
    if st.session_state.get("pending_context"):
        context = st.session_state.pending_context
        st.info("📓 Journal entry loaded. Ask a question about it below.")

        # Auto-send context
        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.session_state.messages.append({"role": "user", "content": context})
        save_message("user", context)

        with st.spinner("Reading your journal..."):
            response = chat_with_codex(context + "\n\nAcknowledge you've read this and ask me what I'd like to discuss about it.", st.session_state.messages[:-1])

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message("assistant", response)
        st.session_state.pending_context = None
        st.rerun()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        history = get_conversation_history()
        if history:
            st.session_state.messages = [
                {"role": m["role"], "content": m["content"]}
                for m in history[-20:]
            ]

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "📓"):
                st.markdown(message["content"])

    # Mode-specific placeholders
    placeholder_text = {
        "Chat": "What's on your mind?",
        "Critique My Idea": "Describe your idea - I'll give you honest feedback...",
        "Research": "What do you want me to research?",
        "Decision Help": "What decision are you facing?"
    }

    # Chat input
    if prompt := st.chat_input(placeholder_text.get(mode, "Type here...")):
        # Add mode context to prompt
        if mode == "Critique My Idea":
            full_prompt = f"""[IDEA CRITIQUE REQUEST]

Here's my idea:
{prompt}

Give me your honest assessment:
1. What's wrong with it? Be specific.
2. What's the biggest risk I'm not seeing?
3. What would make it better?
4. Should I pursue this or not?

Don't hold back."""

        elif mode == "Research":
            full_prompt = f"""[RESEARCH REQUEST]

Topic: {prompt}

Provide:
1. A factual overview
2. Key points I should know
3. What's well-established vs. uncertain
4. Relevant sources or where to learn more
5. Practical implications for me"""

        elif mode == "Decision Help":
            full_prompt = f"""[DECISION HELP]

Here's my situation:
{prompt}

Help me think through this:
1. What are the key factors I should consider?
2. What am I probably not seeing?
3. What questions should I be asking myself?
4. What would you do in my position and why?"""

        else:
            full_prompt = prompt

        # Display user message
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message("user", prompt)

        # Get response
        with st.chat_message("assistant", avatar="📓"):
            with st.spinner("Thinking..."):
                response = chat_with_codex(full_prompt, st.session_state.messages[:-1])
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message("assistant", response)
        st.rerun()

    # Sidebar actions
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Codex Actions**")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            data = load_data()
            data["codex_conversations"] = []
            save_data(data)
            st.rerun()

        if st.session_state.messages:
            chat_export = "\n\n---\n\n".join([
                f"**{'You' if m['role'] == 'user' else 'Codex'}:**\n{m['content']}"
                for m in st.session_state.messages
            ])
            st.download_button(
                "📥 Export Chat",
                chat_export,
                file_name=f"codex_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")

        # Linked journal entries
        st.markdown("**📓 Linked Entries**")
        linked = get_linked_entries()

        if linked:
            for entry in linked[:5]:
                title = entry.get("title") or entry.get("content", "")[:30] + "..."
                date = entry.get("date", "")[:10]
                entry_type = "📝" if entry.get("type") == "journal" else "💭"

                if st.button(f"{entry_type} {title[:20]}...", key=f"ref_{entry.get('date')}", use_container_width=True):
                    # Add entry context to chat
                    context = f"[REFERENCING MY JOURNAL ENTRY from {date}]\n\n"
                    if entry.get("type") == "journal":
                        context += f"Title: {entry.get('title', 'Untitled')}\n"
                        context += f"Mood: {entry.get('mood', 'Unknown')}\n"
                        context += f"Content: {entry.get('content', '')}\n\n"
                    else:
                        context += f"Reflection prompt: {entry.get('prompt', '')}\n"
                        context += f"My response: {entry.get('content', '')}\n\n"

                    context += "Please consider this context in our conversation."

                    st.session_state.pending_context = context
                    st.rerun()

            st.caption(f"{len(linked)} linked entries")
        else:
            st.caption("No linked entries yet")
            st.caption("Link entries in Journal with 🤖")

        st.markdown("---")
        st.caption(f"💬 {len(st.session_state.messages)} messages")


def get_linked_entries():
    """Get journal entries linked to Codex."""
    data = load_data()
    linked = []

    for entry in data.get("journal", []):
        if "codex-linked" in entry.get("tags", []):
            linked.append({
                "type": "journal",
                "title": entry.get("title"),
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
