# coding=utf-8
#---------------------------------------------------------------------------------------------------
# Name:        red_psse.py
# Purpose:     Mdulo para traduccir mediente pandas las resultados para los corto de  ascc y  ic
# Author:      Ricardo Vázquez
# Created:     2017-12-01
#---------------------------------------------------------------------------------------------------
import pandas as pd
import cStringIO
from entidades import *
import re
from redpsse import get_elementos_bus,get_name_ext_to_bus
import redpsse
from math import sqrt, exp


def get_resultados_posicion_ascc_iecs_hompolar_trifa(bus_num, report):
   """
   Retorna los valores del calculo de falta ASCC o IECS en una estructura coherentes
   :param bus_num: bus donde se ha realizado la falta
   :param report: valores obtenido
   :type report: str
   :return: instancia de ElementIcc
   :rtype:  entidades.ElementIcc
   """
   try:

      x_r=None
      x_r_0=None
      #Texto de final de cada tabla de aportacion de las posiciones
      text_fin='-----------------------------------------------------------------------------------------------------------------------------------------------'
      patron = re.compile('X--------- FROM ----------X\s+AREA\sCKT\sI.Z\s+.I\W', re.I | re.MULTILINE) #Patron desde donde empeiza la tabla de oportaciones para trifasica
      patron_2=re.compile('-----------------------------------------------------------------------------------------------------------------------------------------------', re.I | re.MULTILINE)
      patron_3=re.compile('X----------------------------------------THREE PHASE FAULT---------------------------------------X', re.I | re.MULTILINE)
      patron_4=re.compile('Z-:',re.I | re.MULTILINE)
      patron_5=re.compile(' X--------- FROM ----------X\s+AREA\sCKT\sI.Z\s+.IA',re.I | re.MULTILINE) #Patron desde donde empeiza la tabla de oportaciones para hompolar
      patron_6=re.compile('THEVENIN IMPEDANCE,\sX\WR\s+\WOHM\W\s+Z\W:',re.I | re.MULTILINE  )
      patron_7 = re.compile(',.\d+\.', re.I | re.MULTILINE)
      patron_float = re.compile('\d+\.\d+', re.I | re.MULTILINE)
      patron_8 = re.compile('Z0:', re.I | re.MULTILINE)
      patron_9 = re.compile('\n', re.I | re.MULTILINE)

      matcher = patron.search(report)
      matcher_2=patron_2.search(report)
      matcher_4=patron_4.search(report)
      matcher_3 = patron_3.search(report)
      matcher_5 = patron_5.search(report)
      matcher_6=patron_6.search(report)

      if matcher !=None and matcher_2 !=None:
         report_traifasica_posiciones=report[matcher.start():matcher_2.start()]
      else:
         raise StandardError('No se encuentra ala expresion regular para la tabla de apotarciones trifasicas')
      if matcher_6 !=None and matcher_4 !=None:
         report_trifasica_rx=report[matcher_6.end():matcher_4.start()]

         matcher = patron_7.search(report_trifasica_rx)
         if matcher != None:
            x_r = float(report_trifasica_rx[matcher.start() + 1:].strip())
         else:
            raise StandardError(' No se ha encontrado la expresion regular 1 para X/R monofasica')
      else:
         raise StandardError('No se encuentra a la expresion regular para la tabla de X/R trifasica')

      if matcher_5 !=None and matcher_2 !=None:
         report_mono_posiciones=report[matcher_5.start():]
      else:
         raise StandardError('No se encuentra ala expresion regular para la tabla de apotarciones monofasicas')

      matcher = patron_8.search(report)
      if matcher !=None:
         x_r_0=report[matcher.end() + 1:].strip()
         matcher = patron_7.search(x_r_0)
         matcher_1=patron_9.search(x_r_0)
         if matcher != None and matcher_1!=None:
            x_r_0 = float(x_r_0[matcher.start() + 1:matcher_1.start()].strip())
         else:
            raise StandardError(' No see ha encontrado la expresion regular 1 para X/R m')

      else:
         raise StandardError('No se encuentra a la expresion regular para la tabla de X/R monofasica')

      report_mono_posiciones=report_mono_posiciones.replace(text_fin,'')

      fwidths = [28, 5, 4, 8, 11,9]
      names = ['FROM', 'AREA', 'CKT', 'I/Z', 'I+','AN(I+)']
      df_posiciones = pd.read_fwf(cStringIO.StringIO(report_traifasica_posiciones), widths=fwidths, header=0, names=names, converters={'CKT':str})
      df_posiciones = df_posiciones.dropna(how='all')
      df_posiciones.loc[:, :] = df_posiciones.loc[:, :].fillna('')
      df_posiciones['Trafo_3dev'] = pd.Series(False, index=df_posiciones.index)



      fwidths = [28, 5, 4, 8, 11,9]
      names = ['FROM', 'AREA', 'CKT', 'I/Z', 'IA','AN(IA)']
      df_posiciones_mono = pd.read_fwf(cStringIO.StringIO(report_mono_posiciones), widths=fwidths, header=0,
                                  names=names, converters={'CKT':str})
      df_posiciones_mono = df_posiciones_mono.dropna(how='all')
      df_posiciones_mono.loc[:, :] = df_posiciones_mono.loc[:, :].fillna('')
      df_posiciones_mono['Trafo_3dev'] = pd.Series(False, index=df_posiciones_mono.index)


      for item, frame in df_posiciones.iterrows():

         if frame['FROM'].find('3WNDTR') != -1:
            new_bus_to = re.sub(r"3WNDTR", "", frame['FROM']).strip()
            new_bus_to = re.sub(r"WND 1", "", new_bus_to).strip()
            new_bus_to = re.sub(r"WND 2", "", new_bus_to).strip()
            frame['FROM'] = new_bus_to
            frame['Trafo_3dev'] = True
         else:
            new_bus_to = re.sub(r"\s+\[.*", "", frame['FROM'])
            if new_bus_to != '':
               new_bus_to = new_bus_to.strip()
               frame['FROM'] = new_bus_to

         try:
            frame['FROM'] = int(frame['FROM'])
         except:
            frame['FROM'] = frame['FROM']

         try:
            # if frame['CKT'][0]=='0':
            #    frame['CKT'] = str(frame['CKT'])
            # else:
            #    frame['CKT'] = int(frame['CKT'])
            #    frame['CKT'] = str(frame['CKT'])
            frame['CKT'] = str(frame['CKT'])
         except:
            frame['CKT'] = frame['CKT']

         try:
            frame['I+']=float(frame['I+'])
         except:
            pass

         df_posiciones.ix[item] = frame

      for item, frame in df_posiciones_mono.iterrows():

         if frame['FROM'].find('3WNDTR') != -1 or frame['FROM'].find('WND 2') != -1:
            new_bus_to = re.sub(r"3WNDTR", "", frame['FROM']).strip()
            new_bus_to = re.sub(r"WND 1", "", new_bus_to).strip()
            new_bus_to = re.sub(r"WND 2", "", new_bus_to).strip()
            frame['FROM'] = new_bus_to
            frame['Trafo_3dev'] = True
         else:
            new_bus_to = re.sub(r"\s+\[.*", "", frame['FROM'])
            if new_bus_to != '':
               new_bus_to = new_bus_to.strip()
               frame['FROM'] = new_bus_to

         try:
            frame['FROM'] = int(frame['FROM'])
         except:
            frame['FROM'] = frame['FROM']

         try:
            if frame['CKT'][0]=='0':
               frame['CKT'] = str(frame['CKT'])
            else:
               frame['CKT'] = int(frame['CKT'])
               frame['CKT'] = str(frame['CKT'])
         except:
            frame['CKT'] = frame['CKT']

         try:
            frame['IA'] = float(frame['IA'])
         except:
            pass

         df_posiciones_mono.ix[item] = frame

      elemets = get_elementos_bus(bus_num)
      trafos = elemets.get_trafos()
      branchs = elemets.get_branches()
      machine = elemets.get_maqs()

      list_resultados = []

      if trafos != []:
         for trafo in trafos:
            df = None
            if trafo.is_3D and trafo.bus_1kv == None:
               name = '[' + trafo.name + ']'
               df = df_posiciones.loc[
                    lambda df: (df['Trafo_3dev'] == True) & ((df['FROM'] == name) & (df['CKT'] == trafo.id)), :]

               df_mono = df_posiciones_mono.loc[
                    lambda df: (df['Trafo_3dev'] == True) & ((df['FROM'] == name) & (df['CKT'] == trafo.id)), :]
            elif trafo.is_3D and trafo.bus_1kv != None:
               raise NotImplementedError()
            else:
               bus_to = trafo.bus_i if trafo.bus_i != bus_num else trafo.bus_j
               df = df_posiciones.loc[
                    lambda df: (df['Trafo_3dev'] == False) & ((df['FROM'] == bus_to) & (df['CKT'] == trafo.id)), :]
               df_mono = df_posiciones_mono.loc[
                    lambda df: (df['Trafo_3dev'] == False) & ((df['FROM'] == bus_to) & (df['CKT'] == trafo.id)), :]

            if df.empty == False and df_mono.empty==False:
               df = df.iloc[0]
               df_mono = df_mono.iloc[0]
               list_resultados.append(
                  ElementIcc(element=trafo, icc_tri=0, icc_mono=0, icc_tri_posicion=df['I+'], icc_mono_posicion=df_mono['IA'], ang_mono_posicion=df_mono['AN(IA)'], ang_tri_posicion=df['AN(I+)']))

      if branchs != []:
         for branch in branchs:
            df = None
            bus_to = branch.from_bus if branch.from_bus != bus_num else branch.to_bus
            df = df_posiciones.loc[
                 lambda df: (df['Trafo_3dev'] == False) & ((df['FROM'] == bus_to) & (df['CKT'] == branch.idn)), :]

            df_mono = df_posiciones_mono.loc[
                 lambda df: (df['Trafo_3dev'] == False) & ((df['FROM'] == bus_to) & (df['CKT'] == branch.idn)), :]

            if df.empty == False and df_mono.empty==False:
               df = df.iloc[0]
               df_mono = df_mono.iloc[0]
               list_resultados.append(
                  ElementIcc(element=branch, icc_tri=0, icc_mono=0, icc_tri_posicion=df['I+'], icc_mono_posicion=df_mono['IA'], ang_mono_posicion=df_mono['AN(IA)'], ang_tri_posicion=df['AN(I+)']))

      if machine != []:
         for mac in machine:
            df = df_posiciones.loc[
                 lambda df: (df['Trafo_3dev'] == False) & ((df['FROM'].str.strip() == 'SYNCHRONOUS MACHINE') & (df['CKT'] == mac.idn)), :]

            df_mono = df_posiciones_mono.loc[
                 lambda df: (df['Trafo_3dev'] == False) & ((df['FROM'].str.strip() == 'SYNCHRONOUS MACHINE') & (df['CKT'] == mac.idn)), :]

            if df.empty == False and df_mono.empty == False:
               df = df.iloc[0]
               df_mono = df_mono.iloc[0]
               list_resultados.append(
                  ElementIcc(element=mac, icc_tri=0, icc_mono=0, icc_tri_posicion=df['I+'],
                             icc_mono_posicion=df_mono['IA'], ang_mono_posicion=df_mono['AN(IA)'], ang_tri_posicion=df['AN(I+)']))

      return  list_resultados,x_r,x_r_0

   except Exception as e:
      raise StandardError('Error al obtner los resultados del ascc={} '.format(e.message))

