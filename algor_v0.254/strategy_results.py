#!/usr/bin/python2
import os,time,re 
from sys import stdout
import numpy as np
import pandas as pa

import lock_by_ctrl_scheme
import rules_and_settings 

"""
Output files analysis methods and results DataFrame generator
extract: 
	- lattice constant information
	- microstractural information [ requested info ]
	- a certain step of parameterized extraction 
"""


## variables from the `rules_and_settings` file
phase=str(rules_and_settings.phase)
pattern=str(rules_and_settings.pattern)
hkl=rules_and_settings.hkl


# shortening method calling 
findall    	= lock_by_ctrl_scheme.search_tools().findall
grep_index 	= lock_by_ctrl_scheme.search_tools().grep_index
grep_AB    	= lock_by_ctrl_scheme.search_tools().grep_AB
find_index_only = lock_by_ctrl_scheme.search_tools().find_index_only

#-----------DataFrame analysis

def h_min_to_float(jsonName, strgyN):
	"""
	Description:
	h_min_to_float(jsonName, strgyN)
	where jsonName is the name of the database
	strgyN is the number of strategy
	--
	Convert and add a column to a subsection of the whole database 
	makes a subsection of jsonName using strgy
	transformas 
	E2_3h-898423-strgy_85 to 3h to 1800 as float 
	E2_30min.....strgy_85 to 30min to 30 as float
	"""
	d=pa.read_json(jsonName)  
	ds_N=d.loc[d['Strategy']== 'strg_'+str(strgyN)]
	l=[i.split('_')[1].split('-')[0] for i in ds_N['Sample']] 
	ds_N['time']=[float(i.split('h')[0])*60.0 if i.find('h')>0 else float(i.split('min')[0]) for i in l]
	return ds_N
#

def h_min_to_float_on_col(jsonName, columnName):
	"""
	Description:
	where jsonName is the name of the database
	columnName is the column that has the filenames with " h min " format 
	--
	# for future cases use naming convention '1h30min_blabla' no 1p5h and similar

	Returns a list of floats of minutes values extracted from the filename 
	
	it can be then added to the DataFrame and sorted ` d['time']=l ; d.sort(['time']) `

	"""
	l=[]
	for i in d['index']:								 
		if i.find('h')>0:
			#flaot(i.split('h')[0])*60.0
			if i.split('h')[1].find('min')>0:
				l.append(float(i.split('h')[0])*60.0 + float(i.split('h')[1].split('min')[0]))
			else:
				l.append(float(i.split('h')[0])*60.0)
		else:
			l.append(float(i.split('min')[0]))
	return l

#-------------

