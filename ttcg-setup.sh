#!/bin/bash

# This script is still being tested and may still be incomplete.
# This script will run the setup needed for the TTCG project!
if [[ $(uname) == Linux ]]; then
    echo "Running setup for Linux!"
    sudo apt-get install python3
    sudo apt-get install python3-pip
    sudo apt-get install python3-tk
    sudo apt-get install python3-pil python3-pil.imagetk
    pip3 install regex
    pip3 install matplotlib
    pip3 install pytest
    pip3 install pandas
    pip3 install csv
    pip3 install argparse
    pip3 install pytest
    pip3 install tqdm
    pip3 install sv-ttk

else
    echo "Setup not yet configured for your system!"
fi
