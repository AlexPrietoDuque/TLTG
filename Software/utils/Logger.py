# -*- coding: utf-8 -*-
import logging, time, os, sys, string
import logging.handlers
import threading
import multiprocessing
from logging import FileHandler as FH

import traceback


# class Singleton(type):
#    '''Metaclase singleton.
#     No se puede crear una segunda instancia de una clase Singleton
#     ni de las clases que hereden de esta.'''
#
#    def __init__(cls, name, bases, dct):
#       cls.__instance = None
#       type.__init__(cls, name, bases, dct)
#
#    def __call__(cls, *arg):
#       if cls.__instance is None:
#          cls.__instance = type.__call__(cls, *arg)
#          return cls.__instance
#       else:
#          raise Exception('No se puede crear una segunda instancia de una clase Singleton')
#
#    def get_instance(cls):
#       ''' Devuelve la unica instancia de esta clase.'''
#       return cls.__instance
class Logger:
   """Clase que interconecta una aplicacion del usuario con el paquete Logging
   de Python creando la instancia y gestionandola de forma que se simplifican
   las tareas al usuario. Los niveles de mensajes de alerta utilizados son:
   DEBUG, INFO, WARNING, ERROR y CRITICAL.
   Es una clase derivada de Singleton por lo que solo admite una unica instancia."""
   #__metaclass__ = Singleton
   logger=None

   def __init__(self, progamName='SinNombre',fileName='SinNombre', consoleStream=None):
      """Constructor de la clase.
      Inputs: programName: nombre del programa desde el que se instancia
              esta clase."""
      self.__logger = logging.getLogger(progamName)

      self.__logger.setLevel(logging.DEBUG)
      filename = fileName
      #value = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
      #filename += value
      filename += '.log'
      self.__logFile = filename
      self.__consoleHandler = logging.StreamHandler(consoleStream)
      self.__consoleHandler.setLevel(logging.DEBUG)
      self.__dLevel = {'DEBUG': logging.DEBUG,
                       'INFO': logging.INFO,
                       'WARNING': logging.WARNING,
                       'ERROR': logging.ERROR,
                       'CRITICAL': logging.CRITICAL
                       }
      self.__fileHandler = logging.FileHandler(self.__logFile, mode='w')
      self.__fileHandler.setLevel(logging.DEBUG)
      consoleFormatter = logging.Formatter('%(levelname)s : %(name)s : %(module)s : %(funcName)s : %(message)s')
      fileFormatter = logging.Formatter('"%(asctime)-15s: %(name)-18s ; %(levelname)-8s ;%(module)-15s ; %(funcName)-20s ; %(lineno)-6d ; %(message)s"')
      self.__consoleHandler.setFormatter(consoleFormatter)
      self.__fileHandler.setFormatter(fileFormatter)
      self.__logger.addHandler(self.__consoleHandler)
      self.__logger.addHandler(self.__fileHandler)
      self.__captureWarnings = False
      logging.captureWarnings(self.__captureWarnings)
      #self.__initLog()
      self.filename=filename

   def get_logger(self):
      """Devuelve la instancia del logger."""
      return self.__logger

   def get_logFile(self):
      """Devuelve el nombre del fichero log creado."""
      return self.__logFile

   def get_manejadorConsola(self):
      """Devuelve el manejador de los mensajes por consola."""
      return self.__consoleHandler

   def get_manejadorFichero(self):
      """Devuelve el manejador de los mensajes por fichero log."""
      return self.__fileHandler

   def set_nivelPorConsola(self, level):
      """Establece el nivel de alerta para filtrado de mensajes por consola.
      Inputs: level: nivel por debajo del cual se filtran los mensajes."""
      level=self.__dLevel[level]

      self.__consoleHandler.setLevel(level)

   def set_nivelPorFichero(self, level):
      """Establece el nivel de alerta para filtrado de mensajes por fichero log.
      Inputs: level: nivel por debajo del cual se filtran los mensajes."""
      self.__fileHandler.setLevel(self.__dLevel[level])

   def get_captureWarning(self):
      """Establece si se capturan los mensajes generados por el modulo warning de python.
      Inputs: capture: True or False."""
      return self.__captureWarnings

   def set_captureWarning(self, capture):
      """Establece si se capturan los mensajes generados por el modulo warning de python.
      Inputs: capture: True or False."""
      self.__captureWarnings = capture
      logging.captureWarnings(self.__captureWarnings)

   def set_streamHandler(self, consoleStream):
      """Establece el stream donde se envian los mensajes de pantalla.
      Inputs: consoleStream: Clase que contenga un metodo write."""
      self.__consoleHandler.stream = consoleStream

   def debug(self, msj):
      """Genera un mensaje de nivel de alerta DEBUG.
      Inputs: msj: mensaje a procesar."""
      self.__logger.debug(msj)

   def info(self, msj):
      """Genera un mensaje de nivel de alerta INFO.
      Inputs: msj: mensaje a procesar."""
      self.__logger.info(msj)

   def warn(self, msj):
      """Genera un mensaje de nivel de alerta WARNING.
      Inputs: msj: mensaje a procesar."""
      self.__logger.warn(msj)

   def error(self, msj):
      """Genera un mensaje de nivel de alerta ERROR.
      Inputs: msj: mensaje a procesar."""
      self.__logger.error(msj)

   def critical(self, msj):
      """Genera un mensaje de nivel de alerta CRITICAL.
      Inputs: msj: mensaje a procesar."""
      self.__logger.critical(msj)

   def carryReturn(self):
      """Genera una linea en blanco en consola y en fichero log."""
      self.__fileHandler.stream.write('\n')
      self.__consoleHandler.stream.write('\n')

   def destroy(self, finalConError):
      """Destruye el logger.
      Inputs: finalConError: pon True si tu programa termino erroneamente."""
      self.carryReturn()
      self.__finalLog(finalConError)
      self.__fileHandler.close()
      self.__consoleHandler.close()
      logging.shutdown()

   def __initLog(self):
      """Aviso del inicio de la ejecucion"""
      hIni = time.clock()
      value = 'Logger : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
      value = value + ' : inicio de la ejecucion'
      self.__logger.info(value)

   def __finalLog(self, finalConError):
      """Aviso del final de la ejecucion.
      Inputs: finalConError: True si tu programa termino erroneamente."""
      texto = ''
      if finalConError:
         texto = 'con errores '
         mens = 'El programa ha concluido con errores.'
      value = 'Logger : final de la ejecucion ' + texto
      value = value + str('tras %.4f' % time.clock())
      value = value + ' segundos'
      self.__logger.info(value)

   def get_traceback(self):
      """Imprime el taceback en consola y retorna el mensaje"""
      traceback.print_exc(file=sys.stdout)
      error_tb = traceback.format_exc().strip()
      error_msg = u'Traceback: {}'.format(error_tb)

      return error_msg

   def rotating(self, path_dest):
      """
      No funciona
      :param path_dest:
      :return:
      """
      #BaseRotatingHandler
      name=os.path.join(path_dest,self.__logFile )
      handler = logging.handlers.RotatingFileHandler(path_dest, backupCount=50)

      self.__logger.addHandler(handler)

