# -*- coding: utf-8 -*-

import math
import random
from logging import getLogger
from .evaluate import evaluate_states, MAXVALUE

logger = getLogger(__name__)

class DoubutsushogiAI:
    def __init__(self, backend="softmax", threshold: int=0, temperature: float=1.0):
        assert backend in ("softmax", "_greedy", "random")
        self.backend = backend
        self.threshold = threshold
        self.temperature = temperature

    def choose_action(self, state):
        if self.backend == "softmax":
            return _softmax_decision(state, threshold=self.threshold, temperature=self.temperature)
        elif self.backend == "greedy":
            return _greedy_decision(state)
        else:
            return _random_decision(state)

    def __call__(self, state):
        return self.choose_action(state)


def _greedy_decision(state, **kwargs):
    actions = state.valid_actions
    if len(actions) == 0:
        logger.warning("There is no action available for the state %s", state)
        return None
    next_states = [state.action_result(action) for action in actions]
    values = evaluate_states(next_states)
    action_values = list(zip(actions, values))   # list of (action, value) pairs
    logger.debug("Action-value pairs: %s", action_values)
    # filter out Nones
    action_values = [(a, v) for a, v in action_values if v is not None]
    if len(action_values) == 0:
        # no action with value evaluated, so return a random action
        logger.warning("There is not action properly evaluated for the state %s, so pick a random action", state)
        return random.choice(actions)
    # add tiny values to add some randomness to the case of ties
    values = [v + 1e-6*(random.random() - 0.5) for a, v in action_values]
    idx = values.index(max(values) if state.turn == 1 else min(values))
    return action_values[idx][0]
    
def _random_decision(state, **kwargs):
    actions = state.valid_actions
    if len(actions) == 0:
        logger.warning("There is no action available for the state %s", state)
        return None
    return random.choice(actions)
    
def _softmax_decision(state, threshold: int=0, temperature: float=1.0, **kwargs):
    # Pick an action by the softmax and the threshold rule
    # First, we filter out the actions whose value is lower than or equal to threshold
    #   if threshold = 0, then we will choose from winning moves
    #   if threshold is negative, then we will keep some losing moves
    # Second, we normalize the values to [-1, 1]
    # Third, we calculate the probabilities as: p_i = exp(v_i/t) / sum( exp(v_j/t) )
    #   where t is the temperature
    #   as t -> infinity, the decision approaches to the uniform across the choices
    #   as t -> +0, the decision approaches to the argmax of the value (pick the action with the largest value)
    #   in this sense, t is the parameter governing the randomness of the choice
    actions = state.valid_actions
    if len(actions) == 0:
        logger.warning("There is no action available for the state %s", state)
        return None
    next_states = [state.action_result(action) for action in actions]
    values = evaluate_states(next_states)
    action_values = list(zip(actions, values))   # list of (action, value) pairs
    logger.debug("Action-value pairs: %s", action_values)
    # filter out Nones
    action_values = [(a, v) for a, v in action_values if v is not None]
    if len(action_values) == 0:
        # no action with value evaluated, so return a random action
        logger.warning("There is not action properly evaluated for the state %s, so pick a random action", state)
        return random.choice(actions)
    if state.turn == 2:
        # flip the sign for second player
        values = [-v for v in values]
    # Keep the actions with values greater than the threshold
    # but if no action satisfy this condition, we keep all actions
    vmax = max(v for _, v in action_values)
    if vmax >= threshold:
        action_values = [(a, v) for a, v in action_values if v > threshold]
    else:
        logger.debug("No action has value greater than %s, so we keep all actions", threshold)
    logger.debug("Action-value pairs after filtering and transform: %s", action_values)
    actions, values = zip(*action_values)
    probs = _softmax(values, temperature=MAXVALUE*temperature)
    logger.debug("Probabilities to each action: %s", list(zip(actions, probs)))
    action = random.choices(actions, probs, k=1)[0]
    return action

def _softmax(values: list, temperature: float=1, normalize: bool=True)-> list:
    vmax = max(values)
    logits = [(v-vmax)/temperature for v in values]
    probs = [math.exp(l) for l in logits]
    if normalize:
        probs = [p/sum(probs) for p in probs]
    return probs 