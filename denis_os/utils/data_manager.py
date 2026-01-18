"""
Data Manager for DenisOS - Your Personal Codex
Handles all persistent data storage (like Tom Riddle's diary, but friendly)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional, List
import uuid


def get_data_path() -> Path:
    """Get the path to the data file."""
    return Path(__file__).parent.parent / "data" / "codex_data.json"


def _ensure_data_file() -> dict:
    """Ensure data file exists and return its contents."""
    data_path = get_data_path()
    data_path.parent.mkdir(parents=True, exist_ok=True)

    default_structure = {
        "meta": {
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0.0"
        },
        "journal": [],
        "finance": {
            "transactions": [],
            "budgets": {},
            "recurring": []
        },
        "projects": [],
        "notes": [],
        "reflections": [],
        "lumber_calculations": []
    }

    if not data_path.exists():
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(default_structure, f, indent=2)
        return default_structure

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(default_structure, f, indent=2)
        return default_structure


def save_data(data: dict) -> bool:
    """Save data to file."""
    data_path = get_data_path()
    data["meta"]["last_modified"] = datetime.now().isoformat()
    try:
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError:
        return False


def load_data() -> dict:
    """Load all data from file."""
    return _ensure_data_file()


def add_entry(collection: str, entry: dict) -> str:
    """Add an entry to a collection. Returns the entry ID."""
    data = load_data()

    entry_id = str(uuid.uuid4())[:8]
    entry["id"] = entry_id
    entry["created_at"] = datetime.now().isoformat()

    if collection not in data:
        data[collection] = []

    if isinstance(data[collection], list):
        data[collection].append(entry)

    save_data(data)
    return entry_id


def get_entries(collection: str, limit: Optional[int] = None) -> List[dict]:
    """Get entries from a collection."""
    data = load_data()
    entries = data.get(collection, [])

    if isinstance(entries, list):
        entries = sorted(entries, key=lambda x: x.get('created_at', ''), reverse=True)
        if limit:
            entries = entries[:limit]

    return entries


def update_entry(collection: str, entry_id: str, updates: dict) -> bool:
    """Update an entry by ID."""
    data = load_data()

    if collection not in data or not isinstance(data[collection], list):
        return False

    for entry in data[collection]:
        if entry.get('id') == entry_id:
            entry.update(updates)
            entry["updated_at"] = datetime.now().isoformat()
            return save_data(data)

    return False


def delete_entry(collection: str, entry_id: str) -> bool:
    """Delete an entry by ID."""
    data = load_data()

    if collection not in data or not isinstance(data[collection], list):
        return False

    original_len = len(data[collection])
    data[collection] = [e for e in data[collection] if e.get('id') != entry_id]

    if len(data[collection]) < original_len:
        return save_data(data)

    return False


def add_journal_entry(content: str, mood: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
    """Add a journal entry - talk to your codex."""
    entry = {
        "content": content,
        "mood": mood,
        "tags": tags or [],
        "type": "journal"
    }
    return add_entry("journal", entry)


def add_reflection(prompt: str, response: str, category: str = "general") -> str:
    """Add a philosophical reflection."""
    entry = {
        "prompt": prompt,
        "response": response,
        "category": category
    }
    return add_entry("reflections", entry)


def get_stats() -> dict:
    """Get usage statistics."""
    data = load_data()

    return {
        "journal_entries": len(data.get("journal", [])),
        "transactions": len(data.get("finance", {}).get("transactions", [])),
        "projects": len(data.get("projects", [])),
        "reflections": len(data.get("reflections", [])),
        "lumber_calcs": len(data.get("lumber_calculations", [])),
        "last_modified": data.get("meta", {}).get("last_modified", "Never")
    }
