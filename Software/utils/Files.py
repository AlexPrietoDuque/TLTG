# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Py para añadir utilidades para trabajar con directorios y ficheros
#
# Author:      Alejandro Prieto Duque
#
# Iniciado:     26/01/2018
# Finalizado:
#-------------------------------------------------------------------------------
import os
import shutil
from stat import *
import time
import datetime


class File(object):
   def __init__(self,path):
      self.__name=None
      self.__extension=None
      self.__relative_path=None
      self.path=path
      self.__date_create=None
      self.__date_modif=None
      self.__date_last_accessed=None
      self.__size=None
      self.observaciones=None

   @property
   def name(self):
      return self.__name

   @name.setter
   def name(self, value):
      self.__name = value

   @property
   def extension(self):
      return self.__extension

   @property
   def relative_path(self):
      return self.__relative_path

   @property
   def path(self):
      """

      :return:
      :rtype: str
      """
      return self.__path
   @path.setter
   def path(self,value):
      self.__path=value
      if  self.__path !='':
         self.__incializar()

   @property
   def date_create(self):
      try:
         st = os.stat(self.path)
         fecha=time.asctime(time.localtime(st[ST_CTIME]))
         self.__date_create = datetime.datetime.strptime(fecha, '%a %b %d %H:%M:%S %Y')
         pass

      except:
         pass

      return self.__date_create

   @property
   def date_modif(self):
      try:
         st = os.stat(self.path)
         self.__date_modif = time.asctime(time.localtime(st[ST_MTIME]))
      except:
         pass

      return self.__date_modif

   @property
   def date_last_accessed(self):
      try:
         st = os.stat(self.path)
         self.____date_last_accessed = time.asctime(time.localtime(st[ST_ATIME]))
      except:
         pass

      return self.____date_last_accessed

   @property
   def size(self):
      try:
         st = os.stat(self.path)
         self.__size = st[ST_SIZE]
      except:
         pass

      return self.__size

   def __incializar(self):
      self.__extension=os.path.splitext(self.path)[1][1:]
      self.__relative_path=os.path.dirname(self.path)
      self.__name=os.path.basename(self.path)

   def copy(self,path_destino,name=None,remplazar=False ):
      """

      :param path_destino:
      :param name: Por si se quiere guardar con otro nombre el fichero
      :param remplazar:
      :return:
      """

      try:
         if name ==None:
            file_des = os.path.join(path_destino, self.name)
         else:
            file_des = os.path.join(path_destino, name)

         if not os.path.isdir(path_destino):
            os.makedirs(path_destino) #Si el directorio de destino no existe lo creo

         shutil.copy(self.path, file_des)

         # if remplazar and os.path.isfile(file_des): #Si hay que reemplzarlo. Lo remuevo y lo copio
         #    os.remove(file_des)

      except Exception as e:
         if 'same file' in e.message:
            pass #cuando intentas el mismo archivo sobre la misma ruta. Da  a la hora de copiar
         else:
            raise StandardError ('Error al copiar archivos: {}'.format(e))

   def exists(self):
      return os.path.isfile(self.path)

   def delete(self):
      os.remove(self.path)

   def move(self,path_destino):
      if not os.path.isdir(path_destino):
         os.makedirs(path_destino)  # Si el directorio de destino no existe lo creo

      file_destino=os.path.join(path_destino,self.name)
      shutil.move(self.path,file_destino)
      self.path=file_destino

   def versionar_file(self, path_destino, update_path=False):
      """
      Da una version al archivo en caso de que ya exista en una ruta de destino. Es decir cambia su nombre
      :param path_destino:
      :return:
      """
      i = 1
      while os.path.exists(os.path.join(path_destino, self.name)):
         self.name = self.name.replace('.'+self.extension,'').replace('_{}'.format(i-1),'')+'_{}'.format(i) + '.'+self.extension
         i += 1

      if update_path:
         self.path=os.path.join(self.relative_path,self.name)

      return self.name



def get_files_to_directory(path):
   """
   Retonar un listado de fichero sobre un directorio
   :param path: path del directorio
   :return: lsitado de ficheros
   :rtype:list of  File
   """
   files=[]

   # from os import walk
   #
   # for (dirpath, dirnames, filenames) in walk(path):
   #    ddd=filenames
   #
   # pass

   try:
      from os import listdir
      from os.path import isfile, join
      files = [File(os.path.join(path, f)) for f in listdir(path) if isfile(join(path, f))]
   except Exception as e:
      raise StandardError('Error al obtner los archivos del directorio: {}'.format(e))

   return files

def dele_files_bys_directory(path_directory, extensiones=(), extesiones_igual=True):
   """
   :param path_directori: path del diectorio de donde borrrar los archivos
   :param extensiones: Opcional: tupla de las extesiones de los archivos a borrar (sin punto).
   :param extesiones_igual: para idicar si se quiere borrar los archivos con extensiones iguales a las pasadas (True) o disntintas (False)
   :return:
   """
   try:
      onlyfiles = get_files_to_directory(path_directory)
      if extesiones_igual:
         [f.delete() for f in onlyfiles if f.extension in extensiones]
      else:
         onlyfiles=filter(lambda x: x.extension not in extensiones,onlyfiles)
         [f.delete() for f in onlyfiles if f.extension not in extensiones]


   except Exception as e:
      raise StandardError ('Error al borrar los archivos: {}'.format(e.message))

