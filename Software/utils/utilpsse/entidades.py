# coding=utf-8
#---------------------------------------------------------------------------------------------------
# Name:        entidades.py
# Purpose:     Aquí se definen todas las clases que representan elementos de la red PSSE (buses, ramas,
#              trafos, etc)
# Author:      VAZROMRI
# Created:     14/01/2018
#---------------------------------------------------------------------------------------------------
import datosree
from initpsspy import *
import  math

_i, _f, _s = psspy.getdefaultint(), psspy.getdefaultreal(), psspy.getdefaultchar()

sum_bar_sep=40000

class ElementList(object):

   def __init__(self, list_element):
      self.list_element=list_element
      self.maqs = []
      self.trafos = []
      self.sws = []
      self.branchs = []
      self.loads=[]

      self.__filter_elements()

   def __filter_elements(self):
      self.trafos = filter(lambda x: isinstance(x, Transformer), self.list_element)
      self.maqs = filter(lambda x: isinstance(x, Machine), self.list_element)
      self.sws = filter(lambda x: isinstance(x, SwitchedShunt), self.list_element)
      self.branchs = filter(lambda x: isinstance(x, Branch), self.list_element)
      self.loads=filter(lambda x: isinstance(x, Load), self.list_element)

   def get_trafos(self):
      """

      :return:listado de trafos
      :rtype: list of Transformer
      """
      return self.trafos

   def check_trafos(self):
      return True if self.trafos else False

   def get_branches(self):
      """
      :return: Listato de branchs
      :rtype: list of Branch
      """
      return self.branchs

   def check_branches(self):
      return True if self.branchs else False

   def get_sws(self):
      return self.sws

   def check_sws(self):
      return True if self.sws else False

   def get_maqs(self):
      return self.maqs

   def check_maqs(self):
      return True if self.maqs else False

   def get_loads(self):
      """

      :return:listado de trafos
      :rtype list or Transformer
      """
      return self.loads

   def check_loads(self):
      return True if self.loads else False

class ElementIcc(object):
   def __init__(self, element, icc_tri,icc_mono,icc_tri_posicion=0,icc_mono_posicion=0,tipo_algoritmo=None,x_r_trifa=0,x_r_mono=0,ang_tri=0,
                ang_mono=0,ang_mono_posicion=0,ang_tri_posicion=0,x_r_neg=0,z_cero=0,z_posit=0,z_neg=0,icc3_85=0,icc1_85=0,icc3_pos_85=0,icc1_pos_85=0,
                icc3_din=0,icc1_din=0,icc3_pos_din=0,icc1_pos_din=0,icc3_term=0,icc1_term=0,icc3_pos_term=0,icc1_pos_term=0):
      self.element=element
      self.icc_tri=icc_tri
      self.ang_tri = ang_tri
      self.icc_mono=icc_mono
      self.ang_mono = ang_mono
      self.icc_tri_posicion=icc_tri_posicion
      self.icc_mono_posicion=icc_mono_posicion
      self.ang_mono_posicion = ang_mono_posicion
      self.ang_tri_posicion = ang_tri_posicion
      self.tipo_algoritmo=tipo_algoritmo
      self.x_r_trifa=x_r_trifa
      self.x_r_mono = x_r_mono
      self.x_r_neg = x_r_neg
      self.z_cero = z_cero
      self.z_posit = z_posit
      self.z_neg = z_neg
      self.icc3_85 = icc3_85
      self.icc1_85 = icc1_85
      self.icc3_pos_85 = icc3_pos_85
      self.icc1_pos_85 = icc1_pos_85
      self.icc3_din = icc3_din
      self.icc1_din = icc1_din
      self.icc3_pos_din = icc3_pos_din
      self.icc1_pos_din = icc1_pos_din
      self.icc3_term = icc3_term
      self.icc1_term = icc1_term
      self.icc3_pos_term = icc3_pos_term
      self.icc1_pos_term = icc1_pos_term

   def check_istrafo(self):
      return isinstance(self.element, Transformer)

   def check_isload(self):
      return isinstance(self.element, Load)

   def check_isbranch(self):
      return isinstance(self.element, Branch)

   def check_isbus(self):
      return isinstance(self.element, Bus)

   def check_ismachine(self):
      return isinstance(self.element, Machine)


class Machine(object):

   def __init__(self, bus_num=_i, bus_area=_i, bus_zone=_i, bus_type=_i, status=_i, idn=_s, name=_s, pgen=_f, qgen=_f, pmax=_f, pmin=_f, qmax=_f, qmin=_f,
                r=_f,x=_f,r_tran_trans=_f,x_tran_trans=_f,gentap_trans=_f,fraction_owner1=_f,fraction_owner2=_f,fraction_owner3=_f,fraction_owner4=_f,wpf=_f,
                mbase=_f,owner_1=_i,owner_2=_i,owner_3=_i,owner_4=_i,wmod=_i,existe=True,init_derived=True,
                czg=_i,rpos=_f,x_subtran_seq=_f,r_neg=_f,x_neg=_f,x_tran_seq=_f,x_sincr_seq=_f,r_zero=_f,x_zero=_f,r_ground=_f,x_ground=_f ):
      """
      Clase que representa una máquina del caso PSSE cargado en memoria.

      El nombre de los atributos coinciden en gran parte con los del caso. Los atributos derivados no originales
      de PSSE se explican en el propio código.

      BUS_NUM será siempre menor de 40000. Siempre se mantiene el nudo sin barras separadas. En caso de que la máquina
      esté en barras separadas el atributo barras_sep será True

      :Example:

         Mirar la función :func:`get_maq_list` en utilpsse.redpsse

      .. note::
         Esta clase está pensada para, mediante la API, recuperar todas las máquinas del caso y a partir de ahí
         crear una lista de objetos de branches. Mirar ejemplo.
      :param init_derived_attrs: indica si se debe ejecutar el metodo init_derived_attrs
      """
      self.bus_num = bus_num
      self.bus_area = bus_area
      self.bus_zone = bus_zone
      self.bus_type = bus_type
      self.status = status
      self.existe=existe
      self.init_derived=init_derived

      self.idn = idn
      self.name = name
      self.pgen = pgen
      self.qgen = qgen
      self.pmax = pmax
      self.pmin = pmin
      self.qmax = qmax
      self.qmin = qmin

      self.czg=czg # code indicating the units in which the zero sequence grounding impedance is specified 1=for per unit 2=for ohms
      self.rpos=rpos #machine positive sequence fault analysis resistance

      self.x_subtran_seq=x_subtran_seq
      self.x_tran_seq=x_tran_seq
      self.x_sincr_seq=x_sincr_seq
      self.r_neg=r_neg
      self.x_neg=x_neg
      self.r_zero=r_zero
      self.x_zero =x_zero
      self.r_ground=r_ground
      self.x_ground=x_ground

      self.mbase = mbase
      self.r=r
      self.x=x
      self.r_tran_trans  = r_tran_trans
      self.x_tran_trans = x_tran_trans
      self.gentap_trans =gentap_trans


      self.owner_1=owner_1
      self.owner_2=owner_2
      self.owner_3=owner_3
      self.owner_4=owner_4
      self.fraction_owner1=fraction_owner1
      self.fraction_owner2 = fraction_owner2
      self.fraction_owner3 = fraction_owner3
      self.fraction_owner4 = fraction_owner4
      self.wmod=wmod #wind machine reactive power limits mode (0 if this machine is not a wind machine)
      self.wpf=wpf #wind machine power factor


      # Atributos derivados de los principales (inicializacion)
      self.tec = None  # <-- Tipo de tecnología (TER, HID, EOL, ...)
      self.tec2 = None  # <-- En caso de ser térmica, cuál (CAR, NUC, etc)
      self.p_reserv_bajar = None  # <-- Siempre va a ser > 0
      self.p_reserv_subir = None  # <-- Siempre va a ser > 0
      self.barras_sep = False  # <-- Indica si la máquina está en barras separadas

      # Atributos que se asignan externamente
      self.uf = None # <-- Unidad fisica de la máquina. Se debe asignar externamente

      # Se definen los atributos derivados de los principales
      if self.init_derived:
         self.init_derived_attrs()

   def init_derived_attrs(self):
      """Asigna los valores derivados de los atributos de PSSE (reserva, barras_sep, tecnologia, ...)
      """
      self.p_reserv_subir = self.pmax - self.pgen
      self.p_reserv_bajar = self.pgen - self.pmin
      if self.bus_num > 40000:
         self.barras_sep = True
         self.bus_num = self.bus_num - 40000
      else :
         self.barras_sep = False

      # Se define la tecnologia 'TER', 'EOL', etc <tec>
      # Las térmicas pueden tener una subtecnologia ('CAR', 'NUC', etc) <tec2>
      for tec, ids in datosree.tecGen.iteritems():
         if (self.idn[-1:] in ids) and len(self.idn) == 2:
            if tec in ['NUC', 'CC2', 'CAR', 'CC']:
               self.tec = 'TER'
               self.tec2 = tec
            else:
               self.tec = tec
               self.tec2 = None
            break
         else:
            self.tec = None
            self.tec2 = None

   def update_attrs(self):
      """Método que actualiza todos los atributos de la máquina leyendo del PSSE
      """
      # Integers
      ierr_i, self.status = psspy.macint(self.bus_num, self.idn, 'STATUS')

      ierr_f, self.pgen =  psspy.macdat(self.bus_num, self.idn, 'P')
      if  (ierr_f == 4 or ierr_f == 3 or ierr_f==0)==False :
         raise StandardError('Error al obtener la P GEN.cod={}'.format(ierr_f))

      ierr_f, self.qgen = psspy.macdat(self.bus_num, self.idn, 'Q')
      if (ierr_f == 4 or ierr_f == 3 or ierr_f==0)==False:
         raise StandardError('Error al obtener la Q GEN.cod={}'.format(ierr_f))

      ierr_f, self.pmax = psspy.macdat(self.bus_num, self.idn, 'PMAX')
      if (ierr_f == 4 or ierr_f == 3 or ierr_f==0)==False:
         raise StandardError('Error al obtener laPMAX.cod={}'.format(ierr_f))

      ierr_f, self.pmin = psspy.macdat(self.bus_num, self.idn, 'PMIN')
      if (ierr_f == 4 or ierr_f == 3 or ierr_f==0)==False:
         raise StandardError('Error al obtener la PMIN.cod={}'.format(ierr_f))

      ierr_f, self.qmax = psspy.macdat(self.bus_num, self.idn, 'QMAX')
      if (ierr_f == 4 or ierr_f == 3 or ierr_f==0)==False:
         raise StandardError('Error al obtener la QMAX.cod={}'.format(ierr_f))

      ierr_f, self.qmin = psspy.macdat(self.bus_num, self.idn, 'QMIN')
      if (ierr_f == 4 or ierr_f == 3 or ierr_f==0)==False:
         raise StandardError('Error al obtener la QMIN.cod={}'.format(ierr_f))

      ierr_f, self.mbase = psspy.macdat(self.bus_num, self.idn, 'MBASE')
      if (ierr_f == 4 or ierr_f == 3 or ierr_f==0)==False:
         raise StandardError('Error al obtener la MBASE. cod={}'.format(ierr_f))

      ierr_f, complex = psspy.macdt2(self.bus_num, self.idn, 'ZSORCE')
      if (ierr_f == 4 or ierr_f == 3 or ierr_f == 0) == False:
         raise StandardError('Error al obtener la XTRAN. cod={}'.format(ierr_f))
      else:
         self.x=complex.imag
         self.r=complex.real

      if self.init_derived:

         self.init_derived_attrs()


   # SETTERS
   def set_pgen(self, pgen):
      """Función que le asigna a la máquina una pgen nueva,

      tanto en la instancia como en el caso psse cargado en memoria

      :param float pgen: potencia generada por la máquina
      :return:
      :rtype: int
      """
      self.pgen = pgen
      ierr = psspy.machine_chng_2(self.bus_num, self.idn, [_i, _i, _i, _i, _i, _i],
                                  [self.pgen, _f, _f, _f, _f, _f, self.mbase, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f])

      return ierr

   def set_status(self, st):
      """Función que le asigna a la máquina un status nuevo,

      tanto en la instancia como en el caso psse cargado en memoria

      :param int st: status de la máquina nuevo (0, 1)
      :return:
      :rtype: int
      """
      self.status = st
      ierr = psspy.machine_chng_2(self.bus_num, self.idn, [self.status, _i, _i, _i, _i, _i],
                                  [_f, _f, _f, _f, _f, _f, self.mbase, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f])

      return ierr


   def create(self, change_bus_type=True):
      """
      Actualiza o crea una macquina en el caso
      :return:
      """
      existe_planta=self.__check_plant()

      if not existe_planta:
         self.create_plant()

      bus=Bus(bus_num=self.bus_num)
      if (bus.get_bus_type() != 2 and bus.get_bus_type() != 4) and change_bus_type:
         bus.set_bus_type(2)

      intgar=[self.status,self.owner_1,self.owner_2,self.owner_3,self.owner_4,self.wmod]
      realar=[self.pgen, self.qgen,self.qmax,self.qmin,self.pmax,self.pmin,self.mbase,self.r,self.x,self.r_tran_trans,self.x_tran_trans,self.gentap_trans,
              self.fraction_owner1,self.fraction_owner2,self.fraction_owner3,self.fraction_owner4,self.wpf]
      ierr = psspy.machine_data_2(self.bus_num, self.idn, intgar, realar)

      if ierr !=0:
         raise StandardError('Error alo creal la maquina. cod={}'.format(ierr))

   def create_plant(self):
      """
      Crea o modifica una planta asociada al bus de la maquina
      :return:
      """
      irge=_i #remote bus number (0 to control voltage at bus IBUS)
      v_sched=_f ##scheduled voltage magnitude

      rmpct=_f #percent of contributed reactive power

      intgar=[irge]
      realar=[v_sched,rmpct]
      ierr = psspy.plant_data(self.bus_num, intgar, realar)

      if ierr !=0:
         raise StandardError('Error al crea la planta. Cod_Error={}'.format(ierr))

   def __check_plant(self):

      existe=True

      ierr = psspy.moveplnt(self.bus_num, self.bus_num)

      if ierr==2:
         existe=False

      return existe

   def delete(self):
      ierr=psspy.purgmac(self.bus_num, self.idn)

      if ierr !=0:
         raise StandardError('Error al borrar las machine: cod={}. bus_num={}; ckt= {}'.format(ierr, self.bus_num, self.idn))

   def check_existe(self):
      ierr, ival = psspy.macstt(self.bus_num, self.idn)

      if ierr !=0:
         self.existe=False
      else:
         self.existe = True
      return self.existe

   def check_and_reparar(self):
      """
      Chequea si los vaolores del generador son coherentes y en caso de que pueda los repara
      :return:
      """
      try:
         reparar=False
         acoplado=False
         traceback=[]
         self.update_attrs()

         type_bus=Bus(bus_num=self.bus_num).get_bus_type()

         pp=max(self.pmax*self.pmax,self.pmin*self.pmin)
         qq = max(self.qmax *self.qmax, self.qmin *self.qmin)
         sAp = math.sqrt(pp + qq)

         if type_bus!=4:
            acoplado=True

         if self.pmax<=0.0 and self.mbase<=0.0:
            traceback.append('El generador presenta datos incoherentes y no es reperable.  Pmax <= 0 y MBase <= 0')
         elif acoplado and abs(self.pgen)>1.2*self.pmax:
            traceback.append('El generador presenta datos incoherentes y no es reperable. Pgen > 1.2*Pmax.')
         elif self.pmax <=0.0:
            reparar=True
         elif self.mbase<=0.0:
            reparar=True
         elif self.pmax > self.mbase:
            reparar = True
         elif self.pmin>self.pmax:
            reparar = True
         elif self.qmax>0.75*self.mbase:
            reparar = True
         elif self.qmin< -0.5*self.mbase:
            reparar = True
         elif self.qmax<self.qmin:
            reparar = True
         elif sAp >1.01*self.mbase:
            reparar=True

         if reparar:
            if self.pmax<=0.0:
               self.pmax=0.8*self.mbase
            if self.mbase<=0.0:
               self.mbase=1.25*self.pmax
            if self.pmax>self.mbase:
               self.mbase=1.25*self.pmax
            self.pmin=0.0
            self.qmax=self.mbase
            self.qmin=-0.2*self.mbase

            self.create()
      except Exception as e:
         raise StandardError('Error al reparar el generador: {}'.format(e.message))

      return traceback

   def  load_seq_homo(self):

      intgar=[self.czg]
      realar=[self.rpos, self.x_subtran_seq, self.r_neg, self.x_neg, self.r_zero, self.x_zero,self.x_tran_seq,self.x_sincr_seq, self.r_ground,self.x_ground]
      ierr = psspy.seq_machine_data_3(self.bus_num, self.idn, intgar, realar)

      if ierr !=0:
         raise StandardError('Error al cargar la secuancia homo en la maquina: cod={}'.format(ierr))



