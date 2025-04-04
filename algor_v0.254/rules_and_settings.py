#----------------------------------------
# Modify the uncommented lines according
#----------------------------------------

# Extraction of results -----------------------------------------------
# values set for the extraction of results
phase=1
pattern=1

# list of Miller indices for apparent sizes extracted from the mic file
# check for excluded region consistancy - don't try to evaluate reflection that is outside the excluded region

hkl=[[0,0,2],[1,1,2],[0,1,0],[1,1,0],[0,1,1]]

# list of rules [keep the """ in the beginning and end]
rules="""
2 >= p1Biso >= 0 
2 >= o1Biso >=0
2 >= o2Biso >=0
2 >= o3Biso >=0
1.58 >= p1-o1 >= 1.50
1.58 >= p1-o2 >= 1.50
1.58 >= p1-o3 >= 1.50
"""

# number of top results to show
top_list_n = 5

