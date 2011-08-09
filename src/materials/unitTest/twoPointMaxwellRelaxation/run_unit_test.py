#! /usr/bin/env python

import sys
import os
import string
from subprocess import Popen
from math import sqrt

if __name__ == "__main__":

	executable = sys.argv[-1]
	base_name = string.splitfields(executable, '/')[-1]
	logfile = open(base_name + ".log", 'w')

	if not os.path.exists(executable):
		logfile.write("\nError:  " + executable + " not found!\n\n")
		sys.exit(1)

	command = []
	for i in range(len(sys.argv)-1):
		command.append(sys.argv[1+i])

	p = Popen(command, stdout=logfile, stderr=logfile)
	return_code = p.wait()
	if 0<return_code:
		logfile.write("\nExecution of unit test failed\n\n")
		sys.exit(1)
		
	# load computed and gold data
	dFile=open('utPeridigm_twoPointMaxwellRelaxation.dat','r')
	dGFile=open('utPeridigm_twoPointMaxwellRelaxation.dat','r')
	dLines=dFile.readlines()
	dGLines=dGFile.readlines()
	if len(dLines) != len(dGLines):
		logfile.write("\nError: Files have different number of time steps!")
		sys.exit(1)
	dStr=[line.split(" ") for line in dLines]
	d=[(float(dd[0]),float(dd[1]),float(dd[2])) for dd in dStr]
	dGStr=[line.split(" ") for line in dGLines]
	dG=[(float(dd[0]),float(dd[1]),float(dd[2])) for dd in dGStr]
	
	# diff files
	logfile.write("\nDiffing Files ...")
	# input shear strain
	my_gamma=1.0e-6
	# final time
	tMag=4.0
	# displacement is equal to input shear
	uMag=my_gamma
	# young's modulus MPa
	E=68.9e3
	# poissons ratio
	nu=.33
	fMag=2.0 * 15.0 * E * my_gamma / 4.0 / (1+nu) / sqrt(2.0)
	tol=1.0e-15;
	for i in range(len(d)):
		dt=abs(d[i][0]-dG[i][0])
		du=abs(d[i][1]-dG[i][1])
		df=abs(d[i][2]-dG[i][2])
		if dt/tMag > tol or du/uMag > tol or df/fMag > tol:
			logfile.write("\utPeridigm_twoPointMaxwellRelaxation.dat.dat DIFFERs with utPeridigm_twoPointMaxwellRelaxation.dat.gold.dat\n\n")
			sys.exit(1)
			
	logfile.write("\nDiffing Files ...DONE\n")
	sys.exit(0)
