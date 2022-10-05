import smtplib, ssl

port= 587
smtp_server = "smtp.gmail.com"
sender_email = "scsucfittemp@gmail.com"
receiver_email = "scsucfittemp@gmail.com"
password = input("Type your password and press enter:")
message = """\
Subject: Test email

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)