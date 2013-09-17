#
# Alkivi Logger, used in all scripts
#

import logging
import logging.handlers
import sys
import os
import pwd
import socket
import pprint

"""
    Define our levels
"""
CRITICAL    = 50
FATAL       = CRITICAL
ERROR       = 40
WARNING     = 30
WARN        = WARNING
IMPORTANT   = 25
INFO        = 20
LOG         = 15
DEBUG       = 10
DEBUG_DEBUG = 5
NOTSET      = 0

logging.addLevelName(DEBUG_DEBUG, "DEBUG++")
logging.addLevelName(LOG, "LOG")
logging.addLevelName(IMPORTANT, "IMPORTANT")

"""
    Globals used to send extra information using emails
"""
source    = sys.argv[0]
sourceDir = os.path.realpath(source)
pid       = os.getpid()
#user      = os.getlogin()  #crash in cgi and cron
user      = pwd.getpwuid(os.getuid()).pw_name
host      = socket.gethostname()


class AlkiviEmailHandler(logging.Handler):
    def __init__(self, mailhost, fromaddr, toaddrs, level):
        logging.Handler.__init__(self)
        self.mailhost     = mailhost
        self.mailport     = None
        self.fromaddr     = fromaddr
        self.toaddrs      = toaddrs
        self.levelToFlush = level
        
        # Init another buffer which will store everything
        self.allbuffer    = []

        # Buffer is an array that contains formatted messages
        self.buffer = []

    def emit(self, record):
        msg = self.format(record)

        if(record.levelno >= self.levelToFlush):
            self.buffer.append(msg)

        # Add to all buffer in any case
        self.allbuffer.append(msg)

    def generateMail(self):
        # Global header
        msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (self.fromaddr, ','.join(self.toaddrs), self.buffer[0])


        # Script info
        msg = msg + "\r\nScript info : \r\n"
        msg = msg + "%-9s: %s" % ('Script', source) + "\r\n"
        msg = msg + "%-9s: %s" % ('User', user) + "\r\n"
        msg = msg + "%-9s: %s" % ('Host', host) + "\r\n"
        msg = msg + "%-9s: %s" % ('PID', pid) + "\r\n"

        # Current trace
        msg = msg + "\r\nCurrent trace : \r\n"
        for record in self.buffer:
            msg = msg + record + "\r\n"

        # Now add stack trace
        msg = msg + "\r\nFull trace : \r\n"
        for record in self.allbuffer:
            msg = msg + record + "\r\n"

        # Dump ENV
        msg = msg + "\r\nEnvironment:" + "\r\n"
        for name, value in os.environ.items():
             msg = msg + "%-10s = %s\r\n" % (name, value)

        return msg


    def flush(self):
        if len(self.buffer) > 0:
            try:
                import smtplib
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT

                smtp = smtplib.SMTP(self.mailhost, port)
                msg = self.generateMail()

                smtp.sendmail(self.fromaddr, self.toaddrs, msg)
                smtp.quit()
            except:
                self.handleError(None)  # no particular record

        self.buffer    = []
        self.allbuffer = []

    """
        We manually flush
    """
    def shouldFlush(self, record):
        return False

 
from alkivi.common import Singleton

