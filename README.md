# DDIT Code

Code for the DDIT project of Daniel Parak and Ansgar Schubert

## Instructions for running the program

This program requires only the common python packages _pandas_, _datetime_, _numpy_ and _matplotlib_. To execute the program, type

    python main.py <filename>

on the console, where \<filename> refers to a JSON file of the appropriate format in the _scenarios_ folder (without the folder and without file ending).
For the appropriate format, refer to _scenarios/scenario_test.json_. One can also type

    python main.py

on the console to run the program with the default test scenario (scenario_test). Accordingly, please do **not** remove this file.

## Structure of this repository

This repository contains the program code on the top level and associated data and input files in different subfolders:

### data

This folder contains all relevant input data that is not scenario-specific.
This includes the PV, load and price data for the simulation as well as the wheather data used in the process of calculating the PV data.

### scenarios

This folder contains the input files specifying the different scenarios, with one JSON-file per scenario.
The naming is as follows: scenario_<min_offer_quantity>_\<assets>, where \<assets> is one of three levels (low, medium, high),
in line with the description in the paper.

### output

All simulation output is written to this folder. Note that this folder is ignored by git, but will be created locally upon running the program.

### _old_code

This folder contains old code files that are no longer in use, but may be reused or adapted for future versions of the program.
