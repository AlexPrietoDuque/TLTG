# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Fichero para la lectura de los diversos archivos
#
# Author:      Alejandro Prieto Duque
#
# Iniciado:     26/01/2018
# Finalizado:
#-------------------------------------------------------------------------------



import re



def extraer_int_by_text(text):
   num=''
   try:
      match = re.findall('\d+', text)

      if match != None or match == []:
         if match[0] != "":
            num=match[0]
            num = int(num)
         else:
            num = match[1].strip()
            num = int(num)
   except Exception as e:
     raise StandardError ("Error al extaer en numero del texto {}. Debido a {}".format(text,e.message))

   return num


def delete_error_char(exep,text):
   """
   Sirve para eleminar los caracteres que dan error caudno ahcemos un  encode

   El error siemrpe es asi: 'utf8' codec can't decode byte 0xd1 in position 2: invalid continuation byte

   Busco la posicion que da erroe y lo sustituyo por un vacio
   :param e:
   :return:
   """
   try:
      e_oring=exep
      patron = re.compile('position', re.I | re.MULTILINE)
      patron2 = re.compile('\d+', re.I | re.MULTILINE)

      matcher = patron.search(exep)

      if matcher != None:
         exep = exep[matcher.start():]
         matcher = patron2.search(exep)
         if matcher != None:
            exep = exep[matcher.start():matcher.end()]
            posicion=int(exep)
            text=text[:posicion]+text[posicion+2:]
   except Exception as e:
      pass

   return text