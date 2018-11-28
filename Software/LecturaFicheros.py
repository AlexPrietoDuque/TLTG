# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Purpose:     read input files
# Author:      MRCh
# Started:     15/11/2018
# Finished:    19/11/2018
# -------------------------------------------------------------------------------

import ConfigParser as configparse
import os
from os.path import dirname, normpath


class Rutas(object):
   """
   Clase para guardar las rutas
   """
   def __init__(self):
      # se obtiene el directorio del proyecto
      path = os.getcwdu()
      ruta_proyecto = dirname(normpath(path))

      self.ruta_inputs=os.path.join(ruta_proyecto, 'Inputs')
      self.ruta_casos=os.path.join(ruta_proyecto, 'Casos')
      self.ruta_resultados=os.path.join(ruta_proyecto, 'Resultados')
      self.ruta_BBDD=os.path.join(ruta_proyecto, 'BdD')
      self.ruta_Software=os.path.join(ruta_proyecto, 'Software')

      self.ruta_dfax = os.path.join(self.ruta_resultados, 'DFAX')

      self.ruta_log = os.path.join(self.ruta_Software, 'Log')

      self.ruta_casos_procesados = os.path.join(self.ruta_casos, 'Procesados')

class Parametros(object):
   """
   Clase para guardar las varibles de configuracion del fichero de Parametros
   """
   def __init__(self, *args,
                **kw_args):
      self.__factor_distrb_min=0.05
      self.__U_min_p=220
      self.__U_max_p=500
      self.__U_min_i=30
      self.__U_max_i=220
      self.__N_datosN = 5
      self.__N_datosN_1 = 5
      self.__N_datosN_2 = 5
      self.__Rate_A = 100
      self.__Rate_B = 100

   @property
   def factor_distrb_min(self):
      """
      Factor de distribución
      """
      return self.__factor_distrb_min
   @factor_distrb_min.setter

   def factor_distrb_min(self, value):
      try:
         self.__factor_distrb_min = float(value)
      except:
         raise SyntaxError('El parametro "factor_distrb_min" deber ser un numero.')


   @property
   def U_min_p(self):
      """
      Valor inferior del rango de tensiones de Península
      """
      return self.__U_min_p
   @U_min_p.setter

   def U_min_p(self, value):
      try:
         self.__U_min_p = float(value)
      except:
         raise SyntaxError('El parametro "U_min_p" deber ser un numero.')


   @property
   def U_max_p(self):
      """
      Valor superior del rango de tensiones de Península
      """
      return self.__U_max_p
   @U_max_p.setter

   def U_max_p(self, value):
      try:
         self.__U_max_p = float(value)
      except:
         raise SyntaxError('El parametro "U_max_p" deber ser un numero.')


   @property
   def U_min_i(self):
      """
      Valor inferior del rango de tensiones de las islas
      """
      return self.__U_min_i
   @U_min_i.setter

   def U_min_i(self, value):
      try:
         self.__U_min_i = float(value)
      except:
         raise SyntaxError('El parametro "U_min_i" deber ser un numero.')


   @property
   def U_max_i(self):
      """
      Valor superior del rango de tensiones de las islas
      """
      return self.__U_max_i
   @U_max_i.setter

   def U_max_i(self, value):
      try:
         self.__U_max_i = float(value)
      except:
         raise SyntaxError('El parametro "U_max_i" deber ser un numero.')


   @property
   def N_datosN(self):
      """
      Número de ramas limitantes a guardar para caso N
      """
      return self.__N_datosN

   @N_datosN.setter
   def N_datosN(self, value):
      try:
         self.__N_datosN = int(value)
      except:
         raise SyntaxError('El parametro "N_datosN" deber ser un numero entero.')


   @property
   def N_datosN_1(self):
      """
      Número de ramas limitantes a guardar para caso N
      """
      return self.__N_datosN_1

   @N_datosN_1.setter
   def N_datosN_1(self, value):
      try:
         self.__N_datosN_1 = int(value)
      except:
         raise SyntaxError('El parametro "N_datosN_1" deber ser un numero entero.')


   @property
   def N_datosN_2(self):
      """
      Número de ramas limitantes a guardar para caso N
      """
      return self.__N_datosN_2

   @N_datosN_2.setter
   def N_datosN_2(self, value):
      try:
         self.__N_datosN_2 = int(value)
      except:
         raise SyntaxError('El parametro "N_datosN_2" deber ser un numero entero.')


   @property
   def Rate_A(self):
      """
      límite de carga para N
      """
      return self.__Rate_A

   @Rate_A.setter
   def Rate_A(self, value):
      try:
         self.__Rate_A = float(value)
      except:
         raise SyntaxError('El parametro "Rate_A" deber ser un numero.')


   @property
   def Rate_B(self):
      """
      límite de carga para N-1 y N-2
      """
      return self.__Rate_B

   @Rate_B.setter
   def Rate_B(self, value):
      try:
         self.__Rate_B = float(value)
      except:
         raise SyntaxError('El parametro "Rate_B" deber ser un numero.')

