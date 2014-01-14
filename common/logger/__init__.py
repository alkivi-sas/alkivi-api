"""Alkivi Logger used in scripts

Define a logger that can handle mail syslog file and other stuff
See the scripts in sample for better explanation
"""
import logging
import logging.handlers
import sys
import os
import pwd
import socket
import pprint

# Define our levels
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

# Globals used to send extra information using emails
SOURCE = sys.argv[0]
SOURCEDIR = os.path.realpath(SOURCE)
PID = os.getpid()
USER = pwd.getpwuid(os.getuid()).pw_name
HOST = socket.gethostname()


class AlkiviEmailHandler(logging.Handler):
    """Custom class that will handle email sending 
    
    When log level reach a certains level and receive flush :
    - flush the logger with the current message
    - send the full trace of the current logger (all level)
    """
    def __init__(self, mailhost, fromaddr, toaddrs, level):
        logging.Handler.__init__(self)
        self.mailhost = mailhost
        self.mailport = None
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.flush_level = level
        
        # Init another buffer which will store everything
        self.allbuffer = []

        # Buffer is an array that contains formatted messages
        self.buffer = []

    def emit(self, record):
        msg = self.format(record)

        if(record.levelno >= self.flush_level):
            self.buffer.append(msg)

        # Add to all buffer in any case
        self.allbuffer.append(msg)

    def generate_mail(self):
        """Generate the email as MIMEText
        """
        from email.mime.text import MIMEText

        # Script info
        msg = "Script info : \r\n"
        msg = msg + "%-9s: %s" % ('Script', SOURCE) + "\r\n"
        msg = msg + "%-9s: %s" % ('User', USER) + "\r\n"
        msg = msg + "%-9s: %s" % ('Host', HOST) + "\r\n"
        msg = msg + "%-9s: %s" % ('PID', PID) + "\r\n"

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

        real_msg = MIMEText(msg, _charset='utf-8')

        real_msg['Subject'] = self.buffer[0]
        real_msg['To']      = ','.join(self.toaddrs)
        real_msg['From']    = self.fromaddr

        return real_msg


    def flush(self):
        if len(self.buffer) > 0:
            try:
                import smtplib
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT

                smtp = smtplib.SMTP(self.mailhost, port)
                msg = self.generate_mail()

                smtp.sendmail(self.fromaddr, self.toaddrs, msg.__str__())
                smtp.quit()
            except Exception as exception:
                self.handleError(None)  # no particular record

        self.buffer    = []
        self.allbuffer = []

 
from alkivi.common import Singleton

