# -*- coding: utf-8 -*-

import os
import base64
from functools import lru_cache
from collections import namedtuple

# image as bytes or base64
PieceImages = namedtuple("Images", "hiyoko zou kirin tori lion")

@lru_cache(maxsize=128)
def load_images(directory, as_base64: bool=False, ext=("png", "jpg", "jpeg", "gif")):
    if not os.path.isdir(directory):
        raise ValueError(f"Directory '{directory}' does not exist")
    names = ("hiyoko", "zou", "kirin", "tori", "lion")
    files = os.listdir(directory)
    files = [f for f in files if f.lower().endswith(ext)]
    files = {n: [f for f in files if f.startswith(n)] for n in names}
    #print(files)
    # we require files are unique
    for n, f in files.items():
        if len(f) == 0:
            raise ValueError(f"No file for {n} is found in {directory}")
        if len(f) > 1:
            raise ValueError(f"Multiple files for {n} are found in {directory}: {f}")
    files = {n: os.path.join(directory, f[0]) for n, f in files.items()}
    images = {}
    for n, f in files.items():
        with open(f, "rb") as g:
            tmp = g.read()
            #print(n)
            #print(tmp)
            if as_base64:
                tmp = base64.b64encode(tmp).decode("utf8")
            images[n] = tmp
    return PieceImages(**images)

def load_predefined_images(name, as_base64: bool=False):
    directory = os.path.join(os.path.dirname(__file__), "pieces", name)
    return load_images(directory, as_base64=as_base64)