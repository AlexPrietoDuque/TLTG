# coding=utf-8
#---------------------------------------------------------------------------------------------------
# Name:        redpsse.py
# Purpose:     Módulo que contiene todas las funciones útiles para recuperar los elementos de PSSE
#              Ejemplo: get_maq_list() te devuelve todas las máquinas del caso PSSE cargado
# Author:      Ricardo Vázquez(las funciones malas) Alejandro Prieto (las mejores funciones)
# Created:     2017-12-01
#---------------------------------------------------------------------------------------------------
import os
from tempfile import mkstemp
from datetime import datetime as dt
import datosree
import entidades
import time
import psspy
import pssarrays
import contextlib
import sys
import cStringIO
import re


_i, _f, _s = psspy.getdefaultint(), psspy.getdefaultreal(), psspy.getdefaultchar()

sum_bar_sep=entidades.sum_bar_sep

class CasoPSSE(object):

   __prev_case_fname = '.'.join([mkstemp(prefix='temp_case_')[1], 'sav']) # Nombre único del caso temporal que se
                                                                          # guarda para cargarlo al hacer close()
   def __init__(self, filepath, log=None):
      """Clase que representa un caso PSSE. Sus atributos están definidos en el propio código.

      Si el parámetro reload_prev es True, el caso PSSE previamente cargado en memoria se guarda temporalmente y,
      tras inicializar todos los parámetros, se vuelve a cargar. Esto se ha hecho para que si se está trabajando
      con un caso, se pueda consultar el caso filepath sin que se quede cargado en memoria y no interfiera en los
      programas que lo utilizan. Tras cargar el caso previo, el archivo temporal se borrará.

      Nota: Se añade el parámetro load_code (mirar en :param load_code) para indicar si se carga el caso
      al inicializar la instancia de CasoPSSE y si se leer los atributos de demanda, generación, etc. Esto se
      ha hecho para que al aprovechar para crear los objetos (muchas veces desde una listay al haber cargado ya el caso se lean los atributos.

      TODO: idea: hacer que al hacer alguna consulta o modificación PSSE se checkee si el caso cargado en memoria
                  es el mismo que filename

      :param str filepath: ruta completa al archivo del caso (.sav o .raw)
      :param int load_code: código de carga:\n
               load_code = 0:    No se carga el caso al inicializar la instancia
               load_code = 1:    Se carga el caso pero no se leen los atributos (demanda, gen_eol, etc)
                                 al inicializar la instancia
               load_code = 2:    Se carga el caso y se leen todos los atributos (demanda, gen_eol, etc)
                                 al inicializar la instancia
               load_code = 3:    Se carga el caso, se leen todos los atributos (demanda, gen_eol, etc) y
                                 se converge el caso (fnsl) al inicializar la instancia.

      :param bool reload:
         indica si se quiere cargar el caso previamente guardado en memoria tras finalizar la inicialización
      :param bool converger: indica si se quiere converger el caso con un fnsl para comprobar convergencia
      :param logging.Logger log: log
      :rtype: redpsse.CasoPSSE

      :Example:

         >>> import GE_ClasesPSSE
         >>> log, rutaLog, fichLog = creaLog(__file__, 'log','MAIN','Nueva','','','')
         >>> case = 'D:\\Generador_Escenarios\\GE_PSSE\\Fich_Resultados\\Casos_ED2\\01\\18\\ED2_20180118_00.sav'
         >>> caso = CasoPSSE(filepath=case, log=log, reload_prev=False, converger=False)

      .. note::
         Si se cambia el formato del nombre de los casos hay que revisar la lógica de lectura.
      """
      self.read_ok = None # True si ha se ha cargado correctamente el caso / False si no se ha cargado

      # Parámetros de entrada
      self.filepath = filepath # Ruta completa
      self.log = log

      # Inicilización atributos
      # formato (sav, raw), nombre del caso y fecha/tipo caso del nombre del caso
      _, self.format = os.path.splitext(self.filepath) #.sav / .raw
      self.format = self.format.lower() #.sav / .raw
      if self.format not in ['.raw', '.sav']: return # TODO mejorar esto
      self.filename = os.path.basename(self.filepath) # nombre completo (e.g. 'ED2_20180118_00.sav')
      self.__timestamp = None #  datetime 2018-01-16 14:00:00. Se obtiene con get_timestamp()
      self.__case_type = None # ED2, ECP, etc. Se obtiene con get_case_type()

      # lectura del caso
      self.demanda = None # demanda modelada [MW]
      self.gen_ter = None # generación térmica
      self.gen_eolica = None # generación eólica [MW]
      self.gen_pv = None # generación fotovoltaica [MW]
      self.gen_ts = None # generación termosola [MW]
      self.gen_hid = None # generación hidraulica [MW]
      self.gen_swing = None # generación del nudo swing [MW]

      self.sc_110 = None # Sobrecarga de ramas por encima del 110%
      self.sc_115 = None # Sobrecarga de ramas por encima del 115%
      self.sobre_t = None
      self.sub_t = None

      self.int_fr = None # intercambio FR-ES
      self.int_pt = None # intercambio PT-ES
      self.int_ma = None # intercambio MA-ES
      self.converge = None # indica convergencia

      # indica si hay que volver a cargar el caso psse previamente cargado en memoria tras cerrar este
      self.reload = None  #

   # region CARGA y CIERRE
   def load(self, save_previous=False):
      """Carga el caso PSSE en memoria

      :param bool save_previous: Indica si se quiere guardar el caso previo en un archivo temporal para
         poder cargarlo luego al hacer close()
      :return:
      """
      if save_previous:
         self.reload = True
         ierr = psspy.save(self.__prev_case_fname)
         if ierr != 0:
            raise IOError(u'No se ha podido salvar el caso temporal previo <{}>'.format(self.__prev_case_fname))
      else:
         self.reload = False

         # Compruebo al extension del archivo
      extension = os.path.splitext(self.filepath)[1][1:]

      if extension.upper() == "RAW":
         # Se carga el caso .raw
         ierr = psspy.read(0, self.filepath)
      else:
         # Se carga el caso .sav
         ierr = psspy.case(self.filepath)

      if ierr != 0:
         self.read_ok = False
         if self.log != None:
            self.log.error(u'No se ha podido cargar el caso <{}>'.format(self.filepath))
         raise RuntimeError(u'No se ha podido cargar el caso <{}>'.format(self.filepath))
         # hacer un RAISE quiza sea un poco bestia, pero es importante que quede bien claro
         # cuando no se puede cargar un caso
      else:
         self.read_ok = True

   def save(self,path_file):

      ierr = psspy.save(path_file)

      if ierr!=0:
         raise StandardError('Error al gurdar el caso {}'.format(ierr))


   def close(self):
      """ Función que carga el caso previo si al usar el método load() se indico save_previous == True

      :return:
      """
      if self.reload:
         if os.path.isfile(self.__prev_case_fname):
            # Se vuelve a cargar el caso previo
            ierr = psspy.case(self.__prev_case_fname)
            if ierr != 0:
               raise IOError(u'No se ha podido cargar el caso previo <{}>'.format(self.__prev_case_fname))
            os.remove(self.__prev_case_fname)
   # endregion

   # region GETTERS y SETTERS
   def set_interchanges(self, int_fr, int_pt, int_ma, int_bal, log):
      """ Función que modifica los intercambios al caso

      Se comprueba que el caso está cargado en menmoria y si no lo carga

      :param float int_fr: intercambio con Francia
      :param float int_pt: intercambio con Portugal
      :param float int_ma: intercambio con Marruecos
      :param float int_bal: intercambio con Baleares
      :param log: log
      :return: retorna si se ha modificado correctamente (True/False)
      :rtype: bool
      """
      # Se comprueba que el caso instanciado esté cargado
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso'
                           u'cargado no es el correcto. Se procede a cargar el caso con self.load().')
         self.load()

      # Se modifican los intercambios del caso
      all_ok = set_interchanges(int_fr, int_pt, int_ma, int_bal, log)

      # Se cierra el caso y se carga el anterior
      self.close()

      return all_ok

   def get_interchanges(self, update=False):
      """Método que devuelve los intercambios con areas extrangeras (FR, PT, MA)

      :param bool update: indica si se quiere forzar a leer de psse aunque el atributo ya exista
      :return: int_fr, int_pt, int_ma
      :rtype: float, float, float
      """
      if not self.int_fr or update:
         self.int_fr = self.__psse_read_interchange(area=8)

      if not self.int_pt or update:
         self.int_pt = self.__psse_read_interchange(area=6)

      if not self.int_ma or update:
         self.int_ma = self.__psse_read_interchange(area=7)

      return self.int_fr, self.int_pt, self.int_ma

   def get_gen_eol(self, areas=None, update=False):
      """Método que devuelve la generación eólica total de las areas deseadas

      Si no se indican areas, se dejan por defecto las españolas

      :param list areas: listado de areas de las que se quiere leer el dato. (Por defecto las españolas)
      :param bool update: indica si se quiere forzar a leer de psse aunque el atributo ya exista
      :rtype: float
      """
      if not self.gen_eolica or update:
         self.gen_eolica = self.__psse_read_maqs_pgen(['EOL'], areas=areas)

      return self.gen_eolica

   def get_gen_hid(self, areas=None, update=False):
      """Método que devuelve la generación hidraulica total de las areas deseadas

      Si no se indican areas, se dejan por defecto las españolas

      :param list areas: listado de areas de las que se quiere leer el dato. (Por defecto las españolas)
      :param bool update: indica si se quiere forzar a leer de psse aunque el atributo ya exista
      :rtype: float
      """
      if not self.gen_hid or update:
         self.gen_hid = self.__psse_read_maqs_pgen(['HID'], areas=areas)

      return self.gen_hid

   def get_gen_pv(self, areas=None, update=False):
      """Método que devuelve la generación fotovoltaica total de las areas deseadas

      Si no se indican areas, se dejan por defecto las españolas

      :param list areas: listado de areas de las que se quiere leer el dato. (Por defecto las españolas)
      :param bool update: indica si se quiere forzar a leer de psse aunque el atributo ya exista
      :rtype: float
      """
      if not self.gen_pv or update:
         self.gen_pv = self.__psse_read_maqs_pgen(['FV'], areas=areas)

      return self.gen_pv

   def get_gen_ts(self, areas=None, update=False):
      """Método que devuelve la generación termosolar total de las areas deseadas

      Si no se indican areas, se dejan por defecto las españolas

      :param list areas: listado de areas de las que se quiere leer el dato. (Por defecto las españolas)
      :param bool update: indica si se quiere forzar a leer de psse aunque el atributo ya exista
      :rtype: float
      """
      if not self.gen_ts or update:
         self.gen_ts = self.__psse_read_maqs_pgen(['TS'], areas=areas)

      return self.gen_ts

   def get_gen_ter(self, areas=None, update=False):
      """Método que devuelve la generación termosolar total de las areas deseadas

      Si no se indican areas, se dejan por defecto las españolas

      :param list areas: listado de areas de las que se quiere leer el dato. (Por defecto las españolas)
      :param bool update: indica si se quiere forzar a leer de psse aunque el atributo ya exista
      :rtype: float
      """
      if not self.gen_ter or update:
         self.gen_ter = self.__psse_read_maqs_pgen(['TER'], areas=areas)

      return self.gen_ter

   def get_gen_swing(self, update=False):
      """Método que devuelve la generación en el swing

      :param bool update: indica si se quiere forzar a leer de psse aunque el atributo ya exista
      :rtype: float
      """
      if not self.gen_swing or update:
         self.gen_swing = self.__psse_read_swing()

      return self.gen_swing

   def get_demanda(self, update=False):
      """Método que devuelve la demanda modelada total de España

      en el caso

      :param update: indica si se quiere leer de nuevo el dato en el caso psse
      :return:
      """
      if not self.demanda or update:
         self.__psse_read_demanda()

      return self.demanda

   def get_sobrecargas(self, update=False):
      """Función que lee las sobrecargas del caso (>115 y >110 %)

      :param bool update: indica si se quiere leer de nuevo el dato en el caso psse
      :return:
      """
      if not (self.sc_110 and self.sc_115) or update:
         self.sc_115, self.sc_110 = self.__psse_read_pctrta()

      return self.sc_115, self.sc_110

   def get_sobresub_tensiones(self, update=False):
      """Función que lee las sobretensiones y subtensiones del caso

      :param bool update: indica si se quiere leer de nuevo el dato en el caso psse
      :return:
      """
      if not (self.sobre_t and self.sub_t) or update:
         self.sobre_t, self.sub_t = self.__psse_read_sobresub_tensiones()

      return self.sobre_t, self.sub_t

   def get_timestamp(self, dt_format='%Y%m%d_%H', split_pos=1, split_pos_hour=2, sep='_'):
      """Método para obtener timestamp del caso (e.g. datetime.datetime(2018, 2, 24, 16, 30))

      NOTA: Se puede indicar el formato del nombre del caso para poder leer la fecha de cualquier caso
         que contenga la información. El caso por defecto es el de resultados GENES.

      Ejemplos:
         - 'ED2_20180102_23.sav':
               split_pos=1; split_pos_hour=2; dt_format='%Y%m%d_%H'; sep='_'
         - 'ED2_CAPINT_ES-FR_20180116_00_2400.sav':
               split_pos=3; split_pos_hour=4; dt_format='%Y%m%d_%H'; sep='_'
         - 'bla-blabla-2018010223-bla.sav'
               split_pos=2; split_pos_hour=2; dt_format='%Y%m%d%H'; sep='-'


      :param int split_pos_hour: posición de la hora. Ver Nota
      :param int split_pos: posicion de la fecha. Ver Nota
      :param str sep: separador
      :param str dt_format: formato de la fecha contentida en el nombre del caso
      :rtype: datetime.datetime
      """
      ts_str = None
      fname_split = self.filename.split(sep)

      # Se saca el tipo de caso y la fecha en formato str
      try:
         if split_pos != split_pos_hour:
            # ejemplo: '20180228_23'
            ts_str = fname_split[split_pos] + sep + fname_split[split_pos_hour].split('.')[0]
         else:
            # ejemplo: '2018022823'
            ts_str = fname_split[split_pos].split('.')[0]
      except IndexError:
         # se quedan en None
         self.log.error(u'<class CasoPSSE> El formato del nombre del caso no es el esperado. Leer '
                        u'documentación de CasoPSSE.get_timestamp() filename: <{}> [Traceback]'. format(self.filename))

      # Se convierte la fecha en str a datetime
      try:
         self.__timestamp = dt.strptime(ts_str, dt_format)
      except Exception as e:
         self.log.error(u'<class CasoPSSE> El formato de la fecha en el nombre del caso no es el esperado. Leer '
                        u'documentación de CasoPSSE.get_timestamp() filename: <{}> [Traceback] {}'. format(
            self.filename, e.message))

      return self.__timestamp

   def get_case_type(self, split_pos=0, sep='_'):
      """Función que obtiene el tipo de caso (ED2, DACF, etc)

      a partir del nombre del caso

      Ejemplos:
         'ED2_20180102_23.sav'
            split_pos=0; sep='_'
         'blabla-bla-ED2-bla.sav'
            split_pos=2; sep='-'

      :param str sep: separador
      :param int split_pos: indica la posición del tipo de caso en el nombre del caso

      """
      try:
         fname_split = self.filename.split(sep)
         self.__case_type = fname_split[split_pos]
      except IndexError:
         # se quedan en None
         self.log.error(u'<class CasoPSSE> El formato del nombre del caso no es el esperado. Leer '
                        u'documentación de CasoPSSE.get_case_type() filename: <{}> [Traceback]'. format(self.filename))

      return self.__case_type

   def get_num_total_bus(self):
      return psspy.totbus()
   # endregion

   # region OTROS
   def fnsl(self, ajustInt=1, ajDesf=0):
      """Función que hace un Newton_Raphson del caso para ver si converge

      :return:
      """
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso'
                           u'cargado no es el correcto. Se procede a cargar el caso con self.load().')
         self.load()

      if self.read_ok:
         psspy.fnsl([0, ajustInt, ajDesf, 0, 0, 0, 0, 0])
         ival = psspy.solved()
         self.converge =  True if ival == 0 else False

   def update_filepath(self, new_path):
      """Función que le cambia la ruta a un caso (al moverlo)

      :param str new_path: ruta al directorio nuevo (sin el nombre del caso)
      :return:
      """
      self.filepath = os.path.join(new_path, self.filename)
   # endregion

   # region LOG
   def disable_log(self):
      """Función que inhabilita el log

      Esta función se utiliza para cuando se quiere usar multiprocessing. Si se quiere hacer multiprocessing
      a una función que tiene como parámetro una lista de instancias de esta clase el log da problemas ya que todas
      las instancias tendrían el mismo log y dicho log estaría en varios procesos distintos, cosa que no es deseable
      (ni posible)

      IMPORTANTE: Si se usa este método para inhabilitar el log, se le tiene que volver a asignar otro log
         ANTES de volver a utilizar la instancia caso

      :return:
      """
      self.log = None

   def set_log(self, new_log):
      """Función que vuelve a asignar un log a la instancia

      Esta función se utiliza para cuando se quiere usar multiprocessing. Si se quiere hacer multiprocessing
      a una función que tiene como parámetro una lista de instancias de esta clase el log da problemas ya que todas
      las instancias tendrían el mismo log y dicho log estaría en varios procesos distintos, cosa que no es deseable
      (ni posible)

      :param new_log: nuevo log
      :return:
      """
      self.log = new_log
   # endregion


   # region PRIVADOS
   def __psse_check_if_loaded(self):
      """Comprueba si el caso de esta isntancia (self.filename) está cargado en memoria

      :return:
      """
      current_case_loaded = psspy.sfiles()[0] # devuelve la ruta del caso cargado en memoria
      current_case_loaded = os.path.normpath(current_case_loaded)
      instance_case = os.path.normpath(self.filepath)

      if current_case_loaded == instance_case:
         return True
      else:
         return False

   def __load_prev_case(self):
      """Método privado para cargar y después borrar el caso previo en memoria al final de la inicialización
      """
      # Se vuelve a cargar el caso previo
      ierr = psspy.case(self.__prev_case_fname)
      if ierr != 0: self.log.error(u'<class CasoPSSE> No se ha podido cargar el caso previo <{}>'.format(
         self.__prev_case_fname))

      # Se borra el caso SAV previo temporal
      if os.path.isfile(self.__prev_case_fname): os.remove(self.__prev_case_fname)

   def __psse_read_demanda(self):
      """Método privado para leer la demanda total del caso (áreas españolas)
      """
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso cargado no es '
                        u'el correcto. Se procede a cargar el caso con self.load(). <{}>'.format(self.filename))
         self.load()

      total_demand = 0.0

      # Se lee la demanda de todas las areas españolas
      ierr, (area, slack) = psspy.aareaint(sid=-1, flag=2, string=['NUMBER', 'SWING'])

      if ierr != 0: return

      are = [ar for ar in area if ar not in datosree.areExt]
      for ar in are:
         # Obtenemos nombre de área y potencia instalada y real.
         ierr, are_demand = psspy.ardat(ar,'LOAD')
         if ierr == 0:
            total_demand += round(are_demand.real, 2)

      self.demanda = total_demand

   def __psse_read_swing(self):
      """Método privado para leer la generación en el SWING
      """
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso'
                        u'cargado no es el correcto. Se procede a cargar el caso con self.load().')
         self.load()

      # Se busca el nudo swing y se lee su generacion
      gen_swing = None
      sid = -1; flag = 2; are = list()
      ierr, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])
      for areai, slacki in zip(area, slack):
         ierr, codeBus_swing = psspy.busint(slacki, 'TYPE')
         if ierr == 0:
            if codeBus_swing == 3:  # el nudo es swing
               nbus_swing = slacki
               ierr = psspy.inimac(nbus_swing)
               while ierr == 0:
                  ierr, id_swing = psspy.nxtmac(nbus_swing)
                  if ierr != 0: break
                  ierr, st = psspy.macint(nbus_swing, id_swing, 'STATUS')
                  if ierr == 0 and st == 1:
                     swingValido = True
                     # Sacamos el valor de potencia
                     ierr, pq_gen = psspy.macdt2(nbus_swing, id_swing, 'PQ')
                     if ierr == 0:
                        gen_swing = pq_gen.real
                        break

      try:
         gen_swing = round(gen_swing, 2)
      except Exception:
         self.log.error(u'No se ha podido leer la generación del nudo swing. filepath: <{}>'.format(self.filepath))

      return gen_swing

   def __psse_read_interc(self, area):
      """Método privado para leer la generación total eólica del caso (areas españolas)
      """
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso'
                           u'cargado no es el correcto. Se procede a cargar el caso con self.load().')
         self.load()

      # TODO

   def __psse_read_maqs_pgen(self, tecs, areas=None):
      """Método privado para leer la generación total de las máquinas deseadas del caso

      tecas deberá ser una lista de las tecnologías deseadas. Ejemplo:
         tecs=['TER'] # para las termicas en general
         tecs=['HID', 'NUC'] # para las hidraulicas y las nucleares

      Si no se indican areas, se dejan por defecto las españolas

      :param list tecs: listado de tecnologias deseadas
      :param list areas: listado de areas de las que se quiere leer el dato. (Por defecto las españolas)
      """
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso'
                        u'cargado no es el correcto. Se procede a cargar el caso con self.load().')
         self.load()

      # Se obtiene un listado de objetos de todas las máquinas deseadas del caso
      maqs = get_maq_list(areas)

      # Se filtra el listado para quedarse con las máquinas deseadas conectadas (status = 1)
      maqs = [x for x in maqs if x.tec in tecs and x.status == 1 and x.pgen != 0.0]

      # Calculamos la generación total como suma del PGen de todas las máquinas deseadas
      return round(sum([maq.pgen for maq in maqs]), 2)

   def __psse_read_interchange(self, area):
      """Método privado para leer el intercambio con un area

      :param int area: area de la que se quiere saber el intercambio
      :rtype: float
      """
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso'
                        u'cargado no es el correcto. Se procede a cargar el caso con self.load().')
         self.load()

      ierr, inter = psspy.ardat(area, 'INT')

      if ierr != 0:
         self.log.error(u'No se ha leído el intercambio correctamente (ierr!=0). area <{}>'.format(area))
         inter =  None
      else:
         inter = round(inter.real, 2)

      return inter

   def __psse_read_pctrta(self):
      """Función privada que lee las sobrecargas (>115 y >110%)

      :return:
      """
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso'
                        u'cargado no es el correcto. Se procede a cargar el caso con self.load().')
         self.load()

      sid = -1; flag = 2; are = list()
      ierr1, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])
      are = [ar for ar in area if ar not in datosree.areExt]

      sid = 1
      ierr2 = psspy.bsys(sid, usekv=1, basekv=[220.0, 400.0], numarea=len(are), areas=are)

      ierr3, (froms, tos) = psspy.abrnint(sid, 1, 3, 3, 1, ['FROMNUMBER', 'TONUMBER'])

      ierr4, (ckteses,) = psspy.abrnchar(sid, 1, 3, 3, 1, ['ID'])

      branch_list = zip(froms, tos, ckteses)
      contadorSobrecargasRamas115 = 0
      contadorSobrecargasRamas100 = 0
      for fr, to, id in branch_list:
         ierr5, porcentajeCarga = psspy.brnmsc(fr, to, id, 'PCTRTA')
         if porcentajeCarga > 115:
            contadorSobrecargasRamas115 += 1

         if porcentajeCarga > 100:
            contadorSobrecargasRamas100 += 1

      if any([ierr != 0 for ierr in [ierr1, ierr2, ierr3, ierr4, ierr5]]):
         self.log.error(u'No se ha podido leer el número de sobrecargas 110 y 115. ierrs: {}'.format(
            [ierr1, ierr2, ierr3, ierr4, ierr5]))

      return contadorSobrecargasRamas115, contadorSobrecargasRamas100

   def __psse_read_sobresub_tensiones(self):
      """Función privada que lee las sobretensiones y subtensiones

      :return:
      """
      if not self.__psse_check_if_loaded():
         self.log.error(u'PRECAUCION: se esta ejecutando una llamada a la API ppspy pero el caso'
                        u'cargado no es el correcto. Se procede a cargar el caso con self.load().')
         self.load()

      sid = -1; flag = 2; are = list()
      ierr, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])
      are = [ar for ar in area if ar not in datosree.areExt]

      sid = 1
      ierr = psspy.bsys(sid, usekv=1, basekv=[220.0, 400.0], numarea=len(are), areas=are)

      ierr, (froms, tos) = psspy.abrnint(sid, 1, 3, 3, 1, ['FROMNUMBER', 'TONUMBER'])

      ierr, (ckteses,) = psspy.abrnchar(sid, 1, 3, 3, 1, ['ID'])

      ierr, (buses,) = psspy.abusint(sid, 1, ['NUMBER'])

      # Defino los contadores
      contadorSobretensionesInforme = 0
      contadorSubtensionesInforme = 0
      contadorSobretensiones400 = 0
      contadorSubtensiones400 = 0
      contadorSobretensiones220 = 0
      contadorSubtensiones220 = 0

      # recorremos los buses y definimos el vpu
      for bus in buses:
         ierr, baseVolt = psspy.busdat(bus, 'BASE')
         ierr, volt = psspy.busdat(bus, 'KV')
         vpu = volt / baseVolt
         if baseVolt == 400:  # en el caso de que la tensión base sea 400V
            if vpu > 1.075:
               contadorSobretensiones400 += 1

            elif vpu < 0.987:
               contadorSubtensiones400 += 1

         if baseVolt == 220:  # en el caso de que la tensión base sea 220V
            if vpu > 1.091:
               contadorSobretensiones220 += 1

            elif vpu < 0.932:
               contadorSubtensiones220 += 1

      contadorSobretensionesInforme = contadorSobretensiones220 + contadorSobretensiones400
      contadorSubtensionesInforme = contadorSubtensiones220 + contadorSubtensiones400

      return contadorSobretensionesInforme, contadorSubtensionesInforme
   # endregion

