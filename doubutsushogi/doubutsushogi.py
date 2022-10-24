# -*- coding: utf-8 -*-

EMPTY = 0
HIYOKO = 1
ZOU = 2
KIRIN = 3
LION = 4
TORI = 5

LETTERS = " HZKLNnlkzh"

class State:
    def __init__(self, data):
        assert len(data) == 19  # 12 board + 3*captured + turn
        assert all(isinstance(v, int) for v in data)
        self._data = tuple(data)

    def __str__(self):
        out = " ------- "
        for i in range(4):
            out += "\n| "
            out += " | ".join(LETTERS[v] for v in self._data[i*3:(i+1)*3])
            out += " |"
        out += "\n "
        out += " ".join(f"{LETTERS[k+1]}: {v}" for k, v in enumerate(self._data[12:15]))
        out += "\n "
        out += " ".join(f"{LETTERS[-k-1]}: {v}" for k, v in enumerate(self._data[15:18]))
        out += "\n"
        out += "Player 1's turn" if self._data[-1] == 1 else "Player 2's turn"
        return out
    
    def __repr(self):
        return str(self)

    @property
    def board(self):
        return self._data[:12]
    
    @property
    def captured(self, player):
        # player 1 or 2
        i = 12 + (player-1)*2
        return self._data[i:i+3]

    @property
    def turn(self):
        self._data[-1]

    @property
    def flipped(self):
        data = list(self._data)
        data[:12] = reversed(data[:12])
        data[12:15], data[15:18] = data[15:18], data[12:15]
        data[-1] = 3 - data[-1]  # 1 -> 2, 2 -> 1
        return State(data)

    @property
    def mirrored(self):
        data = list(self._data)
        for i in [0,3,6,9]:
            data[i], data[i+2] = data[i+2], data[i]
        return State(data)

    @property
    def state_index(self):
        # state with the mover as the first-player
        x = self._data if self.turn == 1 else self.flipped._data
        # calculate the index by the rule
        idx = 0
        base = 1
        for v in x[:12]:
            idx += base*(v+5)
            base *= 11
        for v in x[12:18]:
            idx += base*v
            base *= 3
        return idx

    def normalized_state_index(self):
        s1 = self.state_index
        s2 = self.mirrored.state_index
        return min(s1, s2)

