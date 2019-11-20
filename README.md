# AlgoRun
## Automated Rietveld refinement code for FullProf software

This repo contains the source code for the automated rietveld strategy testing program that is built on top of [Fullprof](https://www.ill.eu/sites/fullprof/php/downloads.html) crystallographic structure refinement software based on the Rietveld crystallographic refinement method.

### Description

In order to explore the stability of a Rietveld refinement solution a python script “AlgoRun” was written that uses “FullProf”-s refinement engine. Originally “FullProf” can handle multiple file refinements (by applying the same *.pcr file to
many diffraction pattern files), however, it does not have a feature for refinement strategy comparison and stepwise execution of refinements on single and/or multiple datasets and using several crystallographic models. The code described in this thesis
extends “FullProf”-s functionality by accessing the refinement control file (*.pcr file) and directly modifying it programmaticaly. In this way one can test: 1) many variations of the *.pcr file onto one diffraction pattern, where the modification of the *.pcr file can be parametrized as well, 2) evaluation of many diffraction patterns all
with various, altered *.pcr files.

### Source code

The source code is written in python 2.7, migration to python3 is in preparation. 
The program does not require installation. 

Requirement:
- python packages
  - numpy 
  - matplotlib
  - pandas
- ["Fullprof"](https://www.ill.eu/sites/fullprof/php/downloads.html) sotfrare installed

The program is invoke by the `start_0254.py` from the command line and it is a interface for running all subroutines from the python files in the repo.

