# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Purpose:     interact with PSS/E
# Author:      MRCh
# Started:     21/11/2018
# Finished:
# -------------------------------------------------------------------------------

import os
import shutil
from utils.utilpsse import initpsspy as initpss
from utils.utilpsse.entidades import _i,_f,_s
from utils.utilpsse import redpsse
from LecturaFicheros import *
import psspy


def preprocesado(parametros, info_casos):

   # se inicia el PSS/E
   initpss.inicia_psse(print_alert_psse=True)

   for x in info_casos:
      try:
         #se encuentra caso en la carpeta y se carga
         path_caso_psse = os.path.join(Rutas().ruta_casos, str(x.N_Caso) + '.sav')
         caso_pss = redpsse.CasoPSSE(filepath=path_caso_psse)
         caso_pss.load(save_previous=False)
         #se comprueba si el caso es peninsular o insular consultando las areas
         areas = redpsse.get_areas()
         area_numbers = []
         for a in areas:
            area_numbers.append(a.number)
         if 9 in area_numbers:
            Umin = parametros.U_min_i
            Umax = parametros.U_max_i
         else:
            Umin = parametros.U_min_p
            Umax = parametros.U_max_p
      except Exception as e:
         raise StandardError('Error al cargar el caso de referencia: {}'.format(e.message))

      try:
         # Cambio a tipo 2 los buses tipo 1 e incluyo generador con Pgen=0.01 MW
         # se recupera lista con buses tipo 1
         list_bus = redpsse.get_bus_number_used_by_tension_tipo(Umin=Umin, Umax=Umax, tipo=1)
         for bus_num in list_bus:
            # se modifica el tipo del bus
            ierr = psspy.bus_chng_3(bus_num, [2, _i, _i, _i], [_f, _f, _f, _f, _f, _f, _f], _s)
            # se crea una planta en el bus para poder añadir después el generador
            ierr = psspy.plant_data(bus_num, _i, [_f, _f])
            # se crea el generador con Pgen=0.01 MW
            intgar = [_i, _i, _i, _i, _i]
            Pgen = 0.01  # MW
            Qmin = 0  # MVar
            Qmax = 0  # MVar
            realar = [Pgen, _f, Qmin, Qmax, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f]
            idn = str(11)
            ierr = psspy.machine_data_2(bus_num, idn, intgar, realar)
      except Exception as e:
         raise StandardError('Error al modificar los nudos en el caso de referencia: {}'.format(e.message))

      try:
         # Modificacion del rateA y rateB segun ficheros de entrada
         #se recupera una lista con ramas
         list_branches = redpsse.get_branch_list()
         for branch in list_branches:
            ibus = branch.from_bus
            jbus = branch.to_bus
            ckt= branch.idn
            #se calculan los nuevos rates A y B de la rama segun parametros de entrada
            rateA=parametros.Rate_A/100 * branch.rate_a
            rateB=parametros.Rate_B/100 * branch.rate_a
            intgar=[_i,_i,_i,_i,_i,_i]
            realar=[_f,_f,_f,rateA,rateB,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f]
            #se modifica la rama con los nuevos rates A y B
            ierr = psspy.branch_data(ibus, jbus, ckt, intgar, realar)
      except Exception as e:
         raise StandardError('Error al modificar los rates A y B de las ramas en el caso de referencia: {}'.format(e.message))

      #se guarda temporalmente el caso procesado
      ierr = psspy.save(os.path.join(Rutas().ruta_casos_procesados, str(x.N_Caso) + '_procesado.sav'))

