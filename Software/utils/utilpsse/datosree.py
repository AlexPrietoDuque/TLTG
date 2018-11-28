# coding=utf-8

provincias = {
              'Almer':'Almeria',
              'diz':'Cadiz',
              'rdoba':'Cordoba',
              'Granada':'Granada',
              'Huelva':'Huelva',
              'Ja':'Jaen',
              'laga':'Malaga',
              'Sevilla':'Sevilla',
              'Huesca':'Huesca',
              'Teruel':'Teruel',
              'Zaragoza':'Zaragoza',
              'Asturias':'Asturias',
              'Cantabria':'Cantabria',
              'vila':'Avila',
              'Burgos':'Burgos',
              'Le':'Leon',
              'Palencia':'Palencia',
              'Salamanca':'Salamanca',
              'Segovia':'Segovia',
              'Soria':'Soria',
              'Valladolid':'Valladolid',
              'Zamora':'Zamora',
              'Albacete':'Albacete',
              'Ciudad':'Ciudad Real',
              'Cuenca':'Cuenca',
              'Guadalajara':'Guadalajara',
              'Toledo':'Toledo',
              'Barcelona':'Barcelona',
              'Gerona':'Gerona',
              'rida':'Lleida',
              'Tarragona':'Tarragona',
              'Alicante':'Alicante',
              'Castell':'Castellon',
              'Valencia':'Valencia',
              'Badajoz':'Badajoz',
              'ceres':'Caceres',
              'Coru':'Coruna',
              'Lugo':'Lugo',
              'rense':'Ourense',
              'Pontevedra':'Pontevedra',
              'Rioja':'Rioja',
              'Madrid':'Madrid',
              'Murcia':'Murcia',
              'Navarra':'Navarra',
              'Vizcaya':'Vizcaya',
              'zcoa':'Guipuzcoa',
              'Alava':'Alava'
              }

# -------------------------------------------------------------------------------------------------
# Areas extranjeras
# IMPORTANTE: Si se cambia la variable areExt, también hay que cambiarla en el módulo de GE_ClasesPSSE.py
areExt = 6, 7, 8  # Areas extranjeras

# -------------------------------------------------------------------------------------------------
# Zonas península

zonEsp = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18  # Zonas península

# -------------------------------------------------------------------------------------------------
# Buses del HVDC Santa lLogaia - Baixas

HVDC_LLO_BAI_BUSES = 18198, 18197, 18196, 18195
EC_BAIXAS_1 = 18195
EC_BAIXAS_2 = 18196
EC_SLLOGAIGA_1= 18197
EC_SLLOGAIGA_2 = 18198
ID_HVDC = '1 '

# -------------------------------------------------------------------------------------------------
# FACTS
facts = {"TORRSEG": r"""TSG-OLC""",
         "MAG": r"""MGL-OLC"""}

# -------------------------------------------------------------------------------------------------
# DESFASADORES
desfasadores = {"SALINAS": (24238, 24249, '1'),
                "ARKALE": (22024, 22025, '1'),
                "PRAGNERES": (28045, 28047, '1')}

# -------------------------------------------------------------------------------------------------
# Tecnologías generadores
# IMPORTANTE: Si se cambia la variable tecGen, también hay que cambiarla en el módulo de GE_ClasesPSSE.py
tecGen = {'TER':['A','B','C','D','F','G','H','I','J','K','Q'],
          'HID':['0','1','2','3','4'],
          'EOL':['R','S','T'],
          'FV':['U'],
          'TS':['V'],
          'RCR':['Y'],
          'NUC':['Q'],
          'CC2':['J','K'],
          'CAR':['A','B','C','D'],
          'CC':['I','J','K']}

# -------------------------------------------------------------------------------------------------
# Fiestas fijas (mes, dia)

fiestasFijas =[(1, 1), (6, 1), (15, 8), (12, 10), (1, 11), (6, 12), (8, 12)]