def lattice_const(row_name,out):
	# open the `*.out` file
	f=open(out); d=f.readlines(); f.close()

	# open the `*.pcr` file
	pcr=out.split('.')[0]+'.pcr'
	f=open(pcr); p=f.readlines();f.close()

	# define matching strings 
	match_cell_a=' :      Cell_A_ph'+phase+'_pat'+pattern
	match_cell_a_pcr='!-------> Profile Parameters for Pattern #  '+pattern+'\n'
	match_cell_c=' :      Cell_C_ph'+phase+'_pat'+pattern
	match_vol='BRAGG.*R-Factor.*and.*weight.*fractions.*for.*Pattern' #needs '\n'; re.findite removes \n	

	#lattice
	if findall(match_cell_a,d)==[]:
		# lattice const was not refined, take value from `*.pcr`
		ppp=p[p.index((findall(' a ',p)[0]+'\n'))].split()
		cell_a=float(p[p.index((findall(' a ',p)[0]+'\n'))+1].split()[ppp.index('a')-1])
		# a very low value of standard deviation is assigned 
		cell_a_err=1e-16
	else:
		# take refined parameter from `*.out` file
		cell_a=float(findall(match_cell_a,d)[0].split(match_cell_a)[1].split('( +/-')[0])
		cell_a_err=float(findall(match_cell_a,d)[0].split(match_cell_a)[1].split('( +/-')[1].split(')')[0])

	if findall(match_cell_c,d)==[]:
		# lattice const was not refined, take value from `*.pcr`
		ppp=p[p.index((findall(' c ',p)[0]+'\n'))].split()
		cell_c=float(p[p.index((findall(' c ',p)[0]+'\n'))+1].split()[ppp.index('c')-1])
		# a very low value of std is assigned 
		cell_c_err=1e-16
	else:
		# take refined parameter from `*.out` file 
		cell_c=float(findall(match_cell_c,d)[0].split(match_cell_c)[1].split('( +/-')[0])
		cell_c_err=float(findall(match_cell_c,d)[0].split(match_cell_c)[1].split('( +/-')[1].split(')')[0])

	# unit cell volume
	vol_indx=d.index('     BRAGG R-Factors and weight fractions for Pattern #  '+pattern+'\n')
	vol=float(findall('Vol',d[vol_indx:vol_indx+6])[0].split('Vol:')[1].split('(')[0])
	vol_err=float(findall('Vol',d[vol_indx:vol_indx+6])[0].split('Vol:')[1].split('(')[1].split(')')[0])
	weight_fract_ph1=float(findall('Vol',d[vol_indx:vol_indx+6])[0].split('Vol:')[1].split('(')[2].split(':')[1])
	weight_fract_ph1_err=float(findall('Vol',d[vol_indx:vol_indx+6])[0].split('Vol:')[1].split('(')[3].split(')')[0])

	#storing to a DataFrame
	col_names=['cell_a','cell_a_err','cell_c','cell_c_err','vol','vol_err','weight_fract_ph1','weight_fract_ph1_err']
	values=[cell_a,cell_a_err,cell_c,cell_c_err,vol,vol_err,weight_fract_ph1,weight_fract_ph1_err]
	df_lattice=pa.DataFrame(columns=col_names)
	df_lattice.loc[row_name]=values

	return df_lattice

def global_parameters(row_name,sumFile):
	f=open(sumFile); dsum=f.readlines(); f.close()
	
	Zero=dsum[find_index_only('Zero',dsum)[0]].split(':')[1].split()
	SyCos=dsum[find_index_only('Cos.*shift',dsum)[0]].split(':')[1].split()
	SySin=dsum[find_index_only('Sin.*shift',dsum)[0]].split(':')[1].split()

	uvw=find_index_only('Halfwidth parameters',dsum)[0]
	UVW=[i.split()[-2] for i in dsum[uvw:uvw+3]]
	UVW_err=[i.split()[-1] for i in dsum[uvw:uvw+3]]
	
	xy=find_index_only('X and y parameters',dsum)[0]
	XY=[i.split()[-2] for i in dsum[xy:xy+2]]
	XY_err=[i.split()[-1] for i in dsum[xy:xy+2]]

	# Bov 
	bov=find_index_only('Overall tem. factor',dsum)[0]
	Bov=[i.split()[-2] for i in dsum[bov:bov+1]]
	Bov_err=[i.split()[-1] for i in dsum[bov:bov+1]]

	col_names=['Zero_shift','Zero_shift_err','SyCos','SyCos_err','SySin','SySin_err',
			'U','V','W','U_std','V_std','W_std',
			'X','Y','X_std','Y_std','Bov','Bov_std']
	l=[float(Zero[0]),float(Zero[1]),float(SyCos[0]),float(SyCos[1]),float(SySin[0]),float(SySin[1])]
	l=l+UVW+UVW_err+XY+XY_err+Bov+Bov_err
	df=pa.DataFrame(columns=col_names)
	df.loc[row_name]=l
	return df
	
	

def reliability_factors(row_name,out):
	
	f=open(out); d=f.readlines(); f.close()

	#global reliability of the whole fit 
	r1=grep_index('=> Conventional Rietveld',d,1)
	r2=grep_index('RELIABILITY FACTORS FOR',d,6)
	Rp=float(r1[0].split()[6])
	Rwp=float(r1[0].split()[7])
	Re=float(r1[0].split()[8])
	Chi2=float(r1[0].split()[9])
	Deviance=float(r2[4].split()[3])
	Dev_star=float(r2[4].split()[5])
	GoF=float(r2[5].split()[2])
	
	# number of free parameters  
	Npar=float(grep_AB('Number of Least-Squares parameters',d,1)[0].split()[-1])

	# structure R-factors 
	r3=grep_index(' BRAGG R-Factors and weight fractions for Pattern #  '+pattern,d,10)
	r33=grep_index('Phase:  '+phase,r3,3)
	Bragg_R_factor_ph1=float(r33[1].split()[3])
	Rf_factor_ph1=float(r33[2].split()[2])
	
	#storing to a DataFrame 
	col_names=['Rp','Rwp','Re','Chi2','Deviance','Dev_star','GoF','Npar','Bragg_R_factor_ph1','Rf_factor_ph1']
	values=[Rp,Rwp,Re,Chi2,Deviance,Dev_star,GoF,Npar,Bragg_R_factor_ph1,Rf_factor_ph1]
	df_reliability=pa.DataFrame(columns=col_names)
	df_reliability.loc[row_name]=values

	return df_reliability