class PSSElement(object):

   def __init__(self, bus_num=None, name=None):
      """ Inicializa una nueva instancia 'PSSElement'
      """
      self.bus_num = bus_num
      self.name = name


# noinspection PyUnresolvedReferences
class Transformer(object):

   def __init__(self,bus_i,bus_j=None,idn=None,bus_k=None,id_2 = None,id_3 = None,is_3D=False, name=_s,status=_i, vgrp=_s,r1_2=_f,x1_2=_f,r2_3=_f,x2_3=_f,r3_1=_f,x3_1=_f,
                sbs1_2=_f,sbs2_3=_f,sbs3_1=_f,mag1=_f,mag2=_f,owner_1=_i,owner_2=_i,owner_3=_i,owner_4=_i,f_owner1=_f,f_owner2=_f,f_owner3=_f,f_owner4=_f,
                angle1=_f,angle2=_f,angle3=_f,check_trafo=True,cc=_i,met_bus=_i, windv1=_f, windv2=_f, windv3=_f, windv1_2=_f,r_zero_1=_f,
                x_zero_1=_f,r_zero_2=_f, x_zero_2=_f, r_zero_3=_f, x_zero_3=_f,r_ground_1=_f, x_ground_1=_f,r_ground_2=_f, x_ground_2=_f, r_ground_3=_f, x_ground_3=_f,
                bus_i_name=_s,bus_j_name=_s, bus_k_name=_s):
      """
      Para modelar un trafosformador en PSSE.

      Los atributos r y x hasn sido sustituidos por r1_2 y x1_2
      :param bus_i: bus de origen del trafo
      :param bus_j: bus del primer remoto del trafo
      :param idn: numero de cicuito del primario o identifucador del trafo. Es igual al numero de circutio del branch asociado
      :param args:
      :param kw_args:

      En caso de no incializar la clase con los atributos bus_j e idn. El metodo check_trafo obtendra el porimer trafo asociado al bus_i.
      Si estos parametros y los restantes son rellenados, validara que los parametros del trafo son correctos, modelando el trafo correctamente.
      Es decir, si el bus_j corresponde con un nudo de 1kv los atributos seran modificados.

      """
      self.status = status
      # status=0. Si el trafo esta completamnete desconectado
      # status=1. Si el trafo esta completamnete conectado
      # status=2.Si esta desconectado el 2dev. Solo para tafos de 3dev
      # status=3. Si esta desconectado el 3dev. Solo para tafos de 3dev
      # status=4. Si esta desconectado el 1dev. Solo para tafos de 3dev


      self.is_3D = is_3D
      self.name=name
      self.existe = False

      self.bus_1kv = None #bus del nudo de 1kv que modela el trafo de tres devanados

      self.bus_i = bus_i
      self.bus_i_name = bus_i_name

      self.bus_j = bus_j
      self.bus_j_name = bus_j_name

      self.bus_k = bus_k #numero de bus del terciario. Solo en caso de que sea un trafo de tres devanados
      self.bus_k_name = bus_k_name #Para un trafo de 3 dev

      self.id = str(idn).strip() if idn !=None  else idn
      self.id_2 = str(id_2).strip() if id_2 !=None  else id_2 #numero de circuto del secundarios de un trafo de tres devanado modelado con un nudo de 1kv: bus_1kv-->bus_j
      self.id_3 = str(id_3).strip() if id_3 !=None  else id_3 # numero de circuto del terciario de un trafo de tres devanado modelado con un nudo de 1kv: bus_1kv-->bus_k

      self.met_bus = met_bus #non-metered end bus number
      self.cw=_i #winding data I/O code
      self.cz=_i #impedance data I/O code
      self.cm=_i #magnetizing admittance data I/O code
      self.cc=cc #connection code

      self.wn1bus=_i #winding one side bus number
      self.wn2bus=_i #winding two side bus number
      self.wn3bus=_i #winding three side bus number


      self.owner_1 = owner_1
      self.owner_2 = owner_2
      self.owner_3 = owner_3
      self.owner_4 = owner_4

      self.f_owner1 = f_owner1
      self.f_owner2 = f_owner2
      self.f_owner3 = f_owner3
      self.f_owner4 = f_owner4

      self.r = _f
      self.x = _f
      self.b = _f

      self.r1_2=r1_2
      self.x1_2=x1_2
      self.r2_3=r2_3
      self.x2_3=x2_3
      self.r3_1=r3_1
      self.x3_1=x3_1

      self.r_zero_1=r_zero_1 #zero sequence leakage resistance connected to the winding 1 bus. 3DEV= Winding 1, or winding 1 bus to winding 2 bus, leakage resistance
      self.x_zero_1 = x_zero_1 # zero sequence leakage reactance connected to the winding 1 bus. 3DEV= Winding 1, or winding 1 bus to winding 2 bus, leakage reactance
      self.r_zero_2 = r_zero_2 # zero sequence leakage resistance connected to the winding 2 bus.3DEV= Winding 2, or winding 2 bus to winding 3 bus, leakage resistance
      self.x_zero_2 = x_zero_2 # zero sequence leakage reactance connected to the winding 2 bus. 3DEV=Winding 2, or winding 2 bus to winding 3 bus, leakage reactance
      self.r_zero_3 = r_zero_3 # winding 3, or winding 3 bus to winding 1 bus, leakage resistance
      self.x_zero_3 = x_zero_3 # winding 3, or winding 3 bus to winding1 bus, leakage reactance

      self.r_ground_1 = r_ground_1 #grounding resistance at the winding 1 bus for an impedance grounded transformer
      self.x_ground_1 = x_ground_1 # grounding reactance at the winding 1 bus for an impedance grounded transformer
      self.r_ground_2 = r_ground_2  # grounding resistance at the winding 2 bus for an impedance grounded transformer
      self.x_ground_2 = x_ground_2  #grounding reactance at the winding 2 bus for an impedance grounded transformer
      self.r_ground_3 = r_ground_3 #grounding reactance on winding 3 for an impedance grounded transformer
      self.x_ground_3 = x_ground_3 #grounding resistance on winding 3 for an impedance grounded transformer

      self.rn=_f #common neutral grounding resistance
      self.xn = _f #common neutral grounding reactance

      self.cz0=_i #non-grounding impedance data I/O code
      self.czg=_i #grounding impedance data I/O code



      self.sbs1_2=sbs1_2 #winding BASE one to two base MVA
      self.sbs2_3=sbs2_3 #winding BASE two to three base MVA
      self.sbs3_1=sbs3_1 #winding BASE three to one base MVA

      self.mag1=mag1 #magnetizing conductance or no-load losses
      self.mag2 = mag2 # magnetizing susceptance or exciting current

      self.vmstar=_f #star bus voltage magnitude
      self.tar=_f #star bus voltage angle
      self.vgrp = vgrp  # vector group name

      self.ntp1=_i #number of tap positions for winding1
      self.ntp2 = _i  # number of tap positions for winding2
      self.ntp3 = _i  # number of tap positions for winding3

      self.tab1 = _i  # impedance correction table number for winding1
      self.tab2 = _i  # impedance correction table number for winding2
      self.tab3 = _i  # impedance correction table number for winding3

      self.cont1=_i # controlled bus number for winding1
      self.cont2 = _i  # controlled bus number for winding3
      self.cont3 = _i  # controlled bus number for winding3

      self.sicod1=_i # negative for controlled bus on winding bus side for winding1
      self.sicod2 = _i  # negative for controlled bus on winding bus side for winding2
      self.sicod3 = _i  # negative for controlled bus on winding bus side for winding3

      self.cod1 = _i  # adjustment control mode flag for winding1
      self.cod2 = _i  # adjustment control mode flag for winding2
      self.cod3 = _i  # adjustment control mode flag for winding3

      self.windv1=windv1 # winding ratio or voltage for winding1
      self.windv2 = windv2  # winding ratio or voltage for winding2
      self.windv3 = windv3  # winding ratio or voltage for winding3

      self.windv1_2 = windv1_2  # winding ratio 2 or voltage for winding1. Solo para trafos de dos dev

      self.nomv1=_f # winding nominal voltage (KV) for winding1
      self.nomv2 = _f  # winding nominal voltage (KV) for winding2
      self.nomv3 = _f  # winding nominal voltage for (KV) winding3

      self.angle1=angle1 #winding phase shift angle (deg) for winding1
      self.angle2 = angle2  # winding phase shift angle (deg) for winding2
      self.angle3 = angle3  # winding phase shift angle (deg) for winding3


      self.rma1=_f #winding ratio/angle high limit for winding1
      self.rma2 = _f  # winding ratio/angle high limit for winding2
      self.rma3 = _f  # winding ratio/angle high limit for winding3

      self.rmi1 = _f  # winding ratio/angle low limit for winding1
      self.rmi2 = _f  # winding ratio/angle low limit for winding2
      self.rmi3 = _f  # winding ratio/angle low limit for winding3

      self.vma1=_f #winding voltage or flow upper limit for  winding1
      self.vma2 = _f  # winding voltage or flow upper limit for  winding1
      self.vma3 = _f  # winding voltage or flow upper limit for  winding1

      self.vmi1 = _f  # winding voltage or flow lower limit for  winding1
      self.vmi2 = _f  # winding voltage or flow lower limit for  winding2
      self.vmi3 = _f  # winding voltage or flow lower limit for  winding3

      self.cr1=_f # winding load drop compensating resistance  for  winding1
      self.cr2 = _f  # winding load drop compensating resistance  for  winding2
      self.cr3 = _f  # winding load drop compensating resistance  for  winding3

      self.cx1 = _f  # winding load drop compensating reactance  for  winding1
      self.cx2 = _f  # winding load drop compensating reactance  for  winding2
      self.cx3 = _f  # winding load drop compensating reactance  for  winding3

      self.cnxa1=_f #winding connection angle for  winding1
      self.cnxa2 = _f  # winding connection angle for  winding2
      self.cnxa3 = _f  # winding connection angle for  winding3

      self.rateA = _f  #winding rating set A line rating for winding1
      self.rateB = _f  #winding rating set B line rating for winding1
      self.rateC = _f  #winding rating set C line rating for winding1

      self.rateA2 = _f #winding rating set A line rating for winding2
      self.rateB2 = _f
      self.rateC2 = _f

      self.rateA3 = _f #winding rating set A line rating for winding3
      self.rateB3 = _f
      self.rateC3 = _f

      self.g_i = _f
      self.b_i = _f
      self.g_j = _f
      self.b_j = _f
      self.g_k = _f
      self.b_k = _f

      self.len = _f

      super(Transformer, self).__init__()

      if check_trafo:
         self.check_trafo()
         _ = self.check_existe()

   def check_existe(self):

      if self.is_3D:
         if self.bus_1kv ==None:
            self.existe = True
            ie, self.status = psspy.tr3int(self.bus_i, self.bus_j, self.bus_k, self.id, 'STATUS')
            if ie > 0:  # La linea AC no existe
               self.existe = False
         else:
            # TODO Aquí habría que separar el status de cada devanado. Queda pendiente
            self.existe = True
            ie, ival = psspy.xfrint(self.bus_i, self.bus_i, self.id, 'NTPOSN')
            if ie > 0:  # La linea AC no existe
               self.existe = False
            else:
               ie, ival = psspy.xfrint(self.bus_i, self.bus_i, self.id, 'NTPOSN')
               if ie > 0:  # La linea AC no existe
                  ie, ival = psspy.xfrint(self.bus_i, self.bus_i, self.id, 'NTPOSN')
                  if ie > 0:
                     self.existe = False
               else:
                  ie, ival = psspy.xfrint(self.bus_i, self.bus_i, self.id, 'NTPOSN')
                  if ie > 0:  # La linea AC no existe
                     ie, ival = psspy.xfrint(self.bus_i, self.bus_i, self.id, 'NTPOSN')
                     if ie > 0:
                        self.existe = False
      else:
         self.existe = True

         ie, ival = psspy.xfrint(self.bus_i, self.bus_i, self.id, 'NTPOSN')

         if ie > 0:  # La linea AC no existe
            self.existe = False
      return self.existe



   def set_status(self, value):
      if self.is_3D:
         if self.bus_1kv:
            ierr, _ = psspy.two_winding_chng_4(self.bus_i, self.bus_1kv, self.id, [value, _i, _i, _i, _i, _i, _i, _i, _i,
                                                _i, _i, _i, _i, _i, _i], [_f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f,
                                                _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f], [_s, _s])
            if ierr > 0: raise StandardError(u'No se ha podido cambiar el status del trafo (3dev/1kv) ierr: <{}>, bus_i: <{}>, '
                                          u'bus_j: <{}>, bus_k:<{}>'.format(ierr, self.bus_i, self.bus_j, self.bus_k))

            ierr, _ = psspy.two_winding_chng_4(self.bus_j, self.bus_1kv, self.id_2, [value, _i, _i, _i, _i, _i, _i, _i, _i,
                                                _i, _i, _i, _i, _i, _i], [_f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f,
                                                _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f], [_s, _s])
            if ierr > 0: raise StandardError(u'No se ha podido cambiar el status del trafo (3dev/1kv) ierr: <{}>, bus_i: <{}>, '
                                          u'bus_j: <{}>, bus_k:<{}>'.format(ierr, self.bus_i, self.bus_j, self.bus_k))
            ierr, _ = psspy.two_winding_chng_4(self.bus_k, self.bus_1kv, self.id_3, [value, _i, _i, _i, _i, _i, _i, _i, _i,
                                                _i, _i, _i, _i, _i, _i], [_f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f,
                                                _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f], [_s, _s])
            if ierr > 0: raise StandardError(u'No se ha podido cambiar el status del trafo (3dev/1kv) ierr: <{}>, bus_i: <{}>, '
                                          u'bus_j: <{}>, bus_k:<{}>'.format(ierr, self.bus_i, self.bus_j, self.bus_k))
         else:
            # TODO
            pass
      else:
         ierr, _ = psspy.two_winding_chng_4(self.bus_i, self.bus_j, self.id, [value, _i, _i, _i, _i, _i, _i, _i, _i,
                                                                              _i, _i, _i, _i, _i, _i],
                                            [_f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f,
                                             _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f], [_s, _s])
         if ierr > 0: raise StandardError(u'No se ha podido cambiar el status del trafo (2dev) ierr: <{}>, bus_i: <{}>, '
                                          u'bus_j: <{}>, bus_k:<{}>'.format(ierr, self.bus_i, self.bus_j, self.bus_k))
      self.status = value

      return 'dasdasd'

   def check_if_gener(self):
      return chk_is_gen_trafo(self.bus_i, self.bus_j)

   def check_trafo(self):

      list_brach=self.__get_brach_to_bus(self.bus_i)

      if list_brach !=[]:
         numtrafos=filter(lambda x: x['trafo'],list_brach).__len__()
         if numtrafos >=0:
            if self.bus_j !=None  and self.bus_k==None and self.id != None and self.id_2 == None and self.id_3 == None and self.bus_1kv == None:
               #Un trafo que apriori es de dos devanados
               trafo_3d=filter(lambda x: x['trafo_3d'], list_brach)
               trafos = filter(lambda x: x['trafo'] and x['bus_j'] == self.bus_j and x['ckt'] == str(self.id),
                               list_brach)
               if trafos.__len__()>0:
                  self.__set_trafo(trafos[0])
               else:
                  raise Exception(' No hay trafos con los datos especificados: bus_i:{}; bus_j:{}, id:{}'.format(self.bus_i, self.bus_j, self.id))

            elif self.bus_j != None  and self.bus_k == None and self.id_2 == None and self.id == None and self.id_3 == None and self.bus_1kv == None:
               # Un trafo que apriori es de dos devanados, pero que no se ha especificado el id

               trafos = filter(lambda x: x['trafo'] and (x['bus_j'] == self.bus_j or x['bus_k']==self.bus_j),list_brach)#Compruebo si alguna branch que es trafo tiene un el nudo k o j igual al atributo:bus_j

               if trafos.__len__() > 0:
                  #Existe algun con secundario o terciario igual al bus_j
                  self.__set_trafo(trafos[0])
               else:
                  #No existe un trafo de dos devanados o tres devanados (bus_i no conectado a bus_j. las branch del nudo i no estan conectadas al nudo j).
                  # Puede que sea un trafo de tres devanados modelado con 1kv
                  if filter(lambda x: x['trafo'] and x['trafo_3d'],list_brach).__len__()>0: #Compruebo si existe un trafo de tres devanados, asociado al bus_i
                     branchs=self.__get_brach_to_bus(self.bus_j) #Obtengo las branchs asociadas al bus_j
                     if branchs.__len__()>0:
                        branchs = filter(lambda x: x['trafo'] and x['trafo_3d'],branchs)#Obtengo los trafos de tres devanados asociados al bus_j. Puede que tenga un bus_1kv asociado al bus_i
                        if branchs.__len__() > 0:
                           self.__set_trafo(branchs[0])#En caso de que no este ligado con el bus_i retorna un error
                        else:
                           raise Exception('No hay trafos con los datos especificados: bus_i:{}; bus_j:{}'.format(self.bus_i,self.bus_j))
                     else:
                        raise Exception(' No hay trafos con los datos especificados: bus_i:{}; bus_j:{}'.format(self.bus_i,self.bus_j))

            elif self.bus_j != None and self.bus_k != None and self.id_2 == None and self.id == None and self.id_3 == None and self.bus_1kv == None:
               # Un trafo que apriori es de tres devanados, pero que no se ha especificado el id

               trafos = filter(lambda x: x['trafo'] and (x['bus_j'] == self.bus_j or x['bus_k'] == self.bus_j) and (x['bus_j'] == self.bus_k or x['bus_k'] == self.bus_k), list_brach)
               if trafos.__len__() > 0:
                  self.__set_trafo(trafos[0])
               else:
                  # No existe un trafo de tres devanados sin un nudo de 1kv. bus_i no conectado a bus_j. Puede que sea un trafo de tres devanados modelado con 1kv
                  if filter(lambda x: x['trafo'] and x['trafo_3d'],
                            list_brach).__len__() > 0:  # Compruebo si existe un trafo de tres devanados, asociado al bus_i
                     branchs = self.__get_brach_to_bus(self.bus_j)  # Obtengo los bus asociados al bus_j
                     if branchs.__len__() > 0:
                        branchs = filter(lambda x: x['trafo'] and x['trafo_3d'],
                                         branchs)  # Obtengo los trafos de tres devanados asociados al bus_j puede que tenga un bus_1kv asociado al bus_i
                        if branchs.__len__() > 0:
                           self.__set_trafo(branchs[0])
                        else:
                           raise Exception(
                              'No hay trafos con los datos especificados: bus_i:{}; bus_j:{}'.format(self.bus_i,
                                                                                                     self.bus_j))
                     else:
                        raise Exception(
                           ' No hay trafos con los datos especificados: bus_i:{}; bus_j:{}'.format(self.bus_i,
                                                                                                   self.bus_j))

            elif self.bus_j ==None and self.id==None:
               #Solo se ha introducido el bus_i. Retorno el primer trafo quye encuantro asociado a dicho bus
               trafo = filter(lambda x: x['trafo'], list_brach)
               if trafo.__len__() > 0:
                  self.__set_trafo(trafo[0])
               else:
                  raise Exception(
                     ' No hay trafos con los datos especificados: bus_i:{}'.format(self.bus_i))

            elif self.bus_j ==None and self.id!=None:
               #Retorno el primer trafo con el mismo ctk==id
               self.__set_trafo(filter(lambda x: x['trafo'],list_brach)[0])

            elif self.bus_j != None and self.bus_k != None and self.id_2 != None and self.id != None and self.id_3 != None:
               #Trafo de tres devanados en el cual se han especificado los id de cada circuito

               trafos = filter(lambda x: x['trafo'] and (x['bus_j'] == self.bus_j or x['bus_k'] == self.bus_j) and (x['bus_j'] == self.bus_k or x['bus_k'] == self.bus_k)
                                         and (x['ckt']==self.id or x['ckt']==self.id_2 or x['ckt'] == self.id_3), list_brach)
               if trafos.__len__() > 0:
                  self.__set_trafo(trafos[0])
               else:
                  # No existe un trafo de tres devanados sin un nudo de 1kv. bus_i no conectado a bus_j. Puede que sea un trafo de tres devanados modelado con 1kv
                  pass

         #Para el resto de casos no hago nada , me quedo con los parametros que se ha introduccido

         else:
            raise Exception(' No hay trafos asociados al bus {}'.format(self.bus_i))
      else:
         raise Exception (' No se ha podido obtener los brach asociados al bus {}'.format(self.bus_i))

   def __get_brach_to_bus(self, bus_i):
            """
            Obtiene las branch asociados a un bus (lienas mas trafos)
            :param bus_i: bus donde buscar
            :return: listado de datos
            :rtype: list of dict
            """
            list_brach = []
            datos = {'bus_i': None, 'bus_j': None, 'bus_k': None, 'bus_1kv': None, 'ckt': None, 'trafo': None,
                     'trafo_3d': None}

            ierr = psspy.inibrx(bus_i, 2)
            if ierr == 0:
               ie, jBus, kBus, ckt = psspy.nxtbrn3(bus_i)

               while ie == 0:

                  datos = {'bus_i': None, 'bus_j': None, 'bus_k': None, 'bus_1kv': None, 'ckt': None, 'trafo': None,
                           'trafo_3d': None}
                  datos['bus_i'] = bus_i
                  datos['ckt'] = ckt.strip()

                  ie, bi = psspy.busdat(bus_i, 'BASE')
                  ie, bj = psspy.busdat(jBus, 'BASE')
                  ie, bk = psspy.busdat(kBus, 'BASE')
                  if (kBus != 0) and (bi != bk):
                     datos['trafo'] = True
                     datos['trafo_3d'] = True
                     datos['bus_j'] = jBus
                     datos['bus_k'] = kBus
                  elif (kBus == 0) and (bj == 1.0):
                     datos['trafo'] = True
                     datos['trafo_3d'] = True
                     datos['bus_j'] = jBus
                     datos['bus_1kv'] = jBus
                  elif (kBus == 0) and (bi == 1.0):
                     datos['trafo'] = True
                     datos['trafo_3d'] = True
                     datos['bus_j'] = jBus
                     datos['bus_1kv'] = bus_i
                  elif (bj != bi):
                     datos['trafo'] = True
                     datos['trafo_3d'] = False
                     datos['bus_j'] = jBus
                  else:
                     datos['trafo'] = False
                     datos['trafo_3d'] = False
                     datos['bus_j'] = jBus

                  list_brach.append(datos)
                  ie, jBus, kBus, ckt = psspy.nxtbrn3(bus_i)
            else:
               raise Exception('No existe el bus especificado: {}. Cod error: {}'.format(bus_i, ierr))

            return list_brach

   def __set_trafo(self,datos):

      if datos['trafo_3d'] and datos['bus_1kv'] == None:
         # Trafo de tres devanados
         self.is_3D = True
         self.bus_k = datos['bus_k']
      elif datos['trafo_3d']:
         # trafo de trwss devanados modelado con un nudo de 1kv
         self.is_3D = True
         self.bus_1kv = datos['bus_1kv']
         self.id=datos['ckt']
         branchs=self.__get_brach_to_bus(self.bus_1kv)

         branch_1=filter(lambda x: x['bus_j'] != self.bus_i, branchs)
         branch_2=filter(lambda x: x['bus_j'] != self.bus_j, branchs)


         if branch_1.__len__()>0 or branch_2.__len__()>0 :
            # Unicamente va a dar dos branchs. fILTRO PARA QUE NO ME DE LA BRANCH DEL NUDO DEL DEV PRIMARIO
            branchs=branch_1 if  branch_1.__len__()>0 else branch_2

            if branchs.__len__()>=2:
               if self.bus_j==self.bus_1kv: #Para un trafo incializa con el devanado secundario con el bus de 1kv
                  self.bus_j=branchs[0]['bus_j']
                  self.id_2 = branchs[0]['ckt']
                  self.bus_k = branchs[1]['bus_j']
                  self.id_3 = branchs[1]['ckt']
               else: #Para un trafo incializa con el devanado secundario con el bus correcto
                  for bra in branchs:
                     if bra['bus_j']==self.bus_j: #Set id del dev secundario
                        self.id_2=bra['ckt']
                     else: #Set dev terciario
                        self.bus_k = bra['bus_j']
                        self.id_3 = bra['ckt']

            else:
               raise Exception ('El bus de un 1kv: {} no tiene dos bus asociados'.format(self.bus_1kv))
         else:
            raise  Exception ('No existe un bus de un 1kv asociado al bus_i {}'.format(self.bus_i))


      else:
         # trafo de dos devanados
         if self.bus_j==None and self.id==None:
            self.bus_j=datos['bus_j']
            self.id = datos['ctk']
         self.is_3D = False

   def create(self,bus_1kv=False,change_bus_type=True):
      """
      Crea o modifica un transformador
      :param bus_1kv: pAra indicar que el transformador debe ser creado con tres dev con nudo de 1kv
      :return:
      """
      if not  bus_1kv:
         if self.is_3D:

            #Crea el trafode 3 dev

            # INTGAR(1) O1, first owner number (owner of bus IBUS by default)
            # INTGAR(2) O2, second owner number (0 by default)
            # INTGAR(3) O3, third owner number (0 by default)
            # INTGAR(4) O4, fourth owner number (0 by default)
            # INTGAR(5) CW, winding data I/O code (1 by default)
            # INTGAR(6) CZ, impedance data I/O code (1 by default)
            # INTGAR(7) CM, magnetizing admittance data I/O code (1 by default)
            # INTGAR(8) STAT, branch status (1 by default)
            # INTGAR(9) NMETBS, non-metered end bus number (IBUS, JBUS or KBUS) (JBUS by default)
            # INTGAR(10) WN1BUS, winding one side bus number (IBUS, JBUS or KBUS) (IBUS by default)
            # INTGAR(11) WN2BUS, winding two side bus number (IBUS, JBUS or KBUS) (JBUS by default)
            # INTGAR(12) WN3BUS, winding three side bus number (IBUS, JBUS or KBUS) (KBUS by default)

            # REALARI(1) R1-2, nominal bus one to two transformer resistance (0.0 by default)
            # REALARI(2) X1-2, nominal bus one to two transformer reactance (0.0002 by default)
            # REALARI(3) R2-3, nominal bus two to three transformer resistance (0.0 by default)
            # REALARI(4) X2-3, nominal bus two to three transformer reactance (0.0002 by default)
            # REALARI(5) R3-1, nominal bus three to one transformer resistance (0.0 by default)
            # REALARI(6) X3-1, nominal bus three to one transformer reactance (0.0002 by default)
            # REALARI(7) SBS1-2, winding one to two base MVA (SBASE by default)
            # REALARI(8) SBS2-3, winding two to three base MVA(SBASE by default)
            # REALARI(9) SBS3-1, winding three to one base MVA(SBASE by default)
            # REALARI(10) MAG1, magnetizing conductance or no-loadlosses (0.0 by default)
            # REALARI(11) MAG2, magnetizing susceptance or excitingcurrent (0.0 by default)
            # REALARI(12) F1, first owner fraction (1.0 by default)
            # REALARI(13) F2, second owner fraction (0.0 by default)
            # REALARI(14) F3, third owner fraction (0.0 by default)
            # REALARI(15) F4, fourth owner fraction (0.0 by default)
            # REALARI(16) VMSTAR, star bus voltage magnitude (1.0 by default)
            # REALARI(17) TAR, star bus voltage angle (0.0 by default)

            # CHARAR(1) NAME, transformer name (blank by default)
            # CHARAR(2) VGRP, vector group name (blank by default)

            if change_bus_type:
               type_bus=Bus(bus_num=self.bus_i).get_bus_type()
               if type_bus ==4 and (self.status==4 or self.status==0)==False:
                  #Si conecto un trafo con con el 1 dev cnectado a un nudo desconectado
                  if get_existe_machine(self.bus_i):
                     type=2
                  else:
                     type=1
                  Bus(bus_num=self.bus_i).set_bus_type(type)

               type_bus = Bus(bus_num=self.bus_j).get_bus_type()
               if type_bus ==4 and (self.status==2 or self.status==0)==False:
                  if get_existe_machine(self.bus_j):
                     type=2
                  else:
                     type=1
                  Bus(bus_num=self.bus_j).set_bus_type(type)

               type_bus = Bus(bus_num=self.bus_k).get_bus_type()

               if type_bus ==4 and (self.status==3 or self.status==0)==False:
                  if get_existe_machine(self.bus_k):
                     type=2
                  else:
                     type=1
                  Bus(bus_num=self.bus_k).set_bus_type(type)

            intgar= [self.owner_1,self.owner_2,self.owner_3,self.owner_4,self.cw,self.cz,self.cm,self.status,self.met_bus,self.wn1bus,self.wn2bus,self.wn3bus]
            realari=[self.r1_2, self.x1_2, self.r2_3, self.x2_3, self.r3_1, self.x3_1,self.sbs1_2, self.sbs2_3, self.sbs3_1, self.mag1, self.mag2, self.f_owner1,
                     self.f_owner2, self.f_owner3, self.f_owner4,self.vmstar, self.tar]

            charar=[self.name,self.vgrp]

            ierr, realaro = psspy.three_wnd_imped_data_3(self.bus_i,self.bus_j,self.bus_k,self.id,intgar,realari,charar)

            # REALARO(1) actual bus one to two resistance (returned)
            # REALARO(2) actual bus one to two reactance (returned)
            # REALARO(3) actual bus two to three resistance (returned)
            # REALARO(4) actual bus two to three reactance (returned)
            # REALARO(5) actual bus three to one resistance (returned)
            # REALARO(6) actual bus three to one reactance (returned)

            if ierr !=0:
               raise StandardError('Error al crear el three_wnd_imped. Cod={}. bus_i={}; bus_j={};bus_k={}; ckt={}'.format(ierr, self.bus_i,self.bus_j,self.bus_k,self.id))

            #Modifica los valores de 1 devanado
            # INTGAR(1) NTPi, number of tap positions (33 by default)
            # INTGAR(2) TABi, impedance correction table number (0 by default)
            # INTGAR(3) CONTi, controlled bus number (0 by default)
            # INTGAR(4) SICODi, negative for controlled bus on winding bus side (1 by default)
            # INTGAR(5) CODi, adjustment control mode flag (-3through +3, -5 or 5) (0 by default)

            # REALARI(1) WINDVi, winding ratio or voltage
            # (1.0 by default if CW of this transformer is 1 or 3; base voltage of the winding bus by default if CW is 2)
            # REALARI(2) NOMVi, winding nominal voltage (0.0 by default)
            # REALARI(3) i, winding phase shift angle (0.0 by default)
            # REALARI(4) RATAi, winding rating set A line rating (0.0 by default)
            # REALARI(5) RATBi, winding rating set B line rating (0.0 by default)
            # REALARI(6) RATCi, winding rating set C line rating (0.0 by default)
            # REALARI(7) RMAi, winding ratio/angle high limit (1.1 by default)
            # REALARI(8) RMIi, winding ratio/angle low limit (0.9 by default)
            # REALARI(9) VMAi, winding voltage or flow upper limit (1.1 by default)
            # REALARI(10) VMIi, winding voltage or flow lower limit (0.9 by default)
            # REALARI(11) CRi, winding load drop compensating resistance (0.0 by default)
            # REALARI(12) CXi, winding load drop compensating reactance (0.0 by default)
            # REALARI(13) CNXAi, winding connection angle (0.0 by default).Used with adjustment control mode 5
            # (unsymmetric phase shift control of active power) implemented in PSSE version 32.1)


            intgar=[self.ntp1,self.tab1, self.cont1, self.sicod1, self.cod1]
            realari=[self.windv1, self.nomv1, self.angle1,self.rateA, self.rateB, self.rateC, self.rma1, self.rmi1,
                     self.vma1, self.vmi1, self.cr1, self.cx1, self.cnxa1]
            ierr, realaro=psspy.three_wnd_winding_data_3(self.bus_i,self.bus_j,self.bus_k,self.id, 1,intgar ,realari)

            if ierr !=0:
               raise StandardError('Error al modficar los datos de 1 dev. Cod={}'.format(ierr))

            # Modifica los valores de segundo devanado
            intgar = [self.ntp2, self.tab2, self.cont2, self.sicod2, self.cod2]
            realari = [self.windv2, self.nomv2, self.angle2, self.rateA2, self.rateB2, self.rateC2, self.rma2, self.rmi2,
                       self.vma2, self.vmi2, self.cr2, self.cx2, self.cnxa2]
            ierr, realaro = psspy.three_wnd_winding_data_3(self.bus_i, self.bus_j, self.bus_k, self.id, 2, intgar,
                                                           realari)

            if ierr != 0:
               raise StandardError('Error al modficar los datos del segundo dev. Cod={}'.format(ierr))

            # Modifica los valores de tercer devanado
            intgar = [self.ntp3, self.tab3, self.cont3, self.sicod3, self.cod3]
            realari = [self.windv3, self.nomv1, self.angle1, self.rateA3, self.rateB3, self.rateC3, self.rma3, self.rmi3,
                       self.vma3, self.vmi3, self.cr3, self.cx3, self.cnxa3]
            ierr, realaro = psspy.three_wnd_winding_data_3(self.bus_i, self.bus_j, self.bus_k, self.id, 3, intgar,
                                                           realari)
            if ierr != 0:
               raise StandardError('Error al modficar los datos del tercer dev. Cod={}'.format(ierr))

         else:

            if change_bus_type:
               type_bus = Bus(bus_num=self.bus_i).get_bus_type()
               if type_bus == 4 and self.status==1:
                  #Si el nudo esta desconectado y creo un trafo de 2 dev con en servicio cambio el tipo de bus
                  if get_existe_machine(self.bus_i):
                     type=2
                  else:
                     type=1
                  Bus(bus_num=self.bus_i).set_bus_type(type)

               type_bus = Bus(bus_num=self.bus_j).get_bus_type()
               if type_bus == 4 and self.status==1:
                  if get_existe_machine(self.bus_j):
                     type = 2
                  else:
                     type = 1
                  Bus(bus_num=self.bus_j).set_bus_type(type)

            intgar =  [self.status, self.met_bus,self.owner_1, self.owner_2, self.owner_3, self.owner_4,self.ntp1,
                       self.tab1, self.wn1bus, self.cont1, self.sicod1, self.cod1, self.cw, self.cz, self.cm]
            realari = [self.r1_2, self.x1_2,self.sbs1_2,self.windv1, self.nomv1,self.angle1, self.windv2, self.nomv2, self.rateA, self.rateB, self.rateC,self.f_owner1,self.f_owner2,self.f_owner3,self.f_owner4, self.mag1, self.mag2,
                       self.rma1,self.rmi1,self.vma1,self.vmi1, self.cr1, self.cx1, self.cnxa1]
            charar = [self.name, self.vgrp]

            ierr, realaro = psspy.two_winding_data_4(self.bus_i, self.bus_j, self.id,intgar,realari, charar)

            if ierr !=0:
               raise StandardError('Error al crear el trafo de 2 dev. Cod={}: bus_i={}, bus_j={}, ckt={}'.format(ierr, self.bus_i, self.bus_j,self.id))
      else:
         #Creacion de un trafo de tres devanados modelado con un nudo de un 1kv

         raise  NotImplementedError()

   def read_attrs(self):
      """
      Actualiza los atributos con respecto al caso
      :return:
      """
      self.read_sbase()
      self.read_name()
      self.read_resistance_impedance()

   def read_sbase(self):
      if self.is_3D:
         if self.bus_1kv != None:
            ierr, rval = psspy.xfrdat(self.bus_i, self.bus_1kv, self.id, 'SBASE')
            if ierr == 0:
               self.sbs1_2 = rval

            ierr, rval = psspy.xfrdat(self.bus_j, self.bus_1kv, self.id_2, 'SBASE')
            if ierr == 0:
               self.sbs1_2 = rval

            ierr, rval = psspy.xfrdat(self.bus_k, self.bus_1kv, self.id_2, 'SBASE')
            if ierr == 0:
               self.sbs2_3 = rval

         else:
            ierr, rval = psspy.wnddat(self.bus_i, self.bus_j, self.bus_k, self.id, 'SBASE')
      else:
         ierr, rval = psspy.xfrdat(self.bus_i, self.bus_j, self.id, 'SBASE1')
         if ierr==0:
            self.sbs1_2=rval

   def read_resistance_impedance(self):
      if self.is_3D:
         if self.bus_1kv != None:
            ierr, rval = psspy.xfrdat(self.bus_i, self.bus_1kv, self.id, 'CX')
            if ierr == 0:
               self.sbs1_2 = rval

            ierr, rval = psspy.xfrdat(self.bus_j, self.bus_1kv, self.id_2, 'CX')
            if ierr == 0:
               self.sbs1_2 = rval

            ierr, rval = psspy.xfrdat(self.bus_k, self.bus_1kv, self.id_2, 'CX')
            if ierr == 0:
               self.sbs2_3 = rval

         else:
            ierr, rval = psspy.tr3dt2(self.bus_i, self.bus_j, self.bus_k, self.id, 'RX1-2')
            if ierr !=0:
               raise StandardError('Error al obtner el X_12 y R1_2')
            else:
               self.x1_2 = rval.imag
               self.r1_2 = rval.real

            ierr, rval = psspy.tr3dt2(self.bus_i, self.bus_j, self.bus_k, self.id, 'RX2-3')
            if ierr != 0:
               raise StandardError('Error al obtner elX_23 y R_23')
            else:
               self.x2_3 = rval.imag
               self.r2_3 = rval.real

            ierr, rval = psspy.tr3dt2(self.bus_i, self.bus_j, self.bus_k, self.id, 'RX3-1')
            if ierr != 0:
               raise StandardError('Error al obtner el X_31 y R_31')
            else:
               self.x3_1 = rval.imag
               self.r3_1=rval.real

      else:
         ierr, rval = psspy.xfrdat(self.bus_i, self.bus_j, self.id, 'CX')
         if ierr==0:
            self.x1_2=rval
         else:
            raise StandardError('Error al obtner la X')

         ierr, rval = psspy.xfrdat(self.bus_i, self.bus_j, self.id, 'CR')
         if ierr == 0:
            self.r1_2 = rval
         else:
            raise StandardError('Error al obtner la R')

   def read_vector_group(self):
     raise  NotImplementedError('')

   def read_name(self):
      if self.is_3D:
         if self.bus_1kv != None:
            ierr, rval = psspy.xfrnam(self.bus_i, self.bus_1kv, self.id)
            if ierr == 0:
               self.name = rval

         else:
            ierr, rval = psspy.tr3nam(self.bus_i, self.bus_j, self.bus_k, self.id)
      else:
         ierr, rval = psspy.xfrnam(self.bus_i, self.bus_j, self.id)
         if ierr == 0:
            self.name = rval

   def delete(self):
      if self.is_3D:
         if self.bus_1kv !=None:
            ierr = psspy.purgbrn(self.bus_i, self.bus_1kv, self.id)
            if ierr != 0:
               raise StandardError('Error al borrar 1 dev del trafo 3dev con nudos de 1kv. Cod_error={}.bus_i={}; bus_1kv={}, ckt={}'.format(ierr,self.bus_i, self.bus_1kv,self.id))
            ierr = psspy.purgbrn(self.bus_j, self.bus_1kv, self.id_2)
            if ierr != 0:
               raise StandardError('Error al borrar 2 dev del trafo 3dev con nudos de 1kv. Cod_error={}. bus_i={}; bus_1kv={}, ckt={}'.format(ierr,self.bus_j, self.bus_1kv,self.id_2))
            ierr = psspy.purgbrn(self.bus_k, self.bus_1kv, self.id_3)
            if ierr != 0:
               raise StandardError('Error al borrar 3 dev del trafo 3dev con nudos de 1kv. Cod_error={}. bus_i={}; bus_1kv={}, ckt={}'.format(ierr,self.bus_k, self.bus_1kv,self.id_3))
         else:
            ierr = psspy.purg3wnd(self.bus_i, self.bus_j, self.bus_k,  self.id)
            if ierr != 0:
               raise StandardError('Error al borrar el trafo de 3dev. Cod_error={}. bus_i={}; bus_j={}, bus_k={}, ckt={}'.format(ierr,self.bus_i, self.bus_j, self.bus_k,  self.id))

      else:
         ierr = psspy.purgbrn(self.bus_i, self.bus_j, self.id)
         if ierr!=0:
            raise StandardError('Error al borrar el trafo de 2dev. Cod_error={}. bus_i={}; bus_j={}, ckt={}'.format(ierr,self.bus_i, self.bus_j,self.id))

   def load_seq_homopolar(self, r_zero=None, x_zero=None, connect_code=None):
      if r_zero!=None:
         self.r_zero_1=r_zero
         self.r_zero_2 = r_zero
         self.r_zero_3 = r_zero
      if x_zero !=None:
         self.x_zero_1=x_zero
         self.x_zero_2 = x_zero
         self.x_zero_3 = x_zero


      psspy.newseq()

      if self.is_3D and self.bus_1kv==None:
         #APra trafos de 3 dev
         intgar=[self.cz0,self.czg,self.cc]
         realar=[self.r_ground_1,self.x_ground_1,self.r_zero_1,self.x_zero_1,
                 self.r_ground_2, self.x_ground_2,self.r_zero_2,self.x_zero_2,
                 self.r_ground_3, self.x_ground_3, self.r_zero_3, self.x_zero_3,self.rn,self.xn]


         ierr = psspy.seq_three_winding_data_3(self.bus_i, self.bus_j, self.bus_k, self.id, intgar, realar)

         if ierr !=0:
            raise StandardError('Error al cargar la secuencia homopolar al trafo 3 dev: cod= {}'.format(ierr))



      elif self.is_3D and self.bus_1kv!=None:
         #Para trafo de 3dev modelados copn nudo de 1kv
         intgar = [self.cc, self.cz0, self.czg]
         realar = [self.r_ground_1, self.x_ground_1, self.r_zero_1, self.x_zero_1, self.r_ground_2, self.x_ground_2,
                   self.r_zero_2, self.x_zero_2, self.rn, self.xn]

         ierr = psspy.seq_two_winding_data_3(self.bus_i, self.bus_1kv, self.id, intgar, realar)

         if ierr != 0 and ierr !=-1:
            raise StandardError('Error al cargar la secuencia homopolar del dev 1 del trafo de 3dev modelado con 1kv: cod= {}'.format(ierr))

         intgar = [self.cc, self.cz0, self.czg]
         realar = [self.r_ground_2, self.x_ground_2, self.r_zero_2, self.x_zero_2, self.r_ground_3, self.x_ground_3,
                   self.r_zero_3, self.x_zero_3, self.rn, self.xn]

         ierr = psspy.seq_two_winding_data_3(self.bus_j, self.bus_1kv, self.id_2, intgar, realar)


         if ierr != 0 and ierr !=-1:
            raise StandardError(
               'Error al cargar la secuencia homopolar del dev 2 del trafo de 3dev modelado con 1kv: cod= {}'.format(
                  ierr))

         intgar = [self.cc, self.cz0, self.czg]
         realar = [self.r_ground_3, self.x_ground_3, self.r_zero_3, self.x_zero_3, self.r_ground_1, self.x_ground_1,
                   self.r_zero_1, self.x_zero_1, self.rn, self.xn]

         ierr = psspy.seq_two_winding_data_3(self.bus_k, self.bus_1kv, self.id_3, intgar, realar)

         if ierr != 0 and ierr != -1:
            raise StandardError(
               'Error al cargar la secuencia homopolar del dev 2 del trafo de 3dev modelado con 1kv: cod= {}'.format(
                  ierr))

      else:
         #Para trafos de 2 dev
         intgar = [self.cc, self.cz0,self.czg]
         realar = [self.r_ground_1,self.x_ground_1,self.r_zero_1,self.x_zero_1,self.r_ground_2, self.x_ground_2,self.r_zero_2,self.x_zero_2, self.rn, self.xn]

         ierr = psspy.seq_two_winding_data_3(self.bus_i, self.bus_j, self.id, intgar, realar)

         if ierr != 0:
            raise StandardError('Error al cargar la secuencia homopolar al trafo 2 dev: cod= {}'.format(ierr))