# -------------------------------------------------------
# Funcion para comprobar la reactiva del nudo swing.
# Si esta generando reactiva superior a 10 veces
# sus límites de Q, consideramos que el caso tiene algún
# problema de convergencia:

def checkQswing():

   swing = 0; problemasConv = 0
   for ar in range(1,100):
      ival = psspy.areuse(ar) #Ve si el area está en uso
      if ival == 1:
         ierr, swing = psspy.areint(ar,'SWING')
         if ierr == 0 and swing != 0:
            ierr, busCode = psspy.busint(swing,'TYPE')
            if busCode == 3: #se trata de nudo swing
               ierr, cmpval = psspy.gendat(swing) #generación en el nudo swing
               if ierr == 0:
                  Qgen = cmpval.imag  #parte imaginaria: Q
                  #Recorrido por las maquinas del nudo swing:
                  ierr2 = psspy.inimac(swing)
                  QmaxSw = 0; QminSw = 0
                  while 1:
                     ierr2, idmaq = psspy.nxtmac(swing)
                     if ierr2 != 0: break
                     ierr2, Qmax = psspy.macdat(swing, idmaq, 'QMAX')
                     ierr2, Qmin = psspy.macdat(swing, idmaq, 'QMIN')
                     QmaxSw = QmaxSw + Qmax; QminSw = QminSw + Qmin
                  if (Qgen < 20*QminSw) or (Qgen > 20*QmaxSw):
                     problemasConv = 1
               return problemasConv

# -------------------------------------------------------
# Funcion para obtener la solucion del flujo de cargas:

def solFC():
   ival = psspy.solved()
   if ival == 0:
      convSol = "Met convergence tolerance"
   elif ival == 1:
      convSol = "Iteration limit exceeded"
   elif ival == 2:
      convSol = "Blown up"
   elif ival == 3:
      convSol = "Terminated by non-divergent option"
   elif ival == 4:
      convSol = "Terminated by console interrupt"
   elif ival == 5:
      convSol = "Singular Jacobian matrix or voltage of 0.0 detected"
   elif ival == 6:
      convSol = "Inertial power flow dispatch error"
   elif ival == 7:
      convSol = "OPF solution met convergence tolerance"
   else:
      convSol = "Solution not attempted"
   return convSol