@Singleton
class Logger():
    """
        This class defines a custom Logger class, that we will use for all alkivi script
        check /alkivi/samples/testLogger.py for more informations
    """
    def __init__(self, 
            min_log_level_to_print  = INFO,
            min_log_level_to_mail   = WARNING,
            min_log_level_to_save   = INFO,
            min_log_level_to_syslog = WARNING,
            filename                = source + '.log',
            emails                  = [],
            prefix                  = None,
            ):


        self.subject                  = "%s_%i" % (source, pid)
        self.min_log_level_to_print   = min_log_level_to_print
        self.min_log_level_to_save    = min_log_level_to_save
        self.min_log_level_to_mail    = min_log_level_to_mail
        self.min_log_level_to_syslog  = min_log_level_to_syslog
        self.filename                 = filename
        self.emails                   = emails
        self.prefix                   = prefix
        

        self.currentLogger = None
        self.loggers       = []

        # Create object Dumper
        self.pp = pprint.PrettyPrinter(indent=4)

        # Create newLoopLogger, the rootOne
        self.newLoopLogger()


        

    """
        Generic log functions
    """
    def _log(self, priority, message, *args, **kws):
        # format
        for arg in args:
            message = message + "\n" + self.pp.pformat(arg)

        self.currentLogger._log(priority, message, (), **kws)

    """
        All functions that can do log :)
    """
    def debug_debug(self, message, *args, **kws):
        self._log(DEBUG_DEBUG, message, *args, **kws)

    def debug(self, message, *args, **kws):
        self._log(DEBUG, message, *args, **kws)

    def log(self, message, *args, **kws):
        self._log(LOG, message, *args, **kws)

    def info(self, message, *args, **kws):
        self._log(INFO, message, *args, **kws)

    def important(self, message, *args, **kws):
        self._log(IMPORTANT, message, *args, **kws)

    def warn(self, message, *args, **kws):
        self._log(WARNING, message, *args, **kws)

    def warning(self, message, *args, **kws):
        self._log(WARNING, message, *args, **kws)

    def error(self, message, *args, **kws):
        self._log(ERROR, message, *args, **kws)

    def fatal(self, message, *args, **kws):
        self._log(CRITICAL, message, *args, **kws)

    def critical(self, message, *args, **kws):
        self._log(CRITICAL, message, *args, **kws)

    def exception(self, message, *args, **kws):
        self.currentLogger.exception(message, *args, **kws)


    """
        Handles creation of secondary logger, used in loops
    """
    def newLoopLogger(self):
        # Do we have already a logger ?
        newLogger = LoggerIteration(
                subject                  = "%s_%i" % (self.subject, len(self.loggers)),
                min_log_level_to_print   = self.min_log_level_to_print,
                min_log_level_to_save    = self.min_log_level_to_save,
                min_log_level_to_mail    = self.min_log_level_to_mail,
                min_log_level_to_syslog  = self.min_log_level_to_syslog,
                filename                 = self.filename,
                emails                   = self.emails,
                currentLogger            = self.currentLogger
                )


        self.loggers.append(newLogger)
        self.currentLogger = self.loggers[-1]

    def delLoopLogger(self):
        # Flush data (i.e send email if needed)
        self.currentLogger.flush()
        self.currentLogger.disable() # Disable current logger

        # Only if more than one logger
        if(len(self.loggers)>1):
            self.loggers.pop()
            self.currentLogger = self.loggers[-1]
            self.currentLogger.enable() # Was previously disabled

    def newIteration(self, *args, **kwargs):
        # Flush data (i.e send email if needed)
        self.currentLogger.flush()
        self.currentLogger.setPrefix(*args, **kwargs)


    # Helper to reset level after log creation
    def setMinLevelToSave(self, *args, **kwargs):
        print "todo"

    def setMinLevelToPrint(self, level):
        self.min_log_level_to_print = level
        self.currentLogger.setMinLevelToPrint(level)

    def setMinLevelToSave(self, level):
        self.min_log_level_to_save = level
        self.currentLogger.setMinLevelToSave(level)

    def setMinLevelToMail(self, *args, **kwargs):
        self.min_log_level_to_mail = level
        self.currentLogger.setMinLevelToMail(level)

    def setMinLevelToSyslog(self, *args, **kwargs):
        self.min_log_level_to_syslog = level
        self.currentLogger.setMinLevelToSyslog(level)