def occ_Biso(row_name,sumFile,discif,out):
	"""
	Read the occupancy and mean atomic displacement factors from the 
	`*.sum` file

	correct the site occupancy from FullProf's notations 
	"""
	#-----
	# Occupancy in normalized site inhabitancy 
	#
	# find the line of start 
	f=open(discif); dcif=f.readlines(); f.close()
	sp=find_index_only('_symmetry_equiv_pos_as_xyz ',dcif)[0]

	# get the total number of symmetry equivalent positions 
	eq_sym=0
	for ii in dcif[sp+1:]:
		# break from loop when the empty line is found:  ' \n' and '\n' 
		if re.match('[ \n]',ii)==None:
			eq_sym=eq_sym+1
		else:
			break
	# eq_sym : total number of symmetry equivalent position 
	#-----

	f=open(sumFile); dsum=f.readlines(); f.close()
	f=open(out); out=f.readlines(); f.close()

#	# Bov 
#	bov=find_index_only('Overall tem. factor',dsum)[0]
#	Bov=[i.split()[-2] for i in dsum[bov:bov+1]]
#	Bov_err=[i.split()[-1] for i in dsum[bov:bov+1]]
	
	# atomics
	sl=find_index_only('=> Phase No.  '+phase,dsum)[0]			# only one line exists such
	a=find_index_only('==> ATOM PARAMETERS:',dsum)				# as many as phases
	p=find_index_only('==> PROFILE PARAMETERS FOR PATTERN#  '+pattern,dsum)	# as many as phases

	sp=find_index_only('Number of atoms',out)[0]
	number_of_atoms=int(out[sp].split(':')[1])

	
	# all atomic parameters for the selected phase (from ATOM...to...PROFILE)
	#phase_atomics=dsum[ a[int(phase)-1]+3 : p[int(phase)-1]-1 ]   # NO 
	phase_atomics=dsum[ a[int(phase)-1]+3 : a[int(phase)-1]+3+number_of_atoms ]   # -1 since phase numeration starts with 1

	df_atomics=pa.DataFrame()
	for i in phase_atomics:
		k=[j.split('(') for j in i.split(')')]

		a_name=k[0][0].split()[0]  #atom name

		a_Xpos_val =float(k[0][0].split()[1]) # atom Xpos value
		a_Xpos_std =float('0.'+(len(k[0][0].split()[1].split('.')[1])-len(k[0][1].strip()))*'0'+str(k[0][1].strip()))
		#a_Xpos_std =float(k[0][1])            
		a_Ypos_val =float(k[1][0])
		a_Ypos_std =float('0.'+(len(k[1][0].split('.')[1])-len(k[1][1].strip()))*'0'+str(k[1][1].strip()))
		#a_Ypos_std =float(k[1][1])
		a_Zpos_val =float(k[2][0])
		a_Zpos_std =float('0.'+(len(k[2][0].split('.')[1])-len(k[2][1].strip()))*'0'+str(k[2][1].strip()))
		#a_Zpos_std =float(k[2][1])
		a_Biso_val =float(k[3][0])
		a_Biso_std =float('0.'+(len(k[3][0].split('.')[1])-len(k[3][1].strip()))*'0'+str(k[3][1].strip()))
		#a_Biso_std =float(k[3][1])

		a_mult     =float(k[5][0])

		#a_Occ__val =float(k[4][0])
		a_Occ__val =100.0*float(k[4][0])/ (a_mult/eq_sym)
		a_Occ__std_f =float('0.'+(len(k[4][0].split('.')[1])-len(k[4][1].strip()))*'0'+str(k[4][1].strip()))
		a_Occ__std =100.0*a_Occ__std_f / (a_mult/eq_sym)
		#a_Occ__std =float(k[4][1])

		l_col_names=[a_name+'Xpos',a_name+'Xpos_std',
		      	     a_name+'Ypos',a_name+'Ypos_std',
			     a_name+'Zpos',a_name+'Zpos_std',
			     a_name+'Biso',a_name+'Biso_std',
			     a_name+'Occ',a_name+'Occ_std',a_name+'Mult'] #,'Bov','Bov_std']
		# -check the std's and correct for '0' error-> 1e-16   -> no need for this
		# -check and correct occ -> normalized, in %-s         -> done!
		
				

		l=[a_Xpos_val, a_Xpos_std,
		   a_Ypos_val, a_Ypos_std,
		   a_Zpos_val, a_Zpos_std,
		   a_Biso_val, a_Biso_std,
		   a_Occ__val, a_Occ__std, a_mult] #+Bov+Bov_err
		df=pa.DataFrame(columns=l_col_names)
		df.loc[row_name]=l	
		df_atomics=pa.concat([df_atomics,df],axis=1)	

	return df_atomics