def convergeCaso():
   ajustInt=0
   ajustDesf=0
   converge=False

   # Eliminamos posibles islas:
   ierr = psspy.island()

   #Converge con Full N-R:
   psspy.fnsl([0,ajustInt,ajustDesf,0,0,0,0,0])
   #Comprueba convergencia:
   convSol = solFC()

   if convSol != "Met convergence tolerance": #nuevo intento
      psspy.fnsl([0,ajustInt,ajustDesf,0,0,0,0,0])
      convSol = solFC()

   #Comprobamos la reactiva del swing, por si tuviera valores anormales
   problemasConv = checkQswing()
   if problemasConv == 1: #Swing con Qgen anormalmente elevada
      #Newton-Raphson desacoplado, flat start, ignorar limites de reactiva
      psspy.fdns([_i,_i,_i,_i,_i,1,-1,_i])
      #Full Newton-Raphson con límites de reactiva desde la 4ª iteración
      psspy.fnsl([0,0,0,0,0,0,4,0])
      #Full Newton-Raphson con límites de reactiva desde la 1ª iteración y
      #con los ajustes de intercambio y Phase shift que correspondan
      psspy.fnsl([0,ajustInt,ajustDesf,0,0,0,0,0])
      convSol = solFC()

   if convSol != "Met convergence tolerance":
      #Cambiamos parámetros de solución del flujo de cargas
      # Iteraciones máximas en N.Raphson = 50
      # N.Raphson mismatch convergence tolerance = 0.4
      # Automatic adjustment threshold tolerance = 0.2
      psspy.solution_parameters_3([_i,50,_i],[_f,_f,_f,_f,_f, 0.4,_f,_f,_f,_f,_f, 0.2,_f,_f,_f,_f,_f,_f,_f])
      #Newton-Raphson desacoplado, flat start, ignorar limites de reactiva
      psspy.fdns([_i,_i,_i,_i,_i,1,-1,_i])
      #Recuperamos los parámetros de solución originales (por defecto) excepto nº iteraciones
      psspy.solution_parameters_3([_i,50,_i],[_f,_f,_f,_f,_f, 0.1,_f,_f,_f,_f,_f, 0.005,_f,_f,_f,_f,_f,_f,_f])
      convSol = solFC()
      if convSol != "Met convergence tolerance":
         #Newton-Raphson desacoplado, ignorar limites de reactiva. Sin flat start
         psspy.fdns([_i,_i,_i,_i,_i,0,-1,_i])
      #Full Newton-Raphson con límites de reactiva desde la 1ª iteración y
      #con los ajustes de intercambio y Phase shift que correspondan
      psspy.fnsl([0,ajustInt,ajustDesf,0,0,0,0,0])
      convSol = solFC()

   if convSol != "Met convergence tolerance": #nuevo intento
      psspy.fnsl([0,ajustInt,ajustDesf,0,0,0,0,0])
      convSol = solFC()

   if convSol != "Met convergence tolerance":
      #Full Newton-Raphson con flat start:
      psspy.fnsl([0,0,0,0,0,1,0,0])
      #Full Newton-Raphson sin flat start, con límites de reactiva desde la 4ª iteración:
      psspy.fnsl([0,0,0,0,0,0,4,0])
      #Full Newton-Raphson con límites de reactiva desde la 1ª iteración y
      #con los ajustes de intercambio y Phase shift que correspondan
      psspy.fnsl([0,ajustInt,ajustDesf,0,0,0,0,0])
      convSol = solFC()

   if convSol != "Met convergence tolerance":
      #Full Newton-Raphson con non-divergent solution
      psspy.fnsl([0, 0, 0, 0, 0, 0, 0, 1])
      convSol = solFC()

   if convSol == "Met convergence tolerance":
      #Comprobamos la reactiva del swing, por si tuviera valores anormales aunque esté convergido
      problemasConv = checkQswing()
      if problemasConv == 1: #Swing con Qgen anormalmente elevada
         convSol = "Solution not attempted" #Lo consideramos no convergido. Decisión del lado conservador

   if convSol=='Met convergence tolerance':
      converge = True


   return converge

# region Machine
def get_maq_list(areas=None, init_derived=True):
   """
   Función para obtener una lista de objetos (class Machine) con todas las máquinas del caso cargado

   Se recuperarán todas las máquinas del caso (conectadas y desconectadas) pertenecientes a las areas
   indicadas por el parámetro areas. **Si no se especifica ningún área se usarán las areas españolas por defecto**
   Si areas=''all' SE COGERA TODAS LAS AERAS DEL SISTEMA

   **Mirar la documentación de la clase `GE_ClasesPSSE.Machine`** para más información

   :param list of int areas:
      lista de areas (enteros) de las cuales se quieren sacar las máquinas. Si no se le pasa ningún valor, se toman
      por defecto las areas españolas
   :param init_derived: Pra cambiar el numero de bus en caos de encontar la mauina en barra separadas
   :return: devuelve una lista de máquians de la calse Machine

   :rtype: list of entidades.Machine

   :Example:

      >>> # Se obtiene un listado de objetos de todas las máquinas del caso
      >>> maqs = get_maq_list()

      >>> # Se filtra el listado para quedarse con las que están conectadas (status = 1) y
      >>> # pertenecientes a las tecnologías térmica e hidráulica. Excluir si están en pgen = 0.0
      >>> maqs = [x for x in maqs if x.tec in ['TER', 'HID'] and x.status == 1 and x.pgen != 0.0]

   .. :todo: queda meterle un log por si falla
   """
   # Se definen las areas de las que se leen las ramas
   if areas is None:
      # Obtengo áreas:
      sid = -1
      flag = 2
      ierr, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])

      if ierr != 0: return []

      are = [ar for ar in area if ar not in datosree.areExt]
   elif areas == 'all':
      # Obtengo áreas:
      sid = -1
      flag = 2
      ierr, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])

      if ierr != 0: return []

      are = [ar for ar in area]

   elif isinstance(areas, list):
      are = areas
   else:
      return None

   # Definimos subsistema
   sid = 1; flag = 4  # all machines
   ierr = psspy.bsys(sid, numarea=len(are), areas=are)

   # Obtenemos el bus
   ierr, (bus, status) = psspy.amachint(sid=sid, flag=flag, string=['NUMBER', 'STATUS'])

   # Obtenemos el identificador
   ierr, (idn, name) = psspy.amachchar(sid=sid, flag=flag, string=['ID', 'NAME'])
   # Obtenemos valores de Pmax, Pmin y Mbase

   ierr, (pgen, qgen, pmax, pmin, qmax, qmin, mbase) = psspy.amachreal(sid=sid, flag=flag,
                                                                       string=['PGEN', 'QGEN', 'PMAX', 'PMIN',
                                                                               'QMAX', 'QMIN', 'MBASE'])

##   # Se obtiene el area y la zona. amachint no proporciona este dato; hay que sacarlo con abusint
##   ierr, (busnums, area, zone) = psspy.abusint(sid=sid, flag=2, string=['NUMBER','AREA', 'ZONE'])
##
##   bus_list = zip(busnums, area, zone)

   # Se zipea
   maq_zip_list = zip(bus, status, idn, name, pgen, qgen, pmax, pmin, qmax, qmin, mbase)

   maq_list = []
   for busi, statusi, idni, namei, pgeni, qgeni, pmaxi, pmini, qmaxi, qmini, mbasei in maq_zip_list:
      # Se obtiene el area y la zona
##      area_zone_tup = [item for item in bus_list if item[0] == busi]
##      areai = area_zone_tup[0][1]
##      zonei = area_zone_tup[0][2]
      ierr, bus_zone = psspy.busint(busi, 'ZONE')
      ierr, bus_area = psspy.busint(busi, 'AREA')
      ierr, bus_type = psspy.busint(busi, 'TYPE')

      s_ = time.clock()
      maq = entidades.Machine(bus_num=busi, bus_area=bus_area, bus_zone=bus_zone, bus_type=bus_type, status=statusi, idn=idni, name=namei, pgen=pgeni,
                              qgen=qgeni, pmax=pmaxi, pmin=pmini, qmax=qmaxi, qmin=qmini, mbase=mbasei, init_derived=init_derived)
      maq_list.append(maq)


   return maq_list

def get_maq_list_by_tecnologias(list_ids_tecnologia,areas=None, init_derived=False):
   """
   Retorna un lisatod e las maquinas del caso asociados a ciertos tecnologias
   :param list_ids_tecnologia: list de str de los ids de las tecnologias
   :param init_derived: Para no cambiar los bus_num en caso de encontrarse la mauina en una barra separada
   :return:
   """

   list_maqu=get_maq_list(areas=None, init_derived=False)

   list_maqu=filter(lambda x: x.idn[-1:] in list_ids_tecnologia,list_maqu)

   return list_maqu

def get_maq(bus, id_):
   pass
   #TODO

def get_generadores(sid):
   listaGens = []

   string=['NUMBER']
   char=['ID']
   ierr, machs = psspy.amachcount(sid, 4)
   ierr, iarray = psspy.amachint(sid, 4, string)
   if ierr !=0:
      raise StandardError('Error al obtner el amachint de las maquinas={}'.format(ierr))
   ierr, carray = psspy.amachchar(sid, 4, char)
   if ierr != 0:
      raise StandardError('Error al obtner  el amachchar de las maquinas={}'.format(ierr))

   for i in range(0, machs, 1):
      listaGens.append(entidades.Machine(bus_num=iarray[0][i],idn=carray[0][i],init_derived=False))



   return listaGens

def check_machine(list_machine, bus_num, ckt):
   """
   Chequea si existe una maquina dentor de un listado de maquinas
   :param list_machine: listado de mauinas donde buscar la maquina
   :type list_machine: entidades.Machine
   :param bus_num:
   :param ckt:
   :return:
   """
   machine=[]

   machine=filter(lambda x: (x.bus_num==bus_num and x.idn==ckt) or (x.bus_num==bus_num+sum_bar_sep and x.idn==ckt), list_machine)

   return machine

def get_generadores_by_bus(num_bus):
   try:
      lit_gen=[]

      sid_id = create_susbsistem_by_buses([num_bus], 0)
      lit_gen =get_generadores(sid_id)

      return lit_gen
   except Exception as e:
      raise StandardError('Error al obneter las maquinas sobre el bus={}: '.format(num_bus, e.message))

# endregion

# region Branchs
def get_branch_list(bus=None, areas=None):
   """
   Función para obtener una lista de objetos (class Branch) con todas las ramas del caso

   **Si no se especifica un bus, se recuperarán todas las ramas del caso** (conectadas y desconectadas; trafos y lineas)
   pertenecientes a las areas indicadas por el parámetro areas.

   **Si no se especifica ningún área se usarán las areas españolas por defecto. Para usar todas ares=all**


   **Mirar la documentación de la clase `.entidades.Branch`** para más información

   :param int bus: (opcional) bus del que se quieren sacar las ramas salientes
   :param list of int areas: (opcional)
      lista de areas (enteros) de las cuales se quieren sacar las máquinas. Si no se le pasa ningún valor, se toman
      por defecto las areas españolas
   :return: devuelve una lista de ramas de la clase Branch
   :rtype: list of entidades.Branch

   :Example:

      Pendiente

   .. :todo: queda meterle un log por si falla
   """
   # Se definen las areas de las que se leen las ramas
   if areas is None:
      # Obtengo áreas:
      sid = -1
      flag = 2
      ierr, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])
      are = [ar for ar in area if ar not in datosree.areExt]
   elif areas == 'all':
      # Obtengo áreas:
      sid = -1
      flag = 2
      ierr, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])
      are = area
   elif isinstance(areas, list):
      are = areas
   else:
      return None

   brn_list = []
   if bus is None: # Todas las ramas del caso
      # Definimos subsistema
      sid = 1; flag = 4  # all branches
      ierr = psspy.bsys(sid, numarea=len(are), areas=are)

      # Obtenemos los enteros
      ierr, (bus_from, bus_to, status, owner_1, owner_2, metered) = psspy.abrnint(sid=sid, owner=2, ties=3, flag=flag, entry=1,
                                                                          string=['FROMNUMBER', 'TONUMBER', 'STATUS',
                                                                                  'OWN1', 'OWN2', 'METERNUMBER'])
      # Obtenemos los strings
      ierr, (idn, from_name, to_name) = psspy.abrnchar(sid=sid, owner=2, ties=3, flag=flag, entry=1,
                                                       string=['ID', 'FROMNAME', 'TONAME'])
      # Obtenemos los reales y complejos
      ierr, (rate_a, rate_b, rate_c, charg) = psspy.abrnreal(sid=sid, owner=2, ties=3, flag=flag, entry=1,
                                                                          string=['RATEA', 'RATEB', 'RATEC', 'CHARGING'])

      ierr, (rx, ) = psspy.abrncplx(sid=sid, owner=2, ties=3, flag=flag, entry=1, string=['RX'])

      # Se zipea
      brn_zip_list = zip(bus_from, bus_to, status, owner_1, owner_2, metered, idn, from_name, to_name, rate_a, rate_b,
                         rate_c, charg, rx)

      for bus_fromi, bus_toi, statusi, owner_1i, owner_2i, meteredi, idni, from_namei, \
          to_namei, rate_ai, rate_bi, rate_ci, chargi, rxi in brn_zip_list:
         brn = entidades.Branch(from_bus=bus_fromi, to_bus=bus_toi, status=statusi, idn=idni, from_name=from_namei, to_name=to_namei, rx=rxi, b=chargi, metered=meteredi,
                   rate_a=rate_ai, rate_b=rate_bi, rate_c=rate_ci, owner_1=owner_1i, owner_2=owner_2i)
         brn_list.append(brn)

   else: # solo las de un bus

      ier = psspy.inibrx(bus, 2)

      while ier == 0:
         ier, bus_j,bus_k, ckt = psspy.nxtbrn3(bus)
         if ier != 0: break

         ierr, status = psspy.brnint(bus, bus_j, ckt.strip(), 'STATUS')
         ierr, owner_1 = psspy.brnint(bus, bus_j, ckt.strip(), 'OWN1')
         ierr, owner_2 = psspy.brnint(bus, bus_j, ckt.strip(), 'OWN2')
         ierr, metered = psspy.brnint(bus, bus_j, ckt.strip(), 'METER')

         ierr, from_name = psspy.notona(bus)
         ierr, to_name = psspy.notona(bus_j)

         ierr, rate_a = psspy.brndat(bus, bus_j, ckt.strip(), 'RATEA')
         ierr, rate_b = psspy.brndat(bus, bus_j, ckt.strip(), 'RATEB')
         ierr, rate_c = psspy.brndat(bus, bus_j, ckt.strip(), 'RATEC')
         ierr, charg = psspy.brndat(bus, bus_j, ckt.strip(), 'CHARG')

         ierr, rx = psspy.brndt2(bus, bus_j, ckt.strip(), 'RX')

         brn = entidades.Branch(from_bus=bus, to_bus=bus_j, status=status, idn=ckt.strip(), from_name=from_name,
                                to_name=to_name, rx=rx, b=charg, metered=metered,
                                rate_a=rate_a, rate_b=rate_b, rate_c=rate_c, owner_1=owner_1, owner_2=owner_2, bus_k=bus_k)
         brn_list.append(brn)

   return brn_list

