#!/usr/bin/env python3
# Amazon Simple Email Service (ses)

import smtplib, ssl
import config

receiver_email = "karl.rink@nationsinfocorp.com"

sender_email = config.ses['smtp_from']
smtp_server  = config.ses['smtp_host']
port         = config.ses['smtp_port']  # For starttls
smtp_user    = config.ses['smtp_user']
smtp_pass    = config.ses['smtp_pass']

message = """\
Subject: Hello you...

This message is sent from Python.
via Amazon Simple Email Service (ses)
"""

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(smtp_user, smtp_pass)
    server.sendmail(sender_email, receiver_email, message)


