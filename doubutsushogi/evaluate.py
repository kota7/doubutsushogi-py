# -*- coding: utf-8 -*-

import os
import bz2
import shutil
import hashlib
import sqlite3
import sys
import random
from urllib.request import urlopen
from logging import getLogger
from tempfile import TemporaryDirectory

logger = getLogger(__name__)
DB_BZ2_URL = "https://github.com/kota7/doubutsushogi-solve/releases/download/v1/doubutsu.db.bz2"
DB_BZ2_MD5_URL = "https://github.com/kota7/doubutsushogi-solve/releases/download/v1/doubutsu.db.bz2.md5"
DB_MD5_URL = "https://github.com/kota7/doubutsushogi-solve/releases/download/v1/doubutsu.db.md5"
DBFILE_ENVNAME = "DOUBUTSUSHOGI_DBFILE"
DB_SIZE = 1737416
DB_BZ2_SIZE = 552328
MAXVALUE = 10000

def _get_md5(filepath, blocksize=2**20):
    # compute md5 checksum of a file
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(blocksize)
            if len(data) == 0:
                break
            md5.update(data)
    return md5.hexdigest()

def _dbfilepath(filepath: str=None):
    return filepath or os.environ.get(DBFILE_ENVNAME) or "./doubutsu.db"

def _download_db(filepath: str=None):
    dbfile = _dbfilepath(filepath)
    logger.info("DB file: '%s'", dbfile)
    if os.path.isfile(dbfile):
        db_md5 = _get_md5(dbfile)
        logger.info("DB file '%s' exists, md5: '%s'", dbfile, db_md5)
        with urlopen(DB_MD5_URL) as u:
            db_md5_target = u.read().decode("utf8")
        logger.info("Target md5: '%s'", db_md5_target)
        if db_md5 == db_md5_target:
            logger.info("md5 matched, no need to download again")
            return
        logger.info("md5 not matched, will download again")

    with TemporaryDirectory() as dirname:
        bz2file = os.path.join(dirname, "tmp.db.bz2")
        logger.info("Start downloading bz2 file to '%s'", bz2file)
        with urlopen(DB_BZ2_URL) as u, open(bz2file, "wb") as b:
            shutil.copyfileobj(u, b)
        logger.info("Download finished")
        bz2_md5 = _get_md5(bz2file)
        with urlopen(DB_BZ2_MD5_URL) as u:
            bz2_md5_target = u.read().decode("utf8")
        logger.info("Verifying md5 for bz2 file: local: '%s' vs target: '%s'", bz2_md5, bz2_md5_target)
        if bz2_md5 != bz2_md5_target:
            logger.warning("MD5 for bz2 file not matched (local '%s' vs target '%s'), there could have been a problem in downloading",
                           bz2_md5, bz2_md5_target)
        
        logger.info("Decompressing bz2 file to '%s'", dbfile)
        os.makedirs(os.path.dirname(os.path.abspath(dbfile)), exist_ok=True)
        with bz2.open(bz2file, "rb") as f, open(dbfile, "wb") as g:
            shutil.copyfileobj(f, g)
        logger.info("Decompression finished")
    # verify md5 again
    db_md5 = _get_md5(dbfile)
    with urlopen(DB_MD5_URL) as u:
        db_md5_target = u.read().decode("utf8")
    logger.info("Verifying md5 for db file: local: '%s' vs target: '%s'", db_md5, db_md5_target)
    if db_md5 != db_md5_target:
        logger.warning("MD5 for bz2 file not matched (local '%s' vs target '%s'), there could have been a problem in downloading",
                       db_md5, db_md5_target)


def evaluate_states(states: list, dbfile: str=None)-> list:
    # values are from player1's viewpoint
    if len(states) == 0:
        return []
    weights = [3 - 2*s.turn for s in states]  # 1 if first player's turn, -1 if second player's turn
    indices = tuple(s.normalized_state_index for s in states)
    _dbfile = _dbfilepath(dbfile)
    logger.info("Evaluating using the db file at '%s'", _dbfile)
    if not os.path.isfile(_dbfile):
        print(f"DB file '{_dbfile}' is not found, will download", file=sys.stderr)
        _download_db(_dbfile)

    with sqlite3.connect(_dbfile) as conn:
        c = conn.cursor()
        q = """
        SELECT stateIndex, value FROM stateValues WHERE stateIndex IN ({})
        """.format(",".join("?" * len(indices)))
        c.execute(q, indices)
        values = dict(c.fetchall())  # maps stateIndex -> value
    
    out = [MAXVALUE if s.winning else values.get(idx) for idx, s in zip(indices, states)]
    out = [v if v is None else v*w for v, w in zip(out, weights)]
    return out

def optimal_path(state, depth: int=6, action_only: bool=True, randomize: bool=False, seed: int=None)-> list:
    # Return an optimal path up to the given depth (length)
    # If randomize is true, then actions are chosen randomly in case of ties
    out = []
    for i in range(depth):
        actions = state.valid_actions
        if len(actions) == 0:
            return out  # edge case where there is no action available
        next_states = [(a, state.action_result(a)) for a in actions]

        # # check for the winning move
        # for a, (_, status) in next_states:
        #     if status == state.turn:
        #         # can win in one move, return this action and done
        # if action_only:
        #         out.append(a)
        #         return out

        action_values = evaluate_states([s for _, (s, _) in next_states])
        if randomize:
            # add tiny random numbers for the randomness
            random.seed(seed)
            action_values = [None if v is None else v + 1e-6 * (random.random() - 0.5) for v in action_values]

        # find the "best" actions and its index
        action_values_no_none = [v for v in action_values if v is not None]
        optim = max(action_values_no_none) if state.turn == 1 else min(action_values_no_none)
        optim_idx = action_values.index(optim)
        action = actions[optim_idx]
        state = next_states[optim_idx][1][0]
        if action_only:
            out.append(action)
        else:
            out.append((action, state))
    return out