def occ_Biso_2(row_name,sumFile,out):
	"""
	Read the occupancy and mean atomic displacement factors from the 
	`*.sum` file

	correct the site occupancy from FullProf's notations 
	"""
	f=open(out); out=f.readlines(); f.close()
	# eq_sym : total number of symmetry equivalent position 
	sp=find_index_only('General multiplicity',out)[0]
	eq_sym=int(out[sp].split(':')[1])

	#-----

	f=open(sumFile); dsum=f.readlines(); f.close()

#	# Bov 
#	bov=find_index_only('Overall tem. factor',dsum)[0]
#	Bov=[i.split()[-2] for i in dsum[bov:bov+1]]
#	Bov_err=[i.split()[-1] for i in dsum[bov:bov+1]]

	# atomics	
	sl=find_index_only('=> Phase No.  '+phase,dsum)[0]			# only one line exists such
	a=find_index_only('==> ATOM PARAMETERS:',dsum)				# as many as phases
	p=find_index_only('==> PROFILE PARAMETERS FOR PATTERN#  '+pattern,dsum)	# as many as phases
	
	# all atomic parameters for the selected phase (from ATOM...to...PROFILE)
	phase_atomics=dsum[ a[int(phase)-1]+3 : p[int(phase)-1]-1 ]   # -1 since phase numeration starts with 1 and python from 0   
	
	df_atomics=pa.DataFrame()
	for i in phase_atomics:
		k=[j.split('(') for j in i.split(')')]
		a_name     =k[0][0].split()[0] # atom name
		#print k[0][0]
		#print k[0][1]
		a_Xpos_val =float(k[0][0].split()[1]) # atom Xpos value
		a_Xpos_std =float('0.'+(len(k[0][0].split()[1].split('.')[1])-len(k[0][1].strip()))*'0'+str(k[0][1].strip()))
		#a_Xpos_std =float(k[0][1])            
		a_Ypos_val =float(k[1][0])
		a_Ypos_std =float('0.'+(len(k[1][0].split('.')[1])-len(k[1][1].strip()))*'0'+str(k[1][1].strip()))
		#a_Ypos_std =float(k[1][1])
		a_Zpos_val =float(k[2][0])
		a_Zpos_std =float('0.'+(len(k[2][0].split('.')[1])-len(k[2][1].strip()))*'0'+str(k[2][1].strip()))
		#a_Zpos_std =float(k[2][1])
		a_Biso_val =float(k[3][0])
		a_Biso_std =float('0.'+(len(k[3][0].split('.')[1])-len(k[3][1].strip()))*'0'+str(k[3][1].strip()))
		#a_Biso_std =float(k[3][1])

		a_mult     =float(k[5][0])

		#a_Occ__val =float(k[4][0])
		a_Occ__val =100.0*float(k[4][0])/ (a_mult/eq_sym)
		a_Occ__std_f =float('0.'+(len(k[4][0].split('.')[1])-len(k[4][1].strip()))*'0'+str(k[4][1].strip()))
		a_Occ__std =100.0*a_Occ__std_f / (a_mult/eq_sym)
		#a_Occ__std =float(k[4][1])

		l_col_names=[a_name+'Xpos',a_name+'Xpos_std',
		      	     a_name+'Ypos',a_name+'Ypos_std',
			     a_name+'Zpos',a_name+'Zpos_std',
			     a_name+'Biso',a_name+'Biso_std',
			     a_name+'Occ',a_name+'Occ_std',a_name+'Mult'] #,'Bov','Bov_std']
		# -check the std's and correct for '0' error-> 1e-16   -> no need for this
		# -check and correct occ -> normalized, in %-s         -> done!
		
				

		l=[a_Xpos_val, a_Xpos_std,
		   a_Ypos_val, a_Ypos_std,
		   a_Zpos_val, a_Zpos_std,
		   a_Biso_val, a_Biso_std,
		   a_Occ__val, a_Occ__std, a_mult] #+Bov+Bov_err
		df=pa.DataFrame(columns=l_col_names)
		df.loc[row_name]=l	
		df_atomics=pa.concat([df_atomics,df],axis=1)	

	return df_atomics