class LoggerIteration():
    """
        This class defines a custom Logger iteration. Logger class will use those iteration :)
        check /alkivi/samples/testLogger.py for more informations
    """


    def __init__(self, 
            subject                 = source,
            min_log_level_to_print  = INFO,
            min_log_level_to_mail   = WARNING,
            min_log_level_to_save   = INFO,
            min_log_level_to_syslog = WARNING,
            filename                = source + '.log',
            emails                  = [],
            currentLogger           = None,
            ):

        # Create logger
        self.logger = logging.getLogger(subject)
        self.logger.setLevel(NOTSET)

        # Store data
        self.emails   = emails
        self.filename = filename
        self.subject  = subject

        # Empty handler by default
        self.handlers                 = []
        self.bufferHandler            = None
        self.consoleHandler           = None
        self.fileHandler              = None
        self.emailHandler             = None
        self.syslogHandler            = None
        self.min_log_level_to_print   = min_log_level_to_print
        self.min_log_level_to_save    = min_log_level_to_save
        self.min_log_level_to_mail    = min_log_level_to_mail
        self.min_log_level_to_syslog  = min_log_level_to_syslog

        # Define prefixes : add old logger prefix if present
        if(currentLogger != None):
            self.basePrefixes = currentLogger.basePrefixes + currentLogger.prefixes
            currentLogger.disable() # Needed not to print duplicate
        else:
            self.basePrefixes = []

        self.prefixes     = []
        

        # Auto declare handler
        self.setStreamHandler()
        self.setSyslogHandler()
        self.setTimeRotatingFileHandler()
        self.setAlkiviEmailHandler()

        # Create formatter
        self.setFormatter()

        # Set handlers formatter
        self.setHandlers()

        # Set logger handlers
        self.enable()

    """
        Function that ease logger creation
    """
    def setStreamHandler(self):
        if(self.min_log_level_to_print != None):
            self.consoleHandler = logging.StreamHandler()
            self.consoleHandler.setLevel(self.min_log_level_to_print)
            self.handlers.append(self.consoleHandler)

    def deleteStreamHandler(self):
        #TODO
        pass

    def setSyslogHandler(self):
        if(self.min_log_level_to_syslog != None):
            self.syslogHandler = logging.handlers.SysLogHandler(address = '/dev/log')
            self.syslogHandler.setLevel(self.min_log_level_to_syslog)
            self.handlers.append(self.syslogHandler)

    def deleteSyslogHandler(self):
        #TODO
        pass

    def setTimeRotatingFileHandler(self):
        if(self.min_log_level_to_save != None):
            self.fileHandler = logging.handlers.TimedRotatingFileHandler(self.filename, when='midnight')
            self.fileHandler.setLevel(self.min_log_level_to_save)
            self.handlers.append(self.fileHandler)

    def deleteTimeRotatingFileHandler(self):
        #TODO
        pass

    def setAlkiviEmailHandler(self):
        if(self.min_log_level_to_mail != None and len(self.emails) > 0):
            self.emailHandler = AlkiviEmailHandler(mailhost='127.0.0.1', fromaddr="%s@%s" % (user, host), toaddrs=self.emails, level=self.min_log_level_to_mail)
            self.emailHandler.setLevel(NOTSET) # Needed, we want all log to go thought this
            self.handlers.append(self.emailHandler)

    def deleteAlkiviEmailHandler(self):
        #TODO
        pass

    """
        Function to set level to log after creation
    """
    def setMinLevelToPrint(self, level):
        self.min_log_level_to_print = level

        if(self.consoleHandler != None):
            self.consoleHandler.setLevel(level)
        elif(level != None):
            self.setStreamHandler()
        else:
            self.deleteStreamHandler()

    def setMinLevelToSave(self, level):
        self.min_log_level_to_save = level

        if(self.fileHandler != None):
            self.fileHandler.setLevel(level)
        elif(level != None):
            self.setTimeRotatingFileHandler()
        else:
            self.deleteTimeRotatingFileHandler()

    def setMinLevelToSyslog(self, level):
        self.min_log_level_to_syslog = level

        if(self.syslogHandler != None):
            self.syslogHandler.setLevel(level)
        elif(level != None):
            self.setSyslogHandler()
        else:
            self.deleteSyslogHandler()

    def setMinLevelToMail(self, level):
        self.min_log_level_to_mail = level

        if(self.emailHandler != None):
            self.emailHandler.setLevel(level)
        elif(level != None):
            self.setAlkiviEmailHandler()
        else:
            self.deleteAlkiviEmailHandler()

    """
        Only one function to log, called by Logger
    """
    def _log(self, priority, message, *args, **kws):
        self.logger._log(priority, message, (), **kws)

    def exception(self, message, *args, **kws):
        self.logger.exception(message, *args, **kws)


    """
        Generate formatters according to prefixes
    """
    def setFormatter(self):
        format = '[%(asctime)s] [%(levelname)-9s]'

        for prefix in self.basePrefixes:
            if(prefix):
                format += ' [%s]' % (prefix)

        for prefix in self.prefixes:
            if(prefix):
                format += ' [%s]' % (prefix)

        format       = format + ' %(message)s'
        syslogFormat = '[%s] %s' % (source, format)

        self.formatter       = logging.Formatter(format)
        self.syslogFormatter = logging.Formatter(syslogFormat)

    def getFormatter(self, handler):
        # Custom rules for syslog
        if(handler.__class__.__name__ == 'SysLogHandler'):
            return self.syslogFormatter
        else:
            return self.formatter


    """
        Tips to handle loggers ...
    """
    def setHandlers(self):
        for handler in self.handlers:
            handler.setFormatter(self.getFormatter(handler))

    def enable(self):
        for handler in self.handlers:
            self.logger.addHandler(handler)

    def disable(self):
        for handler in self.handlers:
            self.logger.removeHandler(handler)

    def addPrefix(self, prefix):
        self.prefixes.append(prefix)
        self.setFormatter()
        self.setHandlers()

    def setPrefix(self, prefix):
        if(len(self.prefixes)>0):
            self.prefixes[-1] = prefix
        else:
            self.prefixes.append(prefix)

        self.setFormatter()
        self.setHandlers()

    def flush(self):
        # Flush all buffer ? just email ?
        if(self.emailHandler != None):
            self.emailHandler.flush()


