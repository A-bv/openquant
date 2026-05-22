"""
OpenQuant — Audit Trail display component.
Collapsible panel at the bottom of every valuation.
"""
from __future__ import annotations
import streamlit as st
from core.audit_trail import AuditTrail


def render_audit_trail(trail: AuditTrail) -> None:
    """Render collapsible audit trail panel."""
    with st.expander("🔍 Model Audit Trail — How this analysis was produced", expanded=False):
        st.caption(
            f"Generated {trail.generated_at.strftime('%Y-%m-%d %H:%M UTC')} · "
            f"OpenQuant {trail.openquant_version}"
        )
        display = trail.to_display_dict()

        col1, col2 = st.columns(2)
        items = [(k, v) for k, v in display.items() if v != ""]
        mid = len(items) // 2

        with col1:
            for k, v in items[:mid]:
                if k.startswith("─"):
                    st.markdown(f"**{k}**")
                else:
                    st.markdown(f"**{k}:** {v}")

        with col2:
            for k, v in items[mid:]:
                if k.startswith("─"):
                    st.markdown(f"**{k}**")
                else:
                    st.markdown(f"**{k}:** {v}")

        if trail.all_warnings:
            st.divider()
            st.markdown("**Warnings triggered:**")
            for w in trail.all_warnings:
                st.caption(f"⚠ {w}")

        st.divider()
        st.markdown("**Formulas used:**")
        for formula in trail.formula_references:
            with st.expander(f"{formula['name']}", expanded=False):
                st.code(formula['formula'], language=None)
                st.caption(f"Source: {formula['source']}")
                st.caption(formula['description'])
