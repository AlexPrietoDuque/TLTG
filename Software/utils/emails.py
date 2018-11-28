import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import os

#python -m smtpd -n -c DebuggingServer localhost:25
#Ejecuatar el comando anterior para hacer un Servidor en local. Dejar el cmd abiarto si se cierra se elemina el servidor

def send_email_smtp(ipServidor,From,To,Subject,texto,path_adjuntos=[], user=None, password=None, port=None,ssl=False):

   msg = MIMEMultipart()
   msg['From'] = From
   msg['To'] = ', '.join(To)
   msg['Date'] = formatdate(localtime=True)
   msg['Subject'] = Subject

   msg.attach(MIMEText(texto))

   for f in path_adjuntos:
      with open(f, "rb") as fil:
         part = MIMEApplication(
            fil.read(),
            Name=os.path.basename(f))
      # After the file is closed
      part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
      msg.attach(part)

   if ssl==False:
      if port==None:
         smtp = smtplib.SMTP(ipServidor)
      else:
         smtp = smtplib.SMTP(ipServidor,port)
   else:
      if port==None:
         smtp = smtplib.SMTP_SSL(ipServidor)
      else:
         smtp = smtplib.SMTP_SSL(ipServidor,port)


   smtp.set_debuglevel(False)

   if user !=None and password !=None:
      smtp.login(user, password)

   smtp.sendmail(From, To, msg.as_string())
   smtp.close()