def check_linea(list_lineas,from_bus, to_bus, ckt):
   """
     Comprueba si existe los FACT para un nudo origen y destino. La comprobacion tambien se realiza sobre barras separadas
     :param list_lineas: listado de facts
     :type list_lineas: list of entidades.Branch
     :param from_bus: nudo origen
     :param to_bus: nudo destino
     :return: retorna los un facts si existe sino un []
     :rtype: entidades.Branch or list
     """
   linea = []
   linea = filter(lambda x: (x.from_bus == from_bus and x.to_bus == to_bus and x.idn==ckt) or
                             (x.from_bus == from_bus+sum_bar_sep and x.to_bus == to_bus and x.idn==ckt) or
                             (x.from_bus == from_bus and x.to_bus == to_bus+sum_bar_sep and x.idn==ckt) or
                             (x.from_bus == from_bus + sum_bar_sep and x.to_bus == to_bus+sum_bar_sep and x.idn==ckt) or
                             (x.from_bus == to_bus and x.to_bus == from_bus and x.idn==ckt) or  #Comprobacion para sobre el otro sentido
                             (x.from_bus == to_bus+sum_bar_sep and x.to_bus == from_bus and x.idn==ckt) or
                             (x.from_bus == to_bus  and x.to_bus == from_bus + sum_bar_sep and x.idn==ckt) or
                             (x.from_bus == to_bus+ sum_bar_sep  and x.to_bus == from_bus + sum_bar_sep and x.idn==ckt),list_lineas)

   if linea.__len__() > 0:
      linea = linea[0]

   return linea

def get_branch_list_2(bus=None):
   if bus !=None:
      sid = 0
      create_susbsistem_by_buses(list_bus=[bus], sid_id=0)
   else:
      sid=-1

   brn_list=[]
   flag = 4  # all branches


   # Obtenemos los enteros
   ierr, (bus_from, bus_to, status, owner_1, owner_2, metered) = psspy.abrnint(sid=sid, owner=2, ties=3, flag=flag,
                                                                               entry=1,
                                                                               string=['FROMNUMBER', 'TONUMBER',
                                                                                       'STATUS',
                                                                                       'OWN1', 'OWN2', 'METERNUMBER'])
   # Obtenemos los strings
   ierr, (idn, from_name, to_name) = psspy.abrnchar(sid=sid, owner=2, ties=3, flag=flag, entry=1,
                                                    string=['ID', 'FROMNAME', 'TONAME'])
   # Obtenemos los reales y complejos
   ierr, (rate_a, rate_b, rate_c, charg) = psspy.abrnreal(sid=sid, owner=2, ties=3, flag=flag, entry=1,
                                                          string=['RATEA', 'RATEB', 'RATEC', 'CHARGING'])

   ierr, (rx,) = psspy.abrncplx(sid=sid, owner=2, ties=3, flag=flag, entry=1, string=['RX'])

   # Se zipea
   brn_zip_list = zip(bus_from, bus_to, status, owner_1, owner_2, metered, idn, from_name, to_name, rate_a, rate_b,
                      rate_c, charg, rx)

   for bus_fromi, bus_toi, statusi, owner_1i, owner_2i, meteredi, idni, from_namei, \
       to_namei, rate_ai, rate_bi, rate_ci, chargi, rxi in brn_zip_list:
      brn = entidades.Branch(from_bus=bus_fromi, to_bus=bus_toi, status=statusi, idn=idni, from_name=from_namei,
                             to_name=to_namei, rx=rxi, b=chargi, metered=meteredi,
                             rate_a=rate_ai, rate_b=rate_bi, rate_c=rate_ci, owner_1=owner_1i, owner_2=owner_2i)
      brn_list.append(brn)

   return brn_list
# endregion

# region SW
def get_swsh_list():
   """
   Función para obtener una lista de objetos (class SwitchedShunt) con todas los switched shunts del caso cargado

   Se recuperarán todas los switched shunts del caso (conectados y desconectados) pertenecientes a las areas
   indicadas por el parámetro areas. **Si no se especifica ningún área se usarán las areas españolas por defecto**

   **Mirar la documentación de la clase `utilpsse.redpsse.SwitchedShunt`** para más información

   :param list of int areas:
      lista de areas (enteros) de las cuales se quieren sacar los switched shunts. Si no se le pasa ningún valor,
      se toman por defecto las areas españolas
   :return: devuelve una lista de witched shunts de la clase SwitchedShunt
   :rtype: list of entidades.SwitchedShunt

   :Example:

      >>> # Se obtiene un listado de objetos de todas las máquinas del caso
      >>> maqs = get_maq_list()

      >>> # Se filtra el listado para quedarse con las que están conectadas (status = 1) y
      >>> # pertenecientes a las tecnologías térmica e hidráulica. Excluir si están en pgen = 0.0
      >>> maqs = [x for x in maqs if x.tec in ['TER', 'HID'] and x.status == 1 and x.pgen != 0.0]

   .. :todo: queda meterle un log por si falla
   """
   # TODO Una vez acabada la clase SwitchedShunt, terminar esta func usando aSwshInt, etc, com oen get_maq_list
   pass

def get_desc_sws():
   pass

def get_swing_info():
   """Función que devuelve la generación en el swing, su número de PSSE y su ID

   :return:
   """

   gen_swing = None
   nbus_swing = None
   id_swing = None
   area_swing = None

   # Se busca el nudo swing y se lee su generacion
   sid = -1; flag = 2
   ierr, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])
   for areai, slacki in zip(area, slack):
      ierr, codeBus_swing = psspy.busint(slacki, 'TYPE')
      if ierr == 0:
         if codeBus_swing == 3:  # el nudo es swing
            nbus_swing = slacki
            ierr = psspy.inimac(nbus_swing)
            while ierr == 0:
               ierr, id_swing = psspy.nxtmac(nbus_swing)
               if ierr != 0: break
               ierr, st = psspy.macint(nbus_swing, id_swing, 'STATUS')
               if ierr == 0 and st == 1:
                  swingValido = True
                  # Sacamos el valor de potencia
                  ierr, pq_gen = psspy.macdt2(nbus_swing, id_swing, 'PQ')
                  if ierr == 0:
                     gen_swing = pq_gen.real
                     area_swing = areai
                     break
   if gen_swing: gen_swing = round(gen_swing, 2)


   return gen_swing, nbus_swing, id_swing, area_swing

def change_x_swing_trafo(div, log):
   log.info(u'Cambiando la REACTANCIA del TRAFO de generación del SWING...')
   # Se obtiene el bus donde está el generador del swing
   gen_swing, nbus_swing, id_swing, area_swing = get_swing_info()
   log.info(u'INFO SWING: gen_swing: <{}>, nbus_swing <{}>, id_swing <{}>, area_swing <{}>'.format(
      gen_swing, nbus_swing, id_swing, area_swing))

   # Se obtienen las ramas que salen del nudo del swing
   brn_list = get_branch_list(nbus_swing)

   # Se filtra la lista dejando solo las ramas correspondientes a trafos de generacion
   brn_list = [brn for brn in brn_list if brn.is_gen_trafo]

   if not brn_list:
      log.warning(u'No se ha encontrado el tranformador de generación del SWING. No se '
                  u'ha podido modificar su X')
   else:
      gen_trafo = brn_list[0]
      old_x = gen_trafo.x
      new_x = old_x / div
      gen_trafo.set_x(new_x)

      log.info(u'Se ha cambiado la reactancia del trafo del swing de <{}> a <{}>'.format(old_x, new_x))

def get_sw_to_bus(bus_num):
      """ Retorna el SW asociado aun bus
      :param bus_num: numero del bus donde se comprueba si existe un SW
      :return: instancia de la clase SwitchedShunt. En caso de que no exista retorna un None
      :rtype:entidadesSwitchedShunt
      """
      ierr, ival = psspy.swsint(bus_num, 'STATUS')
      sw = None
      if ierr == 0:
         sw = entidades.SwitchedShunt(bus_num=bus_num)
      return sw
# endregion

# region LOADS
def get_load(sid=-1):
   list_load=[]
   flag=4
   ierr, buses = psspy.aloadcount(sid, flag)
   if ierr!=0:
      raise StandardError('Error al alodbuscount. Cod={}'.format(ierr))

   if buses>0:
      string=['NAME', 'EXNAME','ID']
      ierr, carray = psspy.aloadchar(sid, flag, string)
      if ierr != 0:
         raise StandardError('Error al alodbuschar. Cod={}'.format(ierr))

      string_2=['NUMBER', 'AREA', 'ZONE','OWNER','STATUS','SCALE']
      ierr, iarray = psspy.aloadint(sid, flag, string_2)

      for i in range(0,buses, 1):
         list_load.append(entidades.Load(bus_num=iarray[0][i],bus_area=iarray[1][i],
                                         bus_zone=iarray[2][i],owner=iarray[3][i],status=iarray[4][i],scale=iarray[5][i],
                                         idn=carray[2][i]))

   return list_load

def get_load_to_bus(bus_num):

   loads = []

   try:
      create_susbsistem_by_buses(sid_id=0,list_bus=[bus_num])
      loads=get_load(0)
   except Exception as e:

      raise StandardError('Error al obtner las load: {}'.format(e.message))

   #
   # ierr = psspy.inilod(bus_num)
   #
   # if ierr == 0:
   #    ier, id = psspy.nxtlod(bus_num)
   #    while ier == 0:
   #       loads.append(entidades.Load(bus_num=bus_num, idn=id))
   #       ier, id = psspy.nxtlod(bus_num)
   #
   return loads
# endregion



def set_interchanges(int_fr, int_pt, int_ma, int_bal, log):
   """ Función que modifica los intercambios al caso cargado en memoria

   IMPORTANTE: Esta función modifica los intercambios al caso PSSE cargado en memoria. Se debe asegurar que
      el caso al que se le queire cambiar los intercambios está cargado en memoria

   :param float int_fr: intercambio con Francia
   :param float int_pt: intercambio con Portugal
   :param float int_ma: intercambio con Marruecos
   :param float int_bal: intercambio con Baleares
   :param log: log
   :return:
   """
   all_ok = True

   # Francia
   if int_fr is not None:
      ierr = psspy.area_data(8, _i, [int_fr, _f], _s)
      if ierr != 0:
         log.error(u'No se ha ajustado el intercambio con Francia. ierr!=0')
         all_ok = False
   else:
      log.error(u'No se ha ajustado el intercambio con Francia. Venía con valor None')
      all_ok = False

   # Portugal
   if int_pt is not None:
      ierr = psspy.area_data(6, _i, [int_pt, _f], _s)
      if ierr != 0:
         log.error(u'No se ha ajustado el intercambio con Portugal. ierr!=0')
         all_ok = False
   else:
      log.error(u'No se ha ajustado el intercambio con Portugal. Venía con valor None')
      all_ok = False

   # Marruecos
   if int_ma is not None:
      ierr = psspy.area_data(7, _i, [int_ma, _f], _s)
      if ierr != 0:
         log.error(u'No se ha ajustado el intercambio con Marruecos. ierr!=0')
         all_ok = False
   else:
      log.error(u'No se ha ajustado el intercambio con Marruecos. Venía con valor None')
      all_ok = False

   # Baleares
   if int_bal is not None:
      try:
         # Para Baleares, se modifica el valor de las cargas de las estaciones conversoras de Morvedre
         # Chequeo que existan los nudos de las estaciones conversoras
         ecMor1 = 14044
         ecMor2 = 14046
         ierr1 = psspy.busexs(ecMor1)
         ierr2 = psspy.busexs(ecMor2)
         if ierr1 == 1:
            ierr1 = psspy.busexs(ecMor1 + 40000)
            if ierr1 == 0:
               ecMor1 = ecMor1 + 40000
         if ierr2 == 1:
            ierr2 = psspy.busexs(ecMor2 + 40000)
            if ierr2 == 0:
               ecMor2 = ecMor2 + 40000

         # Si existen las cargas de las dos estaciones conversoras, reparto el intercambio entre las 2
         # Si solo existe una l estacion conversora en servicio le asigno todo el intercambio a 1 cargaZ
         if ierr1 == 0 and ierr2 == 0:
            # Reparto entre las dos cargas
            tipoBus1 = psspy.busint(ecMor1, 'TYPE')
            tipoBus2 = psspy.busint(ecMor2, 'TYPE')
            if tipoBus1 < 4 and tipoBus2 < 4:
               psspy.load_chng_4(ecMor1, '99', [_i, _i, _i, _i, _i, _i],
                                 [int_bal / 2, _f, _f, _f, _f, _f])
               psspy.load_chng_4(ecMor2, '99', [_i, _i, _i, _i, _i, _i],
                                 [int_bal / 2, _f, _f, _f, _f, _f])
            elif tipoBus1 < 4 and tipoBus2 == 4:
               psspy.load_chng_4(ecMor1, '99', [_i, _i, _i, _i, _i, _i], [int_bal, _f, _f, _f, _f, _f])
            elif tipoBus1 == 4 and tipoBus2 < 4:
               psspy.load_chng_4(ecMor2, '99', [_i, _i, _i, _i, _i, _i], [int_bal, _f, _f, _f, _f, _f])
         elif ierr1 == 0 and ierr2 == 1:
            tipoBus = psspy.busint(ecMor1, 'TYPE')
            if tipoBus < 4:
               psspy.load_chng_4(ecMor1, '99', [_i, _i, _i, _i, _i, _i], [int_bal, _f, _f, _f, _f, _f])
         elif ierr1 == 1 and ierr2 == 0:
            tipoBus = psspy.busint(ecMor2, 'TYPE')
            if tipoBus < 4:
               psspy.load_chng_4(ecMor2, '99', [_i, _i, _i, _i, _i, _i], [int_bal, _f, _f, _f, _f, _f])
         else:
            all_ok = False
      except Exception:
         log.error(u'Ha ocurrido un erroral modificar el intercambio con Baleares.')
         all_ok = False
   else:
      log.error(u'No se ha ajustado el intercambio con Baleares. Venía con valor None')
      all_ok = False

   return all_ok

