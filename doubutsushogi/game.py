# -*- coding: utf-8 -*-

import os
import sys
from logging import getLogger
from tempfile import TemporaryDirectory

from .images import load_images, load_predefined_images
logger = getLogger(__name__)

EMPTY = 0
HIYOKO = 1
ZOU = 2
KIRIN = 3
TORI = 4
LION = 5

LETTERS = ".HZKNLlnkzh"

PRISONER_INDEX = 12   # from index for the prisoners

class Action:
    def __init__(self, piece, index_from, index_to):
        assert piece in (HIYOKO, ZOU, KIRIN, LION, TORI)
        assert index_from >= 0 and index_from <= 12
        assert index_to >= 0 and index_to <= 12
        self.piece = piece
        self.index_from = index_from
        self.index_to = index_to

    @staticmethod
    def _index_to_coord(index):
        if index == PRISONER_INDEX:
            # using captured piece
            return "*"
        row, col = int(index/3), index % 3
        row = chr(ord("a") + row)
        col = 1 + col
        return f"{col}{row}"

    def __str__(self):
        piece_name = LETTERS[self.piece]
        coord_from = self._index_to_coord(self.index_from)
        coord_to = self._index_to_coord(self.index_to)
        #return f"{piece_name}{coord_from}-{coord_to}"
        return f"{piece_name}{coord_to}({coord_from})"

    def __repr__(self):
        return f"Action({self.piece}, {self.index_from}, {self.index_to})"

    def __eq__(self, another):
        if not isinstance(another, Action):
            logger.warning("Cannot compare an action against '%s' of type %s", another, type(another))
            return None
        return (self.piece == another.piece and
                self.index_from == another.index_from and
                self.index_to == another.index_to)

class State:
    def __init__(self, data):
        assert len(data) == 19  # 12 board + 3*captured + turn
        assert all(isinstance(v, int) for v in data)
        self._data = tuple(data)
 
    def __str__(self):
        out = " ------- "
        for i in range(4):
            out += f"\n| "
            out += " ".join(LETTERS[v] for v in self._data[i*3:(i+1)*3])
            out += " |"
        out += "\n ------- \n"
        out += " ".join(f"{LETTERS[k+1]}: {v}" for k, v in enumerate(self._data[12:15]))
        out += "\n"
        out += " ".join(f"{LETTERS[-k-1]}: {v}" for k, v in enumerate(self._data[15:18]))
        out += "\n"
        out += "Player 1's turn" if self.turn == 1 else "Player 2's turn"
        return out

    def __repr__(self):
        return f"State{self._data}"

    def __eq__(self, another):
        if not isinstance(another, State):
            logger.warning("Cannot compare a state against '%s' of type %s", another, type(another))
            return None
        return all(a==b for a, b in zip(self._data, another._data))

    @property
    def board(self):
        return self._data[:12]
    
    def captured(self, player):
        # player 1 or 2
        i = 12 + 3*(player-1)
        return self._data[i:i+3]

    @property
    def turn(self):
        return self._data[-1]

    @property
    def flipped(self):
        data = list(self._data)
        data[:12] = [-v for v in reversed(data[:12])]
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

    @staticmethod
    def from_index(index, turn: int=1):
        data = [None]*18 + [turn]
        for i in range(18):
            data[i] = (index % 11) - 5;
            index //= 11;
        for i in range(12, 18):
            data[i] = index % 3;
            index //= 3;
        return State(data)

    @staticmethod
    def from_text(text):
        # text in the form
        # "klz.h..H.ZLK0000001"
        # dots could be spaces 
        # '\n' and '\r' are ignored
        text = text.replace("\n", "").replace("\r", "").replace(" ", ".")
        if len(text) == 18:
            text += "1"
        if len(text) != 19:
            raise ValueError(f"text length must be 19, but '{text}'")
        mappings = {
            ".": EMPTY,
            "h": -HIYOKO, "z": -ZOU, "k": -KIRIN, "n": -TORI, "l": -LION,
            "H": HIYOKO, "Z": ZOU, "K": KIRIN, "N": TORI, "L": LION,
            "0": 0, "1": 1, "2": 2
        }
        data = tuple(mappings.get(t) for t in text)
        for i, (t, d) in enumerate(zip(text, data)):
            if d is None:
                raise ValueError(f"Failed to parse '{t}' at position {i}")
        return State(data)

    @property
    def text(self):
        out = [LETTERS[v] for v in self._data[:12]] + [str(v) for v in self._data[12:]]
        return "".join(out)

        
    @property
    def normalized_state_index(self):
        if self.turn != 1:
            return self.flipped.normalized_state_index
        s1 = self.state_index
        s2 = self.mirrored.state_index
        return min(s1, s2)

    @staticmethod
    def initial_state():
        return initial_state()

    def action_result(self, action):
        return after_state(self, action)

    @property
    def valid_actions(self)-> list:
        return valid_actions(self)

    @property
    def status(self)-> int:
        # Returns:
        #   0: not finished
        #   1: won by first player
        #   2: won by second player
        # We won't (can't) check for draws (sennichite)
        return _game_status(self)

    @property
    def winning(self)-> bool:
        # Check if the player can win the game in one step
        for a in self.valid_actions:
            s = self.action_result(a)
            if s.status == self.turn:
                logger.debug("Winning with '%s' from state:\n%s", a, self)
                return True
        return False

    def to_image(self, **kwargs):
        # todo: make arguments more explicit
        return _state_image(self, **kwargs)
    
    def to_html(self, **kwargs):
        # todo: make arguments more explicit
        return _state_html(self, **kwargs)


