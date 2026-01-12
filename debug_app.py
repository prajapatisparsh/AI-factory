#!/usr/bin/env python3
"""
Minimal debug version to trace the exact flow.
Run with: poetry run streamlit run debug_app.py
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.agents.vision import VisionAgent
from src.agents.pm import PMAgent
from src.schemas import DocumentAnalysis

st.set_page_config(page_title="Debug App", layout="wide")

# Initialize session state
if 'debug_phase' not in st.session_state:
    st.session_state.debug_phase = 0
    st.session_state.debug_context = None
    st.session_state.debug_stories = None
    st.session_state.debug_log = []

def add_log(msg):
    st.session_state.debug_log.append(msg)
    print(f"[DEBUG] {msg}")  # Also print to console

# Show current state
st.title("🔍 Debug App")
st.write(f"**Current Phase:** {st.session_state.debug_phase}")

# Show log
with st.expander("Debug Log", expanded=True):
    for log in st.session_state.debug_log:
        st.text(log)

# Phase 0: Input
if st.session_state.debug_phase == 0:
    st.header("Phase 0: Input")
    text = st.text_area("Enter BRD:", "Build a task management app with user login and task creation.")
    
    if st.button("Start Phase 1"):
        st.session_state.debug_text = text
        st.session_state.debug_phase = 1
        add_log("Moving to Phase 1")
        st.rerun()

# Phase 1: Parse
elif st.session_state.debug_phase == 1:
    st.header("Phase 1: Parsing")
    add_log("Phase 1 started")
    
    with st.spinner("Parsing with VisionAgent..."):
        try:
            agent = VisionAgent()
            add_log("VisionAgent created")
            
            context = agent.parse_text_input(st.session_state.debug_text)
            add_log(f"Parsing complete: {len(context.features)} features")
            
            st.session_state.debug_context = context
            st.session_state.debug_phase = 2
            add_log("Moving to Phase 2")
            st.rerun()
            
        except Exception as e:
            add_log(f"ERROR: {e}")
            st.error(f"Error: {e}")

# Phase 2: User Stories
elif st.session_state.debug_phase == 2:
    st.header("Phase 2: User Stories")
    add_log("Phase 2 started")
    
    # Show Phase 1 results
    st.success(f"Phase 1 complete: {len(st.session_state.debug_context.features)} features")
    
    with st.spinner("Generating user stories with PMAgent..."):
        try:
            agent = PMAgent()
            add_log("PMAgent created")
            
            stories = agent.generate_user_stories(st.session_state.debug_context)
            add_log(f"Stories generated: {len(stories)}")
            
            st.session_state.debug_stories = stories
            st.session_state.debug_phase = 3
            add_log("Moving to Phase 3")
            st.rerun()
            
        except Exception as e:
            import traceback
            add_log(f"ERROR: {e}")
            add_log(traceback.format_exc())
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())

# Phase 3: Done
elif st.session_state.debug_phase == 3:
    st.header("Phase 3: Complete!")
    add_log("Phase 3 reached - SUCCESS!")
    
    st.success("All phases complete!")
    
    st.subheader("Context:")
    st.json({
        "project_type": st.session_state.debug_context.project_type.value,
        "features": st.session_state.debug_context.features,
        "personas": st.session_state.debug_context.personas
    })
    
    st.subheader("User Stories:")
    for i, story in enumerate(st.session_state.debug_stories[:5]):
        st.write(f"{i+1}. **{story.title}**")
        st.write(f"   As a {story.user_role}, I want to {story.action} so that {story.benefit}")

# Reset button
if st.button("Reset"):
    st.session_state.debug_phase = 0
    st.session_state.debug_context = None
    st.session_state.debug_stories = None
    st.session_state.debug_log = []
    st.rerun()