def get_resultados_LOUT_thevenin(report, bus_num, posicones, id_tipo_algoritmo):
   """
   Obtiene los valores LOUT de loas impdenacias de thevenin y de las
   :param report:
   :param bus_num:
   :param posicones: datos por posciones
   :type posicones: list of ElementIcc
   :return:
   """

   try:
      errores=[]
      text_fin = '-----------------------------------------------------------------------------------------------------------------------------------------------'
      patron_bus_cabecera = re.compile('X---------- BUS ----------X\s+',re.I | re.MULTILINE)

      patron_fin = re.compile('---------------------------------------------------------------------------------------------------------------\s+',
         re.I | re.MULTILINE)

      patron_4 = re.compile('Z-:', re.I | re.MULTILINE)

      patron_lout_cabecera = re.compile(' X---------- BUS ----------X\sX-------- TO BUS ---------XCKT',
                            re.I | re.MULTILINE)
      patron_impedancia = re.compile('THEVENIN IMPEDANCE,\sX\WR\s+\WOHM\W\s+Z\W:', re.I | re.MULTILINE)
      patron_7 = re.compile(',.\d+\.', re.I | re.MULTILINE)
      patron_float = re.compile('\d+\.\d+', re.I | re.MULTILINE)
      patron_9 = re.compile('\n', re.I | re.MULTILINE)
      patron_z0 = re.compile('Z0:', re.I | re.MULTILINE)
      patron_z_pos = re.compile('Z\w:', re.I | re.MULTILINE)
      patron_z_neg = re.compile('Z-:', re.I | re.MULTILINE)

      matcher_cabe_bus = patron_bus_cabecera.search(report)
      matchers_fin = patron_fin.search(report)

      list_df=[]

      #Obtengo los datos para el BUS
      if matcher_cabe_bus != None and matchers_fin !=None:
         report_bus = report[matcher_cabe_bus.start():matchers_fin.start()]

         fwidths = [28,4, 12, 10, 10]
         names = ['FROM_BUS', 'TIPO', 'MVA', 'AMP', 'DEG']
         df_posiciones = pd.read_fwf(cStringIO.StringIO(report_bus), widths=fwidths, header=0,
                                     names=names)
         df_posiciones = df_posiciones.dropna(how='all')
         df_posiciones.loc[:, :] = df_posiciones.loc[:, :].fillna('')
         df_posiciones = df_posiciones.ix[0:1]
         df_posiciones['FROM_BUS'] = df_posiciones['FROM_BUS'].replace("\s\[.*", "", regex=True)
         df_posiciones['Trafo_3dev'] = pd.Series(False, index=df_posiciones.index)

         from_bus_ = int(df_posiciones['FROM_BUS'].ix[0])
         to_bus = 0
         ckt = ''
         icc_tifa = float(df_posiciones['AMP'].iat[0])
         icc_tifa_ang = float(df_posiciones['DEG'].iat[0])
         icc_mono = float(df_posiciones['AMP'].iat[1])
         icc_mono_ang = float(df_posiciones['DEG'].iat[1])

         impedancias=__get_impedancias_thevenin_by_Pd(report)
         datos = {'from_bus': from_bus_, 'to_bus': to_bus, 'ckt': ckt, 'icc_tifa': icc_tifa,'Trafo_3dev':df_posiciones['Trafo_3dev'].iat[0],
                  'icc_tifa_ang':icc_tifa_ang,'icc_mono': icc_mono, 'icc_mono_ang': icc_mono_ang,
                  'zpos': impedancias['zpos'], 'zcero': impedancias['zcero'], 'zneg': impedancias['zneg'],
                  'xrpos': impedancias['xrpos'], 'xrcero': impedancias['xrcero'], 'xrneg': impedancias['xrneg']}
         list_df.append(datos)
      else:
         raise StandardError('No se encuentra la expresion regular para la tabla de impedancias bus')

      #Obtengo los dataframe para los posiciones
      while True:
         if report=='':
            break

         matcher_lout_cabe = patron_lout_cabecera.search(report)
         if matcher_lout_cabe !=None:
            report=report[matcher_lout_cabe.start():]
         else:
            raise StandardError('No se encuentra la expresion regular para la tabla de impedancias LOUT')
         matchers_fin = patron_fin.search(report)

         if matchers_fin !=None:
            report_lout1=report[:matchers_fin.start()]

            report = report[matchers_fin.end():] #Desecho esta tabla del rsport para que en el siguietne bucle no se duplique

            fwidths = [28, 28,4, 4, 12, 10, 9]
            names = ['FROM_BUS', 'TO_BUS', 'CKT', 'TIPO', 'MVA', 'AMP', 'DEG']
            df_posiciones = pd.read_fwf(cStringIO.StringIO(report_lout1), widths=fwidths, header=0,
                                        names=names,converters={'CKT':str})

            df_posiciones = df_posiciones.dropna(how='all')
            df_posiciones.loc[:, :] = df_posiciones.loc[:, :].fillna('')
            df_posiciones = df_posiciones.ix[0:1] #Solo me quedo con la primera fila.

            df_posiciones['MVA'] = df_posiciones['MVA'].astype('float')
            df_posiciones['AMP'] = df_posiciones['AMP'].astype('float')
            df_posiciones['DEG'] = df_posiciones['DEG'].astype('float')
            df_posiciones=__get_dataframe_lout(df_posiciones) #Adapto el Dataframe

            from_bus_=int(df_posiciones['FROM_BUS'].iat[0])
            to_bus=int(df_posiciones['TO_BUS'].iat[0])
            ckt = df_posiciones['CKT'].iat[0]
            icc_tifa= float(df_posiciones['AMP'].iat[0])
            icc_tifa_ang = float(df_posiciones['DEG'].iat[0])
            icc_mono = float(df_posiciones['AMP'].iat[1])
            icc_mono_ang = float(df_posiciones['DEG'].iat[1])

            matchers_impedancia =patron_impedancia.search(report_lout1)
            if matchers_impedancia !=None:
               report_impedancia=report_lout1[matchers_impedancia.start():]
               impedancias = __get_impedancias_thevenin_by_Pd(report_impedancia) #Obtengo las impedancias
            else:
               raise StandardError('No se encuentra el patron impedancia para las tabla de LOUT')
            datos={'from_bus':from_bus_, 'to_bus':to_bus, 'ckt':ckt,'icc_tifa':icc_tifa,'icc_tifa_ang':icc_tifa_ang,
                   'Trafo_3dev':df_posiciones['Trafo_3dev'].iat[0],
             'icc_mono':icc_mono,'icc_mono_ang':icc_mono_ang,
             'zpos':impedancias['zpos'] , 'zcero':impedancias['zcero'], 'zneg':impedancias['zneg'],
             'xrpos':impedancias['xrpos'], 'xrcero':impedancias['xrcero'], 'xrneg':impedancias['xrneg']}
            list_df.append(datos)
         else:
            raise StandardError('No se encuentra el patron fin tabla de impedancias LOUT')

      df=pd.DataFrame(list_df)
      df['from_bus'] = df['from_bus'].astype('int')
      df['to_bus'] = df['to_bus'].astype('int')
      list_resultados=[]

      bus_falta = Bus(bus_num=bus_num)
      bus_falta.read_attrs()

      posicones.append(ElementIcc(element=bus_falta, icc_tri=0, icc_mono=0,ang_tri=0, ang_mono=0))

      for pos in posicones:
         flag_bus=False
         try:
            pos.tipo_algoritmo=id_tipo_algoritmo
            if pos.check_isbus():
               df_element=df.loc[lambda x: (x['to_bus']==0)&(x['Trafo_3dev'] == False)]
               flag_bus=True
            elif pos.check_isbranch():
               bus_to = pos.element.to_bus if pos.element.to_bus != bus_num else pos.element.from_bus
               df_element = df.loc[lambda x: (x['to_bus'] == bus_to) & (x['ckt'] == pos.element.idn) & (x['Trafo_3dev'] == False), :]

            elif pos.check_ismachine():
               #El lout NO TIENE MACHINE. El lOUT  de una maquina es igual al del nudo menos su aportacion
               resul_2 = filter(lambda x: x.check_isbus(), posicones)

               if resul_2 != []:
                  icc_tri_total = resul_2[0].icc_tri
                  icc_mono_total = resul_2[0].icc_mono
               else:
                  raise StandardError('No se ha encontrado la falta sobre el bus={}'.format(bus_num))

               pos.icc_tri = icc_tri_total - pos.icc_tri_posicion  # El lOUT  de una maquina es igual al del nudo menos su aportacion
               pos.icc_mono = icc_mono_total - pos.icc_mono_posicion
               continue


            elif pos.check_istrafo():
               trafo_3d=pos.element.is_3D
               bus_to = pos.element.bus_j if pos.element.bus_j != bus_num else pos.element.bus_i
               if trafo_3d:
                  df_element = df.loc[lambda x: (x['to_bus'] == 0) & (x['ckt'] == pos.element.id) & (x['Trafo_3dev'] == trafo_3d),: ]
               else:
                  df_element = df.loc[lambda x: (x['to_bus'] == bus_to) & (x['ckt'] == pos.element.id) & (
                           x['Trafo_3dev'] == trafo_3d), :]
            if not df_element.empty:
               pos.icc_tri=float(df_element['icc_tifa'].iat[0])
               pos.ang_tri=float(df_element['icc_tifa_ang'].iat[0])
               pos.icc_mono=float(df_element['icc_mono'].iat[0])
               pos.ang_mono=float(df_element['icc_mono_ang'].iat[0])
               pos.x_r_trifa=float(df_element['xrpos'].iat[0])
               pos.x_r_mono=float(df_element['xrcero'].iat[0])
               pos.x_r_neg=float(df_element['xrneg'].iat[0])
               pos.z_cero=float(df_element['zcero'].iat[0])
               pos.z_posit=float(df_element['zpos'].iat[0])
               pos.z_neg=float(df_element['zneg'].iat[0])
               # calculo corrientes de referencia para analisis de criterios en aparamenta
               if flag_bus==True:
                  pos.icc3_85 = round(pos.icc_tri * 0.85, 2)
                  pos.icc1_85 = round(pos.icc_mono * 0.85, 2)
                  pos.icc3_din = round(pos.icc_tri * sqrt(2) * 1.8, 2)
                  pos.icc1_din = round(pos.icc_mono * sqrt(2) * 1.8, 2)
                  pos.icc3_term = round(sqrt(0.8 * pos.icc_tri ** 2), 2)
                  pos.icc1_term = round(sqrt(0.8 * pos.icc_mono ** 2), 2)
                  pos.icc3_pos_85 = 0
                  pos.icc1_pos_85 = 0
                  pos.icc3_pos_din = 0
                  pos.icc1_pos_din = 0
                  pos.icc3_pos_term = 0
                  pos.icc1_pos_term = 0
               else:
                  pos.icc3_85 = round(pos.icc_tri * 0.85, 2)
                  pos.icc1_85 = round(pos.icc_mono * 0.85, 2)
                  pos.icc3_din = round(pos.icc_tri * sqrt(2) * 1.8, 2)
                  pos.icc1_din = round(pos.icc_mono * sqrt(2) * 1.8, 2)
                  pos.icc3_term = round(sqrt(0.8 * pos.icc_tri ** 2), 2)
                  pos.icc1_term = round(sqrt(0.8 * pos.icc_mono ** 2), 2)
                  pos.icc3_pos_85 = round(pos.icc_tri * 0.85, 2)
                  pos.icc1_pos_85 = round(pos.icc_mono * 0.85, 2)
                  pos.icc3_pos_din = round(pos.icc_tri * sqrt(2) * (1.02+0.98*exp(-3*pos.x_r_trifa)), 2)
                  pos.icc1_pos_din = round(pos.icc_mono * sqrt(2) * (1.02+0.98*exp(-3*pos.x_r_mono)), 2)
                  pos.icc3_pos_term = round(sqrt(0.8 * pos.icc_tri ** 2), 2)
                  pos.icc1_pos_term = round(sqrt(0.8 * pos.icc_mono ** 2), 2)
            else:
               raise StandardError('Error al realizar el filtrado del DataFrame de report sobre las posiciones: {}'.format(pos.element))
         except Exception as e:
            errores.append(e)
            pos.icc_tri = 0
            pos.ang_tri = 0
            pos.icc_mono = 0
            pos.ang_mono = 0
            pos.x_r_trifa = 0
            pos.x_r_mono = 0
            pos.x_r_neg = 0
            pos.z_cero = 0
            pos.z_posit = 0
            pos.z_neg = 0
            pos.icc3_85 = 0
            pos.icc1_85 = 0
            pos.icc3_din = 0
            pos.icc1_din = 0
            pos.icc3_term = 0
            pos.icc1_term = 0
            pos.icc3_pos_85 = 0
            pos.icc1_pos_85 = 0
            pos.icc3_pos_din = 0
            pos.icc1_pos_din = 0
            pos.icc3_pos_term = 0
            pos.icc1_pos_term = 0

      return posicones,errores



   except Exception as e:
      raise StandardError('Error al get_resultados_posicion_thevenin: {}'.format(e))

