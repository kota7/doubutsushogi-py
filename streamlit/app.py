# -*- coding: utf-8 -*-

from logging import getLogger, basicConfig
logger = getLogger(__name__)
basicConfig(level=20)

def _parent_directory_to_path():
    import sys
    import os
    # add previous folder to the package path
    # so that it recognize ./doubutsushogi as the package
    p = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    logger.info("Adding '%s' to the package path", p)
    sys.path.insert(0, p)
_parent_directory_to_path()

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from doubutsushogi import initial_state, State, evaluate_states, optimal_path
from doubutsushogi.evaluate import remaining_steps


def _study_tab():
    def _initialize_session_states():
        if "currentState" not in st.session_state:
            st.session_state["currentState"] = initial_state()
        if "prevStates" not in st.session_state:
            st.session_state["prevStates"] = []

    def _current_state():
        return st.session_state["currentState"] or initial_state()

    def _update_current_state_from_text():
        # _update_current_state(text=st.session_state.stateFromText)
        text = st.session_state.stateFromText
        try:
            state = State.from_text(text)
            st.session_state["prevStates"].append(_current_state())
            st.session_state["currentState"] = state       
        except Exception as e:
            logger.warning("Failed to parse text '%s' due to error: '%s'", state_text, str(e))
            st.error(f"Failed to parse text '{text}' due to error: '{e}'")

    def _update_current_state_by_action():
        action=st.session_state.actionSelected        
        st.session_state["prevStates"].append(_current_state())
        st.session_state["currentState"] = _current_state().action_result(action)
    
    def _initialize_state():
        st.session_state["currentState"] = initial_state()
        st.session_state["prevStates"] = []

    def _back():
        history = st.session_state.get("prevStates", [])
        if len(history) == 0:
            st.session_state["currentState"] = initial_state()
        else:
            st.session_state["currentState"] = history.pop()
               
    _initialize_session_states()

    #with st.sidebar:
    c1, c2, c3, c4, c5, _ = st.columns([2, 2, 1, 1, 1, 7])
    

    state = _current_state()
    logger.info("Current state: %s", state.text)
    actions = state.valid_actions
    actions.sort(key=lambda a: (a.piece, str(a)))
    #print(actions)
    #print(type(actions))

    state_text = c1.text_input("Go to state:", placeholder="klz.h..H.ZLK0000001",
                               on_change=_update_current_state_from_text, key="stateFromText")
    action_select = c2.selectbox("Choose Action", actions, key="actionSelected")
    c3.write("")
    c3.write("")
    c3.button("GO", on_click=_update_current_state_by_action)
    c4.write("")
    c4.write("")
    c4.button("Back", on_click=_back)
    c5.write("")
    c5.write("")
    c5.button("Initialize", on_click=_initialize_state)
 
    c1, _, c2 = st.columns([4, 1, 7]) 
    html = "\n".join(state.to_html(cellsize="100", captured_imgsize="40"))
    with c1:
        components.html(html, width=400, height=600)

    value = evaluate_states([state])[0]
    if value == 0:
        result = "tie"
    else:
        winner = 1 if value > 0 else 2
        steps = remaining_steps(value)
        result = f"win by {winner} in {steps} steps"
    c2.markdown(f"State: `{state.text}`  Value: {value} ({result})")

    actions = state.valid_actions
    next_states = [state.action_result(a) for a in actions]
    next_states_text = [s.text for s in next_states]
    next_values = evaluate_states([s for s in next_states])
    paths = ["-".join(str(a) for a in optimal_path(s, depth=6, randomize=True)) for s in next_states]
    df = pd.DataFrame({
        "action": [str(a) for a in actions],
        "state": next_states_text,
        "value": next_values,
        "path": paths
    }).set_index("action").dropna().sort_values("value", ascending=(state.turn==2))

    c2.dataframe(df)
        # for action in actions:
        #     cs = c2.columns([1,1,1,1])
        #     cs[0].write(str(action))
        #     print(action)


def main():
    st.set_page_config(page_title="Doubutsu Shogi Master", layout="wide")

    with st.spinner("Setting up the database..."):
        # evaluate function automatically download the dbfile if not exists
        # this occurs only for the first time
        evaluate_states([initial_state()])

    tab1, tab2 = st.tabs(["Study", "Play"])
    with tab1:
        _study_tab()

if __name__ == "__main__":
    main()