class Branch(object):

   def __init__(self, from_bus=_i, to_bus=_i, status=_i, idn=_s, from_name=_s, to_name=_s, rx=complex(_f,_f), b=_f,
                metered=_i, rate_a=_f, rate_b=_f, rate_c=_f, owner_1=_i, owner_2=_i,owner_3=_i,owner_4=_i,bus_k=0,r_zero=_f,x_zero=_f,b_zero=_f,
                lineG_from=_f,lineB_from=_f,lineG_to=_f,lineB_to=_f,length=_f,frac_owner_1=_f,frac_owner_2=_f,frac_owner_3=_f,frac_owner_4=_f):
      """
      Clase que representa una rama del caso PSSE cargado en memoria. Sus atributos están definidos en el propio código

      :Example:

         Mirar get_branch_list() en GE_Funciones.py

      .. note:: Esta clase está pensada para, mediante la API, recuperar todas las branches y a partir de ahí
      crear una lista de objetos de branches. Mirar ejemplo.
      """
      self.from_bus = from_bus
      self.to_bus = to_bus
      self.bus_k = bus_k
      self.status = status
      self.idn = idn.strip()
      self.from_name = from_name
      self.to_name = to_name
      self.r, self.x =(rx.real, rx.imag) if rx else (None, None)
      self.b = b
      self.metered = metered  # <-- bus number del metered bus
      self.rate_a = rate_a
      self.rate_b = rate_b
      self.rate_c = rate_c

      self.owner_1 = owner_1
      self.owner_2 = owner_2
      self.owner_3=owner_3
      self.owner_4=owner_4
      self.frac_owner_1 = frac_owner_1
      self.frac_owner_2 = frac_owner_2
      self.frac_owner_3 = frac_owner_3
      self.frac_owner_4 = frac_owner_4

      self.lineG_from=lineG_from
      self.lineB_from=lineB_from
      self.lineG_to=lineG_to
      self.lineB_to=lineB_to
      self.length=length



      self.r_zero=r_zero
      self.x_zero=x_zero
      self.b_zero=b_zero

      self.is_trafo = False  # <-- Booleano que indica si la rama es de un transformador (True) o no (False)
      self.is_gen_trafo = False # <-- Booleano que indica si la rama es de un transformador de generacion (True) o no (False)
      self.check_if_trafo()
      if self.is_trafo:
         self.is_gen_trafo = chk_is_gen_trafo(self.from_bus, self.to_bus)

   def check_if_trafo(self):
      # Método para comprobar si la rama pertenece a un trafo de 2 dev
      ierr, ival = psspy.xfrint(self.from_bus, self.to_bus, self.idn, 'NTPOSN')
      if ierr == 0:
         self.is_trafo = True
      elif ierr == 3:
         self.is_trafo = False

      if self.bus_k != 0:
         self.is_trafo = True

      return self.is_trafo

   def set_x(self, value):
      if not isinstance(value, (long, int, float)):
         raise TypeError(u'El valor de la X debe ser un número')

      if self.is_trafo:
         ierr = psspy.two_winding_chng_4(self.from_bus, self.to_bus, self.idn, [_i, _i, _i, _i, _i, _i, _i,
            _i, _i, _i, _i, _i, _i, _i, _i], [_f, value, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f,
            _f, _f, _f, _f,  _f, _f, _f, _f, _f], ["", ""])
      else:
         ierr = psspy.branch_chng(self.from_bus, self.to_bus, self.idn, [_i, _i, _i, _i, _i, _i],
                                  [_f, value, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f])

      if ierr == 0: self.x = value

   def set_status(self, param):
      if self.is_trafo and not self.bus_k:
         psspy.two_winding_chng_4(self.from_bus, self.to_bus, self.idn, [param, _i, _i, _i, _i, _i, _i, _i, _i, _i,
                                   _i, _i, _i, _i, _i], [_f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f, _f,
                                   _f, _f, _f, _f, _f, _f,  _f, _f, _f], ["", ""])
      else:
         # Falta poner aqui la api de branch branch_chng
         raise NotImplementedError

   def set_rates(self, rate_a=None, rate_b=None, rate_c=None):
      if not rate_a:
         rate_a = self.rate_a
      if not rate_b:
         rate_b = self.rate_b
      if not rate_c:
         rate_c = self.rate_c

      ierr = psspy.branch_chng(self.from_bus, self.to_bus, self.idn, [_i, _i, _i, _i, _i, _i],
                              [_f, _f, _f, rate_a, rate_b, rate_c, _f, _f, _f, _f, _f, _f, _f, _f, _f])
      if ierr > 0:
         raise ReferenceError(u'No ha sido posible cambiar los rates de la linea <{} {} {}>. ierr: <{}>. '
                              u'rate_a: <{}>. rate_b: <{}<. rate_c: <{}>'.format(
            self.from_bus, self.to_bus, self.idn, ierr, rate_a, rate_b, rate_c))

   def create(self, change_type=True):
      """ Crea o modifica una barra existente"""
      if change_type:
         bus=Bus(bus_num=self.from_bus)
         if bus.get_bus_type()==4 and self.status==1:
            if get_existe_machine(self.from_bus):
               type=2
            else:
               type=1
            bus.set_bus_type(type)
         bus = Bus(bus_num=self.to_bus)
         if bus.get_bus_type()==4 and self.status==1:
            if get_existe_machine(self.to_bus):
               type=2
            else:
               type=1
            bus.set_bus_type(type)

      intgar=[self.status, self.metered, self.owner_1, self.owner_2,self.owner_3,self.owner_4]
      realar=[self.r,self.x,self.b,self.rate_a,self.rate_b,self.rate_c,self.lineG_from,self.lineB_from,self.lineG_to,self.lineB_to,
              self.length,self.frac_owner_1,self.frac_owner_2,self.frac_owner_3,self.frac_owner_4]

      ierr = psspy.branch_data(self.from_bus, self.to_bus, self.idn, intgar, realar)

      if ierr !=0:
         raise StandardError('Error al crear la linea: {}'.format(ierr))

   def load_seq_homopolar(self,r_zero=None,x_zero=None,b_zero=None):
      """
      Carga la secuanecia homopolar de una linea
      :return:
      """
      if r_zero!=None:
         self.r_zero=r_zero
      if x_zero !=None:
         self.x_zero=x_zero
      if b_zero !=None:
         self.b_zero=b_zero

      psspy.newseq()
      ierr=psspy.seq_branch_data_3(self.from_bus, self.to_bus, self.idn, _i, [self.r_zero,self.x_zero,self.b_zero, _f, _f, _f, _f, _f])

      if ierr!=0:
         raise StandardError('Error al cargar la secuencia homopolar.Cod= {}'.format(ierr))

      # ierr = psspy.seq_branch_data_3(self.bus_num, self.idn, _i, [_f, _f, self.b_zero, _f, _f, _f, _f, _f])
      #
      # if ierr != 0:
      #    raise StandardError('Error al cargar la B de secuancia homo en la maquina: cod={}'.format(ierr))

   def get_r_zero(self):
      if self.r_zero==_f:
         self.read_rx_zero()
      return self.r_zero

   def get_x_zero(self):
      if self.r_zero == _f:
         self.read_rx_zero()
      return self.x_zero

   def get_r(self):
      if self.r==_f:
         self.read_rx()
      return self.r

   def get_x(self):
      if self.x == _f:
         self.read_rx()
      return self.x

   def read_rx_zero(self):
      ierr, cmpval = psspy.brndt2(self.from_bus, self.to_bus, self.idn, 'RXZ')
      if ierr != 0 and ierr !=5:
         raise StandardError('Error al leer la R ZERO y X ZERO. cod={}'.format(ierr))
      elif ierr !=5:
         self.r_zero=cmpval.real
         self.x_zero = cmpval.imag

   def read_rx(self):
      ierr, cmpval = psspy.brndt2(self.from_bus, self.to_bus, self.idn, 'RX')
      if ierr != 0:
         raise StandardError('Error al leer la X y R. cod={}'.format(ierr))
      else:
         self.r = cmpval.real
         self.x = cmpval.imag

   def read_b_zero(self):
      ierr, cmpval = psspy.brndat(self.from_bus, self.to_bus, self.idn, 'CHARGZ')
      if ierr !=0 and ierr !=5:
         raise StandardError('Error al leer la B ZERO. cod={}'.format(ierr))

   def read_b(self):
      ierr, value = psspy.brndat(self.from_bus, self.to_bus, self.idn, 'CHARG')
      if ierr !=0 and ierr !=5:
         raise StandardError('Error al leer la B ZERO. cod={}'.format(ierr))
      self.b=value

   def read_status(self):
      ierr, ival = psspy.brnint(self.from_bus, self.to_bus, self.idn, 'STATUS')
      if ierr !=0:
         raise StandardError('Error al leer STATUS. cod={}'.format(ierr))

      self.status=bool(ival)