def read_mic(row_name,mic,hkl):
	"""
	Reads the microstructure file of a given phase
	
	hkl is a list and is read out of the rules_and_settings.py file. 
		
	"""
	f=open(mic); d=f.readlines(); f.close()

	def hkl_mic(h,k,l):
		#a='.*'+str(h)+'(\s+)'+str(k)+'(\s+)'+str(l)+'(\s+).*'
		a='.*'+str(h)+'(\s+)'+str(k)+'(\s+)'+str(l)+'.*'
#		for i in d[50:]:
#			if re.match(a,i)!=None:
#				#print d.index(i)
#				return i
		#return [i for i in d[50:] if re.match(a,i)!=None][0]
		return [i for i in d[50:] if re.match(a,'  '.join(i.split()[11:14]))!=None][0]
	col_names=np.array([])
	val=np.array([])
	for i in hkl:
		s=hkl_mic(i[0],i[1],i[2])
		if s!=None:
			#app_size=s.split()[9]
			#strain=s.split()[10]
			val=np.append(val,[s.split()[9],s.split()[10]])
			col_names=np.append(col_names,['size_'+str(i[0])+str(i[1])+str(i[2]),
							'strain_'+str(i[0])+str(i[1])+str(i[2])])
	df=pa.DataFrame(index=[row_name],columns=col_names)
	df.loc[row_name]=val
	return df

def read_dis(row_name,discif):
	"""
	Reads the `*_1_dis.cif` file where the distances
	and the angles are in the form of a list
	"""
	
	f=open(discif); d=f.readlines(); f.close()
	
	# find the starting line of distances:
	n_d=find_index_only(' _geom_bond_atom_site_label_1',d)[0]
	# find the starting line of the angles: 
	n_a=find_index_only('_geom_angle_atom_site_label_1',d)[0]
	
	# get the atom-atom distance:
	dist=[]
	for i in d[n_d:n_a]:
		if len(i.split('_geom_bond'))==1:
			# break from loop when the empty line is found -end of distance list
			if i=='\n':
				break
			if i.split()>2:
				dist.append(i)
	# get the angles:
	angl=[]
	for i in d[n_a:]:
		if len(i.split('_geom_angle'))==1:
			angl.append(i)

	# make column names for distances
	d_atom1_2=[i.split()[0]+'-'+i.split()[1] for i in dist]
	# generate column names for the standard deviation values 
	d_atom1_2_err=[i+'_err' for i in d_atom1_2]
	# get value and std:
	d_value=[clean_std_formatting(i.split()[2])[0] for i in dist]				
	d_std=[clean_std_formatting(i.split()[2])[1] for i in dist]				

	# make column names for angles 
	a_atom1_2_3=[i.split()[0]+'-'+i.split()[1]+'-'+i.split()[2] for i in angl]
	# generate column names for the standard deviation values 
	a_atom1_2_3_err=[i+'_err' for i in a_atom1_2_3]
	# get values and stds:
	a_value=[clean_std_formatting(i.split()[3])[0] for i in angl]
	a_std=[clean_std_formatting(i.split()[3])[1] for i in angl]
	
	# extend the list of values with the standard deviations 
	d_value.extend(d_std)
	a_value.extend(a_std)
	
	# generate DataFrames from the names and concatente 
	df_dist=pa.concat([pa.DataFrame(columns=d_atom1_2),pa.DataFrame(columns=d_atom1_2_err)],axis=1)
	df_angl=pa.concat([pa.DataFrame(columns=a_atom1_2_3),pa.DataFrame(columns=a_atom1_2_3_err)],axis=1)	
	# add rows
	df_dist.loc[row_name]=d_value
	df_angl.loc[row_name]=a_value
	# combine the two DataFrames of bond distance and angles to a unique DF
	df_read_dis=pa.concat([df_dist,df_angl],axis=1)

	return df_read_dis