class LevelLogger:
   INFO='INFO'
   WARNING='WARNING'
   ERROR='ERROR'
   CRITICAL='CRITICAL'


class CustomLogHandler(logging.Handler):
   """multiprocessing log handler

   This handler makes it possible for several processes
   to log to the same file by using a queue.

   """

   def __init__(self, fname):
      logging.Handler.__init__(self)

      self._handler = FH(fname)
      self.queue = multiprocessing.Queue(-1)

      thrd = threading.Thread(target=self.receive)
      thrd.daemon = True
      thrd.start()

   def setFormatter(self, fmt):
      logging.Handler.setFormatter(self, fmt)
      self._handler.setFormatter(fmt)

   def receive(self):
      while True:
         try:
            record = self.queue.get()
            self._handler.emit(record)
         except (KeyboardInterrupt, SystemExit):
            raise
         except EOFError:
            break
         except:
            traceback.print_exc(file=sys.stderr)

   def send(self, s):
      self.queue.put_nowait(s)

   def _format_record(self, record):
      if record.args:
         record.msg = record.msg % record.args
         record.args = None
      if record.exc_info:
         dummy = self.format(record)
         record.exc_info = None

      return record

   def emit(self, record):
      try:
         s = self._format_record(record)
         self.send(s)
      except (KeyboardInterrupt, SystemExit):
         raise
      except:
         self.handleError(record)

   def close(self):
      self._handler.close()
      logging.Handler.close(self)