class SwitchedShunt_depr(PSSElement):
   """ESTA CLASE NO DEBE USARSE. USAR SwitchedShunt
   Se conserva porque aun se usa en una parte (GE_Funciones.init_swshunts(), que en un futuro deberá migrarse"""

   def __init__(self, status=_i, b_init=_f, blk_1_steps=_i, blk_1_mvar=_f, blk_2_steps=_i, blk_2_mvar=_f,
                blk_3_steps=_i, blk_3_mvar=_f, blk_4_steps=_i, blk_4_mvar=_f, blk_5_steps=_i, blk_5_mvar=_f,
                *args, **kw_args):
      """ Inicializa una nueva instancia de 'SwitchedShunt'
      """
      self._status = status
      self._b_init = b_init
      self.blk_1_steps = blk_1_steps
      self.blk_1_mvar = blk_1_mvar
      self.blk_2_steps = blk_2_steps
      self.blk_2_mvar = blk_2_mvar
      self.blk_3_steps = blk_3_steps
      self.blk_3_mvar = blk_3_mvar
      self.blk_4_steps = blk_4_steps
      self.blk_4_mvar = blk_4_mvar
      self.blk_5_steps = blk_5_steps
      self.blk_5_mvar = blk_5_mvar

      super(SwitchedShunt_depr, self).__init__(*args, **kw_args)

   @property
   def b_init(self):
      # Este metodo se ejecuta cada vez que se lee el atributo b_init
      if self._b_init != _f:
         return self._b_init
      else:
         ierr, binit = psspy.swsdt1(self.bus_num, 'BINIT')
         if ierr == 0 or ierr == 5:
            self._b_init = binit
            return self._b_init
         else:
            return None

   @b_init.setter
   def b_init(self, value):
      if isinstance(value, (int, float)):
         self._b_init = value
      else:
         self._b_init = None

   @property
   def status(self):
      if self._status != _i:
         return self._status
      else:
         ierr, status = psspy.swsint(self.bus_num, 'STATUS')
         if ierr == 0 or ierr == 5:
            self._status = status
            return self._status
         else:
            return None

   @status.setter
   def status(self, value):
      # Este metodo se ejecuta cada vez que se lee el atributo status
      if isinstance(value, int):
         self._status = value
      else:
         self._status = None

   def read_all_values(self):
      # Queda pendiente. La idea es que aquí actualice todos los self. con lso datos del caso
      int_strings = []
      real_strings = []
      pass

   def write_in_case(self):
      ierr = psspy.switched_shunt_chng_3(self.bus_num,
                                         [self.blk_1_steps, self.blk_2_steps, self.blk_3_steps, self.blk_4_steps,
                                          self.blk_5_steps, _i, _i, _i, _i, _i, self.status, _i],
                                         [self.blk_1_mvar, self.blk_2_mvar, self.blk_3_mvar, self.blk_4_mvar,
                                          self.blk_5_mvar, _f, _f, _f, _f, _f, self.b_init, _f], "")
      return ierr

   def update_status_attr(self):
      # Metodo para actualizar el valor de status del caso
      ierr, status = psspy.swsint(self.bus_num, 'STATUS')
      if ierr == 0:
         self._status = status
      else:
         self._status = None

   def update_b_init_attr(self):
      # Metodo para actualizar el valor de b_init del caso
      ierr, binit = psspy.swsdt1(self.bus_num, 'BINIT')
      if ierr == 0:
         self._b_init = binit
         return self._b_init
      else:
         return None


