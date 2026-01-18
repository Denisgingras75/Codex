"""
Finance Module for DenisOS
Track expenses, income, and budget like a boss
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_manager import load_data, save_data, add_entry, get_entries
from utils.config import get_config_value


CATEGORIES = [
    "Housing", "Utilities", "Groceries", "Transportation", "Healthcare",
    "Entertainment", "Dining Out", "Shopping", "Tools & Equipment",
    "Lumber & Materials", "Subscriptions", "Income", "Other"
]


def render():
    """Render the finance module UI."""
    st.header("💰 Finance Tracker")

    tab1, tab2, tab3 = st.tabs(["Add Transaction", "View Transactions", "Summary"])

    with tab1:
        _render_add_transaction()

    with tab2:
        _render_transactions_list()

    with tab3:
        _render_summary()


def _render_add_transaction():
    """Render the add transaction form."""
    st.subheader("New Transaction")

    col1, col2 = st.columns(2)

    with col1:
        trans_type = st.radio("Type", ["Expense", "Income"], horizontal=True)
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
        category = st.selectbox("Category", CATEGORIES)

    with col2:
        date = st.date_input("Date", datetime.now())
        description = st.text_input("Description")
        tags = st.text_input("Tags (comma-separated)", placeholder="lumber, project-deck")

    if st.button("Add Transaction", type="primary"):
        if amount > 0:
            transaction = {
                "type": trans_type.lower(),
                "amount": amount if trans_type == "Income" else -amount,
                "category": category,
                "date": date.isoformat(),
                "description": description,
                "tags": [t.strip() for t in tags.split(",") if t.strip()]
            }

            data = load_data()
            if "finance" not in data:
                data["finance"] = {"transactions": [], "budgets": {}, "recurring": []}

            transaction["id"] = f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            transaction["created_at"] = datetime.now().isoformat()
            data["finance"]["transactions"].append(transaction)
            save_data(data)

            st.success(f"Added {trans_type.lower()}: ${abs(amount):.2f}")
            st.rerun()
        else:
            st.error("Please enter a valid amount")


def _render_transactions_list():
    """Render the transactions list."""
    st.subheader("Recent Transactions")

    data = load_data()
    transactions = data.get("finance", {}).get("transactions", [])

    if not transactions:
        st.info("No transactions yet. Add your first one!")
        return

    transactions = sorted(transactions, key=lambda x: x.get('date', ''), reverse=True)

    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
    with col2:
        filter_type = st.selectbox("Filter by Type", ["All", "Income", "Expense"])

    filtered = transactions
    if filter_category != "All":
        filtered = [t for t in filtered if t.get('category') == filter_category]
    if filter_type != "All":
        filtered = [t for t in filtered if t.get('type') == filter_type.lower()]

    for txn in filtered[:20]:
        amount = txn.get('amount', 0)
        color = "green" if amount > 0 else "red"
        icon = "📈" if amount > 0 else "📉"

        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"{icon} **{txn.get('description', 'No description')}**")
                st.caption(f"{txn.get('category', 'Uncategorized')} • {txn.get('date', 'Unknown date')}")
            with col2:
                st.markdown(f":{color}[**${abs(amount):.2f}**]")
            with col3:
                if st.button("🗑️", key=f"del_{txn.get('id')}"):
                    data["finance"]["transactions"] = [
                        t for t in data["finance"]["transactions"]
                        if t.get('id') != txn.get('id')
                    ]
                    save_data(data)
                    st.rerun()
            st.divider()


def _render_summary():
    """Render financial summary."""
    st.subheader("Financial Summary")

    data = load_data()
    transactions = data.get("finance", {}).get("transactions", [])

    if not transactions:
        st.info("Add some transactions to see your summary")
        return

    today = datetime.now()
    this_month = [t for t in transactions
                  if t.get('date', '').startswith(today.strftime('%Y-%m'))]

    total_income = sum(t['amount'] for t in this_month if t.get('amount', 0) > 0)
    total_expenses = abs(sum(t['amount'] for t in this_month if t.get('amount', 0) < 0))
    balance = total_income - total_expenses

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Income (This Month)", f"${total_income:.2f}")
    with col2:
        st.metric("Expenses (This Month)", f"${total_expenses:.2f}")
    with col3:
        delta_color = "normal" if balance >= 0 else "inverse"
        st.metric("Balance", f"${balance:.2f}", delta=f"${balance:.2f}", delta_color=delta_color)

    st.subheader("Spending by Category")
    category_totals = {}
    for txn in this_month:
        if txn.get('amount', 0) < 0:
            cat = txn.get('category', 'Other')
            category_totals[cat] = category_totals.get(cat, 0) + abs(txn['amount'])

    if category_totals:
        for cat, amount in sorted(category_totals.items(), key=lambda x: -x[1]):
            pct = (amount / total_expenses * 100) if total_expenses > 0 else 0
            st.progress(pct / 100, text=f"{cat}: ${amount:.2f} ({pct:.1f}%)")
    else:
        st.info("No expenses recorded this month")


def get_monthly_totals(year: int, month: int) -> Dict[str, float]:
    """Get monthly income and expense totals."""
    data = load_data()
    transactions = data.get("finance", {}).get("transactions", [])

    month_str = f"{year}-{month:02d}"
    monthly = [t for t in transactions if t.get('date', '').startswith(month_str)]

    return {
        "income": sum(t['amount'] for t in monthly if t.get('amount', 0) > 0),
        "expenses": abs(sum(t['amount'] for t in monthly if t.get('amount', 0) < 0))
    }
