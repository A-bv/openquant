"""
OpenQuant — Red Flag Summary display component.
Shown at the top of every valuation — before numbers.
"""
from __future__ import annotations
import streamlit as st
from core.red_flags import RedFlagSummary


def render_red_flags(summary: RedFlagSummary) -> None:
    """Render red flag summary at top of valuation page."""
    if summary.is_clean:
        st.success(
            f"✅ No major concerns — analysis confidence: **{summary.overall_confidence}**"
        )
        return

    confidence_colors = {
        "High": st.success,
        "Moderate": st.warning,
        "Low": st.error,
        "Very Low": st.error,
    }
    render_fn = confidence_colors.get(summary.overall_confidence, st.warning)

    with st.container():
        render_fn(
            f"Analysis confidence: **{summary.overall_confidence}** "
            f"— {summary.flag_count} concern(s) flagged"
        )
        if summary.flags:
            st.markdown("**Before reading this valuation:**")
            for flag in summary.flags:
                st.markdown(f"- {flag}")