@Singleton
class Logger():
    """
        This class defines a custom Logger class, that we will use for all alkivi script
        check /alkivi/samples/testLogger.py for more informations
    """
    def __init__(self, 
            min_log_level_to_print = INFO,
            min_log_level_to_mail = WARNING,
            min_log_level_to_save = INFO,
            min_log_level_to_syslog = WARNING,
            filename = None,
            emails = None,
            prefix = None,
            ):

        if filename is None:
            filename = '%s.log' % SOURCE

        if emails is None:
            emails = []

        self.subject = "%s_%i" % (SOURCE, PID)
        self.min_log_level_to_print = min_log_level_to_print
        self.min_log_level_to_save = min_log_level_to_save
        self.min_log_level_to_mail = min_log_level_to_mail
        self.min_log_level_to_syslog = min_log_level_to_syslog
        self.filename = filename
        self.emails = emails
        self.prefix = prefix
        

        self.current_logger = None
        self.loggers = []

        # Create object Dumper
        self.pretty_printer = pprint.PrettyPrinter(indent=4)

        # Create new_loop_logger, the rootOne
        self.new_loop_logger()


        

    def _log(self, priority, message, *args, **kws):
        """Generic log functions
        """
        for arg in args:
            message = message + "\n" + self.pretty_printer.pformat(arg)

        self.current_logger.log(priority, message, (), **kws)

    def debug_debug(self, message, *args, **kws):
        """Lowest level of logging, use for low leel
        """
        self._log(DEBUG_DEBUG, message, *args, **kws)

    def debug(self, message, *args, **kws):
        """Debug level to use and abuse when coding
        """
        self._log(DEBUG, message, *args, **kws)

    def log(self, message, *args, **kws):
        """Log level still not used by default, use for more debug info
        """
        self._log(LOG, message, *args, **kws)

    def info(self, message, *args, **kws):
        """More important level : default for print and save
        """
        self._log(INFO, message, *args, **kws)

    def important(self, message, *args, **kws):
        """A bit more important
        """
        self._log(IMPORTANT, message, *args, **kws)

    def warn(self, message, *args, **kws):
        """Send email and syslog by default ...
        """
        self._log(WARNING, message, *args, **kws)

    def warning(self, message, *args, **kws):
        """Alias to warn
        """
        self._log(WARNING, message, *args, **kws)

    def error(self, message, *args, **kws):
        """Should not happen ...
        """
        self._log(ERROR, message, *args, **kws)

    def fatal(self, message, *args, **kws):
        """Same as critical
        """
        self._log(CRITICAL, message, *args, **kws)

    def critical(self, message, *args, **kws):
        """Highest level
        """
        self._log(CRITICAL, message, *args, **kws)

    def log_exception(self, message, *args, **kws):
        """Handle expcetion
        """
        self.current_logger.log_exception(message, *args, **kws)


    def new_loop_logger(self):
        """Create a secondary logger, used in loops with a customer prefix
        """
        # Do we have already a logger ?
        new_logger = LoggerIteration(
            subject = "%s_%i" % (self.subject, len(self.loggers)),
            min_log_level_to_print = self.min_log_level_to_print,
            min_log_level_to_save = self.min_log_level_to_save,
            min_log_level_to_mail = self.min_log_level_to_mail,
            min_log_level_to_syslog = self.min_log_level_to_syslog,
            filename = self.filename,
            emails = self.emails,
            current_logger = self.current_logger
        )

        self.loggers.append(new_logger)
        self.current_logger = self.loggers[-1]

    def del_loop_logger(self):
        """Delete the loop previsouly created and continues
        """
        # Flush data (i.e send email if needed)
        self.current_logger.flush()
        self.current_logger.disable() # Disable current logger

        # Only if more than one logger
        if len(self.loggers) > 1 :
            self.loggers.pop()
            self.current_logger = self.loggers[-1]
            self.current_logger.enable() # Was previously disabled

    def new_iteration(self, *args, **kwargs):
        """When inside a loop logger, created a new iteration
        """
        # Flush data (i.e send email if needed)
        self.current_logger.flush()
        self.current_logger.set_prefix(*args, **kwargs)

    def set_prefix(self, *args, **kwargs):
        """Set prefix used on the logger (static text always present)
        """
        self.current_logger.set_prefix(*args, **kwargs)

    def set_min_level_to_print(self, level):
        """Allow to change print level after creation
        """
        self.min_log_level_to_print = level
        self.current_logger.set_min_level_to_print(level)

    def set_min_level_to_save(self, level):
        """Allow to change save level after creation
        """
        self.min_log_level_to_save = level
        self.current_logger.set_min_level_to_save(level)

    def set_min_level_to_mail(self, level):
        """Allow to change mail level after creation
        """
        self.min_log_level_to_mail = level
        self.current_logger.set_min_level_to_mail(level)

    def set_min_level_to_syslog(self, level):
        """Allow to change syslog level after creation
        """
        self.min_log_level_to_syslog = level
        self.current_logger.set_min_level_to_syslog(level)