def close_discharged_elements():
   """Función que lleva a cabo el cierre de las lineas/trafos/shunts abiertas por descargo

   IMPORTANTE: Esta función detecta las lineas abiertas por descargo mediante el owner.
      Se sigue la lógica en la que si una linea/trafo/shunt tiene owner=9999 en PSSE es que fue abierta
      por descargo

   :return:
   """
   sid = -1
   flag = 2
   ierr, (area, slack) = psspy.aareaint(sid=sid, flag=flag, string=['NUMBER', 'SWING'])
   are = [ar for ar in area if ar not in datosree.areExt]
   sid = 1
   ierr = psspy.bsys(sid, numowner=1, owners=[9999], numarea=len(are), areas=are)
   ierr, (buses_from, buses_to,) = psspy.abrnint(sid, owner=2, ties=3, flag=4, string=['FROMNUMBER', 'TONUMBER'])
   ierr, (ckteses,) = psspy.abrnchar(sid, owner=2, ties=3, flag=4, string=['ID'])
   lista_ramas_cerrar = zip(buses_from, buses_to, ckteses)
   for bus_from, busTo, ckt in lista_ramas_cerrar:
      ierr, ival = psspy.xfrint(bus_from, busTo, ckt, 'NTPOSN')
      if ierr == 0:
         psspy.two_winding_chng_4(bus_from, busTo, ckt, [1, _i, 1, _i, _i, _i, _i, _i, _i, _i, _i, _i, _i, _i, _i],
                                  [_f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f,
                                   _f, _f, _f], ["", ""])
      elif ierr == 3:
         psspy.branch_chng(bus_from, busTo, ckt, [1, _i, 1, _i, _i, _i],
                           [_f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f])

   ierr, (buses_shunts,) = psspy.aswshint(sid, flag=4, string=['NUMBER'])
   for bus_shunt in buses_shunts:
      psspy.bus_chng_3(bus_shunt, [_i, _i, _i, 1], [_f, _f, _f, _f, _f, _f, _f], _s)
      psspy.switched_shunt_chng_3(bus_shunt, [_i, _i, _i, _i, _i, _i, _i, _i, _i, _i, 1, _i],
                                  [_f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f], "")



def get_nudos_asociados(bus_num,list_ramas=None):
   """
   Obtiene los nudos conectados a un bus en concreto
   :param bus: numero de bus
   :param list_ramas: listado de ramas.
   :type bus: int
   :type list_ramas: list of entidades.Branch
   :return: listados Bus() de los nudos asociados
   :rtype nudos_asociados:list of entidades.Bus
   """
   nudos_asociados=[]
   if list_ramas==None:
      list_ramas=get_branch_list(bus=bus_num,areas='all')
   else:
      list_ramas = filter(lambda x: x.to_bus==bus_num or x.from_bus==bus_num,list_ramas )


   for brach in list_ramas:
      if brach.to_bus == bus_num: #Si el nudo de destino es el de busqueda, me quedo con el nudo de orgien
         nudos_asociados.append(entidades.Bus(bus_num=brach.from_bus))
      else:#Si no con el nudo de destino
         nudos_asociados.append(entidades.Bus(bus_num=brach.to_bus))

   return nudos_asociados

def get_nudos_T(bus_num, list_nudosT, list_ramas):
   """
   Retorna los nudos T conectados a un bus. Hasta un segundo nivel, es decir, si el nudo tiene un nudo en T , se compurba si este nudo en t tiene mas nudo en T asociados

   :param bus: bus sobre el cual se desa obtener lo nudos en t
   :type bus:entidades.Bus
   :param list_nudosT: listado de int donde se especifican los nudos en t de la red
   :type list_nudosT: list of int
   :param list_ramas: Listado de are (int) necdesarios para obtener los nudos asociados a bus
   :type list_ramas: list of entidades.Branch
   :return: listado de int de los nudos en t asociados al bus. En caso de que sea vacia no se tiene nudos en t
   :rtype: list of entidades.Bus
   """
   nudosT = []
   nudosT_segundo = []

   #Comprobacion de primer nivel
   buses_asocia = get_nudos_asociados(bus_num, list_ramas=list_ramas) # Obtengo los los nudos asociados al bus de simulacion.
   for bus_aso in buses_asocia:

      if bus_aso.bus_num in list_nudosT: #Compruebo si los bus asocidas al bus de simulacion estan en la listade nudos en T
         nudosT.append(bus_aso) #Añdo el bus a la listade  nudos en T

   #Comprobacion de segundo nivel (sobre los nudos en T asociados al nudo de simualcion)
   for bus in nudosT:
      buses_asocia = get_nudos_asociados(bus.bus_num, list_ramas=list_ramas) #Extraigo los nudos asociados al nudo T

      for bus_aso in buses_asocia:
         if bus_aso.bus_num in list_nudosT:
            nudosT_segundo.append(bus_aso)

   if nudosT_segundo !=[]:
      nudosT += nudosT_segundo

   return nudosT

# region Simulaciones dinamicas
def configurar_modelo_avisos3(idata):
   """
   Cambia los parammetros del modelo avisos 3
   :param idata: datos
   :type idata: entidades.ParamAvisos3
   :return:
   """

   if (idata.AplicaPgenEol  and idata.AplicaPgenTer ):
      ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 1, 2)
      if ierr!=0:
         raise ValueError ('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   elif (not idata.AplicaPgenEol  and not idata.AplicaPgenTer):
      ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 1, 1)
      if ierr!=0:
         raise ValueError ('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))
   elif (idata.AplicaPgenEol == 1 and not idata.AplicaPgenTer ):
      ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 1, 3)
      if ierr!=0:
         raise ValueError ('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))
   elif (not idata.AplicaPgenEol and idata.AplicaPgenTer ):
      ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 1, 4)
      if ierr!=0:
         raise ValueError ('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 2, idata.NET_Max)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 3, idata.MinDRS)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 4, idata.SelecMon)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 5, idata.AreZon_1)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 6, idata.AreZon_2)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 7, idata.AreZon_3)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 8, idata.AreZon_4)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 9, idata.AreZon_5)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 10, idata.AreZon_6)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 11, idata.AreZon_7)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 12, idata.AreZon_8)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 13, idata.AreZon_9)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_icon('Avisos3', 1, 14, idata.AreZon_10)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   #######

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 1, idata.Ret_DRS)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 2, idata.Ret_PS)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 3, idata.Perdgen)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 4, idata.PorcDCMax)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 5, idata.Ret_PG)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 6, idata.VinfEst400)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 7, idata.VinfEst220)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 8, idata.VinfEst132)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 9, idata.VinfEst50)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 10, idata.VinfEst30)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 11, idata.VsupEst400)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 12, idata.VsupEst220)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 13, idata.VsupEst132)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 14, idata.VsupEst50)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 15, idata.VsupEst30)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 16, idata.OVERLestLIN)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))


   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 17, idata.OVERLestLIN)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

   ierr = psspy.change_cctmscomod_con('Avisos3', 1, 18, idata.OVERLestTR)
   if ierr != 0:
      raise ValueError('Error al cambiar los paraemtros del aviso 3: {}'.format(ierr))

def generar_archivo_snap(file_path=None):
   if file_path !=None:
      file_path=os.path.join(file_path,"Fiche005.snp")
   else:
      file_path = "Fiche005.snp"

   if os.path.isfile(file_path):
      os.remove(file_path)
   ierr=psspy.snap([-1, -1, -1, -1, -1], file_path)
   if ierr>0:
      raise ValueError ('Error al generar los achivos de snap: {}'.format(ierr))

def generar_archivo_strt(file_path=None):
   if file_path != None:
      file_path = os.path.join(file_path, "strt.sal")
   else:
      file_path = "strt.sal"

   if os.path.isfile(file_path):
      #os.remove(file_path)
      pass
   ierr = psspy.strt(0, file_path)
   if ierr > 0:
      raise ValueError('Error al generar los achivos de snap: {}'.format(ierr))
# endregion

# region Caso PSSE
def check_load_case():
   current_case_loaded =psspy.sfiles()[0]
   load=False
   if current_case_loaded !='':
      load=True

   return load

def get_path_case_load():
   """
   Retorna el path del caso psse cargado en memoria
   :return:
   """
   current_case_loaded = psspy.sfiles()[0]
   return current_case_loaded
# endregion



def get_elementos_bus(bus_num):
   """Obtiene los elementos conectados a un bus en concreto

   :param int bus_num: numero del bus del cual se desae extaer los elementos conectados
   :return: listado de elementos conectados al bus. Retorna un listado de clases, cada clases corrsponde con el tipo de elementos (Trasformer, Branch...).
      Para saber que tipo de ellentos se puee hacer filtrados del tipos:  trafos=filter(lambda x: isinstance(x, entidades.Transformer), elementos)
   :rtype entidades.ElementList
   """
   list_elementos=[]
   branchs_to_bus=get_branch_list_2(bus=bus_num)

   trafos=get_trafo_by_bus(bus_num)
   if trafos!=[]:
      list_elementos.extend(trafos)


   for branch in branchs_to_bus:

      # if branch.is_trafo: #Elemento es un trafo
      #    trafo=entidades.Transformer(bus_i=branch.from_bus, bus_j=branch.to_bus, idn=branch.idn)
      #    list_elementos.append(trafo)
      # else:
      #    list_elementos.append(branch)
      if not branch.is_trafo:
         list_elementos.append(branch)


   generadores=get_generadores_by_bus(bus_num)
   loads = get_load_to_bus(bus_num)

   [list_elementos.append(gen) for gen in generadores]
   [list_elementos.append(load) for load in loads]

   sw_shunt=get_sw_to_bus(bus_num)
   if sw_shunt !=None:
      list_elementos.append(sw_shunt)


   list_elementos= entidades.ElementList(list_elementos)

   return list_elementos


# region VSC
def get_vscs():
   """
   Rotorna la todosd lo facts del caso
   :return:
   :rtype: entidades.Fact
   """

   try:

      list=[]
      ierr, brnchs = psspy.avscdccount(-1, 3, 3)

      ierr, iarray_NAMES = psspy.avscdcchar(-1, 3, 3, ['VSCNAME','FROMEXNAME','TOEXNAME'])
      if ierr != 0:
         raise StandardError('Error al obenter el FACTSNAME de los FACTS. Cod={}'.format(ierr))

      ierr, iarray_BUSNUMBER = psspy.avscdcint(-1, 3, 3, ['FROMNUMBER','TONUMBER'])
      if ierr != 0:
         raise StandardError('Error al obenter el FROMNUMBER y  el TONUMBER  de los vscs. Cod={}'.format(ierr))

      i=0
      for i in range(0,brnchs,1):
         list.append(entidades.Vsc(name=iarray_NAMES[0][i],convert1_bus_num= iarray_BUSNUMBER[0][i],convert2_bus_num=iarray_BUSNUMBER[1][i],
                                         convert1_name=iarray_NAMES[1][i],convert2_name=iarray_NAMES[2][i]))


      return list

   except Exception as e :
      raise StandardError('{}'.format(e))

def get_names_vsc():
   """
   Retorna un listado con los nombre de las lineas vsc
   :return:
   """
   list_name_vsc=[]

   ierr = psspy.inivsc()

   if ierr == 0:
      ier,line_name = psspy.nxtvsc()
      while ier==0:
         list_name_vsc.append(line_name)
         ier, line_name = psspy.nxtvsc()

   return list_name_vsc

def check_vsc_line(name, bus):
   existe=True
   ierr, ival=psspy.vsccdt(name, bus, 'MVA')
   if ierr!=0:
      existe=False

   return existe

def check_vsc(list_vscs, from_bus, to_bus):
   """
   Comprueba si existe los FACT para un nudo origen y destino.
   :param list_vscs: listado de facts
   :type list_vscs: list of entidades.Vsc
   :param from_bus: nudo origen
   :param to_bus: nudo destino
   :return: retorna los un facts si existe sino un []
   :rtype: entidades.Vsc or list
   """
   list=[]
   list=filter(lambda x: (x.convert1_bus_num == from_bus and x.convert2_bus_num == to_bus)or
                                (x.convert1_bus_num == to_bus and x.convert2_bus_num == from_bus), list_vscs)

   if list.__len__()>0:
      list=list[0]

   return list
# endregion


# region FACTS
def get_facts():
   """
   Rotorna la todosd lo facts del caso
   :return:
   :rtype: entidades.Fact
   """

   try:

      list_facts=[]
      ierr, brnchs = psspy.afactscount(-1, 3, 2, 3)

      ierr, iarray_NAMES = psspy.afactschar(-1, 3, 2, 3, ['FACTSNAME','FROMEXNAME','TOEXNAME'])
      if ierr != 0:
         raise StandardError('Error al obenter el FACTSNAME de los FACTS. Cod={}'.format(ierr))

      ierr, iarray_BUSNUMBER = psspy.afactsint(-1, 3, 2, 3, ['SENDNUMBER','TERMNUMBER'])
      if ierr != 0:
         raise StandardError('Error al obenter el TERMNUMBER y el SENDNUMBER de los FACTS. Cod={}'.format(ierr))

      i=0
      for i in range(0,brnchs,1):
         list_facts.append(entidades.Fact(name=iarray_NAMES[0][i],send_bus_num=iarray_BUSNUMBER[0][i],terminal_bus_num=iarray_BUSNUMBER[1][i],
                                          send_bus_name=iarray_NAMES[1][i],terminal_bus_name=iarray_NAMES[2][i]))


      return list_facts

   except Exception as e :
      raise StandardError('{}'.format(e))

def get_names_facts():
   """
   Retorna el numero de buses que son VSC
   :return:
   """
   list_name_vsc=[]

   ierr = psspy.inifax()

   if ierr == 0:
      ier,line_name = psspy.nxtfax()
      while ier==0:
         list_name_vsc.append(line_name)
         ier, line_name = psspy.nxtfax()



   return list_name_vsc

def check_facts(list_facts, from_bus, to_bus):
   """
   Comprueba si existe los FACT para un nudo origen y destino. La comprobacion tambien se realiza sobre barras separadas
   :param list_facts: listado de facts
   :type list_facts: list of entidades.Fact
   :param from_bus: nudo origen
   :param to_bus: nudo destino
   :return: retorna los un facts si existe sino un []
   :rtype: entidades.Fact or list
   """

   fact=filter(lambda x: (x.send_bus_num == from_bus and x.terminal_bus_num == to_bus)
                          or (x.send_bus_num == from_bus + sum_bar_sep and x.terminal_bus_num == to_bus)
                          or (x.send_bus_num == from_bus and x.terminal_bus_num == to_bus + sum_bar_sep)
                          or (x.send_bus_num == from_bus + sum_bar_sep and x.terminal_bus_num == to_bus + sum_bar_sep)
                    or (x.send_bus_num == to_bus and x.terminal_bus_num == from_bus)
                                or (x.send_bus_num == to_bus + sum_bar_sep and x.terminal_bus_num == from_bus)
                                or (x.send_bus_num == to_bus and x.terminal_bus_num == from_bus + sum_bar_sep)
                                or (x.send_bus_num == to_bus+sum_bar_sep and x.terminal_bus_num == from_bus + sum_bar_sep), list_facts)

   if fact.__len__()>0:
      fact=fact[0]

   return fact
# endregion

