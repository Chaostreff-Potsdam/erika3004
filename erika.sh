#!/usr/bin/env bash
# PYTHON_ARGCOMPLETE_OK
# ^ is about auto-completion, see https://argcomplete.readthedocs.io/en/latest/#global-completion

# Forward all to Python Command Line Interface
# e.g.
#
# * help output:
# ./erika.sh -h
# ./erika.sh render_ascii_art -h
#
# * demo output
# ./erika.sh demo -p "COM3"
# ./erika.sh demo -p "/dev/ttyACM0"
#
# * simulation + "on-screen cinematics"
# ./erika.sh render_ascii_art -d -f ./tests/test_resources/test_ascii_art.txt -s PerpendicularSpiralInward 
# ./erika.sh render_ascii_art -d -f ./tests/test_resources/test_ascii_art.txt -s ArchimedeanSpiralOutward  
# ./erika.sh render_ascii_art -d -f ./tests/test_resources/test_ascii_art.txt -s RandomDotFill  
#
# * tic tac toe game
# ./erika.sh tictactoe -p "/dev/ttyACM0"
# ./erika.sh tictactoe -d
#
# * real output
# ./erika.sh render_ascii_art -p "COM3" -f ./tests/test_resources/test_ascii_art_small.txt
# ./erika.sh render_ascii_art -p "/dev/ttyACM0" -f ./tests/test_resources/test_ascii_art_small.txt -s PerpendicularSpiralInward
python3 -m erika.cli $@