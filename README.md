DOUBUTSUSHOGI
=============
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://kota7-doubutsushogi-py-streamlitapp-fyc9on.streamlit.app/)
A [doubutsushogi (animal chess)](https://en.wikipedia.org/wiki/D%C5%8Dbutsu_sh%C5%8Dgi) analyzer.


## Install

```shell
# from pypi
pip3 install doubutsushogi

# or from github
git clone https://github.com/kota7/doubutsushogi-py.git
pip3 install -U ./doubutsushogi-py
```

## Some usage

```python
from doubutsushogi.game import State

# game state at the beginning
s = State.initial_state()
print(s)
#  ------- 
# | k l z |
# | . h . |
# | . H . |
# | Z L K |
#  ------- 
# H: 0 Z: 0 K: 0
# h: 0 z: 0 k: 0
# Player 1's turn
```

```python
from doubutsushogi.evaluate import evaluate_states

# numeric evalutation of the state
# positive value indicates that the first player is winning, 
# negative the second player,
# and zero means a tie.
evaluate_states([s])
#[-4612]
```


## Launch streamlit app 

An interactive app is deployed on the [Streamlit Cloud]((https://kota7-doubutsushogi-py-streamlitapp-fyc9on.streamlit.app/)).
To run the app on the computer locally, run the following:

```shell
pip3 install -U streamlit-doubutsushogi
python3 -m streamlit run streamlit/app.py
```