def __get_impedancias_thevenin_by_exprRe(report):
   """
   Obtiene las impedancias de report de Faul ASCC o IECS
   :param report:
   :return:
   """

   try:
      patron_float = re.compile('\d+\.\d+', re.I | re.MULTILINE)
      patron_z0 = re.compile('Z0:', re.I | re.MULTILINE)
      patron_z_pos = re.compile('Z.:', re.I | re.MULTILINE)
      patron_z_neg = re.compile('Z-:', re.I | re.MULTILINE)
      patron_xr=re.compile(',\s+/d+\.\d+', re.I | re.MULTILINE) #, 14.50651

      matcher_zpos = patron_z_pos.search(report)
      report_z=report[matcher_zpos.start():]
      matcher_di = patron_float.search(report_z)
      z_posi = report_z[matcher_di.start():matcher_di.end()]
      matcher_xr=patron_xr.search(report[matcher_zpos.start():])
      xr_posi=report_z[matcher_xr.start():matcher_xr.end()]


      matcher_z0 = patron_z0.search(report)
      matcher_di = patron_float.search(report[matcher_z0.start():])
      z_0 = report[matcher_z0.start():][matcher_di.start():matcher_di.end()]

      matcher_z_neg = patron_z_neg.search(report)
      matcher_di = patron_float.search(report[matcher_z_neg.start():])
      z_neg = report[matcher_z_neg.start():][matcher_di.start():matcher_di.end()]

      return z_posi,z_0,z_neg
   except Exception as e:
      raise StandardError('Error al __get_impedancias_thevenin {}'.format(e))