class LoggerIteration():
    """
        This class defines a custom Logger iteration. Logger class will use those iteration :)
        check /alkivi/samples/testLogger.py for more informations
    """


    def __init__(self, 
            subject = None,
            min_log_level_to_print = INFO,
            min_log_level_to_mail = WARNING,
            min_log_level_to_save = INFO,
            min_log_level_to_syslog = WARNING,
            filename = None,
            emails = None,
            current_logger = None,
            ):

        if subject is None:
            subject = SOURCE
        if filename is None:
            filename = '%s.log' % SOURCE
        if emails is None:
            emails = []

        # Create logger
        self.logger = logging.getLogger(subject)
        self.logger.setLevel(0)

        # Store data
        self.emails = emails
        self.filename = filename
        self.subject = subject

        # Empty handler by default
        self.handlers = []
        self.buffer_handler = None
        self.console_handler = None
        self.file_handler = None
        self.email_handler = None
        self.syslog_handler = None
        self.min_log_level_to_print = min_log_level_to_print
        self.min_log_level_to_save = min_log_level_to_save
        self.min_log_level_to_mail = min_log_level_to_mail
        self.min_log_level_to_syslog = min_log_level_to_syslog

        # Define prefixes : add old logger prefix if present
        if current_logger is None:
            self.b_prefix = []
        else:
            self.b_prefix = current_logger.b_prefix + current_logger.prefixes
            current_logger.disable() # Needed not to print duplicate

        self.prefixes     = []
        
        # Create formatter
        self.formatter = None
        self.syslog_formatter = None
        self.set_formatter()

        # Auto declare handler
        self._set_stream_handler()
        self._set_syslog_handler()
        self._set_file_handler()
        self._set_email_handler()

        # Set logger handlers
        self.enable()

    def set_min_level_to_print(self, level):
        """Set the level to start printing log
        """
        self.min_log_level_to_print = level

        if self.console_handler and level:
            self.console_handler.setLevel(level)
        elif level:
            self._set_stream_handler()
        else:
            self._delete_stream_handler()

    def _set_stream_handler(self):
        """Create the handler responsible to print log (console_handler)
        """
        if self.min_log_level_to_print:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(self.min_log_level_to_print)
            self.console_handler.setFormatter(
                self.get_formatter(self.console_handler))
            self.logger.addHandler(self.console_handler)
            self.handlers.append(self.console_handler)

    def _delete_stream_handler(self):
        """Delete a previously created console_handler
        """
        if self.console_handler:
            for handler in self.handlers:
                if handler == self.console_handler:
                    self.logger.removeHandler(handler)
            self.console_handler = None

    def set_min_level_to_syslog(self, level):
        """Set the level to start sending syslog logs
        """
        self.min_log_level_to_syslog = level

        if self.syslog_handler and level:
            self.syslog_handler.setLevel(level)
        elif level:
            self._set_syslog_handler()
        else:
            self._delete_syslog_handler()

    def _set_syslog_handler(self):
        """Create the handler responsible to send syslog
        """
        if self.min_log_level_to_syslog:
            self.syslog_handler = logging.handlers.SysLogHandler(
                address='/dev/log')
            self.syslog_handler.setLevel(self.min_log_level_to_syslog)
            self.syslog_handler.setFormatter(
                self.get_formatter(self.syslog_handler))
            self.logger.addHandler(self.syslog_handler)
            self.handlers.append(self.syslog_handler)

    def _delete_syslog_handler(self):
        """Delete a previously created syslog_handler
        """
        if self.syslog_handler:
            for handler in self.handlers:
                if handler == self.syslog_handler:
                    self.logger.removeHandler(handler)
            self.syslog_handler = None

    def _set_min_level_to_save(self, level):
        """Set the level to start saving log to files
        """
        self.min_log_level_to_save = level

        if self.file_handler and level:
            self.file_handler.setLevel(level)
        elif level:
            self._set_file_handler()
        else:
            self._delete_file_handler()

    def _set_file_handler(self):
        """Create the handler responsible to save logs
        """
        if self.min_log_level_to_save:
            self.file_handler = logging.handlers.TimedRotatingFileHandler(
                self.filename, 
                when='midnight')
            self.file_handler.setLevel(self.min_log_level_to_save)
            self.file_handler.setFormatter(
                self.get_formatter(self.file_handler))
            self.logger.addHandler(self.file_handler)
            self.handlers.append(self.file_handler)

    def _delete_file_handler(self):
        """Delete a previously created file_handler
        """
        if self.file_handler:
            for handler in self.handlers:
                if handler == self.file_handler:
                    self.logger.removeHandler(handler)
            self.file_handler = None

    def set_min_level_to_mail(self, level):
        """Set the level to start emailing log
        """
        self.min_log_level_to_mail = level

        if self.email_handler and level:
            self.email_handler.setLevel(level)
        elif level:
            self._set_email_handler()
        else:
            self._delete_email_handler()

    def _set_email_handler(self):
        """Create the handler responsible to email logs
        """
        if self.min_log_level_to_mail and self.emails:
            self.email_handler = AlkiviEmailHandler(
                mailhost='127.0.0.1', 
                fromaddr="%s@%s" % (USER, HOST), 
                toaddrs=self.emails, 
                level=self.min_log_level_to_mail)
            # Needed, we want all log to go thought this
            self.email_handler.setLevel(NOTSET)
            self.email_handler.setFormatter(
                self.get_formatter(self.email_handler))
            self.logger.addHandler(self.email_handler)
            self.handlers.append(self.email_handler)

    def _delete_email_handler(self):
        """Delete a previously create email_handler
        """
        if self.email_handler:
            for handler in self.handlers:
                if handler == self.email_handler:
                    self.logger.removeHandler(handler)
            self.email_handler = None




    def log(self, priority, message, *args, **kws):
        """Main log function
        """
        self.logger._log(priority, message, (),  **kws)

    def log_exception(self, message, *args, **kws):
        """Special case for exception
        """
        self.logger.exception(message, *args, **kws)


    def set_formatter(self):
        """Generate formater according to the prefix used
        """
        formatter = '[%(asctime)s] [%(levelname)-9s]'
        syslog = '[%(levelname)-9s]'

        for prefix in self.b_prefix:
            if(prefix):
                formatter += ' [%s]' % (prefix)
                syslog += ' [%s]' % (prefix)

        for prefix in self.prefixes:
            if(prefix):
                formatter += ' [%s]' % (prefix)
                syslog += ' [%s]' % (prefix)

        formatter = formatter + ' %(message)s'
        syslog = syslog + ' %(message)s'
        syslog = '%s: %s' % (SOURCE, syslog)

        self.formatter = logging.Formatter(formatter)
        self.syslog_formatter = logging.Formatter(syslog)

    def get_formatter(self, handler):
        """Return logger formatter according to his class
        """
        if(handler.__class__.__name__ == 'SysLogHandler'):
            return self.syslog_formatter
        else:
            return self.formatter


    def _set_handlers(self):
        """Helpers to _set_handlers on all loggers
        """
        for handler in self.handlers:
            handler.setFormatter(self.get_formatter(handler))

    def enable(self):
        """Globally enable an iteration
        """
        for handler in self.handlers:
            self.logger.addHandler(handler)

    def disable(self):
        """Globally disable an iteration
        """
        for handler in self.handlers:
            self.logger.removeHandler(handler)

    def set_prefix(self, prefix):
        """Allow to change prefix after logger creation
        """
        if(len(self.prefixes)>0):
            self.prefixes[-1] = prefix
        else:
            self.prefixes.append(prefix)

        self.set_formatter()
        self._set_handlers()

    def flush(self):
        """Override flush
        """
        # Flush all buffer ? just email ?
        if(self.email_handler != None):
            self.email_handler.flush()


