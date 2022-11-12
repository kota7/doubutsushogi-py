# -*- coding: utf-8 -*-

import setuptools
import os
import sys

# get local readme
readmefile = os.path.join(os.path.dirname(__file__), "README.md")
with open(readmefile) as f:
    readme = f.read()
# get version number from the package __init__.py file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "doubutsushogi")))
from doubutsushogi import __version__ as version

setuptools.setup(
    name='doubutsushogi',
    version=version,
    description='Doubutsu shogi AI',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Kota Mori', 
    author_email='kmori05@gmail.com',
    url='https://github.com/kota7/doubutsushogi-py',
    #download_url='',

    packages=['doubutsushogi'],
    install_requires=["htmlwebshot", "pillow"],
    test_require=[],
    package_data={"doubutsushogi": ["pieces/*/*.png"]},
    entry_points={},

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha'

        # Indicate who your project is intended for
        ,'Intended Audience :: Science/Research'
        ,'Topic :: Scientific/Engineering :: Artificial Intelligence'
        
        ,'Programming Language :: Python :: 3.6'
        ,'Programming Language :: Python :: 3.7'
    ],
    test_suite='tests'
)