def copy_files_bys_directory(path_directory,path_destino, extensiones=(), extesiones_igual=True):
   """
   :param path_directori: path del diectorio de donde borrrar los archivos
   :param extensiones: Opcional: tupla de las extesiones de los archivos a borrar (sin punto).
   :param extesiones_igual: para idicar si se quiere borrar los archivos con extensiones iguales a las pasadas (True) o disntintas (False)
   :return:
   """
   try:
      onlyfiles = get_files_to_directory(path_directory)
      if extesiones_igual:
         [f.copy(path_destino) for f in onlyfiles if f.extension in extensiones]
      else:
         onlyfiles=filter(lambda x: x.extension not in extensiones,onlyfiles)
         [f.copy(path_destino) for f in onlyfiles if f.extension not in extensiones]


   except Exception as e:
      raise StandardError ('Error al borrar los archivos: {}'.format(e.message))

def sincronizar_directorios(path_directory_fuente,path_directory_destino,extensiones=(), nombre_files=(), nombre_files_excluidos=()):
   """
   Sincroniza un rdirectorio con otro
   :param path_directory_fuente: directorio donde estan los archivos a sincronizar
   :param path_directory_destino: ddirecorio donde actualziar los archivos
   :param extensiones: listado de extensiones de los archivos que se debn sinclinizar
   :param nombre_files_excluidos: listado de los nombre+extension de los rchivos que se deben excluir
   :param nombre_files: listado de nombre de archivos a sincornizar
   :return:
   """

   try:
      onlyfiles_directorio_fuente = get_files_to_directory(path_directory_fuente)
      onlyfiles_directorio_destino= get_files_to_directory(path_directory_destino)

      if nombre_files !=():
         onlyfiles_directorio_fuente = filter(lambda x:x.name in nombre_files,onlyfiles_directorio_fuente )

      if extensiones !=():
         onlyfiles_directorio_fuente = filter(lambda x: x.extension in extensiones, onlyfiles_directorio_fuente)

      if nombre_files_excluidos !=():
         onlyfiles_directorio_fuente = filter(lambda x: x.name not in nombre_files_excluidos, onlyfiles_directorio_fuente)


      copiar=False

      for file_fuente in  onlyfiles_directorio_fuente:
         file_exis=filter(lambda x:x.name==file_fuente.name,onlyfiles_directorio_destino)
         if file_exis.__len__()>0:
            if file_exis[0].date_modif<file_fuente.date_modif:
               copiar = True
            else:
               # TODO Ver si la fecha de actualizacion en direcrio fuente es mayor o al direcorio destino
               copiar = True

         else:
            copiar=True

         if copiar:
            file_fuente.copy(path_directory_destino, True)

   except Exception as e:
      raise StandardError ('Error al sincronizar directorios: {}'.format(e.message))


def get_file_by_extension(path_directorio, list_extensiones):
   """
   Obtiene los archivos con cierta extension de un directorio
   :param path_directorio: path del directorio, puede ser un archivo, por lo que solo retornara este archivo
   :param list_extensiones: lista de extensiones . Ejmeplo ['raw','sav','RAW','SAV']
   :return: el path completo del archivo
   """
   path_casos=[]

   if not os.path.exists:
      raise StandardError('El directprio especificado no existe={}'.format(path_casos))

   if not os.path.isfile(path_directorio):

      files=get_files_to_directory(path_directorio)

      for fil in filter(lambda x: x.extension in list_extensiones,files):
         path_casos.append(fil.path)
   else:
      path_casos.append(path_directorio)


   return path_casos


def get_file_by_extension_subdirectorio(path_directorio, list_extensiones=[]):
   """
   Obtiene todos los archivos con ciertas entenxiones dentro de un directorio y de todos
   :param path_directorio: ruta input
   :param list_extensiones: listado de str de las extensiones. Si esta vacio se retornaran todas las extensiones
   :return:
   :rtype: list of File
   """

   path_casos = []

   if not os.path.exists:
      raise StandardError('El directorio especificado no existe={}'.format(path_casos))

   if not os.path.isfile(path_directorio):

      subdirectory=[x[0] for x in os.walk(path_directorio)]

      for dir in subdirectory:

         files = get_files_to_directory(dir)
         if list_extensiones !=[]:
            fil=[x for x in filter(lambda x: x.extension in list_extensiones, files)]
            if fil !=[]:
               path_casos.extend(fil)
         else:
            if files !=[]:
               path_casos.extend(files)
   else:
      path_casos.append(path_directorio)

   return path_casos


def get_immediate_subdirectories(a_dir):
   return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]