def _reachable_indices(piece, from_index)-> list:
    #print(piece, from_index)
    # returns the indices where the given piece can move
    # from the from_index in one step
    if piece < 0:
        # flip the player and find the indices from first player's viewpoint
        # then flip the indices
        return [11-c for c in _reachable_indices(-piece, 11-from_index)]

    # we can assume it is the first player's turn
    if not piece in (HIYOKO, ZOU, KIRIN, TORI, LION):
        # we may add warning
        return []

    if piece == HIYOKO:
        if from_index < 3:
            return []  # at the first row, can go nowhere
        return [from_index-3]
    elif piece == ZOU:
        out = []
        if from_index % 3 != 0:
            if from_index >= 3:
                out.append(from_index - 4)
            if from_index < 9:
                out.append(from_index + 2)
        if from_index % 3 != 2:
            if from_index >= 3:
                out.append(from_index - 2)
            if from_index < 9:
                out.append(from_index + 4)
        return out
    elif piece == KIRIN:
        out = []
        if from_index >= 3:
            out.append(from_index - 3)
        if from_index < 9:
            out.append(from_index + 3)
        if from_index % 3 != 0:
            out.append(from_index - 1)
        if from_index % 3 != 2:
            out.append(from_index + 1)
        return out
    elif piece == TORI:
        out = []
        if from_index >= 3:
            out.append(from_index - 3)
            if from_index % 3 != 0:
                out.append(from_index - 4)
            if from_index % 3 != 2:
                out.append(from_index - 2)
        if from_index < 9:
            out.append(from_index + 3)
        if from_index % 3 != 0:
            out.append(from_index - 1)
        if from_index % 3 != 2:
            out.append(from_index + 1)
        return out
    else:
        # lion = zou + kirin
        return _reachable_indices(ZOU, from_index) + _reachable_indices(KIRIN, from_index)

def valid_actions(state: State)-> list:
    # returns all available actions from the given state
    actions = []
    # use pieces on the board
    for i, piece in enumerate(state.board):
        if piece * (3 - 2*state.turn) <= 0:
            # if this condition is true, then cannot move this piece
            # if state.turn=1, then equivalent to piece <= 0
            # if state.turn=2, then equivalent to piece >= 0
            continue
        indices = _reachable_indices(piece, i)
        #print(indices)
        for j in indices:
            if piece * state.board[j] <= 0:
                # not the same sign, i.e. own piece is not on the target cell
                actions.append(Action(abs(piece), i, j))
    # use captured pieces
    empty_indices = [i for i, piece in enumerate(state.board) if piece == EMPTY]
    for k, num in enumerate(state.captured(state.turn)):
        piece = k + 1  # 0,1,2 -> HIYOKO,ZOU,KIRIN
        if num <= 0:
            continue
        for j in empty_indices:
            actions.append(Action(piece, PRISONER_INDEX, j))
    return actions

def initial_state():
    return State([-KIRIN, -LION, -ZOU, EMPTY, -HIYOKO, EMPTY,
                  EMPTY, HIYOKO, EMPTY, ZOU, LION, KIRIN,
                  0, 0, 0, 0, 0, 0, 1])

def after_state(state: State, action: Action)-> State:
    # return the state resulted from the given action played on the given state
    # do not check for the validity of the action
    if action.index_from == PRISONER_INDEX:
        # using a captured piece
        data = list(state._data)
        data[11 + action.piece + 3*(state.turn-1)] -= 1
        # turn-1 = 0 if first player, 1 if second player
        # adding 3 to the index for the second player
        data[action.index_to] = action.piece * (3 - 2 * state.turn)
        data[-1] = 3 - data[-1]  # turn 1 -> 2, 2 -> 1
        return State(data)
    # moving a piece on the board
    data = list(state._data)
    if data[action.index_to] not in (EMPTY, LION, -LION):
        # this piece will become a prisoner
        piece = abs(data[action.index_to])
        if piece == TORI:
            piece = HIYOKO
        data[11 + piece + 3*(state.turn-1)] += 1
    piece = action.piece
    index_to = action.index_to
    if piece == HIYOKO and ((state.turn==1 and action.index_to < 3) or (state.turn==2 and action.index_to >= 9)):
        piece = TORI  # promotion
    data[action.index_to] = piece * (3 - 2 * state.turn)
    data[action.index_from] = EMPTY
    data[-1] = 3 - data[-1]  # turn 1 -> 2, 2 -> 1
    return State(data)