#
# Define global functions that can be use using logger.log directly in code :)
#
def debug_debug(message, *args, **kws):
    """Lowest level of logging, use for low leel
    """
    Logger.instance().debug_debug(message, *args, **kws)

def debug(message, *args, **kws):
    """Debug level to use and abuse when coding
    """
    Logger.instance().debug(message, *args, **kws)

def log(message, *args, **kws):
    """Log level still not used by default, use for more debug info
    """
    Logger.instance().log(message, *args, **kws)

def info(message, *args, **kws):
    """More important level : default for print and save
    """
    Logger.instance().info(message, *args, **kws)

def important(message, *args, **kws):
    """A bit more important
    """
    Logger.instance().important(message, *args, **kws)

def warn(message, *args, **kws):
    """Send email and syslog by default ...
    """
    Logger.instance().warning(message, *args, **kws)

def warning(message, *args, **kws):
    """Alias to warn
    """
    Logger.instance().warning(message, *args, **kws)

def error(message, *args, **kws):
    """Should not happen ...
    """
    Logger.instance().error(message, *args, **kws)

def log_exception(message, *args, **kws):
    """Handle expcetion
    """
    Logger.instance().log_exception(message, *args, **kws)

def fatal(message, *args, **kws):
    """Same as critical
    """
    Logger.instance().critical(message, *args, **kws)

def critical(message, *args, **kws):
    """Highest level
    """
    Logger.instance().critical(message, *args, **kws)

def new_loop_logger():
    """Create a secondary logger, used in loops with a customer prefix
    """
    Logger.instance().new_loop_logger()

def del_loop_logger():
    """Delete the loop previsouly created and continues
    """
    Logger.instance().del_loop_logger()

def set_prefix(*args, **kws):
    """Set prefix used on the logger (static text always present)
    """
    Logger.instance().set_prefix(*args, **kws)

def new_iteration(*args, **kws):
    """When inside a loop logger, created a new iteration
    """
    Logger.instance().new_iteration(*args, **kws)

def set_min_level_to_print(level):
    """Allow to change print level after creation
    """
    Logger.instance().set_min_level_to_print(level)

def set_min_level_to_save(level):
    """Allow to change save print level after creation
    """
    Logger.instance().set_min_level_to_save(level)

def set_min_level_to_mail(level):
    """Allow to change save print mail after creation
    """
    Logger.instance().set_min_level_to_mail(level)

def set_min_level_to_syslog(level):
    """Allow to change save print syslog after creation
    """
    Logger.instance().set_min_level_to_syslog(level)