#
# Define global functions that can be use using logger.log directly in code :)
#
def debug_debug(message, *args, **kws):
    Logger.instance().debug_debug(message, *args, **kws)

def debug(message, *args, **kws):
    Logger.instance().debug(message, *args, **kws)

def log(message, *args, **kws):
    Logger.instance().log(message, *args, **kws)

def info(message, *args, **kws):
    Logger.instance().info(message, *args, **kws)

def important(message, *args, **kws):
    Logger.instance().important(message, *args, **kws)

def warn(message, *args, **kws):
    Logger.instance().warning(message, *args, **kws)

def warning(message, *args, **kws):
    Logger.instance().warning(message, *args, **kws)

def error(message, *args, **kws):
    Logger.instance().error(message, *args, **kws)

def exception(message, *args, **kws):
    Logger.instance().exception(message, *args, **kws)

def fatal(message, *args, **kws):
    Logger.instance().critical(message, *args, **kws)

def critical(message, *args, **kws):
    Logger.instance().critical(message, *args, **kws)

def newLoopLogger():
    Logger.instance().newLoopLogger()

def delLoopLogger():
    Logger.instance().delLoopLogger()

def newIteration(*args, **kws):
    Logger.instance().newIteration(*args, **kws)

def setMinLevelToPrint(level):
    Logger.instance().setMinLevelToPrint(level)

def setMinLevelToSave(level):
    Logger.instance().setMinLevelToSave(level)

def setMinLevelToPrint(level):
    Logger.instance().setMinLevelToPrint(level)

def setMinLevelToPrint(level):
    Logger.instance().setMinLevelToPrint(level)
