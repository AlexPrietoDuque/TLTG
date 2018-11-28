# coding=utf-8
import os, sys

class PSSpy(object):

   def __init__(self):
      self.path_pss()

      import psspy
      import redirect

      self._i = psspy.getdefaultint()
      self._f = psspy.getdefaultreal()
      self._s = psspy.getdefaultchar()

   def path_pss(self):

      if os.path.isdir('C:\\Archivos de programa\\PTI\\PSSE33'):
         rutaPSSE = 'C:\\Archivos de programa\\PTI\\PSSE33'
      if os.path.isdir('C:\\Archivos de programa (x86)\\PTI\\PSSE33'):
         rutaPSSE = 'C:\\Archivos de programa (x86)\\PTI\\PSSE33'
      if os.path.isdir('C:\\Program Files (x86)\\PTI\\PSSE33'):
         rutaPSSE = 'C:\\Program Files (x86)\\PTI\\PSSE33'
      sys.path.append(rutaPSSE + "\\PSSBIN")  # PYTHONPATH
      os.environ['PATH'] += ";" + rutaPSSE + "\\PSSBIN"  # PATH
      os.environ['PATH'] += ";" + rutaPSSE + "\\PSSLIB"

   def get_defaults(self):

      return self._i, self._f, self._s

   def inicia_psse(self):

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
