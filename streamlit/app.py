# -*- coding: utf-8 -*-

from logging import getLogger, basicConfig
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from doubutsushogi import initial_state, State, evaluate_states, optimal_path

logger = getLogger(__name__)
basicConfig(level=20)

# if "history" not in st.session_state:
#     st.session_state["history"] = []
# if "index" not in st.session_state:
#     st.session_state["index"] = -1

# def _current_state():
#     if len(st.session_state["history"]) == 0:
#         state = initial_state()
#     else:
#         state = st.session_state["history"][max(0, st.session_state["index"])]
#     return state

st.set_page_config(page_title="Doubutsu Shogi Master", layout="wide")

with st.spinner("Setting up the database..."):
    # evaluate function automatically download the dbfile if not exists
    # this occurs only for the first time
    evaluate_states([initial_state()])

with st.sidebar:
    state_text = st.text_input("Game state", value="", placeholder="klz.h..H.ZLK0000001")

state = initial_state()
try:
    state = State.from_text(state_text)
except Exception as e:
    logger.warning("Failed to parse text: '%s'", str(e))

# current state
# logger.info("Current history length is %d", len(st.session_state["history"]))
# logger.info("Current history: %s", st.session_state["history"])
# logger.info("Current index: %s", st.session_state["index"])

#state = _current_state()
logger.info("Current state:\n %s", state)
c1, _, c2 = st.columns([4, 1, 7]) 
#img = state.to_image()
#c1.image(np.asarray(img), width=300)
#c = c1.container()
html = "\n".join(state.to_html(cellsize="100"))
with c1:
    components.html(html, width=400, height=600)
#    c.markdown(h, unsafe_allow_html=True)
# if c1.button("Back"):
#     st.session_state["index"] = max(-1, st.session_state["index"] - 1)

# if c1.button("Next"):
#     st.session_state["index"] = min(len(st.session_state["history"])-1, st.session_state["index"] + 1)


value = evaluate_states([state])[0]
c2.markdown(f"### State Value = {value}")

actions = state.valid_actions
next_states = [state.action_result(a) for a in actions]
next_states_text = [s.text for s, _ in next_states]
next_values = evaluate_states([s for s, _ in next_states])
paths = ["-".join(str(a) for a in optimal_path(s, depth=6, randomize=True)) for s, _ in next_states]
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