DOUBUTSUSHOGI
=============
[![](https://badge.fury.io/py/doubutsushogi.svg)](https://badge.fury.io/py/doubutsushogi)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://kota7-streamlit-doubutsushogi-appstreamlit-app-weir3f.streamlit.app/)

A [doubutsushogi (animal chess)](https://en.wikipedia.org/wiki/D%C5%8Dbutsu_sh%C5%8Dgi) analyzer.

- This project uses the complete state values calculated in [doubutsushogi-solve](https://github.com/kota7/doubutsushogi-solve/releases) project.
- An interactive analyzer app is deployed on the [Streamlit Cloud](https://github.com/kota7/doubutsushogi-solve/releases).

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

# Numeric evalutation of the state
# The first run takes some time (typically a few minutes) to downloading database from https://github.com/kota7/doubutsushogi-solve/releases
evaluate_states([s])
#[-4612]
# Note: positive value indicates that the first player is winning, 
#       negative the second player,
#       and zero means a tie.
```