def _is_try(state):
    # check if the opponent player has successfully tried
    if state.turn != 1:
        return _is_try(state.flipped)
    # first player's turn
    # check the opponent lion
    if -LION not in state.board[9:12]:
        return False
    # check if we can capture the opponent lion
    index_op_lion = state.board.index(-LION)
    for a in state.valid_actions:
        if a.index_to == index_op_lion:
            # there is an action that can capture the lion
            return False
    return True

def _game_status(state: State)-> int:
    # check the current game status
    if LION not in state.board:
        return 2
    if -LION not in state.board:
        return 1

    # check if the opponent lion has tried
    if _is_try(state):
        return 3 - state.turn  # won by the opponent

    # check if there is no action available
    if len(state.valid_actions) == 0:
        return 3 - state.turn  # won by the opponent

    # winning conditions are not satisfied, so game is not finished yet
    return 0


def _state_html(state: State, imagename: str=None, imagedir: str=None,
                bordersize="2px", bordercolor="#424242", bordertype="solid",
                boardcolor="#d1edf2", cellsize="70",
                captured_imgsize="30", captured_color="#efefef"):
    if imagedir is not None:
        images = load_images(imagedir, as_base64=True)
    else:
        images = load_predefined_images(imagename or "emoji1", as_base64=True)
    
    def _cell_img(value, **kwargs):
        if value == EMPTY:
            return ""
        piece = ["hiyoko", "zou", "kirin", "tori", "lion"][abs(value)-1]
        rotate = (value < 0)
        properties = kwargs.copy()
        properties["src"] = f"data:image/png;base64,{getattr(images, piece)}"
        if rotate:
            properties["style"] = "transform:rotate(180deg);" + properties.get("style", "")
        return "<img {}>".format(" ".join(f'{k}="{v}"' for k, v in properties.items()))

    board = """
    <table style="table-layout: fixed;">
    <tr><td {tdprop}>{}</td><td {tdprop}>{}</td><td {tdprop}>{}</td></tr>
    <tr><td {tdprop}>{}</td><td {tdprop}>{}</td><td {tdprop}>{}</td></tr>
    <tr><td {tdprop}>{}</td><td {tdprop}>{}</td><td {tdprop}>{}</td></tr>
    <tr><td {tdprop}>{}</td><td {tdprop}>{}</td><td {tdprop}>{}</td></tr>
    </table>
    """.format(
        *[_cell_img(v, width=cellsize, height=cellsize) for v in state.board],
        tdprop=f'style="border: {bordersize} {bordercolor} {bordertype}; text-align: center; vertical-align: middle; aspect-ratio: 1" bgcolor={boardcolor} width="{cellsize}" height="{cellsize}" align="center" valign="middle"'
    )
    
    def _captured(values):
        args = []
        for i in range(3):
            args.append(_cell_img(i+1, width=captured_imgsize))
            args.append(values[i])
        out ="""
        <table>
        <tr><td bgcolor={color}>{} <span>{}</span></td><td bgcolor={color}>{} <span>{}</span></td><td bgcolor={color}>{} <span>{}</span></td></tr>
        </table>
        """.format(*args, color=captured_color)
        return out
    mover = f"<span>Next mover: {state.turn}</span>"
    return [_captured(state.captured(2)), board, _captured(state.captured(1)), mover]

def _state_image(state: State, padding=10, threshold=0.99, **kwargs):
    # we take screenshot of the HTML
    # this is crude implementation
    # we may refactor this function
    from htmlwebshot import WebShot
    from PIL import Image
    import numpy as np
    html = "\n".join(_state_html(state, **kwargs))
    shot = WebShot()
    with TemporaryDirectory() as dirname:
        imgfile = os.path.join(dirname, "tmp.png")
        shot.create_pic(html=html, quality=100, output=imgfile)
        img = Image.open(imgfile).convert("RGB")
    # crop white rows and cols
    a = np.asarray(img)
    white_flag = (a == 255).min(axis=2)  # todo. we may better to allow some deviation from white
    tmp = np.where(white_flag.mean(axis=0) <= threshold)[0]
    i1 = np.clip(min(tmp) - padding, 0, a.shape[0])
    i2 = np.clip(max(tmp) + padding, 0, a.shape[0])
    tmp = np.where(white_flag.mean(axis=1) <= threshold)[0]
    j1 = np.clip(min(tmp) - padding, 0, a.shape[1])
    j2 = np.clip(max(tmp) + padding, 0, a.shape[1])
    img = Image.fromarray(a[j1:j2,i1:i2])

    return img