def __get_impedancias_thevenin_by_Pd(report):
   """
   Obtiene las impedancias de report de Faul ASCC o IECS
   :param report:
   :return:
   :rtype:{'zpos':None,'zcero':None,'zneg':None,xrpos':None,'xrcero':None,'xrneg':None}
   """

   try:
      patron_float = re.compile('\d+\.\d+', re.I | re.MULTILINE)
      patron_z0 = re.compile('Z0:', re.I | re.MULTILINE)
      patron_z_pos = re.compile('Z.:', re.I | re.MULTILINE)
      patron_z_neg = re.compile('Z-:', re.I | re.MULTILINE)
      patron_xr=re.compile(',\s+/d+\.\d+', re.I | re.MULTILINE) #, 14.50651
      patron_saltoliena = re.compile('\n\n', re.I | re.MULTILINE)

      matcher_zpos = patron_z_pos.search(report)
      matcher_z0 = patron_z0.search(report)
      matcher_z_neg = patron_z_neg.search(report)
      if matcher_zpos !=None and matcher_z0!=None and matcher_z_neg!=None:
         str_z_posi=report[matcher_zpos.start():matcher_z_neg.start()].replace(',','/').replace(':','')
         str_z_nega=report[matcher_z_neg.start():matcher_z0.start()].replace(',','/').replace(':','')
         str_z_cero = report[matcher_z0.start():].replace(',','/').replace(':','')
         matcher_saltoliena=patron_saltoliena.search(str_z_cero)
         str_z_cero = str_z_cero[:matcher_saltoliena.start()]
         tabla=str_z_posi+'\n'+str_z_nega+'\n'+str_z_cero

         names = ['VARIABLE', 'MOD', 'ANG', 'X/R']
         df_posi = pd.read_fwf(cStringIO.StringIO(str_z_posi), delimiter='/', names=names)
         df_nega = pd.read_fwf(cStringIO.StringIO(str_z_nega), delimiter='/', names=names)
         df_cero = pd.read_fwf(cStringIO.StringIO(str_z_cero), delimiter='/', names=names)
         df=df_posi.append(df_nega.loc[0,:]).append(df_cero.loc[0,:])

         df['ANG'] = df['MOD'].astype('float')
         df['ANG'] = df['ANG'].astype('float')
         df['X/R'] = df['X/R'].astype('float')

         df_posi = df.loc[lambda df: (df['VARIABLE'] == 'Z+')]
         df_nega = df.loc[lambda df: (df['VARIABLE'] == 'Z-')]
         df_cero = df.loc[lambda df: (df['VARIABLE'] == 'Z0')]


         zpos=df_posi['MOD'][0]

         datos={'zpos':df_posi['MOD'].iat[0],'zcero': df_cero['MOD'].iat[0],'zneg':df_nega['MOD'].iat[0],
                'xrpos':df_posi['X/R'].iat[0],'xrcero': df_cero['X/R'].iat[0],'xrneg':df_nega['X/R'].iat[0]}

      else:
         raise StandardError('No se ha en contrado los patron para las posiciones de Z+,Z0 o Z-')


      return datos

   except Exception as e:
      raise StandardError('Error al __get_impedancias_thevenin_by_Pd {}'.format(e))

