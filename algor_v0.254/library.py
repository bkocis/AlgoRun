#!/usr/bin/python
import numpy as np
import pandas as pa
from sys import exit,stdout
import os,shutil,subprocess,time,re
from  multiprocessing import Process
from distutils.dir_util import mkpath

import config
import strategy_results
#import rules_and_settings
import lock_by_ctrl_scheme


def greeting_message():
	print """
	' ____________________________________________________ '
	'|                                                    |'
	'|               AlgorRun --version 0.253             |'
	'| 		       22-04-2017                     |'
	'|____________________________________________________|'
	'|New in this version:                                |'
	'| - libraries modified and start.py added            |'
	'| - `rules_and_settings` modified	              |'
	'|					              |'
	'|Bug fixes:				              |'
	'| - df.concatenation error on repeating column names |'
	'| - subprocess and os.mkdir conflict                 |'
	'| - at case of `*new`, change the code under Pcr     |'
	'|   from 2 to 1  			              |'
	'|					              |'
	'|  					              |'
	'|Remaining tasks:				      |'	
	'| - add block_strgary list in order to know which    |'
	'|	blocks form which strategy	              |'
	'| - change config.py to config.config readout        |'
	'| - '_pcr_folder'                                    |'
	'| - result organizer insted ot R_Chi2 bash script    |'
	'|____________________________________________________|'
	"""
