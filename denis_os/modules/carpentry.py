"""
Carpentry & Timber Calculator Module for DenisOS
Calculate lumber needs, costs, and save calculations for the workshop
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_manager import load_data, save_data, add_entry, get_entries
from utils.config import get_config_value


LUMBER_PRICES = {
    "2x4x8": {"name": "2x4 - 8ft", "price": 5.99, "actual": (1.5, 3.5, 96)},
    "2x4x10": {"name": "2x4 - 10ft", "price": 7.99, "actual": (1.5, 3.5, 120)},
    "2x4x12": {"name": "2x4 - 12ft", "price": 9.99, "actual": (1.5, 3.5, 144)},
    "2x6x8": {"name": "2x6 - 8ft", "price": 8.99, "actual": (1.5, 5.5, 96)},
    "2x6x10": {"name": "2x6 - 10ft", "price": 11.99, "actual": (1.5, 5.5, 120)},
    "2x6x12": {"name": "2x6 - 12ft", "price": 14.99, "actual": (1.5, 5.5, 144)},
    "2x8x8": {"name": "2x8 - 8ft", "price": 12.99, "actual": (1.5, 7.25, 96)},
    "2x8x12": {"name": "2x8 - 12ft", "price": 18.99, "actual": (1.5, 7.25, 144)},
    "2x10x8": {"name": "2x10 - 8ft", "price": 16.99, "actual": (1.5, 9.25, 96)},
    "2x10x12": {"name": "2x10 - 12ft", "price": 24.99, "actual": (1.5, 9.25, 144)},
    "2x12x8": {"name": "2x12 - 8ft", "price": 21.99, "actual": (1.5, 11.25, 96)},
    "2x12x12": {"name": "2x12 - 12ft", "price": 32.99, "actual": (1.5, 11.25, 144)},
    "4x4x8": {"name": "4x4 Post - 8ft", "price": 14.99, "actual": (3.5, 3.5, 96)},
    "4x4x10": {"name": "4x4 Post - 10ft", "price": 18.99, "actual": (3.5, 3.5, 120)},
    "plywood_1/2": {"name": "Plywood 4x8 - 1/2\"", "price": 45.99, "actual": (0.5, 48, 96)},
    "plywood_3/4": {"name": "Plywood 4x8 - 3/4\"", "price": 59.99, "actual": (0.75, 48, 96)},
    "osb_7/16": {"name": "OSB 4x8 - 7/16\"", "price": 32.99, "actual": (0.4375, 48, 96)},
}


def render():
    """Render the carpentry module UI."""
    st.header("🪵 Timber Calculator")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Quick Calc", "Project Estimator", "Saved Calculations", "Reference"
    ])

    with tab1:
        _render_quick_calc()

    with tab2:
        _render_project_estimator()

    with tab3:
        _render_saved_calcs()

    with tab4:
        _render_reference()


def _render_quick_calc():
    """Quick lumber calculation."""
    st.subheader("Quick Lumber Calculator")

    col1, col2 = st.columns(2)

    with col1:
        lumber_type = st.selectbox(
            "Lumber Type",
            options=list(LUMBER_PRICES.keys()),
            format_func=lambda x: LUMBER_PRICES[x]["name"]
        )
        quantity = st.number_input("Quantity Needed", min_value=1, value=1, step=1)
        waste_factor = st.slider("Waste Factor (%)", 0, 30, 10) / 100 + 1

    with col2:
        lumber = LUMBER_PRICES[lumber_type]
        adjusted_qty = math.ceil(quantity * waste_factor)
        total_cost = adjusted_qty * lumber["price"]

        st.metric("Unit Price", f"${lumber['price']:.2f}")
        st.metric("Quantity (with waste)", adjusted_qty)
        st.metric("Total Cost", f"${total_cost:.2f}")

        actual = lumber["actual"]
        st.caption(f"Actual dimensions: {actual[0]}\" x {actual[1]}\" x {actual[2]}\"")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Calculation", type="primary"):
            calc = {
                "lumber_type": lumber_type,
                "lumber_name": lumber["name"],
                "quantity": quantity,
                "adjusted_quantity": adjusted_qty,
                "waste_factor": waste_factor,
                "unit_price": lumber["price"],
                "total_cost": total_cost
            }
            add_entry("lumber_calculations", calc)
            st.success("Calculation saved!")

    with col2:
        if st.button("Add to Finance"):
            data = load_data()
            if "finance" not in data:
                data["finance"] = {"transactions": [], "budgets": {}, "recurring": []}

            transaction = {
                "id": f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "expense",
                "amount": -total_cost,
                "category": "Lumber & Materials",
                "date": datetime.now().date().isoformat(),
                "description": f"{adjusted_qty}x {lumber['name']}",
                "tags": ["lumber", "materials"],
                "created_at": datetime.now().isoformat()
            }
            data["finance"]["transactions"].append(transaction)
            save_data(data)
            st.success(f"Added ${total_cost:.2f} expense to Finance")


def _render_project_estimator():
    """Full project lumber estimator."""
    st.subheader("Project Estimator")

    project_name = st.text_input("Project Name", placeholder="Deck Build - Backyard")

    st.markdown("**Add Materials**")

    if "project_items" not in st.session_state:
        st.session_state.project_items = []

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        add_lumber = st.selectbox(
            "Select Lumber",
            options=list(LUMBER_PRICES.keys()),
            format_func=lambda x: LUMBER_PRICES[x]["name"],
            key="add_lumber_select"
        )
    with col2:
        add_qty = st.number_input("Qty", min_value=1, value=1, key="add_qty")
    with col3:
        st.write("")
        st.write("")
        if st.button("Add Item"):
            st.session_state.project_items.append({
                "type": add_lumber,
                "name": LUMBER_PRICES[add_lumber]["name"],
                "quantity": add_qty,
                "price": LUMBER_PRICES[add_lumber]["price"]
            })

    if st.session_state.project_items:
        st.markdown("---")
        st.markdown("**Project Materials**")

        total = 0
        for i, item in enumerate(st.session_state.project_items):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(item["name"])
            with col2:
                st.write(f"x{item['quantity']}")
            with col3:
                item_total = item["quantity"] * item["price"]
                total += item_total
                st.write(f"${item_total:.2f}")
            with col4:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.project_items.pop(i)
                    st.rerun()

        st.markdown("---")
        waste_pct = st.slider("Add Waste Factor (%)", 0, 30, 10, key="proj_waste") / 100
        total_with_waste = total * (1 + waste_pct)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Subtotal", f"${total:.2f}")
        with col2:
            st.metric("Total (with waste)", f"${total_with_waste:.2f}")

        if st.button("Save Project Estimate", type="primary"):
            project = {
                "name": project_name or "Unnamed Project",
                "items": st.session_state.project_items.copy(),
                "subtotal": total,
                "waste_factor": 1 + waste_pct,
                "total": total_with_waste
            }
            add_entry("projects", project)
            st.success(f"Project '{project['name']}' saved!")
            st.session_state.project_items = []
            st.rerun()


def _render_saved_calcs():
    """Display saved calculations."""
    st.subheader("Saved Calculations")

    data = load_data()
    calcs = data.get("lumber_calculations", [])
    projects = data.get("projects", [])

    if projects:
        st.markdown("**Saved Projects**")
        for proj in sorted(projects, key=lambda x: x.get('created_at', ''), reverse=True)[:5]:
            with st.expander(f"📁 {proj.get('name', 'Unnamed')} - ${proj.get('total', 0):.2f}"):
                for item in proj.get('items', []):
                    st.write(f"• {item['quantity']}x {item['name']} - ${item['quantity'] * item['price']:.2f}")
                st.caption(f"Created: {proj.get('created_at', 'Unknown')[:10]}")

    if calcs:
        st.markdown("**Quick Calculations**")
        for calc in sorted(calcs, key=lambda x: x.get('created_at', ''), reverse=True)[:10]:
            st.write(
                f"• {calc.get('adjusted_quantity', calc.get('quantity', 0))}x "
                f"{calc.get('lumber_name', 'Unknown')} = ${calc.get('total_cost', 0):.2f}"
            )

    if not calcs and not projects:
        st.info("No saved calculations yet. Use Quick Calc or Project Estimator to get started!")


def _render_reference():
    """Lumber reference guide."""
    st.subheader("Lumber Reference")

    st.markdown("**Current Prices**")

    for key, lumber in LUMBER_PRICES.items():
        actual = lumber["actual"]
        st.write(
            f"**{lumber['name']}** - ${lumber['price']:.2f}  \n"
            f"*Actual: {actual[0]}\" × {actual[1]}\" × {actual[2]}\"*"
        )

    st.markdown("---")
    st.markdown("""
    **Common Conversions**
    - 1 board foot = 144 cubic inches (1\" × 12\" × 12\")
    - Deck boards: ~21 per 100 sq ft (5.5\" wide)
    - Joist spacing: 16\" on center standard, 12\" for heavy loads

    **Tips**
    - Always buy 10-15% extra for waste and mistakes
    - Check boards for warping before purchase
    - Store lumber flat and covered
    """)
