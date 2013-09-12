from alkivi.common import logger
import os
import tempfile

class Lock:

    """
        Class used to avoid running multiple instance of the same script
        A file is touch in /tmp, using filename of the script. Pid and other information are stored inside :)
    """

    def __init__(self):
        import sys
        import datetime
        self.initialized = False

        # Get infos
        self.fullPath   = os.path.realpath(sys.argv[0])
        self.scriptName = self.fullPath.split('/')[-1]
        self.pid        = os.getpid()
        #self.user       = os.getlogin()    #crash in cgi and cron
        self.user       = pwd.getpwuid(os.getuid()).pw_name
        self.startTime  = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Remove weird caracters
        self.scriptName = self.scriptName.replace("/", "-").replace(":", "").replace("\\", "-")

        # Define lock file
        self.baseName = self.scriptName + '.lock'

        # Make it in a temp dir
        self.lockFile = os.path.normpath(tempfile.gettempdir() + '/' + self.baseName)

        # If file exist warn
        if(os.path.exists(self.lockFile)):
            logger.warning("Another instance is already running, quitting.") # TODO add info
            self.readLockFile()
            sys.exit(-1)
        else:
            # Write info to file
            self.writeLockFile()

                
        logger.debug("Lock acquired : %s" % (self.lockFile))
        self.initialized = True

    def writeLockFile(self):
        import json
        self.f = open(self.lockFile, 'w')

        # Add extra
        self.f.write(json.dumps({'script':self.scriptName, 'path':self.fullPath, 'pid':self.pid, 'user':self.user, 'startTime':self.startTime, 'lockFile':self.lockFile}))
        self.f.close()

    def readLockFile(self):
        import json
        self.f = open(self.lockFile, 'r')
        rawData = self.f.read()
        jsonData = json.loads(rawData)
        for k, v in jsonData.iteritems():
            logger.log('%-10s: %s' % (k, v))

    def __del__(self):
        import sys
        import os
        if not self.initialized:
            return

        try:
            # Delete file
            if os.path.isfile(self.lockFile):
                os.unlink(self.lockFile)
                logger.debug("Lockfile %s released" % (self.lockFile))

        except Exception as e:
            logger.warning("Error during __del__ of lock", e)
            sys.exit(-1)
