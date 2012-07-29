import logging #registro de errores, van a consola y al fichero de texto.
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).
import os
import threading

#Libs
import cons


class SMTPHandler(logging.Handler):
    """

    DEPRECATED
    
    A handler class which sends an SMTP email for each logging event.
    """
    def __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials=None, secure=None):
        """
        Initialize the handler.

        Initialize the instance with the from and to addresses and subject
        line of the email. To specify a non-standard SMTP port, use the
        (host, port) tuple format for the mailhost argument. To specify
        authentication credentials, supply a (username, password) tuple
        for the credentials argument. To specify the use of a secure
        protocol (TLS), pass in a tuple for the secure argument. This will
        only be used when authentication credentials are supplied. The tuple
        will be either an empty tuple, or a single-value tuple with the name
        of a keyfile, or a 2-value tuple with the names of the keyfile and
        certificate file. (This tuple is passed to the `starttls` method).
        """
        logging.Handler.__init__(self)
        if isinstance(mailhost, tuple):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost, self.mailport = mailhost, None
        if isinstance(credentials, tuple):
            self.username, self.password = credentials
        else:
            self.username = None
        self.fromaddr = fromaddr
        if isinstance(toaddrs, basestring):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure

    def getSubject(self, record):
        """
        Determine the subject for the email.

        If you want to specify a subject line which is record-dependent,
        override this method.
        """
        return self.subject

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            from email.utils import formatdate
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                            self.fromaddr,
                            ",".join(self.toaddrs),
                            self.getSubject(record),
                            formatdate(), msg)
            if self.username:
                if self.secure is not None:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

class SMTPLogger(threading.Thread):
    """
    clase SMTP Handler: SMTPHandler(self, mailhost, fromaddr, toaddrs, subject, credentials=None, secure=None)
    logging.handlers.SMTPHandler no soporta TLS (secure=None) para gmail y otros en python 2.6
    """
    def __init__(self, old_log=cons.OLD_LOG):
        """"""
        threading.Thread.__init__(self) #iniciar threading.Thread
        self.old_log = old_log
    
    def run(self):
        """"""
        self.send_log()
    
    def send_log(self):
        """"""
        try:
            if os.path.exists(self.old_log):
                with open(self.old_log, "rb") as fh:
                    exct_found = False
                    lines_buffer = ""
                    for line in fh:
                        lines_buffer += line
                        if not "INFO" in line: #except or critical message
                            exct_found = True
                        elif "SENDED" in line:
                            exct_found = False
                        #if len(lines_buffer) > 4048 and not exct_found:
                            #lines_buffer = ""
                if exct_found:
                    smtp = SMTPHandler(("smtp.gmail.com", 587), "bugs@ochdownloader.com", "ochdownloader@gmail.com", "Bug-Found "+cons.APP_VER, ("user@gmail.com", "pass"), ())
                    smtp.emit(logging.LogRecord(None, None, "", 0, lines_buffer, None, None))
                    logger.info("SENDED")
        except Exception as err:
            logger.exception(err)
