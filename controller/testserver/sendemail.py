#! /usr/bin/python
# -*- coding: utf-8 -*-

import smtplib
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import os.path

from library import myglobal
from library import configuration
import logging
import logging.config



def sendmail(smtpserver, port, sender, subject,fromname, passwd, to, cc, mailbody, attachments):

    logging.config.fileConfig(myglobal.LOGGINGINI)
    logger=logging.getLogger('sendemail')
    nRet = True

    #
    main_msg = email.MIMEMultipart.MIMEMultipart()

    #
    text_msg = email.MIMEText.MIMEText(mailbody, 'html')
    main_msg.attach(text_msg)

    #
    contype = 'application/octet-stream'
    maintype, subtype = contype.split('/', 1)

    ##
    if attachments is not None:
        for attachment in attachments:
            #print attachment
            data = open(attachment, 'rb')
            file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
            file_msg.set_payload(data.read())
            data.close()
            email.Encoders.encode_base64(file_msg)
            ##
            attachment = os.path.basename(attachment)
            #print attachment
            file_msg.add_header('Content-Disposition',
             'attachment', filename = attachment)
            main_msg.attach(file_msg)

    #
    main_msg['From'] = fromname
    main_msg['To'] = to

    main_msg['Subject'] = subject
    main_msg['Date'] = email.Utils.formatdate()
    toall = to
    if cc != '':
        main_msg['Cc'] = cc
        toall = to + "," + cc
    #
    fullText = main_msg.as_string()

    #
    server = None
    try:
        server = smtplib.SMTP(smtpserver, int(port))
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender,passwd)
        server.sendmail(sender, toall.split(","), fullText)
    except Exception,e:
            nRet = False
            logger.error("The exception is %s" % e.message)
    finally:
        if server:
            server.quit()
        return nRet