def __get_dataframe_lout(df_posiciones):

   try:
      df_posiciones['Trafo_3dev'] = pd.Series(False, index=df_posiciones.index)

      patron = re.compile(u'\s+\[.*')
      df_posiciones['FROM_BUS'] = df_posiciones['FROM_BUS'].replace("\s\[.*", "", regex=True)
      df_posiciones['TO_BUS'] = df_posiciones['TO_BUS'].replace("\s\[.*", "", regex=True)

      for item, frame in df_posiciones.iterrows():
         matcher = patron.search(frame['TO_BUS'])

         if frame['TO_BUS'].find('3WNDTR') != -1:
            new_bus_to = re.sub(r"3WNDTR",'0', frame['TO_BUS']).strip()
            frame['TO_BUS'] = new_bus_to
            frame['Trafo_3dev'] = True

         else:
            new_bus_to = re.sub(r"\s+\[.*", "", frame['TO_BUS'])
            if new_bus_to != '':
               new_bus_to = new_bus_to.strip()
               frame['TO_BUS'] = new_bus_to
         try:

            frame['TO_BUS'] = int(frame['TO_BUS'])
         except:
            frame['TO_BUS'] = frame['TO_BUS']

         try:
            frame['CKT'] = str(frame['CKT'])
         except:
            frame['CKT'] = frame['CKT']

         df_posiciones.ix[item] = frame

      return df_posiciones
   except Exception as e:
      raise StandardError('Error al __get_dataframe_lout: {} '.format(e))

