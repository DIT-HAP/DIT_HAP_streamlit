"""Shared fragments for the usage-guide UI."""

from collections.abc import Callable, Mapping

import streamlit as st


def _open_selected_guide(usage_guides: Mapping[str, Callable[[], object]]) -> None:
    """Open the selected usage guide, ignoring a cleared selection."""
    selected_guide = st.session_state.usage_guide_selector
    if selected_guide:
        usage_guides[selected_guide]()


@st.fragment
def usage_guide_bar(usage_guides: Mapping[str, Callable[[], object]]) -> None:
    """Render the usage-guide bar in a fragment so a click only reruns the bar."""
    st.segmented_control(
        label="📖 Usage Guides",
        options=list(usage_guides.keys()),
        key="usage_guide_selector",
        on_change=_open_selected_guide,
        args=(usage_guides,),
        width="stretch",
        label_visibility="collapsed",
    )
