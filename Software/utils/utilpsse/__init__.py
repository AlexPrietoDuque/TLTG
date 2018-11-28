import os, sys
import time
start = time.clock()

if os.path.isdir('C:\\Archivos de programa\\PTI\\PSSE33'):
   rutaPSSE = 'C:\\Archivos de programa\\PTI\\PSSE33'
if os.path.isdir('C:\\Archivos de programa (x86)\\PTI\\PSSE33'):
   rutaPSSE = 'C:\\Archivos de programa (x86)\\PTI\\PSSE33'
if os.path.isdir('C:\\Program Files (x86)\\PTI\\PSSE33'):
   rutaPSSE = 'C:\\Program Files (x86)\\PTI\\PSSE33'
if os.path.isdir('C:\\PSSE33'):
   rutaPSSE = 'C:\\PSSE33'
sys.path.append(rutaPSSE + "\\PSSBIN")  # PYTHONPATH
os.environ['PATH'] += ";" + rutaPSSE + "\\PSSBIN"  # PATH
os.environ['PATH'] += ";" + rutaPSSE + "\\PSSLIB"

# start22 = time.clock()
from initpsspy import inicia_psse
# print "(__init__)\tTiempo en importar inicia_psse:\t\t{:.2f} s".format(round(time.clock() - start22, 2))
from entidades import *
from redpsse import *

# print "Tiempo de carga del modulo 'utilpsse':\t\t {} s".format(round(time.clock() - start, 2))

# asdasd 222