def read_dis_tet(row_name,dis):
	"""
	Reads the `*.dis` file, to extract the O-O distances sine they are not listed in the `*dis.cif` file !!!

	"""	
	f=open(dis); d=f.readlines(); f.close()

	l=[i for i in d if re.search('Atm-1.*Atm-2.*Atm-3',i)!=None]
	ll=[i.split('d13')[1].strip().split('=')[-1] for i in l]
	lll=[clean_std_formatting(i) for i in ll]
	vals=[i[0] for i in lll]
	stds=[i[1] for i in lll]
	
	if len(vals)==6:
		# the data corresponds to a tetrahedra presumably 
		
#		a=[[0, 1, 1, 1, 1],
#		   [1, 0, d12**2, d13**2, d14**2],
#		   [1, d21**2, 0, d23**2, d24**2],
#		   [1, d31**2, d32**2, 0, d34**2],
#		   [1, d41**2, d42**2, d43**2, 0]]
		a=[[0, 1, 1, 1, 1],
		   [1, 0, vals[0]**2, vals[1]**2, vals[2]**2],
		   [1, vals[0]**2, 0, vals[3]**2, vals[4]**2],
		   [1, vals[1]**2, vals[3]**2, 0, vals[5]**2],
		   [1, vals[2]**2, vals[4]**2, vals[5]**2, 0]]
		tet_vol=np.sqrt(np.linalg.det(a)/288.00)
		
		df=pa.DataFrame(index=[row_name],columns=['tet_vol'])
		df.loc[row_name]=tet_vol
		return df

	

#---------
def sampleName_strategy(row_name,m,s,d):
	df=pa.DataFrame(index=[row_name],columns=['Model','Strategy','Sample'])
	df.loc[row_name]=[m,s,d]
	return df
	

def sampleName_parametrized_value(s,v):
	df=pa.DataFrame(index=[row_name],columsn=['Parametrized_variable','step_#'])
	df.loc[row_name]=[]
	return df


def clean_std_formatting(element):
	"""
	takes a string formatted value and std as:
	1.530(4) 
	and returns a list of floats 
	[1.53,0.004]
	
	It distinguishes case of absent "." 
	111(2)
	[111,2]
	
	"""	
	# check for existance of standard deviation in the string 
	if element.count('(')>0:
		# std is contained in the string
		if element.split('(')[0].find('.')>0:
			#it has a '.' in the first section before the '('
			d=len(element.split('(')[0].split('.')[1])
			a=float(element.split('(')[0])	
			s=float(element.split('(')[1].split(')')[0])/10**d
		else:
			#there is no '.' before the '(' : case 111(2)			
			a=float(element.split('(')[0])	
			s=float(element.split('(')[1].split(')')[0])
	else:
		a=float(element)
		s=1e-16
	return list([a,s])


def drop_repeating_cols(df):
	"""
	check for repeating column names like p1-o3 since 
	there are two atoms at the same position 
	"""
	Cols = list(df.columns)
	for i,item in enumerate(df.columns):
		if item in df.columns[:i]:
			#print Cols[i]
			Cols[i] = "toDROP"
	df.columns = Cols
	df = df.drop("toDROP",1)
	return df


#------------------------------------------------------------------
# the row_name should be the idenfifier if the refinement.
#	it can be a dataset name of a certain step (last) of a strategy
#			index 		col1 ...
#		1_106_11_strgy_04
#		1_106_15_strgy_04
#		      ...
#		1_106_11_strgy_05
#		1_106_15_strgy_05
#		      ...
#
#	or it can be the step number in the parameterisation,
#	since the parametrization is always on one dataset
#		1_106_11_step_1
#		1_106_11_step_2
#		      ...
#		1_106_11_step_50
#-------------------------------------------------------------------