def get_resultados_pcc_ascc(bus_num, id_tipo_algoritmo):
   try:
      # Obengo los resultado del estudio por posicion
      value = redpsse.ascc_fault_posiciones([bus_num])
      # Los resultados del estudio por posicion/Aportacion los paso a clases
      resul_posiciones, x_r, x_r_0 = get_resultados_posicion_ascc_iecs_hompolar_trifa(bus_num=bus_num,report=value)
      value = redpsse.ascc_fault_lout_thevenin([bus_num])
      resul_posiciones,errores = get_resultados_LOUT_thevenin(bus_num=bus_num, report=value, posicones=resul_posiciones,id_tipo_algoritmo=id_tipo_algoritmo)

      return resul_posiciones,errores
   except Exception as e:
      raise StandardError('Erro al obtner los resultados de ASCC: {}'.format(e))

def get_resultados_pcc_iecs(bus_num,id_tipo_algoritmo):
   try:
      # Obengo los resultado del estudio por posicion
      value = redpsse.iecs_fault_posiciones([bus_num])
      # Los resultados del estudio por posicion los paso a clases
      resul_posiciones, x_r, x_r_0 = get_resultados_posicion_ascc_iecs_hompolar_trifa(bus_num=bus_num,report=value)
      value = redpsse.iecs_fault_lout_thevenin([bus_num])
      resul_posiciones,errores = get_resultados_LOUT_thevenin(bus_num=bus_num, report=value, posicones=resul_posiciones,
                                                      id_tipo_algoritmo=id_tipo_algoritmo)

      return resul_posiciones,errores
   except Exception as e:
      raise StandardError('Erro al obtner los resultados de IECS: {}'.format(e))




