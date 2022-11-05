# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='doubutsushogi',
    version='0.0.1',
    description='Doubutsu shogi AI',
    author='Kota Mori', 
    author_email='kmori05@gmail.com',
    #url='',
    #download_url='',

    packages=find_packages(),
    install_requires=[],
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
