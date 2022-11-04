# -*- coding: utf-8 -*-

EMPTY = 0
HIYOKO = 1
ZOU = 2
KIRIN = 3
TORI = 4
LION = 5

LETTERS = " HZKNLlnkzh"

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
            return "**"
        row, col = int(index/3), index % 3
        row = chr(ord("a") + row)
        col = 1 + col
        return f"{col}{row}"

    def __str__(self):
        piece_name = LETTERS[self.piece]
        coord_from = self._index_to_coord(self.index_from)
        coord_to = self._index_to_coord(self.index_to)
        return f"{piece_name}{coord_from}-{coord_to}"

    def __repr__(self):
        return f"Action({self.piece}, {self.index_from}, {self.index_to})"


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

    @property
    def board(self):
        return self._data[:12]
    
    def captured(self, player):
        # player 1 or 2
        i = 12 + (player-1)*2
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

    def normalized_state_index(self):
        s1 = self.state_index
        s2 = self.mirrored.state_index
        return min(s1, s2)

    @staticmethod
    def initial_state():
        return State([-KIRIN, -LION, -ZOU, EMPTY, -HIYOKO, EMPTY,
                      EMPTY, HIYOKO, EMPTY, ZOU, LION, KIRIN,
                      0, 0, 0, 0, 0, 0, 1])

    def action_result(self, action)-> tuple:
        # returns a tuple of
        #   - the new state resulted from the given action
        #   - status (1: won by first player, 2: won second player, 0: not finish)
        state = after_state(self, action)
        value = _game_status(state)
        return state, value

    @property
    def valid_actions(self)-> list:
        return valid_actions(self)

    @property
    def status(self)-> 1:
        # Returns:
        #   0: not finished
        #   1: won by first player
        #   2: won by second player
        # We won't (can't) check for draws (sennichite)
        return _game_status(self)

def _reachable_indices(piece, from_index, turn=1)-> list:
    #print(piece, from_index, turn)
    # returns the indices where the given piece can move
    # from the from_index in one step
    if turn != 1:
        # flip the player and find the indices from first player's viewpoint
        # then flip the indices
        return [11-c for c in _reachable_indices(piece, 11-from_index, turn=1)]

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
        return _reachable_indices(ZOU, from_index, turn=turn) + _reachable_indices(KIRIN, from_index, turn=turn)

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
        indices = _reachable_indices(piece, i, state.turn)
        #print(indices)
        for j in indices:
            if piece * state.board[j] <= 0:
                # not the same sign, i.e. own piece is not on the target cell
                actions.append(Action(piece, i, j))
    # use captured pieces
    empty_indices = [i for i, piece in enumerate(state.board) if piece == EMPTY]
    for piece in state.captured(state.turn):
        if piece <= 0:
            continue
        for j in empty_indices:
            actions.append(Action(piece, PRISONER_INDEX, j))
    return actions

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
    if data[action.index_to] != EMPTY:
        # this piece will become a prisoner
        data[11 + abs(data[action.index_to]) + 3*(state.turn-1)] += 1
    data[action.index_to] = action.piece
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

    # winning conditions are not satisfied, so game is not finished yet
    return 0