class SistemasEstudio(object):
   """
   Clase para guardar los sistemas de estudio
   """
   def __init__(self, *args,
                **kw_args):
      self.Tipo=None
      self.Nombre=None
      self.Sistema=None

class Info_Casos(object):
   """
   Clase para guardar Info_Casos
   """
   def __init__(self, *args,
                **kw_args):
      self.N_Caso=None
      self.Probabilidad=None

class Contingencias_N2(object):
   """
   Clase para guardar ContingenciasN2
   """
   def __init__(self, *args,
                **kw_args):
      self.Name=None
      self.Description = None
      self.Npss_1 = None
      self.Npss_2 = None
      self.Npss2_1 = None
      self.Npss2_2 = None
      self.ckt_1 = None
      self.ckt_2 = None


def lecturaficheros():
   parametros=get_parametros()
   sistemas_estudio=get_sist_est()
   info_casos=get_info_casos()
   contingenciasN_2=get_cont_N2()

   return parametros, sistemas_estudio, info_casos, contingenciasN_2

def get_parametros():

   #Lee el archivo de configuracion de parametros

   try:
      #se obtiene la ruta
      filename = os.path.join(Rutas().ruta_inputs, 'Fich_Parametros.cfg')
      #se establece la seccion a leer
      seccion='PARAMETROS'
      #se llama a la funcion de lectura
      cfg = configparse.ConfigParser()

      if not cfg.read([filename]):
         #si no es posible leer el fichero devuelve un error
         print "No existe el archivo en la ruta especificada {}".format(filename)
         raise StandardError("No existe el archivo de configuracion en la ruta especificada {}".format(filename))
      else:
         if not cfg.has_section(seccion):
            #si no se encuentra la seccion indicada devuelve un error
            raise StandardError(
               "No se ha encontrado la seccion indicada en el archivo de configuracion {}".format(seccion))
         else:
            #se leen los parametros de la seccion indicada
            secc = cfg.sections()
            secc = filter(lambda x: str.lower(x) == str.lower(seccion), secc)
            seccion = secc[0]
            param = cfg

      #se relacionan los parametros con su clase
      parametros = Parametros()

      parametros.factor_distrb_min = param.get(seccion, 'factor_distrb_min')
      parametros.U_min_p = param.get(seccion, 'U_min_p')
      parametros.U_max_p = param.get(seccion, 'U_max_p')
      parametros.U_min_i = param.get(seccion, 'U_min_i')
      parametros.U_max_i = param.get(seccion, 'U_max_i')
      parametros.N_datosN = param.get(seccion, 'N_datosN')
      parametros.N_datosN_1 = param.get(seccion, 'N_datosN_1')
      parametros.N_datosN_2 = param.get(seccion, 'N_datosN_2')
      parametros.Rate_A = param.get(seccion, 'Rate_A')
      parametros.Rate_B = param.get(seccion, 'Rate_B')

      return parametros

   except Exception as e:
      raise StandardError('Error en la obtencion de los parametros de configuracion: {}'.format(e.message))