class SwitchedShunt(object):

   def __init__(self, bus_num=_i, bus_owner=_i):
      """
      Clase que representa una máquina del caso PSSE cargado en memoria.

      El nombre de los atributos coinciden en gran parte con los del caso. Los atributos derivados no originales
      de PSSE se explican en el propio código.

      BUS_NUM será siempre menor de 40000. Siempre se mantiene el nudo sin barras separadas. En caso de que la máquina
      esté en barras separadas el atributo barras_sep será True

      :Example:

         Mirar la función :func:`get_maq_list` en utilpsse.redpsse

      .. note::
         Esta clase está pensada para, mediante la API, recuperar todas las máquinas del caso y a partir de ahí
         crear una lista de objetos de branches. Mirar ejemplo.
      """
      self.bus_num = bus_num
      self.bus_owner = bus_owner

      #TODO Acabarlo al estilo Machine


class Bus(PSSElement):

   def __init__(self, bus_type=_i, base_kv=_f, volt_pu=_f, angle_deg=_f, v_max=_f, v_min=_f, owner_name=_s, owner_num=_i,zona_num=_i,area_num=_i,e_max=_f,e_min=_f, *args,
                **kw_args):
      """ Inicializa una nueva instancia de 'Bus'
      """
      self.bus_type = bus_type
      self.owned_num = owner_num
      self.owner_name = owner_name
      self.base_kv = base_kv
      self.volt_pu = volt_pu
      self.angle_deg = angle_deg
      self.v_max = v_max
      self.v_min = v_min
      self.e_max = e_max
      self.e_min = e_min
      self.existe = True
      self.area_num = area_num
      self.zona_num = zona_num
      self.area_name = None
      self.zona_name = None
      self.switched_shunt=False
      self.barra_separadas=False


      super(Bus, self).__init__(*args,**kw_args)


   def check_existe(self):
      """
      Obtine un bool para indicar si bus existe
      :return: bool
      """
      ierr = psspy.busexs(self.bus_num)
      if ierr == 0:
         self.existe = True
         return  True
      else:
         self.existe = False
         return False

   def get_area(self):
      """
      Obtiene el area del bus
      :return: area del bus y su nombre
      :rtype :int and string
      """

      if self.area_name == None:
         self.read_area()

      return  self.area_num,self.area_name

   def get_area_num(self):
      """
      Obtiene el area del bus
      :return: area del bus y su nombre
      :rtype :int
      """

      if self.area_name == None:
         self.read_area()

      return self.area_num

   def read_area(self):

      ierr, ival = psspy.busint(self.bus_num, 'AREA')

      if ierr == 0:
         self.area_num = int(ival)

         err, ival = psspy.arenam(self.area_num)

         if ierr ==0:
            self.area_name=ival
         else:
            raise StandardError("Error al obtener nombre del area del bus: codigo {}".format(ierr))


      else:
         raise StandardError(u"Error al obtener el numero area del bus: codigo {}".format(ierr))

   def get_zona(self):
      """
      Retonar el numero de zona y su nombre
      :return:
      """

      if self.zona_name is None:
         self.read_zona()

      return  self.zona_num, self.zona_name

   def get_zona_num(self):
      if self.zona_name is None:
         self.read_zona()

      return self.zona_num

   def read_zona(self):

      ierr, ival = psspy.busint(self.bus_num, 'ZONE')

      if ierr == 0:
         self.zona_num = int(ival)

         ierr, ival = psspy.zonnam(self.zona_num)

         if ierr == 0:
            self.zona_name=ival
         else:
            raise StandardError("Error al obtener el nombre de zona del bus: codigo {}".format(ierr))

      else:
         raise StandardError("Error al obtener el numero de zona del bus: codigo {}".format(ierr))

   def get_base_kv(self):
      if self.base_kv==_f:
         self.read_base_kv()

      return self.base_kv

   def read_base_kv(self):
      ierr, ival = psspy.busdat(self.bus_num ,'BASE')

      if ierr == 0:
         self.base_kv = int(ival)
      else:
         raise StandardError("Error al obtener el voltaje base: codigo {}".format(ierr))

   def read_bus_name(self):
      ierr, ival = psspy.notona(self.bus_num)

      if ierr == 0:
         self.name = ival
      else:
         raise StandardError("Error al obtener el nombre del bus: codigo {}".format(ierr))

   def get_bus_name(self):
      if not self.name == _s:
         self.read_bus_name()
      return self.name

   def read_attrs(self):
      self.read_angle_deg()
      self.read_area()
      self.read_zona()
      self.read_base_kv()
      self.read_bus_type()
      self.read_emax()
      self.read_emin()
      self.read_vmax()
      self.read_vmin()
      self.read_volt_pu()
      self.read_owner()

   #V MIN
   def read_vmin(self):
      v_min = self.__get_busdat('NVLMLO')
      self.v_min = v_min

   #V MAX
   def read_vmax(self):
      v_max = self.__get_busdat('NVLMHI')
      self.v_max = v_max

   #OWNER
   def read_owner(self):
      owned_num=self.__get_busint('OWNER')
      self.owned_num=owned_num

   #E_MAX
   def read_emax(self):
      e_max = self.__get_busdat('EVLMHI')
      self.e_max = e_max

   #E_MIN
   def read_emin(self):
      e_min = self.__get_busdat('EVLMLO')
      self.e_min = e_min

   def check_switched_shunt(self):
      ierr, ival = psspy.swsint(self.bus_num, 'STATUS')

      if ierr == 0:
         self.switched_shunt = True
      return self.switched_shunt

   # TIPO BUS
   def read_bus_type(self):
      bus_type = self.__get_busint('TYPE')
      self.bus_type = bus_type

   def get_bus_type(self):
      if not self.bus_type or self.bus_type == _i:
         self.read_bus_type()
      return self.bus_type

   def set_bus_type(self, param):
      if not isinstance(param, (int, long)):
         raise TypeError(u'Bus.set_bus_type(): el valor de tipo bus debe ser un entero (int). param:<{}>, '
                         u'bus_num: <{}>'.format(param, self.bus_num))
      ierr = psspy.bus_chng_3(self.bus_num, [param, _i, _i, _i], [_f, _f, _f, _f, _f, _f, _f], _s)
      if ierr == 0:
         self.bus_type = param
      else:
         raise StandardError(u"Error ierr en bus_chng_3. bus_num: <{}>, ierr: <{}>, bus_type: <{}>".format(self.bus_num,
                                                                                                     ierr, param))

   def set_bus_num(self, param):
      if not isinstance(param, (int, long)):
         raise TypeError(u'Bus.set_bus_num(): el valor de tipo bus debe ser un entero (int). param:<{}>, '
                         u'bus_num: <{}>'.format(param, self.bus_num))
      ierr = psspy.bus_chng_3(self.bus_num, [_i, _i, _i, _i], [_f, _f, _f, _f, _f, _f, _f], _s)
      if ierr == 0:
         self.bus_num = param
      else:
         raise StandardError(
            u"Error ierr en bus_chng_3. bus_num: <{}>, ierr: <{}>, bus_num: <{}>".format(self.bus_num,
                                                                                          ierr, param))

   # TENSION
   def read_volt_pu(self):
      pu = self.__get_busdat('PU')
      self.volt_pu = pu

   def get_volt_pu(self):
      if not self.volt_pu or self.volt_pu == _f:
         self.read_volt_pu()
      return self.volt_pu

   def set_volt_pu(self, param):
      if not isinstance(param, float):
         raise TypeError(u'Bus.set_volt_pu(): el valor de voltage pu debe ser un numero real (float). param:<{}>, '
                         u'bus_num: <{}>'.format(param, self.bus_num))
      ierr = psspy.bus_chng_3(self.bus_num, [_i, _i, _i, _i], [_f, param, _f, _f, _f, _f, _f], _s)
      if ierr == 0:
         self.volt_pu = param
      else:
         raise StandardError(u"Error ierr en bus_chng_3. bus_num: <{}>, ierr: <{}>, volt_pu: <{}>".format(self.bus_num,
                                                                                                     ierr, param))

   # ANGULO
   def read_angle_deg(self):
      angle_deg = self.__get_busdat('ANGLED')
      self.angle_deg = angle_deg

   def get_angle_deg(self):
      if not self.angle_deg or self.angle_deg == _f:
         self.read_angle_deg()
      return self.angle_deg

   def set_angle_deg(self, param):
      if not isinstance(param, float):
         raise TypeError(u'Bus.set_angle_deg(): el valor del angulo del voltage (deg) debe ser un numero real (float). '
                         u'param:<{}>, bus_num: <{}>'.format(param, self.bus_num))
      ierr = psspy.bus_chng_3(self.bus_num, [_i, _i, _i, _i], [_f, _f, param, _f, _f, _f, _f], _s)
      if ierr == 0:
         self.angle_deg = param
      else:
         raise StandardError(u"Error ierr en bus_chng_3. bus_num: <{}>, ierr: <{}>, angle_deg: <{}>".format(self.bus_num,
                                                                                                     ierr, param))

   # region MÉTODOS PRIVADOS
   def __get_busdat(self, string):

      ierr, rval = psspy.busdat(self.bus_num, string)

      if ierr == 0 or ierr == 3:
         return rval
      else:
         raise StandardError(u"Error ierr en busdat. bus_num: <{}>, ierr: <{}>, string: <{}>".format(self.bus_num,
                                                                                                     ierr, string))

   def __get_busint(self, string):

      ierr, ival = psspy.busint(self.bus_num, string)

      if ierr == 0:
         return int(ival)
      else:
         raise StandardError(u"Error ierr en busint. ierr: <{}>, string: <{}>".format(ierr, string))
   # endregion

   def create(self):
      """
      Crea o modifica un bus
      :return:
      """

      if self.name !=None:
         num_char_bus_name=len(self.name)
         self.name=quitar_caracteres_problematicos(self.name)


         if len(self.name)>12:
            self.name=self.name.strip().replace(" ", "")
            if len(self.name)>12:
               self.name=self.name[0:12]
      else:
         self.name="BUS {}".format(self.bus_num)

      intgar=[self.bus_type,self.area_num, self.zona_num, self.owned_num]
      realar=[self.base_kv,self.volt_pu,self.angle_deg,self.v_max,self.v_min,self.e_max,self.e_min]



      ierr = psspy.bus_data_3(self.bus_num,intgar, realar, self.name)

      if ierr !=0:
         raise StandardError('Error al crear el bus= {}. Cod_error={}'.format(self.bus_num,ierr))

   def delete(self):

      if self.bus_num==None:
         raise StandardError('El numero de bus a borrar no puede ser None')

      ierr=psspy.bsysinit(1)
      if ierr !=0:
         raise  StandardError('Error al borrar el bus.Cod= {}'.format(ierr))
      ierr =psspy.bsyso(1, self.bus_num)
      if ierr != 0:
         raise StandardError('Error al borrar el bus.Cod= {}'.format(ierr))
      ierr =psspy.extr(1, 0, [0, 0])
      if ierr != 0:
         raise StandardError('Error al borrar el bus.Cod= {}'.format(ierr))

   def check_barra_separas(self):
      ierr = psspy.busexs(self.bus_num-sum_bar_sep)
      if ierr == 0:
         self.barra_separadas = True
         return True
      else:
         self.barra_separadas = False
         return False



