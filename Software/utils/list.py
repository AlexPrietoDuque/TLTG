# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Fichero para la lectura de los diversos archivos
#
# Author:      Alejandro Prieto Duque
#
# Iniciado:     26/01/2018
# Finalizado:
#-------------------------------------------------------------------------------



def lastOfDefault(list):
   """
   :param list: type list of object
   :return:
   """
   try:
      indice=list.__len__()
      elem=list[indice-1]

   except Exception as e:
      pass

   return elem