def get_bus_number_used(buslower=1, bushigh=999997):
   """
   Rentorna un listado de int con todos los numero de los bus usados.
   Si se espficia limietes superior e inferior se dara los buses no usados en ese rango
   :param buslower: los buses retornadaos será iguales o mayores a este limite
   :param bushigh: los buses retornadaos será igaules o menores a este limite
   :return:
   :rtype: list of int
   """

   list_bus=[]

   ierr, iarray = psspy.abusint(-1,2,'NUMBER')


   if ierr !=0:
      raise StandardError ('Error al obtner lo buses usados.Cod_erro= {}'.format(ierr))
   else:
      list_bus=iarray[0]
      list_bus=filter(lambda x: buslower<=x and x<=bushigh, list_bus)

   return list_bus

def get_bus_number_used_by_voltaje(voltajelower=1, voltajehigh=999997):
   """
   Rentorna un listado de int con todos los numero de los bus usados.
   Si se espficia limietes superior e inferior de los voltajes se obtendra los buses entre esos rangos de tensiones
   :param buslower: los buses retornados tendra voltajes iguales o mayores a este limite
   :param bushigh: los buses retornados tendra voltajes igaules o menores a este limite
   :return:
   :rtype: list of int
   """

   list_bus=[]
   ierr, buses = psspy.abuscount(-1,2)
   if ierr !=0:
      raise StandardError ('Error al obtner abuscount.Cod_erro= {}'.format(ierr))

   ierr, iarray = psspy.abusint(-1,2,'NUMBER')
   if ierr !=0:
      raise StandardError ('Error al obtner abusint .Cod_erro= {}'.format(ierr))

   ierr, rarray = psspy.abusreal(-1,2,'BASE')
   if ierr !=0:
      raise StandardError ('Error al obtner abusreal.Cod_erro= {}'.format(ierr))

   for i in range(0,buses,1):
      if voltajelower <=rarray[0][i] <= voltajehigh:
         list_bus.append(iarray[0][i])


   return list_bus

def get_bus_number_used_by_tension_tipo(Umin=1, Umax=999997, tipo=1):
   """
   Rentorna un listado de int con todos los numeros de buses usados y su tipo.
   Si se especifican los limites superior e inferior de las tensiones, se obtendran los buses en ese rangos.
   :param Umin: los buses retornados tendra tension igual o mayor a este limite
   :param Umax: los buses retornados tendra tension igaul o menor a este limite
   :return:
   :rtype:
   """

   list_bus=[]
   ierr, buses = psspy.abuscount(-1,2)
   if ierr !=0:
      raise StandardError ('Error al obtener abuscount. Cod_erro= {}'.format(ierr))

   ierr, iarray = psspy.abusint(-1,2,'NUMBER')
   if ierr !=0:
      raise StandardError ('Error al obtener abusin. Cod_erro= {}'.format(ierr))

   ierr, rarray = psspy.abusreal(-1,2,'BASE')
   if ierr !=0:
      raise StandardError ('Error al obtener abusreal. Cod_erro= {}'.format(ierr))

   for i in range(0,buses,1):
      if Umin <=rarray[0][i] <= Umax:
         ierr, ival = psspy.busint(iarray[0][i], 'TYPE')
         if ival==tipo:
            list_bus.append(iarray[0][i])

   return list_bus

def get_bus_number_by_area(lis_areas):
   """
   Obtiene los buses usados sobre un listado de areas
   :param lis_areas: list of int
   :type lis_areas: list of int
   :return:
   """
   try:
      list_bus = []
      ierr =psspy.bsys(0, 0, [1.0, 400.], lis_areas.__len__(), lis_areas, 0, [], 0, [], 0,[])
      if ierr != 0:
         raise StandardError('Al crear el susbsitema de areas. Cod={}'.format(ierr))

      ierr, iarray = psspy.abusint(0, 2, 'NUMBER')
      if ierr != 0:
         raise StandardError('Al obtner los buses. Cod={}'.format(ierr))
      else:
         list_bus = iarray[0]

      return list_bus


   except Exception as e:
      raise StandardError('Error al obtener los buses asociados a las areas: {}'.format(e.message))

def get_bus_number_by_zonas(lis_zonas):
   """
   Obtiene los buses usados sobre un listado de areas
   :param lis_zonas: list of int
   :type lis_zonas: list of int
   :return:
   """
   try:
      list_bus = []
      sid=0
      ierr=psspy.bsys(sid, 0, [1.0, 400.], 0, [], 0, [], 0, [],  lis_zonas.__len__(), lis_zonas)
      if ierr != 0:
         raise StandardError('Al crear el susbsitema de zonas. Cod={}'.format(ierr))

      ierr, iarray = psspy.abusint(sid, 2, 'NUMBER')
      if ierr != 0:
         raise StandardError('Al obtener los buses. Cod={}'.format(ierr))
      else:
         list_bus = iarray[0]

      return list_bus


   except Exception as e:
      raise StandardError('Error al obtener los buses asociados a las areas: {}'.format(e.message))

def get_bus_number_unsed(buslower=1, bushigh=999997, list_num_exclu=[]):
   """
   El primero numero de bus no usado denetro de un rango (ordenados de menor a mayor).
   Si se espficia limietes superior e inferior se dara los buses no usados en ese rango
   :param buslower: los buses retornadaos será iguales o mayores a este limite
   :param bushigh: los buses retornadaos será igaules o menores a este limite
   :param list_num_exclu: listado de los nudos que se deb excluir
   :return:
   :rtype: int
   """

   try:
      num_bus=None
      list_bus_used=get_bus_number_used(buslower, bushigh)

      ran= range(buslower, bushigh+1,1)

      for num in ran:
         if num  not in list_bus_used and  num not in list_num_exclu:
            num_bus=num
            break

      if num_bus==None:
         raise StandardError ('No existen buses libres en el rango {};{}'.format(buslower,bushigh))
      return num_bus
   except Exception as e:
      raise StandardError('Error al obtener los buses no usados. {}'.format(e.message))

def get_bus_by_voltaje_base(voltajebase):
   """
   Retoarn los numeros de buses apartir de un voltaje base
   :param: listado de int para indicar los voltajes base
   :return:
   :rtype: entidades.Bus
   """
   try:
      list_bus=[]
      ierr, buses = psspy.abuscount(-1, 2)

      if ierr != 0:
         raise StandardError('Cod_erro= {}'.format(ierr))
      else:
         ierr, iarray = psspy.abusint(-1, 2, 'NUMBER')
         ierr, rarray = psspy.abusreal(-1, 2, 'BASE')

         if ierr ==0:
            for i in range(0,buses,1):
               list_bus.append(entidades.Bus(bus_num=iarray[0][i], base_kv=rarray[0][i]))
               list_bus = filter(lambda x: x.base_kv in voltajebase, list_bus)
         else:

            raise StandardError('Cod_erro= {}'.format(ierr))
      return list_bus

   except Exception as e:
      raise StandardError('Error al obtener los buses a partir del voltaje. {}'.format(e.message))

def get_bus_voltaje_base(bus_num):
   """
   Obtiene el voltaje base de un bus dado
   :param bus_num:
   :return:
   """

   try:
      bus_base=0
      sid_id=create_susbsistem_by_buses([bus_num], 0)
      ierr, iarray = psspy.abusreal(sid_id,2,'BASE')

      bus_base=iarray[0][0]

      return bus_base


   except:
      pass

def get_areas():
   """
   Obtiene las areas de un caso
   :return:
   :rtype: list of entidades.Areas
   """
   list_ares=[]
   ierr, areas = psspy.aareacount(-1, 1)
   if ierr !=0:
      raise StandardError('Error al obtener el aareacount . Cod={}'.format(ierr))

   ierr, xarray = psspy.aareacplx(-1, 1, 'PQLOAD')
   if ierr != 0:
      raise StandardError('Error al obtener el aareacplx . Cod={}'.format(ierr))

   ierr, iarray = psspy.aareaint(-1, 1, ['NUMBER','BUSES'])
   if ierr != 0:
      raise StandardError('Error al obtener el aareaint . Cod={}'.format(ierr))

   ierr, carray = psspy.aareachar(-1, 1, 'AREANAME')
   if ierr != 0:
      raise StandardError('Error al obtener el aareachar . Cod={}'.format(ierr))

   ierr, rarray = psspy.aareareal(-1, 1, 'PGEN')
   if ierr != 0:
      raise StandardError('Error al obtener el aareareal . Cod={}'.format(ierr))

   for i in range(0,areas,1):
      list_ares.append(entidades.Area(number=iarray[0][i], name=carray[0][i],
                                       pload=xarray[0][i], buses=iarray[1][i]))

   return list_ares

def get_name_ext_to_bus(bus_num):
   """
   Retor al nombre 18 caracteres de un bus
   :param bus_num:
   :return:
   """
   name=''
   ierr, cval = psspy.notona(bus_num)
   if ierr !=0:
      raise StandardError('Error al obtener el nombre de bus. Cod={}'.format(ierr))
   name=cval

   return name

def get_zonas():
   """
     Obtiene las zonas de un caso
     :return:
     :rtype: list of entidades.Zona
   """
   list_zonas=[]
   ierr, zones = psspy.azonecount(-1, 1)
   if ierr !=0:
      raise StandardError('Error al obtener el azonecount . Cod={}'.format(ierr))

   ierr, carray = psspy.azonechar(-1, 1, 'ZONENAME')
   if ierr !=0:
      raise StandardError('Error al obtener el azonechar. Cod={}'.format(ierr))

   ierr, xarray = psspy.azonecplx(-1, 1, 'PQLOAD')

   if ierr !=0:
      raise StandardError('Error al obtener el azonecplx. Cod={}'.format(ierr))

   ierr, iarray = psspy.azoneint(-1, 1, ['NUMBER','BUSES'])

   if ierr != 0:
      raise StandardError('Error al obtener el azoneint. Cod={}'.format(ierr))

   for i in range(0,zones,1):
      list_zonas.append(entidades.Zona(number=iarray[0][i], name=carray[0][i],
                                       pload=xarray[0][i], buses=iarray[1][i]))

   return list_zonas