class ParamAvisos3(object):

   def __init__(self,Perdgen,PorcDCMax,Ret_PG,MinDRS,Ret_DRS,
                Ret_PS,NET_Max,AplicaPgenEol,AplicaPgenTer,SelecMon,
                AreZon_1,AreZon_2,AreZon_3,AreZon_4,AreZon_5,
                AreZon_6,AreZon_7,AreZon_8,AreZon_9,AreZon_10,
                OVERLestLIN,OVERLestTR,VsupEst400,VinfEst400,VsupEst220,
                VinfEst220,VsupEst132,VinfEst132,VsupEst50,VinfEst50,
                VsupEst30,VinfEst30):
      self.Perdgen = Perdgen   # Valor de la generación disparada maxima admisible en MW
      self.PorcDCMax = PorcDCMax # Porcentaje de deslastre de cargas respecto de la demanda (%) admisible
      self.Ret_PG = Ret_PG  # Retardo de parada de la simulación por superar pérdida de generación o deslastre de cargas permitido
      self.MinDRS = MinDRS # Número mínimo de disparos por DRS para parar la simulacion
      self.Ret_DRS = Ret_DRS  # Retardo de parada de la simulación por superar disparo DRS permitidos
      self.NET_Max = NET_Max # Numero maximo de no convergencias admisibles
      self.Ret_PS = Ret_PS  # Retardo de parada de la simulación por perdida de sincronismo no admisible
      self.AplicaPgenEol = AplicaPgenEol # Contabilizacion de la eolica/fotovoltaica disparada. 1 -> Considera la Pgen, 0 -> Considera la Pmax
      self.AplicaPgenTer = AplicaPgenTer # Contabilizacion de la térmica disparada. 1 -> Considera la Pgen, 0 -> Considera la Pmax
      self.SelecMon = SelecMon # Selección del sistema a monitorizar (0 = Todo el caso. 1 = Selección por áreas. 2 = Selección por zonas)
      self.AreZon_1 = AreZon_1  # Código de área/zona a considerar (0 = no selección)
      self.AreZon_2 = AreZon_2 # Código de área/zona a considerar (0 = no selección)
      self.AreZon_3 = AreZon_3 # Código de área/zona a considerar (0 = no selección)
      self.AreZon_4  = AreZon_4# Código de área/zona a considerar (0 = no selección)
      self.AreZon_5  = AreZon_5# Código de área/zona a considerar (0 = no selección)
      self.AreZon_6 = AreZon_6# Código de área/zona a considerar (0 = no selección)
      self.AreZon_7  =AreZon_7# Código de área/zona a considerar (0 = no selección)
      self.AreZon_8  =AreZon_8# Código de área/zona a considerar (0 = no selección)
      self.AreZon_9  =AreZon_9# Código de área/zona a considerar (0 = no selección)
      self.AreZon_10  =AreZon_10# Código de área/zona a considerar (0 = no selección)
      self.OVERLestLIN = OVERLestLIN # Maxima sobrecarga admisible (%) en líneas en el estudio estático final
      self.OVERLestTR = OVERLestTR # Maxima sobrecarga admisible (%) en trafos en el estudio estático final
      self.VsupEst400 = VsupEst400 # Limite superior (pu) de tensión para el estudio estático final (400 kV)
      self.VinfEst400 = VinfEst400 # Limite inferior (pu) de tensión para el estudio estático final (400 kV)
      self.VsupEst220 =VsupEst220 # Limite superior (pu) de tensión para el estudio estático final (220 kV)
      self.VinfEst220 = VinfEst220# Limite inferior (pu) de tensión para el estudio estático final (220 kV)
      self.VsupEst132 = VsupEst132# Limite superior (pu) de tensión para el estudio estático final (110-132-138 kV)
      self.VinfEst132 = VinfEst132# Limite inferior (pu) de tensión para el estudio estático final (110-132-138 kV)
      self.VsupEst50 = VsupEst50# Limite superior (pu) de tensión para el estudio estático final (45-50-66 kV)
      self.VinfEst50 = VinfEst50# Limite inferior (pu) de tensión para el estudio estático final (45-50-66 kV)
      self.VsupEst30 = VsupEst30# Limite superior (pu) de tensión para el estudio estático final (V < 45 kV)
      self.VinfEst30 = VinfEst30 # Limite inferior (pu) de tensión para el estudio estático final (V < 45 kV)