def get_resultados_lout_ascc_iecs_hompolar_trifa(bus_num, report):
   """
   Retorna los valores del calculo de falta ASCC o IECS en una estructura coherentes
   :param bus_num: bus donde se ha realizado la falta
   :param report: valores obtenido
   :type report: str
   :return: instancia de ElementIcc
   :rtype:  list of entidades.ElementIcc
   """
   try:

      list_resultados=[]

      patron = re.compile('THREE\sPHASE\sFAULT\s+X----LG FAULT---X', re.I | re.MULTILINE) #Patron desde donde empeiza la tabla de oportaciones para trifasica

      matcher = patron.search(report)

      if matcher !=None:
         report_traifasica_posiciones=report[matcher.start():]
      else:
         raise StandardError('No se encuentra ala expresion regular de THREE PHASE FAULT  X----LG FAULT---X')


      fwidths = [28,28,3,11,10,9,10,9]
      names=['FROM_BUS','TO_BUS','CKT','UNIT','I+','AN(I+)','3I0','AN(IA)']
      df_posiciones = pd.read_fwf(cStringIO.StringIO(report_traifasica_posiciones), widths=fwidths, header=1,names=names)
      df_posiciones = df_posiciones.dropna(how='all')
      df_posiciones.loc[:, :] = df_posiciones.loc[:, :].fillna('')
      df_posiciones['I+'] = df_posiciones['I+'].astype('float')
      df_posiciones['AN(I+)'] = df_posiciones['AN(I+)'].astype('float')
      df_posiciones['3I0'] = df_posiciones['3I0'].astype('float')
      df_posiciones['AN(IA)'] = df_posiciones['AN(IA)'].astype('float')

      #3WNDTR
      patron=re.compile(u'\s+\[.*')

      df_posiciones['Trafo_3dev'] = pd.Series(False, index=df_posiciones.index)


      df_posiciones['FROM_BUS'] = df_posiciones['FROM_BUS'].replace("\s\[.*", "", regex=True)

      for item, frame in df_posiciones.iterrows():
         matcher=patron.search(frame['TO_BUS'])

         if frame['TO_BUS'].find('3WNDTR') != -1:
            new_bus_to = re.sub(r"3WNDTR", "", frame['TO_BUS']).strip()
            frame['TO_BUS'] = new_bus_to
            frame['Trafo_3dev']=True

         else:
            new_bus_to=re.sub(r"\s+\[.*", "", frame['TO_BUS'])
            if new_bus_to !='':
               new_bus_to = new_bus_to.strip()
               frame['TO_BUS']=new_bus_to
         try:
            frame['TO_BUS']=int(frame['TO_BUS'])
         except:
            frame['TO_BUS']=frame['TO_BUS']

         try:
            frame['CKT']=int(frame['CKT'])
            frame['CKT'] = str(frame['CKT'])
         except:
            frame['CKT']=frame['CKT']



         df_posiciones.ix[item]=frame

      elemets = get_elementos_bus(bus_num)
      trafos=elemets.get_trafos()
      branchs=elemets.get_branches()

      df_bus_falta=df_posiciones.ix[0]
      bus_falta=Bus(bus_num=int(df_bus_falta['FROM_BUS']))
      bus_falta.read_attrs()

      list_resultados.append(ElementIcc(element=bus_falta,icc_tri=df_bus_falta['I+'],icc_mono=df_bus_falta['3I0'], ang_tri=df_bus_falta['AN(I+)'],ang_mono=df_bus_falta['AN(IA)']))

      if trafos !=[]:
         for trafo in trafos:
            df=None
            if trafo.is_3D and trafo.bus_1kv==None:
               name = '['+trafo.name+']'
               df = df_posiciones.loc[lambda df: (df['Trafo_3dev'] == True) & ((df['TO_BUS'] == name) & (df['CKT'] == trafo.id)), :]
            elif trafo.is_3D and trafo.bus_1kv !=None:
               raise NotImplementedError()
            else:
               bus_to= trafo.bus_i if trafo.bus_i !=bus_num else trafo.bus_j
               df = df_posiciones.loc[lambda df: (df['Trafo_3dev'] == False) & ((df['TO_BUS'] == bus_to) & (df['CKT'] == trafo.id)), :]

            if df.empty==False:
               df=df.iloc[0]
               list_resultados.append(ElementIcc(element=trafo, icc_tri=df['I+'], icc_mono=df['3I0'],icc_tri_posicion=0, icc_mono_posicion=0, ang_tri=df['AN(I+)'],ang_mono=df['AN(IA)']))

      if branchs !=[]:
         for branch in branchs:
            df=None
            bus_to = branch.from_bus if branch.from_bus != bus_num else branch.to_bus
            df = df_posiciones.loc[lambda df: (df['Trafo_3dev'] == False) & ((df['TO_BUS'] == bus_to) & (df['CKT'] == branch.idn)), :]

            if df.empty==False:
               df = df.iloc[0]
               list_resultados.append(ElementIcc(element=branch, icc_tri=df['I+'], icc_mono=df['3I0'], icc_tri_posicion=0, icc_mono_posicion=0,ang_tri=df['AN(I+)'],ang_mono=df['AN(IA)']))


      return list_resultados
   except Exception as e:
      raise StandardError('Error al obtner los resultados del ascc={} '.format(e.message))