# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Purpose:
# Author:      MRCh
# Started:     15/11/2018
# Finished:
# -------------------------------------------------------------------------------

from BdD import *
from Modulo_PSSE import *


def main():

   #lectura de datos de entrada
   parametros, sistemas_estudio, info_casos, contingenciasN_2=lecturaficheros()
   #creacion de BdD
   crearBdD(parametros, sistemas_estudio, info_casos, contingenciasN_2)
   #preprocesado de casos
   preprocesado(parametros,info_casos)
   list_dfax=crea_sub_mon_con(sistemas_estudio,parametros,info_casos)
   list_output=run_TLTG(list_dfax)

   print 'Finalizadoooo'

if __name__ == '__main__':

   main()