def chk_is_gen_trafo(bus_from, bus_to):
   """Función que comprueba si un trafo es de generación"""
   generation_trafo=False
   try:
      ierr,base_kv_from = psspy.busdat(bus_from,'BASE')
      ierr,base_kv_to = psspy.busdat(bus_to,'BASE')
      if (1.0 < base_kv_from <= 30.0): nudo_baja = int(bus_from)
      if (1.0 < base_kv_to <= 30.0): nudo_baja = int(bus_to)
      if (1.0 < base_kv_from <= 30.0) or (1.0 < base_kv_to <= 30.0): #se tratará de un nudo de generación
         ierr = psspy.inimac(nudo_baja) #miro si tiene maq
         if ierr != 0:
            generation_trafo = False
         else:
            generation_trafo = True
      else:
         generation_trafo = False
   except:
      generation_trafo = None

   return generation_trafo

# a ver si con esto se arregla lo corrupto

class Load(object):

   def __init__(self, bus_num=_i, bus_area=_i, bus_zone=_i, bus_type=_i,
                status=_i, idn=_s, pload=_f, qload=_f, ipload=_f,iqload=_f,
                ypload=_f,yqload=_f,scale=_i, owner=_i, intrpt=_i ):
      """
      Clase que representa una carga del caso PSSE cargado en memoria.

      El nombre de los atributos coinciden en gran parte con los del caso. Los atributos derivados no originales
      de PSSE se explican en el propio código.

      BUS_NUM será siempre menor de 40000. Siempre se mantiene el nudo sin barras separadas. En caso de que la máquina
      esté en barras separadas el atributo barras_sep será True

      :Example:

         Mirar la función :func:`get_maq_list` en utilpsse.redpsse

      .. note::
         Esta clase está pensada para, mediante la API, recuperar todas las máquinas del caso y a partir de ahí
         crear una lista de objetos de branches. Mirar ejemplo.
      """
      self.bus_num = bus_num
      self.bus_area = bus_area
      self.bus_zone = bus_zone
      self.bus_type = bus_type
      self.status = status
      self.idn = idn
      self.pload = pload
      self.qload = qload
      self.ipload =ipload
      self.iqload = iqload
      self.ypload = ypload
      self.yqload = yqload
      self.scale=scale
      self.owner=owner
      self.intrpt=intrpt

   def create(self):
      intgar=[self.status,self.bus_area,self.bus_zone,self.owner,self.scale,self.intrpt]
      realar=[self.pload,self.qload,self.ipload,self.iqload,self.ypload,self.yqload]

      ierr = psspy.load_data_4(self.bus_num, self.idn, intgar, realar)

      if ierr !=0:
         raise StandardError('Error al crear la carga. Cod={}'.format(ierr))


