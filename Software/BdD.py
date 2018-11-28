# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     create DB and load data
# Author:      MRCh
# Started:     20/11/2018
# Finished:    21/11/2018
#-------------------------------------------------------------------------------

from LecturaFicheros import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String,Integer, ForeignKey, Float
from sqlalchemy.orm import relationship, sessionmaker,session
from sqlalchemy.pool import StaticPool
import os
import time


try:
   Base = declarative_base()
   ruta_BdD_caso = os.path.join(Rutas().ruta_BBDD, 'BdD_' + time.strftime("%Y%m%d_%H%M") + '.sql')
   engine = create_engine(r'sqlite:///{}'.format(ruta_BdD_caso), echo=False, connect_args={'check_same_thread': False}, poolclass=StaticPool)
   engine.raw_connection().connection.text_factory = str
   Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
   s = Session() #type: session.Session
except Exception as e:
   raise StandardError('Error en la inicializacion de la base de datos: {}'.format(e.message))

class Param_Entrada(Base):
   __tablename__ = 'Param_Entrada'
   Id_Param_Entrada = Column(Integer, primary_key=True, autoincrement=True)
   Factor_Distrib_Min = Column(Float,nullable=False)
   N_datosN=Column(Integer,nullable=False)
   N_datosN_1=Column(Integer,nullable=False)
   N_datosN_2=Column(Integer,nullable=False)
   U_min_p = Column(Integer, nullable=False)
   U_max_p = Column(Integer, nullable=False)
   U_min_i = Column(Integer, nullable=False)
   U_max_i = Column(Integer, nullable=False)
   Rate_A=Column(Integer,nullable=False)
   Rate_B=Column(Integer,nullable=False)

class Info_Casos(Base):
   __tablename__ = 'Info_Casos'
   N_Caso = Column(Integer, primary_key=True)
   Probabilidad = Column(Float,nullable=False)

   salida_re = relationship("Salida_TLTG")

class Sist_Estudio(Base):
   __tablename__ = 'Sist_Estudio'
   Id_Sist_Est = Column(Integer, primary_key=True, autoincrement=True)
   Tipo = Column(String(36),nullable=False)
   Nombre = Column(String(100),nullable=False)
   Sistema = Column(String(100),nullable=False)

   salida_re = relationship("Salida_TLTG")

class Contingencias(Base):
   __tablename__ = 'Contingencias'
   Cont_Id = Column(Integer, primary_key=True, autoincrement=True)
   Name = Column(String(100), nullable=False)
   Description = Column(String(100),nullable=False)
   Npss_1 = Column(Integer, nullable=False)
   Npss_2 = Column(Integer, nullable=False)
   Npss2_1 = Column(Integer, nullable=False)
   Npss2_2 = Column(Integer, nullable=False)
   ckt_1 = Column(Integer, nullable=False)
   ckt_2 = Column(Integer, nullable=False)

   salida_re = relationship("Salida_TLTG")

class Salida_TLTG(Base):
   __tablename__ = 'Salida_TLTG'
   Id_Sal = Column(Integer, primary_key=True, autoincrement=True)
   Tipo = Column(String(36), nullable=False)
   N_caso = Column(Integer, ForeignKey("Info_Casos.N_Caso"), nullable=False)
   Pot_Gen_Base = Column(Float,nullable=False)
   Incr_Trans_Cap = Column(Float,nullable=False)
   RatA = Column(Float,nullable=False)
   RatB = Column(Float,nullable=False)
   Distr_Factor = Column(Float,nullable=False)
   Cont_Descr = Column(String(100),nullable=False)
   Nombre_Sist_Est = Column(String(100),nullable=False)
   Id_Sist_Est = Column(Integer, ForeignKey("Sist_Estudio.Id_Sist_Est"), nullable=False)
   Cont_Id = Column(Integer, ForeignKey("Contingencias.Cont_Id"), nullable=False)

   info_re = relationship("Info_Casos")
   sist_re = relationship("Sist_Estudio")
   cont_re = relationship("Contingencias")


def crearBdD(parametros, sistemas_estudio, info_casos, contingenciasN_2):

   try:
      Base.metadata.create_all(engine)

      param_data = [Param_Entrada(Factor_Distrib_Min=parametros.factor_distrb_min, N_datosN=parametros.N_datosN,
                                  N_datosN_1=parametros.N_datosN_1,
                                  N_datosN_2=parametros.N_datosN_2, U_min_p=parametros.U_min_p, U_max_p=parametros.U_max_p,
                                  U_min_i=parametros.U_min_i, U_max_i=parametros.U_max_i,
                                  Rate_A=parametros.Rate_A, Rate_B=parametros.Rate_B)]

      sist_data=[]
      for x in sistemas_estudio:
         sist_data.append(Sist_Estudio(Tipo=x.Tipo, Nombre=x.Nombre,Sistema=x.Sistema))

      infocasos=[]
      for x in info_casos:
         infocasos.append(Info_Casos(N_Caso=x.N_Caso, Probabilidad=x.Probabilidad))

      cont_N2=[]
      for x in contingenciasN_2:
         cont_N2.append(Contingencias(Name=x.Name, Description=x.Description, Npss_1=x.Npss_1, Npss_2=x.Npss_2, ckt_1=x.ckt_1, Npss2_1=x.Npss2_1, Npss2_2=x.Npss2_2, ckt_2=x.ckt_2))

      s.bulk_save_objects(param_data)
      s.bulk_save_objects(sist_data)
      s.bulk_save_objects(infocasos)
      s.bulk_save_objects(cont_N2)

      s.commit()

   except Exception as e:
      raise StandardError('Error en la creacion de la base de datos: {}'.format(e.message))