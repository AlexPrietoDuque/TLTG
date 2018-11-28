# coding=utf-8
import os, sys, time

# def add_path_pss():
#    if os.path.isdir('C:\\Archivos de programa\\PTI\\PSSE33'):
#       rutaPSSE = 'C:\\Archivos de programa\\PTI\\PSSE33'
#    if os.path.isdir('C:\\Archivos de programa (x86)\\PTI\\PSSE33'):
#       rutaPSSE = 'C:\\Archivos de programa (x86)\\PTI\\PSSE33'
#    if os.path.isdir('C:\\Program Files (x86)\\PTI\\PSSE33'):
#       rutaPSSE = 'C:\\Program Files (x86)\\PTI\\PSSE33'
#    sys.path.append(rutaPSSE + "\\PSSBIN")  # PYTHONPATH
#    os.environ['PATH'] += ";" + rutaPSSE + "\\PSSBIN"  # PATH
#    os.environ['PATH'] += ";" + rutaPSSE + "\\PSSLIB"

# add_path_pss()
# start1 = time.clock()
import psspy
# print "(initpsspy)\tTiempo en importar psspy:\t\t{:.2f} s".format(round(time.clock() - start1, 2))
import redirect
psspy.throwPsseExceptions=False

def inicia_psse(print_alert_psse=False):
   """

   :param print_alert_psse: Para indicar si en la consal debe aparecer las alaertas de PSSE
   :return:
   """

   # start = time.clock()
   # Guardamos el stdout
   consola = sys.stdout
   # Abrimos archivo nulo (no existe)
   sys.stdout = open(os.devnull, 'w')
   #Redireccion de los mensajes de PSS/E a Python
   redirect.psse2py()
   #Inicializacion del numero de nudos en memoria del PSS/E
   psspy.psseinit(150000)
   # Redirigimos el stdout a la consola
   sys.stdout = consola

   if print_alert_psse:
      psspy.prompt_output(6, "", [0, 0])
      psspy.alert_output(6, "", [0, 0])
      psspy.progress_output(6, "", [0, 0])


   # print "Tiempo en ejecutar inicia_psse:\t\t{:.2f} s".format(round(time.clock() - start, 2))