class Fact(object):
   def __init__(self,name,send_bus_num,terminal_bus_num,send_bus_name=None,terminal_bus_name=None):
      self.name=name
      self.send_bus_num=send_bus_num
      self.send_bus_name=send_bus_name
      self.terminal_bus_num =terminal_bus_num
      self.terminal_bus_name =terminal_bus_name

   def delete_facts(self):
      """
      Borra una VSC dc LINE DEL CASO PSSE
      :param name: nOMBRE DEL VSC
      :return:
      """
      ierr = psspy.purgfacts(self.name)
      if ierr != 0:
         raise StandardError('Error al borra la linea fact: {}'.format(ierr))


class Vsc(object):
   def __init__(self,name,convert1_bus_num,convert2_bus_num,convert1_name=None,convert2_name=None):
      self.name=name
      self.convert1_bus_num=convert1_bus_num
      self.convert2_bus_num=convert2_bus_num
      self.convert1_name =convert1_name
      self.convert2_name =convert2_name

   def delete_vsc(self):
      """
      Borra una VSC dc LINE DEL CASO PSSE
      :param name: nOMBRE DEL VSC
      :return:
      """
      ierr = psspy.purgvsc(self.name)
      if ierr != 0:
         raise StandardError('Error al borra la linea vsc: {}'.format(ierr))


class Zona(object):
   def __init__(self,number, name, pload, buses):
      self.number=number
      self.name=name
      self.pload=pload
      self.buses=buses


class Area(object):

   def __init__(self,number, name, pload, buses):
      self.number=number
      self.name=name
      self.pload=pload
      self.buses=buses


def quitar_caracteres_problematicos(text):
   try:
      text = text.decode('utf8').replace(u'\xf1', 'n').replace(u'\xf1', 'n').replace(u'\xd1', 'N').replace(u'\xe1',
                                                                                                           'a') \
         .replace(u'\xe9', 'e').replace(u'\xed', 'i').replace(u'\xf3', 'o').replace(u'\xfa', 'u').replace(
         u'\xc3\x93', 'O'). \
         replace('á', 'a').replace('é', 'e').replace('í', 'i') \
         .replace('ó', 'o').replace('ú', 'u').replace('Á', 'A').replace('É', 'E').replace('I', 'Í').replace('Ó','O').replace(
         'Ú', 'U') \
         .replace('Ñ', 'N').replace('ñ', 'n').replace('¿', '?').replace('¡', '!').replace('Ñ', 'N').replace('ñ',
                                                                                                            'n').encode(
         'utf-8')
   except Exception as e:
      pass

   return text

def get_existe_machine(bus_num):
   ierr = psspy.bsys(0, 0, [1.0, 400.], 0, [], 3, bus_num, 0, [], 0, [])
   flag = 4  # all machines
   ierr, (bus, status) = psspy.amachint(sid=0, flag=flag, string=['NUMBER', 'STATUS'])
   [].__len__()

   if bus.__len__()>0 and filter(lambda x: x==1,status):
      #Hay maquinas conectadas
      return True
   else:
      return False

