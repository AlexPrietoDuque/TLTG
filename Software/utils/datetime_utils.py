import datetime
import pytz

def convert_fecha_utc(fecha):

   # Cambio la hora del caso a utc

   local=pytz.timezone('Europe/Madrid')
   local_dt=local.localize(fecha,is_dst = None)
   utc_dt=local_dt.astimezone(pytz.utc)

   return utc_dt