def get_results():
	# mode	- denotes the mode of the refinement: 
	# 	strategy_comparison or parametrised
	#	
	#mode=''

	# generate the DataFrame which will be filled in the following section
	df_1=pa.DataFrame()

	# above the _refinement folder 
	mm=os.getcwd()
	os.chdir('_refinements')

	# inside the _refinemet folder 


	m0=os.getcwd()
	l0=filter(os.path.isdir, os.listdir(os.path.curdir))

	for iii in l0:
		"""
		loop over all models		

		"""
		m1=os.getcwd()
		os.chdir(iii)

		m=os.path.basename(os.getcwd())

		l=filter(os.path.isdir, os.listdir(os.path.curdir))
		for i in l:	
			"""
			loop over all strategy folders 
			l - list of all strategy folder names 
			"""
			m2=os.getcwd()
			os.chdir(i)
			# s - strategy name (ctrl file name)
			s=os.path.basename(os.getcwd())
			#l1=os.listdir(os.getcwd())
			l1=filter(os.path.isdir, os.listdir(os.path.curdir))
			for ii in l1:
				"""
				loop over all datafile folders 
				l1 - list of datafiles
				"""
				stdout.write(' %s %s %s ' %(iii,i,ii)) 

				while True:
					try:

						m3=os.getcwd()
						# go the the folders of the measurement-dataset
						os.chdir(ii)
						
						# d - dataset filename refinement of a diffraction pattern
						d=os.path.basename(os.getcwd())
						# define the row name in the DataFrame
						row_name=m+'_'+d+'_'+s
						#print row_name			
						pcr=[k for k in os.listdir(os.getcwd()) if k.endswith(".pcr")]
						out=[k for k in os.listdir(os.getcwd()) if k.endswith(".out")]
						dis_cif=[k for k in os.listdir(os.getcwd()) if k.endswith(phase+"_dis.cif")]
						dis=[k for k in os.listdir(os.getcwd()) if k.endswith('_'+phase+".dis")]
						dsum=[k for k in os.listdir(os.getcwd()) if k.endswith(".sum")]
						mic=[k for k in os.listdir(os.getcwd()) if k.endswith(phase+".mic")]
						# concatenate all section DataFrames
						if pcr and out and dsum and dis and dis_cif and mic != []:
							df_res=pa.concat([sampleName_strategy(row_name,m,s,d),
									  lattice_const(row_name,out[0]),
									  reliability_factors(row_name,out[0]),
									  global_parameters(row_name,dsum[0]),
									  occ_Biso(row_name,dsum[0],dis_cif[0],out[0]),
									  read_mic(row_name,mic[0],hkl),
									  read_dis(row_name,dis_cif[0]),
									  read_dis_tet(row_name,dis[0])],axis=1)
						else:
							if pcr and out and dsum and dis and dis_cif != []:
								df_res=pa.concat([sampleName_strategy(row_name,m,s,d),
										  lattice_const(row_name,out[0]),
										  reliability_factors(row_name,out[0]),
										  global_parameters(row_name,dsum[0]),

										  occ_Biso(row_name,dsum[0],dis_cif[0],out[0]),
										  read_dis(row_name,dis_cif[0]),
										  read_dis_tet(row_name,dis[0])],axis=1)
							elif pcr and out and dsum and mic   != [] :
								df_res=pa.concat([sampleName_strategy(row_name,m,s,d),
										  lattice_const(row_name,out[0]),
										  reliability_factors(row_name,out[0]),
										  global_parameters(row_name,dsum[0]),

										  read_mic(row_name,mic[0],hkl),
										  occ_Biso_2(row_name,dsum[0],out[0]),
										  ],axis=1)

							elif pcr and out and dsum != []:
								df_res=pa.concat([sampleName_strategy(row_name,m,s,d),
										  lattice_const(row_name,out[0]),
										  reliability_factors(row_name,out[0]),
										  global_parameters(row_name,dsum[0]),
						
										  occ_Biso_2(row_name,dsum[0],out[0]),
										  ],axis=1)

						# dropping repeating columns (such as like p1-o3 p1-o3)
						# in case there are no repeating columns this will retrun an error 
						while True:
							try:
								df_res=drop_repeating_cols(df_res)
								break
							except ValueError:
								break
						#df_res=drop_repeating_cols(df_res)
						df_1=pa.concat([df_1,df_res])
			
						break
					#except (ValueError, IndexError):
					except Exception as e:
						stdout.write(" ------------refinement failed! \n")
						break
				stdout.write('\n')

				os.chdir(m3)
			os.chdir(m2)
		os.chdir(m1)
	os.chdir(mm)

	# save the data frame
	if os.path.isdir('_results')==False:
		os.mkdir('_results')
	df_name='_'+"_".join([str(i) for i in time.localtime()[:5]])
	jsonName='./_results/ref_res'+df_name+'.json'
	df_1.to_json(jsonName)

	# return the saved json' name for the 'set_rules_sort_find.py'
	return jsonName