def time_me(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '\n [The refinements took %0.3f minutes ]' % ((time2-time1)*1000.0/60.0)
        return ret
    return wrap

def step_organizer():
	"""
	Description:
		organizes the steps numbering in the `*ctrl` files 

	Details:
		search for the "#", assign them a number of occurrence and 
		then exchange the whole line with a syntax:
		"#step_"+i 
		where i is the number of occurrence of the next #step
	"""
	#a=[i for i in os.listdir(os.getcwd()) if i.split('.')[-1]=='ctrl'][0]
	
	a=os.listdir('_strategies')
	for ii in a:
		s='./_strategies/'+ii
		f=open(s,'r')
		d=f.readlines()
		f.close()
		t=1
		for i in range(0,len(d)):
			if d[i].find('#')>-1:
				d[i]="#step_"+str(t)+'\n'
				t=t+1
		f=open(s,'w')
		f.writelines(d)
		f.close()
	# return the line: 
	print "\n `*.ctrl` file is organized\n" 

def check_folders():
	"""
	Description:
		function that checks if the `_refinements` folder exist or not. It is needed in case multiple 
		refinemnt sessions are conducted over the same data and strategies. it makes sure that the 
		refinements stored in proper folder.
		
	"""
	if os.path.isdir('_refinements')==True:
		# overwrite of make new
		print 'A refinement folder already exist. \n [a] Overwrite? \n [b] Rename existing one.'
		answer=raw_input()
		while True:
			if answer=='a':
				# remove old, create new
				print '...preparing folder [this way take a while]'
				shutil.rmtree('_refinements', ignore_errors=True)
				print 'finished'
				os.mkdir('_refinements')
				break
			elif answer=='b':
				print 'enter name:'
				addName=raw_input()
				os.rename('_refinements','_refinements'+'_'+addName)
				os.mkdir('_refinements')
				break
			elif answer=='q':
				break
			else:
				print "enter [y,n,q]"
				answer=raw_input()
	else:
		os.mkdir('_refinements')

def list_of_databases():
	"""
	Description:
		A function for the `start.py` module, that lists out available databases in the `_results` folder 
		uppon executing the option of to evaluate a database.
	Returns:
		the name of the selected database

	"""
	h=os.getcwd()
	l=os.listdir('_results')
	l.sort()
	
	print 'enter database name from the "_results" folder:'
	#if len(l)>0:

	def pipi(i,li):
		print '['+str(i)+']'+'  '+ li
	ll=[pipi(i,l[i]) for i in range(0,len(l))]
	
	print "select database:"
	a=raw_input()

	os.chdir('_results')
	selected_db=os.path.abspath(l[int(a)])
	os.chdir(h)
	print selected_db
	return selected_db
#	else:
#		print '...folder empty'
#		return '0'
#

def run_multiple_files(n):
	"""
	Description:
		the function takes all data files all strategies and for each runs the refinement.

	Parameters: 
		n is the number of the simultaneously running refinements - it is the number of simultaneous processes 
		n can be more then 1; giving higher number than the number of cores is not advised. 
		n is given in the config.py file 
	"""
	

	dat=os.listdir('./_data_files/')
	dat.sort()
#	pcr=[i for i in os.listdir(os.getcwd()) if i.split('.')[-1]=='pcr'][0]
	pcr=os.listdir('./_models/')
	pcr.sort()

	ctrl=os.listdir('./_strategies/')
	ctrl.sort()

#	for ii in ctrl:
#		s='./_strategies/'+ii
#		shutil.copy(s,os.getcwd())
#		c=0;b=[]
#		for i in dat:
#			c=c+1
#			t='./_data_files/'+i
#			shutil.copy(t,os.getcwd())
#
#			p1=Process(target=algorRun, args=(pcr,i,ii,))
#			p1.start()
#			b.append(p1)
#			# limiting condition of n-the number of cpu-s == simultaneous threads
#			if c==n:
#				p1.join()
#				b=[]
#				c=0
#		# join will wait for the first bunch to finish
#		p1.join()
	c2=0;b2=[]
	for iii in pcr:
		o='./_models/'+iii
		shutil.copy(o,os.getcwd())	
		c1=0;b1=[]
		for ii in ctrl:
			s='./_strategies/'+ii
			shutil.copy(s,os.getcwd())
			c=0;b=[]
			for i in dat:
				c=c+1
				t='./_data_files/'+i
				shutil.copy(t,os.getcwd())

				p1=Process(target=algorRun, args=(iii,i,ii,))
				p1.start()
				b.append(p1)
				# limiting condition of n-the number of cpu-s == simultaneous threads
				if c==n:
					p1.join()
					b=[]
					c=0
				time.sleep(0.1)
			c1=c1+1
			b1.append(p1)
			#if c1==n or c==n:
			if c1+c==n:
				p1.join()
				b1=[]
				c1=0
			#time.sleep(0.1)
		c2=c2+1
		b2.append(p1)
		#if c2==n or c1==n or c==n:
		if c2+c1==n:
			p1.join()
			b2=[]
			c2=0
		# join will wait for the first bunch to finish
		p1.join()	

	[os.remove(i) for i in dat]
	[os.remove(i) for i in ctrl]
	[os.remove(i) for i in pcr]

@time_me
def multiple_file_run():
	"""
	Description:
		Runs the refinement by encapsulating the:

		$ python algorRun.py .PCR .DAT .CTRL 

		Sequence. 

	Details:
		Remarks for the windows version:

		DON'T USE WHITESPACE IN THE PATH WHEN THE shell=True is on ! 
		the shell=True just be on of the argument running fullprof 
		so NO WHITESPACE IN PATH! 

		The path to the 'algorRun.py' needs to be given here only 
		once. At the execution of the code 'multiplt_file_run.py' is 
		only needed to be pointed every time to the folder where 
		it's located. 
	"""
	greeting_message()
	
	# check the `*ctrl` file and order the steps 
	step_organizer() 
	check_folders()	

	# set the number of simultaneous datasets evaluated 
	n_cpu=config.n_cpu

	run_multiple_files(n_cpu)


	# if it is not able to do the get_result -> capture the error and print 
	# to jsonName we assign the output of the get_results method
	jsonName=strategy_results.get_results() 
	print jsonName

	# apply the rules immediately 
	#set_of_rules_sort_find().apply_rules(jsonName)



#------------------------------------------------------------------------------
search_tools			= lock_by_ctrl_scheme.search_tools
atomic_parameters		= lock_by_ctrl_scheme.atomic_parameters
displacement_parameters 	= lock_by_ctrl_scheme.displacement_parameters
bgg_section			= lock_by_ctrl_scheme.background().bgg_section
#------------------------------------------------------------------------------
fill_arr			= lock_by_ctrl_scheme.organize_folders_and_steps().fill_arr
copy_file_no_dirs_to_dir	= lock_by_ctrl_scheme.organize_folders_and_steps().copy_file_no_dirs_to_dir
get_stepname			= lock_by_ctrl_scheme.organize_folders_and_steps().get_stepname
read_step_and_separate		= lock_by_ctrl_scheme.organize_folders_and_steps().read_step_and_separate
scale_parameter 		= lock_by_ctrl_scheme.scale_parameter().scale_it_up
profile_parameters 		= lock_by_ctrl_scheme.prof_par().profile_parameters


def run_fp2k(pcr,dat):
	"""
	Description:
		Executes the system call for the fp2k with arguments for the execution of 
		the refinement. 
	
	Details:
		the above time.sleep is chosen instead of process.wait() for the reason of 
		considering the case of a stuck process, where a wait command would simply 
		wait till eternity.
		a frequent process.poll() would tell if the command is still running or it
		is finished. Evaluating the poll()'s output can hint for how to deal with 
		the stuck process. Fortunately fullrpof does write the `*.new` file before 
		it stuck to this could be used as a cue for a process.kill() call, which 
		terminated the process and allows the code to continue or to return a 
		appropriate error message for the user, or just simply exit the code 
	"""
	process=subprocess.Popen(['fp2k',pcr,dat,'log'],stdout=subprocess.PIPE)
	marker=0
	for i in range(0,20):
		time.sleep(1) 
		if process.poll()==int or process.poll()==0:
			#True : it's done 
			#print "Refinement done under %s seconds!" %i
			break
		else:
			#false : it's still running
			if search_tools().find_file_with_extension('new') > 0 :  # is there `*.new` in dir?
				#True
				print 'Subprocess stuck here but `*.new` found!'
				print 'Program will terminate here. Check log for the type of warning occurred!'
				process.kill()
				#marker=0
				sys.exit()
				break
			else:
				# case of running(stuck) program but no `*.new` file 
				#print 'Subprocess running, but there is no `*.new` file!'
				marker=1
				#pass
				if i==10:
					process.kill()
				else:
					pass
	for i in os.listdir(os.getcwd()):
		if i.endswith('.new')==True:
			print '2-A ".new" file has been renamed and "Pcr" code changed!!\n'
			os.rename(i,pcr)
			# change the 'Pcr' code from '2' to '1' in the case of `*.new` which contains altered 'Pcr' code
			f=open(pcr,'r')
			p=f.readlines()
			f.close()
			lineOfPcr=	 search_tools().find_index_only('Pcr',p)
			lineOfPcr_index= p[lineOfPcr[0]].split().index('Pcr')
			pp=p[lineOfPcr[0]+1].split()
			pp[lineOfPcr_index]='1'
			ppp='  '+'  '.join(pp)+'\n'
			p[lineOfPcr[0]+1]=ppp

			f=open(pcr,'w')
			f.writelines(p)
			f.close()

			# run one more time to generate output 
			process=subprocess.Popen(['fp2k',pcr,dat,'log'],stdout=subprocess.PIPE)
			marker=0
			for i in range(0,20):
				time.sleep(1) 
				if process.poll()==int or process.poll()==0:
					#True : it's done 
					#print "2-Refinement done under %s seconds!" %i
					#process.kill()
					break
				else:
					#false : it's still running
					if search_tools().find_file_with_extension('new') > 0 :  # is there `*.new` in dir?
						#True
						print '2-Subprocess stuck here but `*.new` found!'
						print '2-Program will terminate here. Check log for the type of warning occurred!'
						process.kill()
						#marker=0
						sys.exit()
						break
					else:
						# case of running(stuck) program but no `*.new` file 
						#print '2-Subprocess running, but there is no `*.new` file!'
						marker=1
						pass



def algorRun(c1,c2,c3):
	"""
	Description:
		runs the distribution of the steps that modify the `*pcr` file. 
		It makes a modification to the `pcr` one at a time. 
		After each modification it runs the refinement. 
		The pcr file name is always the same, even though each step changes it.

	Parameters:
		c1 the pcr file
		c2 the data file 
		c3 the step control, ctrl file

	Details:
		Scheme:
		  (c1,       aa[:,i][1], aa[:,i][2], aa[:,i][3])
		  (filename, codeword,   values,     code)
	"""
	switch=config.switch
	f=open(c3)      
	d=f.readlines()  
	f.close()
	r=read_step_and_separate(d)

#	while os.path.isdir('_refinements/'+ c1.strip()[:-4]  + '/'+ c3.strip()[:-5])==False:
#		try:
#			#os.mkdir('_refinements/'+ c3.strip()[:-5])
#			os.mkdir('_refinements/'+ c1.strip()[:-4]  + '/'+ c3.strip()[:-5])
#			break
#		except OSError:
#			print 'here'
#			break

	#result_folder='./_refinements/'+ c3.strip()[:-5] +'/' +c2.strip()[:-4]
	#result_folder='./_refinements/'+ c1.strip()[:-4] + '/' +c3.strip()[:-5] +'/' +c2.strip()[:-4]
	#result_folder='/_refinements/'+ c1.strip()[:-4] + '/' +c3.strip()[:-5] +'/' +c2.strip()[:-4]
	result_folder='./_refinements/'+ c1.strip()[:-4] + '/' +c3.strip()[:-5] +'/' +c2.strip()[:-4]
	#print os.getcwd()

	# Copy ONLY the pcr,ctrl, irf (if exists) and the CURRENT DATAFILE to the "result_folder"
#	os.mkdir(result_folder)

#	mkpath(result_folder)

	os.makedirs(result_folder)


	shutil.copy(c1,result_folder)
	shutil.copy(c2,result_folder)
	shutil.copy(c3,result_folder)
	[shutil.copy(i,result_folder) for i in os.listdir(os.getcwd()) if i.split('.')[-1]=='irf']

	os.chdir(result_folder)
	
	stdout.write("Starting__[model]   : %s\n\t__[strategy]: %s\n\t__[dataset] : %s \n" %(c1.strip()[:-4], c3.strip()[:-5], c2.strip()[:-4]))

	for ii in r: 			# for all elements of the r  ii is then one step
		aa=fill_arr(ii)		# fill arrays with codewords
		stepname=get_stepname(ii)
		#stdout.write(" %s" %stepname)
		print " %s" %stepname
		for i in range(0,len(aa[0])):
			if aa[:,i][1].find('bgg') >=0:
				bgg_section(c1,aa[:,i][1],aa[:,i][2],aa[:,i][3])
			if aa[:,i][1].find('bgg') !=0:
				if aa[:,i][1].find('Biso') >=0:
					atomic_parameters().change_Biso(c1,aa[:,i][1],aa[:,i][2],aa[:,i][3])
				elif aa[:,i][1].find('Occ') >=0:
					atomic_parameters().change_occ(c1,aa[:,i][1],aa[:,i][2],aa[:,i][3])
				elif aa[:,i][1].find('Xpos') >=0:
					atomic_parameters().change_Xpos(c1,aa[:,i][1],aa[:,i][2],aa[:,i][3])
				elif aa[:,i][1].find('Ypos') >=0:
					atomic_parameters().change_Ypos(c1,aa[:,i][1],aa[:,i][2],aa[:,i][3])
				elif aa[:,i][1].find('Zpos') >=0:
					atomic_parameters().change_Zpos(c1,aa[:,i][1],aa[:,i][2],aa[:,i][3])
				elif aa[:,i][1].find('Zero') >=0 or aa[:,i][1].find('SyCos') >=0 or aa[:,i][1].find('SySin') >=0:
					displacement_parameters().displacement(c1,aa[:,i][1],aa[:,i][2],aa[:,i][3])	
				elif aa[:,i][1].find('Scale') >=0:
					scale_it_up(c1)
					profile_parameters(c1,aa[:,i][0], aa[:,i][1], aa[:,i][2], aa[:,i][3])
				else:
					profile_parameters(c1,aa[:,i][0], aa[:,i][1], aa[:,i][2], aa[:,i][3]) 	
		run_fp2k(c1,c2)   
		copy_file_no_dirs_to_dir(switch, stepname)
#		stdout.write("%s " %stepname)
	#stdout.write("____done! \n")
	stdout.write("__done!__[model]: %s__[strategy]: %s__[dataset]: %s \n\n" %(c1.strip()[:-4], c3.strip()[:-5], c2.strip()[:-4]))


#-----------

class set_of_rules_sort_find():
	"""
	Description:
		Evaluates the `rules_and_settings.py` 
		Evaluates all condition and applies them on the results. 
		Returns the best matching refinement.

	"""
#	def get_values_of_a_solution(self,jsonName,strategyName,sample):
#		"""	
#		evaluates one solution in terms of the rules given in `rules_and_settings` file 
#		the rules should be written leaving the curly brackets. <,>,=>,>= are equally allowed
#		1. the empty spaces are removed. 
#		2. a list of the parameter names is formed 
#		3. json database is read and the values for the parameters are extracted
#		4. the rules are evaluated as a string where the parameter name string is replaced with
#		it's value 
#		"""
#		
#		#d=rules_and_settings.rules # no,import rules_and_setting from the code folder, we need rules_and_settings from refinement dir
#		import rules_and_settings
#		d=rules_and_settings.rules
#		
#		l=d.replace(' ','').split('\n')
#		l.sort()
#		[l.pop(0) for i in range(0,len(l)) if l[0]=='']
#		pars=[]
#		for i in l:
#			if re.split('<|>|=',i)[-2]!='':
#				pars.append(re.split('<|>|=',i)[-2])
#			else:
#				pars.append(re.split('<|>|=',i)[-3])
#
#		df=pa.read_json(jsonName)
#
#		pars_val=[]
#		for i in pars:
#			pars_val.append(df.loc[(df['Strategy']== strategyName ) & (df['Sample']== sample )][i].values[0])
#
#		a=np.array([])
#		for i in range(0,len(l)):
#			a=np.append( a, eval(l[i].replace(pars[i],str(pars_val[i]))))
#
#		return a
#
#
#	def apply_rules(self,jsonName):
#		"""
#		method that applies the extracted rules, sorts the results and returns the best match 
#
#		"""	
#		# the starting folder ('_data... _ref... _results.... `*.pct`')
#		refinements_folder=os.getcwd()
#		# go to the _refinement folder and extract the R-s 
#		os.chdir('_refinements')	
#		a=subprocess.Popen('R_Chi2_-v_stesp | sort -k5 -V > R_results.txt',shell=True); a.wait()
#		f=open('R_results.txt'); d=f.readlines(); f.close()
#
#		# change to the folder _results, where the jsonName is 
#		os.chdir(refinements_folder)
#
#
#		for i in d[:-1]:
#			folder = '/'.join(i.split()[0].split('/')[:-1]) 	  	# path 
#			strategyName = i.split()[0].split('/')[1]   	# strategy name is always the first 
#			sample = i.split()[0].split('/')[2] 		# data fileName is the second 
#
#			print "Strategy: %s  on measurement: %s" %(strategyName,sample)
#			# does the particular refinement satisfies the RULES? 
#			a=set_of_rules_sort_find().get_values_of_a_solution(jsonName,strategyName,sample)
#			print a 
#			if a.all(): # if all elements are same True -> break the loop, report the i
#				print "\n%s satisfies all given rules and has the smallest Rwp" %strategyName
#				break
#			
#		if a.all()==False:
#			print "Non of the strategies satisfies the rules. Correct the rules or strategies" 


	def pars_rules_and_settings(self,d,ddd,modelName,strategyName,sample):

		
		l=d.replace(' ','').split('\n')
		l.sort()
		[l.pop(0) for i in range(0,len(l)) if l[0]=='']

		pars=[]
		for i in l:
			if re.split('<|>|=',i)[-2]!='':
				pars.append(re.split('<|>|=',i)[-2])
			else:
				pars.append(re.split('<|>|=',i)[-3])

		df=ddd

		pars_val=[]
		for i in pars:
			ss=df.loc[(df['Model']==modelName) & (df['Strategy']==strategyName) & (df['Sample']==sample)][i].values[0]
			
			if df.loc[(df['Model']==modelName) & (df['Strategy']==strategyName) & (df['Sample']==sample)][i].isnull().values[0]==True:
				# there is a NaN
				pars_val.append('NaN')
			else:
				pars_val.append(ss)
		print pars
		print pars_val
		def papa(i):
			"""
			uses eval
			BE CAREFUL WHAT STRING IS FORWAEDED TO EVAL!!
			evaluates the rules in the `rules_and_settings` file.
			"""
			ppp=l[i].replace(pars[i],str(pars_val[i]))
			print ppp
			if type(pars_val[i]) == unicode or type(pars_val[i])==str:

				if pars_val[i]=='NaN':
					return eval('1==0')
				else:
					sss=ppp.split('==')
					ppp_us= '\'' + sss[0] +'\' ' + ' is '  + ' \''+sss[1] + '\''
					#print ppp
					#print ppp_us
					return eval(ppp_us)
			else:
				#return eval(l[i].replace(pars[i],str(pars_val[i])))
				return eval(ppp)

		a=np.array([])
		for i in range(0,len(l)):
			a=np.append( a, papa(i))

#		for i in range(0,len(l)):
#			a=np.append( a, eval(l[i].replace(pars[i],str(pars_val[i]))))

		return a

	def apply_rules(self,jsonName):
		# open the dataframe 
		# sort it by Rwp
		# loop over the sorted dataframe 
		# send the row to the `get_values_of_a_solution` if a.all() == true -> all rules as sattisfied !

		import rules_and_settings
		d=rules_and_settings.rules

		df=pa.read_json(jsonName)
		#ddd=df.sort('Rwp')
		ddd=df.sort(['Chi2'])

		top_list=[]
		show_first_n= rules_and_settings.top_list_n

		for i in range(0, len(ddd)):

			modelName = ddd['Model'][i]
			strategyName = ddd['Strategy'][i]  	# strategy name is always the first 
			sample = ddd['Sample'][i] 		# data fileName is the second 

			print "model: %s with strategy: %s  on measurement: %s" %(modelName,strategyName,sample)
			a=set_of_rules_sort_find().pars_rules_and_settings(d,ddd,modelName,strategyName,sample)
			print a                   
			if a.all(): # if all elements are same True -> break the loop, report the i
				print "\n \033[91m model %s with strategy %s on sample %s satisfies all given rules and has the smallest chi2" %(modelName,strategyName,sample)
				wichi2=ddd.loc[(df['Model']==modelName) & (df['Strategy']==strategyName) & (df['Sample']==sample)]['Chi2'].values[0]
				top_list.append((wichi2,modelName,strategyName,sample))
				if len(top_list)== show_first_n:
					break
		if a.all()==False:
			print "Non of the strategies satisfies the rules. Correct the rules or strategies" 
				
		for element in top_list:		
			print '\n \033[92m \t %s %s %s %s' %element
		
#-----------

def strategy_maker():
	"""
	Description: 
		Builds all combinations of refinement step blocks. 

	"""
	h=os.getcwd()
	os.chdir('_blocks')

	[os.remove(i) for i in os.listdir(os.getcwd()) if i.endswith('ctrl')]

	print '...refinement step-bloks accessed'
	f=open('blocks_01_background.txt')
	bgg=f.read(); f.close()
	b=bgg.split('block')

	f=open('blocks_02_profile.txt')
	prof=f.read(); f.close()
	p=prof.split('block')

	f=open('blocks_03_atomics.txt')
	ato=f.read(); f.close()
	a=ato.split('block')

	nn=1
	fl=open('strategy_log.log','w')
	fl.writelines('strg\tblock of bgg\tblock of profile\tblock of atomics\n')

	for i in range(1,len(b)):
		for ii in range(1,len(p)):
			for iii in range(1,len(a)):
				f=open('strg_'+str(nn)+'.ctrl','w')
				f.writelines( b[i].replace('\t','').split('{')[1].split('}')[0])
				f.writelines( p[ii].replace('\t','').split('{')[1].split('}')[0])
				f.writelines( a[iii].replace('\t','').split('{')[1].split('}')[0])
				f.close()
				# make a log of used block numbers for a a strategy and sum of all strategies
				fl.writelines('strg_'+str(nn)+'\t'+b[i].split('{')[0]
								 +p[ii].split('{')[0]
								 +a[iii].split('{')[0]+'\n')
				nn=nn+1
	fl.close()
	print '\t %s strategies generated' %(nn-1)
	[os.remove('../_strategies/'+i) for i in os.listdir('../_strategies') if i.endswith('ctrl')]
	[shutil.copy(i,'../_strategies') for i in os.listdir(os.getcwd()) if i.split('.')[-1]=='ctrl']
	os.chdir(h)

