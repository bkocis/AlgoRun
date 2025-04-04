#!/usr/bin/python3

import os
import sys
sys.path.append(os.getcwd())
import library as lb
import strategy_results as sr
#import step_parametrisation as sp


while True:
	print("""
	Choose a task:

	[1] run refinements (assumes all files and folders are set) - returns a database
	[2] evaluation using new rules (optionally generating new database) 
	[3] parametrisation
	[4] setup folders and files for refinement 
	[5] scramble and make strategies from 'refinement step blocks' in '_blocks' folder
	[6] help

	[q] quit

	enter [1-5 or q]
	""")


	a=input()
	if a=='1':
		lb.multiple_file_run()
		break
	elif a=='2':
		print("""
			 [a] Apply rules on existing database (will ask for a database name)
			 [b] Build a new database from results and apply rules?
			 [q] quit
			 """)
		b=input()
		while True:
			if b=='a':
				if os.path.isdir('_results'):
					jsonName= lb.list_of_databases()
					lb.set_of_rules_sort_find().apply_rules(jsonName)
				else:
					print('ups...no "_resutls" folder!')
					pass
				break
			elif b=='b':
				jsonName = sr.get_results()
				lb.set_of_rules_sort_find().apply_rules(jsonName)
				break
			elif b=='q':
				break
			else:
				print('enter [a,b, or q]')
				b=input()
		break
	elif a=='3':
		#sp.run_parametrisation()
		pass
		break	

	elif a=='4':
		pass
		break
	
	elif a=='5':
		print('Any previous strategies will be removed and overwritten. \n [c] Continue \n [q] quit')
		a=input()
		if a=='c':
			lb.strategy_maker()
			print('Done! \n [y] Go back to main menu? \n [q] Quit')
			a=input()
			if a=='y':
				pass
			elif a=='q':
				break
		elif a=='q':
			break
		else:
			print('enter [c or q]')
			a=input()
	
	elif a=='6':
		pass
		break
	
	elif a=='q':
		print('bye')
		break
		sys.exit()
	
	else:
		print('enter [1-5 or q]')
		a=input()
	
