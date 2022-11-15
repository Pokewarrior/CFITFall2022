
import smtplib
server = smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login('scsucfittemp@gmail.com','ujmtrpjrcsfnsejn')
message = """Subject: New Acessment made 

\n A new accessment was made by your instructor \n"""
server.sendmail('scsucfittemp@gmail.com','espeonfan96@gmail.com', message)
print('mail sent')
