#!/usr/bin/python3

#------------------------------------------
# Modify the uncommented lines accordingly
#------------------------------------------

# number of datasets simoultaneously refined; effectivelly it is the number of threads in multiprocessing
n_cpu=2


# toggle output saving 
# [0] store every refinement step output files
# [1] store only the `pcr` and log.log for every refinement step
#
# Note: option [0] will consume more hard drive space
switch=1