def get_sist_est():

   #lee el archivo de configuracion de sistemas de estudio

   try:
      # se obtiene la ruta
      filename = os.path.join(Rutas().ruta_inputs, 'Fich_Sist_Estudio.txt')
      #se inicializan las variables
      read = False
      sist_est=[]

      #se abre el fichero a leer
      flist = open(filename).readlines()

      #se guardan las lineas entre INICIO y FIN del fichero
      for line in flist:
         line = line.rstrip()
         if line.startswith("#INICIO"):
            #cuando se encuentra la linea INICIO se comienza la creacion de la lista
            read = True
            continue
         elif line.startswith("#FIN"):
            #cuando se encuentra la linea FIN se termina la lista
            read = False
         if read:
            #se relaciona con la clase de los sistemas de estudio
            sist_inf = SistemasEstudio()
            sist_inf.Tipo = line.split(';')[0]
            sist_inf.Nombre = line.split(';')[1]
            sist_inf.Sistema = line.split(';')[2]

            sist_est.append(sist_inf)

      return sist_est

   except Exception as e:
      raise StandardError('Error en la obtencion de los sistemas de estudio: {}'.format(e.message))

def get_info_casos():

   # lee el archivo de con la informacion de los casos

   try:
      # se obtiene la ruta
      filename = os.path.join(Rutas().ruta_casos, 'INFO_CASOS.txt')
      #se crea la lista vacia y se inicializa la variable probabilidad total
      info_casos=[]
      prob_total=0

      #se abre el fichero
      with open(filename) as f:
         flist = f.readlines()

      #se guarda la info necesaria en una lista
      for line in flist:
         infoC=Info_Casos()
         line = line.rstrip()
         infoC.N_Caso=int(line.split()[1])
         infoC.Probabilidad=float(line.split()[5])
         info_casos.append(infoC)
         #se van sumando los valores de probabilidad para obtener la prob. total
         prob_total= prob_total + infoC.Probabilidad

      #si la prob. total es distinta a la ud. se normaliza
      if prob_total != 1:
            info_casos=normalizar(info_casos, prob_total)

      return info_casos

   except Exception as e:
      raise StandardError('Error en la obtencion de los casos en INFO_CASOS: {}'.format(e.message))

def get_cont_N2():

   # lee el archivo de con las contingencias dobles
   try:
      # se obtiene la ruta
      filename = os.path.join(Rutas().ruta_inputs, 'Contingencias_N_2.con')
      #se crea la lista vacia
      contingencias_dobles=[]
      i = 0

      #se abre el fichero
      with open(filename) as f:
          flist = f.readlines()
      #se guarda la info necesaria en una lista
      #se guardan las lineas entre INICIO y FIN del fichero
      for line in flist:
         line = line.rstrip()
         if 'COM' in line:
            #cuando se encuentra la linea que contine COM se guarda el nombre
            contN2=Contingencias_N2()
            contN2.Description=unicode(line.split('\'')[1].decode('unicode_escape'))
            continue
         if line.startswith("OPEN") and i==0:
            #cuando se encuentra la primera linea OPEN se guarda BUS1, BUS2 y ckt
            contN2.Npss_1=line.split()[4]
            contN2.Npss_2 =line.split()[7]
            contN2.ckt_1 =line.split()[9]
            i=i+1
            continue
         if line.startswith("OPEN") and i==1:
            #cuando se encuentra la segunda linea OPEN se guarda BUS1, BUS2 y ckt
            contN2.Npss2_1=line.split()[4]
            contN2.Npss2_2 =line.split()[7]
            contN2.ckt_2 =line.split()[9]
            i=0
            continue
         if line.startswith("CONTINGENCY"):
            #cuando se encuentra la linea CONTIGENCY se guarda el identificador de la contigencia
            contN2.Name=line
            continue
         elif line.startswith("END") and contN2!=[]:
            #cuando se encuentra la linea END y se han guardado datos, se añade la contingencia al listado
            contingencias_dobles.append(contN2)
            contN2 = []

      return contingencias_dobles

   except Exception as e:
      raise StandardError('Error en la obtencion de las contingencias N-2: {}'.format(e.message))

def normalizar(info_casos, prob_total):

   #se recorren todos los valores de prob. de la clase creada y se modifican para que la prob. total sea 1
   for x in info_casos:
      x.Probabilidad=x.Probabilidad/prob_total

   return info_casos