# region Transformer
def get_transformer_2dev(sid=-1):
   """
   Obtiene los trafos de 2 dev  y los de 3dev mdelados con un nudo de 1kv,
   sobre un subsistema (sid=-1 sobre todo el caso)
   :param sid: para indicar sobre que subsistema obtner los trafos (sid=-1 sobre todo el caso)
   :return: un listado de trafos
   :rtype: list of entidades.Transformer
   """

   owner=2
   ties=2
   flag=2
   entry=1

   try:
      list_trafo=[]

      ierr, brnchs = psspy.atrncount(sid, owner, ties, flag, entry)

      if brnchs>0:
         if ierr==0:
            string=['FROMNUMBER','TONUMBER','STATUS','METERNUMBER','NMETERNUMBER','OWNERS','OWN1','OWN2','OWN3','OWN4','ICONTNUMBER']
            string2 = ['ID', 'VECTORGROUP', 'XFRNAME','TOEXNAME','FROMEXNAME']
            string3 = ['RXACT', 'RXNOM']
            string4 = ['FRACT1', 'FRACT2','FRACT3','FRACT4','RATEA','RATEB','RATEC','ANGLE','SBASE1', 'RATIO', 'RATIO2']

            ierr, iarray = psspy.atrnint(sid, owner, ties, flag, entry, string)
            ierr2, carray = psspy.atrnchar(sid, owner, ties, flag, entry, string2)
            ierr3, xarray = psspy.atrncplx(sid, owner, ties, flag, entry, string3)
            ierr4, rarray = psspy.atrnreal(sid, owner, ties, flag, entry, string4)

            if ierr==0 and ierr2==0 and ierr3==0 and ierr4 ==0 :

               i=0
               for i in range(0,brnchs,1):

                  trafo=entidades.Transformer(bus_i=iarray[0][i],bus_j=iarray[1][i],idn=carray[0][i],bus_k=None,id_2 = None,id_3 = None,is_3D=False, name=carray [2][i],status=iarray[2][i],
                                              met_bus=iarray[3][i],vgrp=carray [1][i],x1_2=xarray[0][i].imag,r1_2=xarray[0][i].real, sbs1_2=rarray[8][i],
                                                owner_1=iarray[6][i],owner_2=iarray[7][i],owner_3=iarray[8][i],owner_4=iarray[9][i],
                                                f_owner1=rarray[0][i],f_owner2=rarray[1][i],f_owner3=rarray[2][i],
                                                f_owner4=rarray[3][i],angle1=rarray[7][i], check_trafo=False, windv1=rarray[9][i], windv1_2=rarray[10][i],
                                                bus_i_name=carray [3][i],bus_j_name=carray [4][i])

                  list_trafo.append(trafo)

               #Obtengo un listado de buses que tienen por voltaje base=1.0
               bus_1kv=get_bus_by_voltaje_base([1.0])

               for item in bus_1kv:

                  #Compruebo si hay algun trafo con al bus de 1kv en alguno de sus extremos
                  trafo_1kv=filter(lambda x: x.bus_i==item.bus_num or x.bus_j==item.bus_num, list_trafo)

                  #Obtengo los tres trafos de 2 dev que modela un trafo de 3dev pero un con un nudo de 1kv.
                  # En teoria el nudo de un kv solo es utilizado para mdelar el trafo
                  if trafo_1kv.__len__()==3:
                     #Si hay tres trafos con el bus de 1kv en lguno de sus extreos este trafo en de tres dev modeloado con el nudo de 1 kv
                     #transformo el primer trafo a un trafo de 3dev mdelado con un nudod de un 1kv y elimino de la lista los dos siguientes
                     bus_0=trafo_1kv[0].bus_i if trafo_1kv[0].bus_i != item.bus_num else  trafo_1kv[0].bus_j
                     bus_1=trafo_1kv[1].bus_i if trafo_1kv[1].bus_i != item.bus_num else  trafo_1kv[1].bus_j
                     bus_2=trafo_1kv[2].bus_i if trafo_1kv[2].bus_i != item.bus_num else  trafo_1kv[2].bus_j

                     name_bus_0 = trafo_1kv[0].bus_i_name if trafo_1kv[0].bus_i != item.bus_num else  trafo_1kv[0].bus_j_name
                     name_bus_1 = trafo_1kv[1].bus_i_name if trafo_1kv[1].bus_i != item.bus_num else  trafo_1kv[1].bus_j_name
                     name_bus_2 = trafo_1kv[2].bus_i_name if trafo_1kv[2].bus_i != item.bus_num else  trafo_1kv[2].bus_j_name

                     try:
                        vol_1=get_bus_voltaje_base(bus_0)
                     except:
                        vol_1=0
                     try:
                        vol_2 = get_bus_voltaje_base(bus_1)
                     except:
                        vol_2=0
                     try:
                        vol_3 = get_bus_voltaje_base(bus_2)
                     except:
                         vol_3=0

                     lis_num=sorted([vol_1, vol_2,vol_3],reverse=True)
                     id_trafo_primario=0
                     id_trafo_secuandario = 1
                     id_trafo_terciario = 2


                     #Cambio todos los parametros de trafo[0] para que sea semenjante a un trafo de 3 dev
                     if (lis_num[2]==vol_3):
                        #En caso de que el menor voltaje sea el del trafo con id=2

                        if vol_2 > vol_1:
                           # El trafo con id=1 es el primario
                           id_trafo_primario = 1
                           id_trafo_secuandario = 0
                           id_trafo_terciario = 2
                           bus_i = bus_1
                           bus_j = bus_0
                           bus_k = bus_2

                        else:
                           id_trafo_primario = 0
                           id_trafo_secuandario = 1
                           id_trafo_terciario = 2
                           bus_i = bus_0
                           bus_j = bus_1
                           bus_k = bus_2


                     elif (lis_num[2]==vol_2):
                        # En caso de que el menor voltaje sea el del trafo con id=1

                        if vol_3>vol_1:
                           #El trafo con id=2 es el primario
                           id_trafo_primario = 2
                           id_trafo_secuandario = 0
                           id_trafo_terciario = 1
                           bus_i = bus_2
                           bus_j = bus_0
                           bus_k = bus_1
                        else:
                           id_trafo_primario = 0
                           id_trafo_secuandario = 2
                           id_trafo_terciario = 1
                           bus_i = bus_0
                           bus_j = bus_2
                           bus_k = bus_1


                     else:
                        # En caso de que el menor voltaje sea el del trafo con id=0
                        if vol_3 > vol_2:
                           # El trafo con id=2 es el primario
                           id_trafo_primario = 2
                           id_trafo_secuandario =1
                           id_trafo_terciario = 0
                           bus_i = bus_2
                           bus_j = bus_1
                           bus_k = bus_0
                        else:
                           id_trafo_primario = 1
                           id_trafo_secuandario = 2
                           id_trafo_terciario =0
                           bus_i = bus_1
                           bus_j = bus_2
                           bus_k = bus_0

                     #Convierto los tres trafos aun trafo de 3dev modelado con un nudode de 1kv.
                     #El rpiamrio simrep será el de a mayor voltaje
                     #Y el terciario el de menor voltaje


                     trafo_1kv[id_trafo_primario].bus_1kv = item.bus_num
                     trafo_1kv[id_trafo_primario].is_3D = True
                     trafo_1kv[id_trafo_primario].bus_i = bus_i
                     trafo_1kv[id_trafo_primario].bus_j = bus_j
                     trafo_1kv[id_trafo_primario].bus_k = bus_k


                     trafo_1kv[id_trafo_primario].id=trafo_1kv[id_trafo_primario].id
                     trafo_1kv[id_trafo_primario].id_2 = trafo_1kv[id_trafo_secuandario].id
                     trafo_1kv[id_trafo_primario].id_3 = trafo_1kv[id_trafo_terciario].id

                     trafo_1kv[id_trafo_primario].r1_2 = trafo_1kv[id_trafo_primario].r1_2
                     trafo_1kv[id_trafo_primario].x1_2 = trafo_1kv[id_trafo_primario].x1_2
                     trafo_1kv[id_trafo_primario].r2_3 = trafo_1kv[id_trafo_secuandario].r1_2
                     trafo_1kv[id_trafo_primario].x2_3 = trafo_1kv[id_trafo_secuandario].x1_2
                     trafo_1kv[id_trafo_primario].r3_1 = trafo_1kv[id_trafo_terciario].r1_2
                     trafo_1kv[id_trafo_primario].x3_1 = trafo_1kv[id_trafo_terciario].x1_2

                     trafo_1kv[id_trafo_primario].sbs1_2 = trafo_1kv[id_trafo_primario].sbs1_2
                     trafo_1kv[id_trafo_primario].sbs2_3 = trafo_1kv[id_trafo_primario].sbs1_2
                     trafo_1kv[id_trafo_primario].sbs3_1 = trafo_1kv[id_trafo_primario].sbs1_2

                     trafo_1kv[id_trafo_primario].windv1 = trafo_1kv[id_trafo_primario].windv1
                     trafo_1kv[id_trafo_primario].windv2 = trafo_1kv[id_trafo_secuandario].windv1
                     trafo_1kv[id_trafo_primario].windv3 = trafo_1kv[id_trafo_terciario].windv1

                     status1= trafo_1kv[id_trafo_primario].status
                     status2 = trafo_1kv[id_trafo_secuandario].status
                     status3 = trafo_1kv[id_trafo_terciario].status
                     status=1

                     if status1==0 and status2==0 and status3==0:
                        status=0 #Si todos los devanados estan desconectados el estado del trafo de tres devenados en 0
                     elif status1==0 and status2==1 and status3==1:
                        status = 4 #Sie sta desconectado el devanado 1 el estatus del trafo de 3dev es
                     elif status1==1 and status2==0 and status3==1:
                        status = 2 #Sie sta desconectado el devanado 2 el estatus del trafo de 3dev es
                     elif status1 == 1 and status2 == 1 and status3 == 0:
                        status = 3 #Sie sta desconectado el devanado 3 el estatus del trafo de 3dev es

                     trafo_1kv[id_trafo_primario].status=status

                     list_trafo.remove(trafo_1kv[id_trafo_secuandario])
                     list_trafo.remove(trafo_1kv[id_trafo_terciario])





                  elif trafo_1kv.__len__()==2:
                     #Implimentar un warning
                     pass



            else:
               raise StandardError('Cod error={}'.format(ierr))
         else:
            raise StandardError('Cod error={}'.format(ierr))

      return  list_trafo
   except Exception as e:
      raise  StandardError ('Error al obtner los trafos: {}'.format(e.message))

def get_transformer_3dev(sid=-1):
   """
      Obtiene los trafos de 3 dev sobre un subsistema (sid=-1 sobre todo el caso). Sin incluir los de 3 dev modelado con un nudo de 1kv
      :param sid: para indicar sobre que subsistema obtner los trafos (sid=-1 sobre todo el caso)
      :return: un listado de trafos
      :rtype: lsi8t of entidades.Transformer
      """
   owner = 2
   ties = 2
   flag = 2
   entry = 1

   try:
      list_trafo = []

      ierr, brnchs = psspy.atr3count(sid, owner, ties, flag, entry)

      if brnchs>0:
         if ierr == 0:

            string = ['WIND1NUMBER', 'WIND2NUMBER', 'WIND3NUMBER', 'STATUS', 'NMETERNUMBER', 'OWNERS', 'OWN1', 'OWN2',
                      'OWN3','OWN4']

            string2 = ['ID', 'VECTORGROUP', 'XFRNAME']

            string3 = ['RX1-2ACT', 'RX1-2ACTCZ','RX1-2NOM','RX1-2NOMCZ','RX2-3ACT','RX2-3ACTCZ','RX2-3NOM','RX2-3NOMCZ','RX3-1ACT','RX3-1ACTCZ'
                       ,'RX3-1NOM','RX3-1NOMCZ','YMAG']

            string4 = ['FRACT1', 'FRACT2', 'FRACT3', 'FRACT4','VMSTAR', 'ANSTAR']

            ierr, iarray = psspy.atr3int(sid, owner, ties, flag, entry, string)
            ierr2, carray = psspy.atr3char(sid, owner, ties, flag, entry, string2)
            ierr3, xarray = psspy.atr3cplx(sid, owner, ties, flag, entry, string3)
            ierr4, rarray = psspy.atr3real(sid, owner, ties, flag, entry, string4)

            if (ierr == 0 or ierr == 10) and ierr2 == 0 and (ierr3 == 0 or ierr3== 10) and ierr4 == 0:

               i = 0
               for i in range(0, brnchs, 1):
                  trafo = entidades.Transformer(bus_i=iarray[0][i],bus_j=iarray[1][i],idn=carray[0][i],bus_k=iarray[2][i],
                                                id_2 = None,id_3 = None,is_3D=True, name=carray[2][i],status=iarray[3][i], vgrp=carray[1][i],
                                                r1_2=xarray[2][i].real,x1_2=xarray[2][i].imag,r2_3=xarray[6][i].real,x2_3=xarray[6][i].imag,r3_1=xarray[10][i].real,x3_1=xarray[10][i].imag,
                                                sbs1_2=_f,sbs2_3=_f,sbs3_1=_f,
                                                mag1=_f,mag2=_f,
                                                owner_1=iarray[6][i],owner_2=iarray[7][i],owner_3=iarray[8][i],owner_4=iarray[9][i],
                                                f_owner1=rarray[0][i],f_owner2=rarray[1][i],f_owner3=rarray[2][i],f_owner4=rarray[3][i],
                                                angle1=_f,angle2=_f,angle3=_f,check_trafo=False)

                  list_trafo.append(trafo)

            else:
               raise StandardError('Cod error={}'.format(ierr))
         else:
            raise StandardError('Cod error={}'.format(ierr))

      return list_trafo
   except Exception as e:
      raise StandardError('Error al obtner los trafos: {}'.format(e.message))

def convert_trafo_3dev_estrella_triangulo(trafo):
   """

   :param trafo:
   :type trafo: entidades.Transformer
   :return:
   """

   try:


      z1=complex(trafo.r1_2,trafo.x1_2)
      z2=complex(trafo.r2_3,trafo.x2_3)
      z3=complex(trafo.r3_1,trafo.x3_1)

      #import numpy as np
      # a=np.array([[1/2,1/2,-1/2],[1/2,-1/2,1/2],[-1/2,1/2,1/2]],dtype=float)
      # b = np.array([z1, z2, z3], dtype=complex)
      # zij=np.linalg.solve(a,b)

      trafo.r1_2= z1.real +z2.real
      trafo.x1_2 = z1.imag +z2.imag

      trafo.r2_3 = z2.real + z3.real
      trafo.x2_3 = z2.imag + z3.imag

      trafo.r3_1 = z1.real + z3.real
      trafo.x3_1 = z1.imag + z3.imag


      return trafo

      pass
   except Exception as e:
      pass

def get_trafo_by_bus(num_bus):
   """
   Obtiene los trafos asocidos a un bus
   :param num_bus:
   :return:
   """
   list_trafos=[]
   sid_id = create_susbsistem_by_buses([num_bus], 0)

   list_trafos.extend(get_transformer_2dev(sid=sid_id))
   list_trafos.extend(get_transformer_3dev(sid=sid_id))

   return list_trafos

def check_trafo(list_trafos, bus_i, bus_j,ckt,bus_k=None):
   """
   Comprueba si un trafosrmador existe . La comprbacion se realiza tambien sobre barras separadas
   :param list_trafos:
   :param bus_i: num bus del primario
   :param bus_j: num bus del secundario
   :param bus_k: num bus del terciario.Si es None es de 2 dev
   :param ckt: indica el id del ciciuto del trafo
   :return:
   """

   tra_cso=[]

   if bus_k==None:


      tra_cso = filter(lambda x: ((x.bus_i == bus_i and x.bus_j == bus_j and x.id == ckt) or
                                 (x.bus_i == bus_i+sum_bar_sep and x.bus_j == bus_j and x.id == ckt) or
                                 (x.bus_i == bus_i and x.bus_j == bus_j+ sum_bar_sep and x.id == ckt) or

                                 (x.bus_i == bus_j and x.bus_j == bus_i and x.id == ckt) or
                                 (x.bus_i == bus_j+ sum_bar_sep and x.bus_j == bus_i and x.id == ckt) or
                                 (x.bus_i == bus_j and x.bus_j+ sum_bar_sep == bus_i and x.id == ckt)) and x.is_3D==False,list_trafos)

   else:
      #El terciario siempre va ser el de menor voltaje

      tra_cso = filter(lambda x: (x.bus_i == bus_i and x.bus_j == bus_j and x.bus_k == bus_k and x.id == ckt) or
                                 (x.bus_i == bus_i + sum_bar_sep and x.bus_j == bus_j and x.bus_k == bus_k and x.id == ckt) or
                                 (x.bus_i == bus_i and x.bus_j == bus_j + sum_bar_sep and x.bus_k == bus_k and x.id == ckt) or
                                 (x.bus_i == bus_i and x.bus_j == bus_j and x.bus_k == bus_k + sum_bar_sep and x.id == ckt) or

                                 (x.bus_i == bus_j  and x.bus_j == bus_i and x.bus_k == bus_k and x.id == ckt) or
                                 (x.bus_i == bus_j  + sum_bar_sep and x.bus_j == bus_i and x.bus_k == bus_k and x.id == ckt) or
                                 (x.bus_i == bus_j and x.bus_j == bus_i + sum_bar_sep and x.bus_k == bus_k and x.id == ckt) or
                                 (x.bus_i == bus_j  and x.bus_j == bus_i and x.bus_k == bus_k + sum_bar_sep and x.id == ckt),list_trafos)

      # if tra_cso==[]:
      #    tra_cso = filter(lambda x: (x.bus_i == bus_i and x.bus_j == bus_j and x.bus_k == bus_k ) or
      #                               (x.bus_i == bus_i + sum_bar_sep and x.bus_j == bus_j and x.bus_k == bus_k) or
      #                               (x.bus_i == bus_i and x.bus_j == bus_j + sum_bar_sep and x.bus_k == bus_k) or
      #                               (x.bus_i == bus_i and x.bus_j == bus_j and x.bus_k == bus_k + sum_bar_sep) or
      #
      #                               (x.bus_i == bus_j and x.bus_j == bus_i and x.bus_k == bus_k ) or
      #                               (x.bus_i == bus_j + sum_bar_sep and x.bus_j == bus_i and x.bus_k == bus_k) or
      #                               (x.bus_i == bus_j and x.bus_j == bus_i + sum_bar_sep and x.bus_k == bus_k) or
      #                               ( x.bus_i == bus_j and x.bus_j == bus_i and x.bus_k == bus_k + sum_bar_sep),list_trafos)


   return tra_cso
# endregion


def create_susbsistem_by_buses(list_bus, sid_id):
   """
   Crea un susbsistema desde un listado de buses
   :param list_bus: list int
   :param sid_id: id del susistema
   :return:
   """
   ierr=psspy.bsys(sid_id, 0, [1.0, 400.], 0, [], list_bus.__len__(), list_bus, 0, [], 0, [])

   if ierr!=0:
      raise StandardError('Error al crear el subsistema. Cod_Error= {}'.format(ierr))

   return sid_id

