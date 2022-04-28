#!/bin/bash
python checkdeps.py
python src/bitmessagemain.py -t
python -bm tests
