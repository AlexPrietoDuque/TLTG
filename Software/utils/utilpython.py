# coding=utf-8
import os
import subprocess
import sqlite3
from pytz import timezone
from datetime import datetime as dt
import traceback


class MyDB(object):
   __db_connection = None
   __db_cur = None
   conn_ok = None # BOOL: indica si hay conexión a la BdD
   __closed = None

   def __init__(self, db_path, log):
      self.__closed = False
      self.log = log
      try:
         self.__db_connection = sqlite3.connect(db_path)
         self.__db_cur = self.__db_connection.cursor()
         self.conn_ok = True
      except Exception as e:
         self.conn_ok = False
         tb = traceback.format_exc()
         self.log.critical(u'ERROR en la conexión a la Base de Datos Backup. [Traceback] msg <{}>'
                      .format(tb))
         self.log.error(u'ERROR en la conexión a la Base de Datos Backup. [Traceback] msg <{}>'
                   .format(tb))

   def query(self, query, params=None):
      if params is None: params = ''
      try:
         return self.__db_cur.execute(query, params)
      except Exception as e:
         self.log.error(u'No se ha podido ejecutar la consulta en la base de datos [Traceback] msg <{}>'
                   .format(e))

   def close(self):
      if self.__db_connection and not self.__closed:
         self.__db_connection.close()
         self.__closed = True
      else:
         self.log.error(u'No se ha podido cerrar la conexión a la base de datos. [Traceback]')

   def commit(self):
      if self.__db_connection:
         self.__db_connection.commit()
      else:
         self.log.error(u'No se ha podido hacer COMMIT a la base de datos. [Traceback]')

   def __del__(self):
      if self.__db_connection and not self.__closed:
         self.__db_connection.close()
         self.__closed = True


def check_if_cambio_hora(date_time):
   """Función que comprueba si en la fecha (sin tener en cuenta la hora) hay cambio de hora

   :param datetime.datetime date_time:
   :return: cambio_hora = 0 si no hay cambio de hora, \n
            cambio_hora = 1 si hay cambio de hora de invierno (habrá 25 horas), \n
            cambio_hora = 2 si hay cambio de hora de verano  (habrá 23 horas)

   """
   if date_time is None:
      raise TypeError(u'La fecha proporcionada es None. No se puede comprobar cambio de hora')
   tz = timezone("Europe/Madrid")  # obtenemos la hora de Madrid
   tz_trans_times = tz._utc_transition_times[120:]
   tz_trans_days = [tz.localize(dt(x.year, x.month, x.day)) for x in tz_trans_times]
   cambio_hora = 0
   if tz.localize(date_time) in tz_trans_days:
      cambio_hora = 2 if date_time.month == 3 else 1

   return cambio_hora


def extract_7z(f_7z, extract_path):
   """Función que extrae el contenido de un fichero comprimido .7z

   Si ya existen los archivos en la ruta de destino, se omite la extracción ( -bso0 -bsp0)

   :param list of str f_7z: ruta del archivo archivo .7z
   :param str extract_path: ruta de destino.
   :return: devuelve True/False en función de si se ha extraído correctamente o no
   """

   # Se busca la ruta de instalación del 7z
   if os.path.exists("C:\\Program Files\\7-Zip"):
      root = "C:\\Program Files\\7-Zip"
   elif os.path.exists("C:\\Program Files\\7-Zip"):
      root = "C:\\Program Files (x86)\\7-Zip"
   else:
      raise RuntimeError(u'No se ha encontrado la ruta de instalación de 7z. No se pueden descomprimir los ficheros')

   try:
      # Se extrae el archivo 7z usando el shell
      ext_ierr = subprocess.call(r'"'+root+'\\7z.exe" x -aoa ' + f_7z + ' -o' + extract_path + ' -bso0 -bsp0')

      # Si se han extraído correctamente, se borra el archivo 7z
      if ext_ierr == 0:
         extract_ok = True
      else:
         extract_ok = False

   except Exception as e:
      raise RuntimeError(u'No se ha podido descomprimir el fichero <{}>. e: {}'.format(f_7z, e))

   return extract_ok


def print_traceback(level=None, log=None, printmsg=True):
   """Función que hace un print (en donde se indique) del traceback del último error sucedido

   :param str level: nivel del log donde se quiere registrar el traceback: 'error', 'debug', 'info', 'critical'
   :param log: log donde se quiere registrar. Si no se le pasa como parámetro, n ose registrará en el log
   :param bool printmsg: booleano que indica si se quiere hacer un print del traceback. True por defecto
   :return:
   """
   error_tb = traceback.format_exc().strip()

   try:
      error_msg = u'ERROR durante la ejecucion: {}'.format(error_tb)
   except UnicodeDecodeError:
      error_msg = 'ERROR durante la ejecucion: {}'.format(error_tb)

   if printmsg: print error_msg
   if level and not log:
      pass
   elif not level or not log:
      pass
   elif level == 'error':
      log.error(error_msg)
   elif level == 'critical':
      log.critical(error_msg)
   elif level == 'info':
      log.info(error_msg)
   elif level == 'debug':
      log.debug(error_msg)
   else:
      # el level indicado no es correcto
      pass

class List_Caracteres_Erroneos(object):
   def __init__(self):
      self.__list_caracteres=None

   @property
   def list_caracteres(self):
      return self.__list_caracteres
   @list_caracteres.getter
   def list_caracteres(self):
      list_item=[]
      list_caracteres=[]


      list_item.append(['¡', '161', u'\xa1', '\xc2\xa1', '\xa1'])
      list_item.append(['?', '191', u'\xbf', '\xc2\xbf', '\xbf'])
      list_item.append(['A', '193', u'\xc1', '\xc3\x81', '\xc1'])
      list_item.append(['E', '201', u'\xc9', '\xc3\x89', '\xc9'])
      list_item.append(['I', '205', u'\xcd', '\xc3\x8d', '\xcd'])
      list_item.append(['N', '209', u'\xd1', '\xc3\x91', '\xd1'])
      list_item.append(['O', '191', u'\xbf', '\xc3\x93', '\xbf'])
      list_item.append(['U', '218', u'\xda', '\xc3\x9a', '\xda'])
      list_item.append(['U', '220', u'\xdc', '\xc3\x9c', '\xdc'])
      list_item.append(['A', '225', u'\xe1', '\xc3\xa1', '\xe1'])
      list_item.append(['e', '233', u'\xe9', '\xc3\xa9', '\xe9'])
      list_item.append(['i', '237', u'\xed', '\xc3\xad', '\xed'])
      list_item.append(['n', '241', u'\xf1', '\xc3\xb1', '\xf1'])
      list_item.append(['o', '243', u'\xf3', '\xc3\xb3', '\xf3'])
      list_item.append(['u', '250', u'\xfa', '\xc3\xba', '\xfa'])
      list_item.append(['u', '252', u'\xfc', '\xc3\xbc', '\xfc'])


      for item in list_item:
         list_caracteres.append(Caracteres_Error(char=item[0],ansi=item[1],unicode=item[2],utf_8=item[3],latin1=item[4]))

      self.__list_caracteres=list_caracteres

      return self.__list_caracteres

class Caracteres_Error(object):
   def __init__(self,char,ansi,unicode,utf_8,latin1):
      self.char=char
      self.ansi=ansi
      self.unicode=unicode
      self.utf_8=utf_8
      self.latin1=latin1

      # s = u'éô'
      # ffff = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))