def crea_sub_mon_con(sistemas_estudio,parametros,info_casos):

   def func_sistema():
      #escribe el fichero de definición del subsistema para el sistema de transporte
      #se obtienen las areas del caso y se cuentan
      areas = redpsse.get_areas()
      area_numbers=[]
      for x in areas:
         area_numbers.append(x.number)
      n=area_numbers.__len__()

      #si existe el area 9, se considera caso islas
      if 9 in area_numbers:
         Umin=parametros.U_min_i
         Umax=parametros.U_max_i
      else:
         Umin=parametros.U_min_p
         Umax=parametros.U_max_p

      #ruta del fichero del subsistema
      path = os.path.join(Rutas().ruta_casos_procesados, str(caso.N_Caso) + '_' + str(sistema.Nombre) + '.sub')
      Sub = open(path, 'w')
      #escritura del fichero del subsistema
      Sub.write('SUBSYSTEM \'CON_MON\'\n')
      Sub.write('   JOIN GROUP_1\n')
      for area in area_numbers:
         if area not in [6,7,8]:
            Sub.write('      AREA ' + str(area) + '\n')
      Sub.write('      KVRANGE ' + str(Umin) +' '+ str(Umax)+ '\n')
      Sub.write('   END\n')
      Sub.write('END\n')
      Sub.write('SUBSYSTEM \'S.ESTUDIO\'\n')
      Sub.write('   KVRANGE ' + str(Umin) +' '+ str(Umax)+ '\n') #como sistema de estudio se considera el rango de tensiones definido
      Sub.write('END\n')
      Sub.write('SUBSYSTEM \'S.OPUESTO\'\n')
      Sub.write('   KVRANGE ' + str(1) +' '+ str(Umin-1) + '\n') #como sistema opuesto se considera el resto de tensiones
      Sub.write('END\n')
      Sub.write('END\n')

      return path

   def func_ca():
      # escribe el fichero de definición del subsistema para el caso de comunidades autónomas
      #se obtienen las zonas del estudio y se cuentan
      zonas = []
      zona = sistema.Sistema.split(',')
      for z in zona:
         zonas.append(int(z))

      #se mueven los buses una zona ficticia 99
      #primero es necesario obtener los buses de las zonas de estudio
      bus_list=redpsse.get_bus_number_by_zonas(zonas)
      l = bus_list.__len__()
      psspy.bsys(0, 0, [1, 400], 0, [], l, bus_list, 0, [], 0, [])
      #cambio la zona del subsistema a 99
      psspy.zonm_2(0, 0, [1, 1, 1], 99)
      #se resetea el subsistema
      psspy.bsysdef(0, 0)

      #se obtienen todas las zonas del caso
      zonas_caso = []
      zona_caso = redpsse.get_zonas()
      for zc in zona_caso:
         if zc.number != 99:
            zonas_caso.append(int(zc.number))
      nz=zonas_caso.__len__()

      #se obtienen las areas del caso
      areas = redpsse.get_areas()
      area_numbers=[]
      for x in areas:
         area_numbers.append(x.number)

      #si existe el area 9, se considera caso islas
      if 9 in area_numbers:
         Umin=parametros.U_min_i
         Umax=parametros.U_max_i
      else:
         Umin=parametros.U_min_p
         Umax=parametros.U_max_p


      # Ruta del fichero
      path = os.path.join(Rutas().ruta_casos_procesados, str(caso.N_Caso) + '_' + str(sistema.Nombre) + '.sub')
      Sub = open(path, 'w')
      # Escribimos el fichero
      Sub.write('SUBSYSTEM \'CON_MON\'\n')
      Sub.write('   JOIN GROUP_1\n')
      for area in area_numbers:
         if area not in [6,7,8]:
            Sub.write('      AREA ' + str(area) + '\n')
      Sub.write('      KVRANGE ' + str(Umin) +' '+ str(Umax)+ '\n')
      Sub.write('   END\n')
      Sub.write('END\n')
      Sub.write('SUBSYSTEM \'S.ESTUDIO\'\n')
      Sub.write('ZONE 99\n')
      Sub.write('END\n')
      Sub.write('SUBSYSTEM \'S.OPUESTO\'\n')
      for zonac in zonas_caso:
         Sub.write('ZONE ' + str(zonac) + '\n')
      for i in range(0,nz,1):
         Sub.write('END\n')
      Sub.write('END\n')

      return path

   def func_nudos():

      # escribe el fichero de definición del subsistema para el caso de agrupaciones de nudos
      buses = []
      bus = sistema.Sistema.split(',')
      for b in bus:
         buses.append(int(b))
      n = buses.__len__()

      #se crea el area 99
      psspy.area_data(99, _i, [_f, _f], r"""S.ESTUDIO""")
      #se mueven los buses del sistema de estudio
      for bus in buses:
         psspy.bus_chng_3(bus, [_i, 99, _i, _i], [_f, _f, _f, _f, _f, _f, _f], _s)

      #se obtienen las areas del caso y se cuentan
      areas = redpsse.get_areas()
      area_numbers=[]
      for x in areas:
         if x.number !=99:
            area_numbers.append(x.number)
      na=area_numbers.__len__()

      #si existe el area 9, se considera caso islas
      if 9 in area_numbers:
         Umin=parametros.U_min_i
         Umax=parametros.U_max_i
      else:
         Umin=parametros.U_min_p
         Umax=parametros.U_max_p

      # Ruta del fichero
      path = os.path.join(Rutas().ruta_casos_procesados, str(caso.N_Caso) + '_' + str(sistema.Nombre) + '.sub')
      Sub = open(path, 'w')
      # Escribimos el fichero
      Sub.write('SUBSYSTEM \'CON_MON\'\n')
      Sub.write('   JOIN GROUP_1\n')
      for area in area_numbers:
         if area not in [6,7,8]:
            Sub.write('      AREA ' + str(area) + '\n')
      Sub.write('      AREA 99\n')
      Sub.write('      KVRANGE ' + str(Umin) +' '+ str(Umax)+ '\n')
      Sub.write('   END\n')
      Sub.write('END\n')
      Sub.write('SUBSYSTEM \'S.ESTUDIO\'\n')
      Sub.write('AREA 99\n')
      Sub.write('END\n')
      Sub.write('SUBSYSTEM \'S.OPUESTO\'\n')
      for area in area_numbers:
         Sub.write('AREA ' + str(area) + '\n')
      for a in range(0,na,1):
         Sub.write('END\n')
      Sub.write('END\n')

      return path

   def select_case():

      try:
         # se selcciona funcion a aplicar segun tipo de fichero .sub a crear
         dict = {
            'SISTEMA': func_sistema,
            'CA': func_ca,
            'NUDOS': func_nudos,
         }
      except Exception as e:
         raise StandardError('Error al crear el fichero .sub: {}'.format(e.message))

      return dict

   def crear_mon():
      #escribe el fichero de monitorizacion
      try:
         # Ruta del fichero
         path = os.path.join(Rutas().ruta_casos_procesados, str(caso.N_Caso) + '.mon')
         Sub = open(path, 'w')
         # Escribimos el fichero
         Sub.write('MONITOR BRANCHES IN SUBSYSTEM \'CON_MON\'\n')
         Sub.write('MONITOR TIES FROM SUBSYSTEM \'CON_MON\'\n')
         Sub.write('END\n')
         Sub.write('END\n')
      except Exception as e:
         raise StandardError('Error al crear el fichero .mon: {}'.format(e.message))

      return path

   def crear_con():
      #escribe el fichero de contingencias
      try:
         # Ruta del fichero

         path= os.path.join(Rutas().ruta_casos_procesados, str(caso.N_Caso) + '.con')
         pathN_2  = os.path.join(Rutas().ruta_inputs, 'Contingencias_N_2.con')
         shutil.copy(pathN_2, path)
         Sub=open(path, 'a')
         # Escribimos el fichero
         Sub.write('SINGLE BRANCH IN SUBSYSTEM \'CON_MON\'\n')
         Sub.write('SINGLE TIE FROM SUBSYSTEM \'CON_MON\'\n')
         Sub.write('END\n')
         Sub.write('END\n')
      except Exception as e:
         raise StandardError('Error al crear el fichero .con: {}'.format(e.message))

      return path

   # se elige caso aparamenta y se calculan los criterios de corto
   list_dfax=[]
   for caso in info_casos:

      try:
         #se encuentra caso en la carpeta y se carga
         path_caso_psse = os.path.join(Rutas().ruta_casos_procesados, str(caso.N_Caso) + '_procesado.sav')
         caso_pss = redpsse.CasoPSSE(filepath=path_caso_psse)
         caso_pss.load()
         convergencia = redpsse.convergeCaso()
         print('Convergencia del caso ' + str(caso.N_Caso) + '_procesado.sav: ' + str(convergencia))
      except Exception as e:
         raise StandardError('Error al cargar el caso de referencia: {}'.format(e.message))

      fichero_mon = crear_mon()
      fichero_con = crear_con()

      for sistema in sistemas_estudio:
         tipo=sistema.Tipo
         crear_sub = select_case()
         fichero_sub = crear_sub[tipo]()
         try:
            fichero_dfax = os.path.join(Rutas().ruta_dfax, str(caso.N_Caso) + '_' + str(sistema.Nombre) + '.dfx')
            ierr = psspy.dfax_2([1, 1, 0], fichero_sub, fichero_mon, fichero_con, fichero_dfax)
            list_dfax.append(fichero_dfax)
            if ierr!=0:
               print('Error al crear el fichero DFAX ' + str(caso.N_Caso) + '_' + str(sistema.Nombre) + '.dfx, ierr=' + str(ierr))
         except Exception as e:
            raise StandardError('Error al crear el fichero DFAX: {}'.format(e.message))

   return list_dfax

def run_TLTG(list_DFAX):

   list_output=[]

   for fichero_dfax in list_DFAX:
      #se guarda en un fichero de texto la salida del TLTG
      ruta_output = fichero_dfax.replace('.dfx', '.txt')
      list_output.append(ruta_output)
      psspy.report_output(2, ruta_output, options=[0, 1])
      # ierr = tltg(options, values, labels, dfxfile)
      options=[1,2,1,0,0,0,0,0,0,0,0,1,1,0,1,10000,1]
      values=[ 1.1, 100.0, 5000.0, 0.05, 1.0, 0.03, 300.0]
      ierr=psspy.tltg(options, values,[r"""S.ESTUDIO""", r"""S.OPUESTO""", "", "", "", "", "", ""],fichero_dfax)
      if ierr != 0:
         print('Error al lanzar el TLTG del fichero ' + str(fichero_dfax) + ', ierr=' + str(ierr))

   return list_output