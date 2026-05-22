"""
OpenQuant — Assumption Diagnostic display component.
Renders the 8-dimension diagnostic before valuation numbers.
"""
from __future__ import annotations
import streamlit as st
from core.assumption_diagnostic import AssumptionDiagnostic, DiagnosticRating


RATING_EMOJI = {
    DiagnosticRating.GREEN: "🟢",
    DiagnosticRating.AMBER: "🟡",
    DiagnosticRating.RED: "🔴",
}

CONFIDENCE_COLOR = {
    "High": "green",
    "Moderate": "orange",
    "Low": "red",
    "Very Low": "red",
}


def render_diagnostic(diagnostic: AssumptionDiagnostic) -> None:
    """Render the full 8-dimension diagnostic panel."""
    overall_emoji = RATING_EMOJI[diagnostic.overall_rating]
    st.markdown(f"### {overall_emoji} Assumption Diagnostic")
    st.caption(diagnostic.disclaimer)
    st.markdown(f"**{diagnostic.summary_text}**")
    st.divider()

    cols = st.columns(4)
    for i, dim in enumerate(diagnostic.dimensions):
        with cols[i % 4]:
            emoji = RATING_EMOJI[dim.rating]
            st.markdown(f"{emoji} **{dim.name}**")
            st.caption(dim.message)
            if dim.detail and dim.rating != DiagnosticRating.GREEN:
                with st.expander("Detail", expanded=False):
                    st.caption(dim.detail)


def render_diagnostic_compact(diagnostic: AssumptionDiagnostic) -> None:
    """Compact single-line diagnostic for page headers."""
    overall_emoji = RATING_EMOJI[diagnostic.overall_rating]
    n_issues = len(diagnostic.red_dimensions) + len(diagnostic.amber_dimensions)
    if n_issues == 0:
        st.success(f"{overall_emoji} All 8 diagnostic dimensions Green")
    elif diagnostic.overall_rating == DiagnosticRating.RED:
        st.error(f"{overall_emoji} {diagnostic.summary_text}")
    else:
        st.warning(f"{overall_emoji} {diagnostic.summary_text}")