def cal_R_in_pu_by_linea(r_ohm, bus_1, bus_2):
   """
   Calcula la  resistencia a partir de sus valores en Ohmios para una linea. Util para potencia de corto
   :return:
   """
   r=r_ohm
   vol_from=get_bus_voltaje_base(bus_1)
   vol_to = get_bus_voltaje_base(bus_2)
   r=r_ohm/(vol_from*vol_to)

   return r

def cal_X_in_pu_by_linea(x_ohm, bus_1, bus_2):
   """
   Calcula la  resistencia a partir de sus valores en Ohmios para una linea. Util para potencia de corto
   :return:
   """
   x=x_ohm
   vol_from=get_bus_voltaje_base(bus_1)
   vol_to = get_bus_voltaje_base(bus_2)
   x=x_ohm/(vol_from*vol_to)

   return x


def create_acoplamiento_mutuo_branchs(ibus, jbus, ckt1, kbus, lbus, ckt2, rm, xm,inil1,finl1, inil2, finl2):
   """

   :param ibus:
   :param jbus:
   :param ckt1:
   :param kbus:
   :param lbus:
   :param ckt2:
   :param rm:
   :param xm:
   :param inil1: distancia del origen de la linea hasta el inicio del acoplamiento de la primera linea en PU
   :param finl1: distancia del origen de la linea hasta el final del acoplamiento de la primera linea en PU
   :param inil2: distancia del origen de la linea hasta el inicio del acoplamiento de la segunda linea en PU
   :param finl2: istancia del origen de la linea hasta el final del acoplamiento de la segunda linea en PU
   :return:
   """
   psspy.newseq()
   realar=[rm, xm,inil1, finl1, inil2, finl2]
   ierr=psspy.seq_mutual_data(ibus, jbus, ckt1, kbus, lbus, ckt2, realar)
   if ierr !=0:
      if ierr==5:
         raise StandardError('Error al add acoplamiento mutuo. cod=5: mutual couples a branch to itself'.format(ierr))
      else:
         raise StandardError('Error al add acoplamiento mutuo. cod={}'.format(ierr))

def get_estaciones_po12(fecha):
   """
   Obtiene las estaciones segun la P.O.1.2 para una fecha dada
   :param fecha:
   :type fecha: datetime
   :return:
   :rtype: Estaciones
   """

   estacion=None
   try:

      #Calculo de la fecha horizonte
      Fecha_horizonte=fecha

      #Definición de estaciones según P.O.1.2

      Primavera=[4,5]
      Verano=[6,7,8]
      Otono=[9,10]

      #Comprobamos en que estación estamos

      if Fecha_horizonte.month in Primavera:
         estacion=Estaciones.primavera
      elif Fecha_horizonte.month in Verano:
         estacion=Estaciones.verano
      elif Fecha_horizonte.month in Otono:
         estacion=Estaciones.otono
      else:
         estacion=Estaciones.invierno

      return estacion

   except Exception as e:
      raise StandardError('Error al obtner la estacion segun la PO1.2: {}'.format(e.message))

      return None, Incidencia

class Estaciones(object):
   primavera=0
   otono=1
   verano=2
   invierno=3

def ascc_fault_lout(list_buses):
   """
   Realiza la activiad de ASCC para un listado de buses
   :param list_buses: listado de buses
   :type list_buses: list of int
   :return: un string con el report
   :rtype str
   """
   try:

      psspy.short_circuit_units(1) #Cambio a unidades fisicas
      psspy.short_circuit_coordinates(1) #Cambio a polares

      report=None
      status=[1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0]
      sid=0
      all=0
      scfile ='nooutput'

      create_susbsistem_by_buses(sid_id=sid, list_bus=list_buses)

      @contextlib.contextmanager
      def stdout_redirect(where):
         sys.stdout = where
         try:
            yield where
         finally:
            sys.stdout = sys.__stdout__

      with stdout_redirect(cStringIO.StringIO()) as new_stdout:
         ierr = psspy.ascc_3(sid, all, status, 1.0, "", "", scfile)

      if ierr !=0:
         psspy.short_circuit_units(0)  # Cmabio a PU
         psspy.short_circuit_coordinates(0)  # Cambio a rectangulares
         raise StandardError('Ejecutar ascc_3. Cod={}'.format(ierr))

      new_stdout.seek(0)
      report = new_stdout.read()

      psspy.short_circuit_units(0)
      psspy.short_circuit_coordinates(0)

      return report

   except Exception as e:
      raise StandardError('Error al relizar la falta ASCC: {}'.format(e.message))

def iecs_fault_lout(list_buses):
   """
   Realiza la activiad de ASCC para un listado de buses
   :param list_buses: listado de buses
   :type list_buses: list of int
   :return: un string con el report
   :rtype str
   """
   try:
      report=None
      status=[1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0]
      sid=0
      all=0
      scfile ='nooutput'

      psspy.short_circuit_units(1)  # Cambio a unidades fisicas
      psspy.short_circuit_coordinates(1)  # Cambio a polares

      create_susbsistem_by_buses(sid_id=sid, list_bus=list_buses)

      @contextlib.contextmanager
      def stdout_redirect(where):
         sys.stdout = where
         try:
            yield where
         finally:
            sys.stdout = sys.__stdout__

      with stdout_redirect(cStringIO.StringIO()) as new_stdout:
         ierr = psspy.iecs_4(sid,0,status,[ 0.1, 1.1],"","","")

      if ierr !=0:
         psspy.short_circuit_units(0) #Cmabio a PU
         psspy.short_circuit_coordinates(0)#Cambio a rectangulares
         raise StandardError('Ejecutar ascc_3. Cod={}'.format(ierr))

      new_stdout.seek(0)
      report = new_stdout.read()

      psspy.short_circuit_units(0) #Cmabio a PU
      psspy.short_circuit_coordinates(0) #Cambio a rectangulares

      return report

   except Exception as e:
      raise StandardError('Error al relizar la falta iecs: {}'.format(e.message))

def ascc_fault_posiciones(list_buses):
   """
   Realiza la activiad de ASCC para un listado de buses
   :param list_buses: listado de buses
   :type list_buses: list of int
   :return: un string con el report
   :rtype str
   """
   try:

      psspy.short_circuit_units(1) #Cambio a unidades fisicas
      psspy.short_circuit_coordinates(1) #Cambio a polares

      report=None
      status=[1,0,0,0,0,3,0,0,0,0,1,0,0,0,0,0,0]
      [1, 1, 0, 0, 0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
      sid=0
      all=0
      scfile ='nooutput'

      create_susbsistem_by_buses(sid_id=sid, list_bus=list_buses)

      @contextlib.contextmanager
      def stdout_redirect(where):
         sys.stdout = where
         try:
            yield where
         finally:
            sys.stdout = sys.__stdout__

      with stdout_redirect(cStringIO.StringIO()) as new_stdout:
         ierr = psspy.ascc_3(sid, all, status, 1.0, "", "", scfile)

      if ierr !=0:
         psspy.short_circuit_units(0)  # Cmabio a PU
         psspy.short_circuit_coordinates(0)  # Cambio a rectangulares
         raise StandardError('Ejecutar ascc_3. Cod={}'.format(ierr))

      new_stdout.seek(0)
      report = new_stdout.read()

      psspy.short_circuit_units(0)
      psspy.short_circuit_coordinates(0)

      return report

   except Exception as e:
      raise StandardError('Error al relizar la falta ASCC: {}'.format(e.message))

def iecs_fault_posiciones(list_buses):
   """
   Realiza la activiad de ASCC para un listado de buses
   :param list_buses: listado de buses
   :type list_buses: list of int
   :return: un string con el report
   :rtype str
   """
   try:
      report=None
      status= [1, 1, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      sid=0
      all=0
      scfile ='nooutput'

      psspy.short_circuit_units(1)  # Cambio a unidades fisicas
      psspy.short_circuit_coordinates(1)  # Cambio a polares

      create_susbsistem_by_buses(sid_id=sid, list_bus=list_buses)

      @contextlib.contextmanager
      def stdout_redirect(where):
         sys.stdout = where
         try:
            yield where
         finally:
            sys.stdout = sys.__stdout__

      with stdout_redirect(cStringIO.StringIO()) as new_stdout:
         ierr = psspy.iecs_4(sid,0,status,[ 0.1, 1.1],"","","")

      if ierr !=0:
         psspy.short_circuit_units(0) #Cmabio a PU
         psspy.short_circuit_coordinates(0)#Cambio a rectangulares
         raise StandardError('Ejecutar ascc_3. Cod={}'.format(ierr))

      new_stdout.seek(0)
      report = new_stdout.read()

      psspy.short_circuit_units(0) #Cmabio a PU
      psspy.short_circuit_coordinates(0) #Cambio a rectangulares

      return report

   except Exception as e:
      raise StandardError('Error al relizar la falta iecs: {}'.format(e.message))

def ascc_fault_lout_thevenin(list_buses):
   """
   Realiza la activiad de ASCC para un listado de buses
   :param list_buses: listado de buses
   :type list_buses: list of int
   :return: un string con el report
   :rtype str
   """
   try:

      psspy.short_circuit_units(1) #Cambio a unidades fisicas
      psspy.short_circuit_coordinates(1) #Cambio a polares

      report=None
      status=[1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0]

      sid=0
      all=0
      scfile ='nooutput'
      create_susbsistem_by_buses(sid_id=sid, list_bus=list_buses)

      @contextlib.contextmanager
      def stdout_redirect(where):
         sys.stdout = where
         try:
            yield where
         finally:
            sys.stdout = sys.__stdout__

      with stdout_redirect(cStringIO.StringIO()) as new_stdout:
         ierr = psspy.ascc_3(sid, all, status, 1.0, "", "", scfile)

      if ierr !=0:
         psspy.short_circuit_units(0)  # Cmabio a PU
         psspy.short_circuit_coordinates(0)  # Cambio a rectangulares
         raise StandardError('Ejecutar ascc_3. Cod={}'.format(ierr))

      new_stdout.seek(0)
      report = new_stdout.read()

      psspy.short_circuit_units(0)
      psspy.short_circuit_coordinates(0)

      return report

   except Exception as e:
      raise StandardError('Error al relizar la falta ASCC: {}'.format(e.message))

def iecs_fault_lout_thevenin(list_buses):
   """
   Realiza la activiad de ASCC para un listado de buses
   :param list_buses: listado de buses
   :type list_buses: list of int
   :return: un string con el report
   :rtype str
   """
   try:
      report=None
      status= [1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      sid=0
      all=0
      scfile ='nooutput'

      psspy.short_circuit_units(1)  # Cambio a unidades fisicas
      psspy.short_circuit_coordinates(1)  # Cambio a polares

      create_susbsistem_by_buses(sid_id=sid, list_bus=list_buses)

      @contextlib.contextmanager
      def stdout_redirect(where):
         sys.stdout = where
         try:
            yield where
         finally:
            sys.stdout = sys.__stdout__

      with stdout_redirect(cStringIO.StringIO()) as new_stdout:
         ierr = psspy.iecs_4(sid,0,status,[ 0.1, 1.1],"","","")

      if ierr !=0:
         psspy.short_circuit_units(0) #Cmabio a PU
         psspy.short_circuit_coordinates(0)#Cambio a rectangulares
         raise StandardError('Ejecutar ascc_3. Cod={}'.format(ierr))

      new_stdout.seek(0)
      report = new_stdout.read()

      psspy.short_circuit_units(0) #Cmabio a PU
      psspy.short_circuit_coordinates(0) #Cambio a rectangulares

      return report

   except Exception as e:
      raise StandardError('Error al relizar la falta iecs: {}'.format(e.message))

def ascc_currents(list_buses):
   """
   Reliza las falta  con el algoritmo ASCC pero retorna un array con los resultados. Lo utilizo para extraer la R/X
   :param list_buses: list de buses
   :type list_buses: list
   :return: listado de diccionarios {'bus_num':None, 'x_r':None}
   :rtype: {'bus_num':None, 'x_r':None
   """

   try:
      psspy.short_circuit_units(0)  # Cambio a unidades PU
      psspy.short_circuit_coordinates(0)  # Cambio a rectangulares
      datos={'bus_num':None, 'x_r':None}
      list_datos=[]

      sid = 0
      all = 0
      scfile = 'nooutput'

      create_susbsistem_by_buses(sid_id=sid, list_bus=list_buses)

      rlst = pssarrays.ascc_currents(sid, all, 1, 1, 0, 0, 1, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, '','','')

      if rlst.ierr !=0:
         raise StandardError('Cod_erro={}'.format(rlst.ierr))

      i=0
      for bus in rlst.fltbus:
         datos = {'bus_num': None, 'x_r': None}
         z_thevenin=rlst.thevzpu[i].z1
         r=complex(z_thevenin).real
         x=complex(z_thevenin).imag
         x_r=x/r
         datos['bus_num']=bus
         datos['x_r']=x_r
         list_datos.append(datos)

      return list_datos

   except Exception as e:
      raise StandardError('Error al ascc_currents: {} '.format(e.message))

def iecs_currents(list_buses):
   """
      Reliza las falta  con el algoritmo IECS pero retorna un array con los resultados. Lo utilizo para extraer la R/X
      :param list_buses: list de buses
      :type list_buses: list
      :return: listado de diccionarios {'bus_num':None, 'x_r':None}
      :rtype: {'bus_num':None, 'x_r':None
   """

   try:
      psspy.short_circuit_units(0)  # Cambio a unidades PU
      psspy.short_circuit_coordinates(0)  # Cambio a rectangulares
      datos={'bus_num':None, 'x_r':None}
      list_datos=[]

      sid = 0
      all = 0
      scfile = 'nooutput'

      create_susbsistem_by_buses(sid_id=sid, list_bus=list_buses)

      rlst = pssarrays.iecs_currents(sid, all, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, _f, _f, '', '', '')

      if rlst.ierr !=0:
         raise StandardError('Cod_erro={}'.format(rlst.ierr))

      i=0
      for bus in rlst.fltbus:
         datos = {'bus_num': None, 'x_r': None}
         z_thevenin=rlst.thevzpu[i].z1
         r=complex(z_thevenin).real
         x=complex(z_thevenin).imag
         x_r=x/r
         datos['bus_num']=bus
         datos['x_r']=x_r
         list_datos.append(datos)

      return list_datos

   except Exception as e:
      raise StandardError('Error al ascc_currents: {} '.format(e.message))


def check_sequence_data(bus):
   sid=create_susbsistem_by_buses([bus], 0)

   @contextlib.contextmanager
   def stdout_redirect(where):
      sys.stdout = where
      try:
         yield where
      finally:
         sys.stdout = sys.__stdout__

   with stdout_redirect(cStringIO.StringIO()) as new_stdout:
      ierr = psspy.check_sequence_data(sid, 1, 0)

   if ierr !=0:
    return False
   else:
      return True


