def get_results_parametrisation(nn,df_parameters_in_steps):
	"""
	In the case of the parameterizaton a small Dataframe is 
	forwared to this method in order to include the values 
	and exact refinements into the final result DataFrame stored
	in the /_results folder. 
	"""
	df_par_step=df_parameters_in_steps
	
	# generate the DataFrame which will be filled in the following section
	df_1=pa.DataFrame()

	# above the _refinement folder
	# nn is the parameterization folder 
	os.chdir(nn)
	m0=os.getcwd()
	os.chdir('_refinements')

	# inside the _refinemet folder 
	m1=os.getcwd()
	#l=os.listdir(os.getcwd())
	l=filter(os.path.isdir, os.listdir(os.path.curdir))
	for i in l:	
		"""
		loop over all strategy folders 
		l - list of all strategy folder names 
		"""
		m2=os.getcwd()
		os.chdir(i)
		# s - strategy name (ctrl file name)
		s=os.path.basename(os.getcwd())
		#l1=os.listdir(os.getcwd())
		l1=filter(os.path.isdir, os.listdir(os.path.curdir))
		for ii in l1:
			"""
			loop over all datafile folders 
			l1 - list of datafiles
			"""

			print i,ii

			m3=os.getcwd()
			# go the the folders of the measurement-dataset
			os.chdir(ii)
			
			# d - dataset filename refinement of a diffraction pattern
			d=os.path.basename(os.getcwd())
			pcr=[k for k in os.listdir(os.getcwd()) if k.endswith(".pcr")][0]
			out=[k for k in os.listdir(os.getcwd()) if k.endswith(".out")][0]
			dis_cif=[k for k in os.listdir(os.getcwd()) if k.endswith(phase+"_dis.cif")][0]
			dsum=[k for k in os.listdir(os.getcwd()) if k.endswith(".sum")][0]
			mic=[k for k in os.listdir(os.getcwd()) if k.endswith(phase+".mic")][0]
			# define the row name in the DataFrame
			row_name=d+'_'+s

			# concatenate all section DataFrames
			df_res=pa.concat([sampleName_strategy(row_name,s,d),
					  lattice_const(row_name,out),
					  read_dis(row_name,dis_cif),
					  reliability_factors(row_name,out),
					  occ_Biso(row_name,dsum,dis_cif),
					  global_parameters(row_name,dsum),
					  read_mic(row_name,mic,hkl),
					  read_dis_tet(row_name)],axis=1)

			# dropping repeating columns (such as like p1-o3 p1-o3)
			df_res=drop_repeating_cols(df_res)
			df_1=pa.concat([df_1,df_res])
			
			# concatenate with the df_parameter_step from the `*ctrl` generation module
			# need to rename to avoid ValueError: cannot reindex from a duplicate axis
			df_2=pa.concat([df_par_step,df_1],axis=1)
			os.chdir(m3)
		os.chdir(m2)

	os.chdir(m0)

	# save the data frame
	if os.path.isdir('_results')==False:
		os.mkdir('_results')
	df_name='_'+"_".join([str(i) for i in time.localtime()[:5]])
	df_2.to_json('./_results/param_ref_res'+df_name+'.json')


#if __name__=="__main__":
