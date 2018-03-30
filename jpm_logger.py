import logging
import inspect

__author__ = "James Paul Mason"
__contact__ = "jmason86@gmail.com"


class JpmLogger:
    def __init__(self, console=True, path='./', filename='log'):
        """Log to disk and optionally console with ISO timestamp, script name, severity level, and message.

        Inputs:
            None.

        Optional Inputs:
            console [bool]:    Set this to output to console in addition to disk. Default is True.
            path [string]:     Set this to the path for the log file. Default is the current directory.
            filename [string]: Set this to the name for the output log file. Default is 'log.log'.

        Outputs:
            Generates a log file.

        Optional Outputs:
            Will also print messages to console if the console optional input is true.

        Example:
            logger = JpmLogger()
        """

        # Set up the logger
        logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
        self.rootLogger = logging.getLogger()
        self.rootLogger.setLevel(logging.NOTSET)

        # Set up the file part of the logger
        fileHandler = logging.FileHandler("{0}/{1}.log".format(path, filename))
        fileHandler.setFormatter(logFormatter)
        self.rootLogger.addHandler(fileHandler)

        # Set up the console part of the logger
        if console:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            self.rootLogger.addHandler(consoleHandler)

    def critical(self, message):
        """Generate critical message in log.

        Inputs:
            message [string]: The message to add to the log.

        Optional Inputs:
            None.

        Outputs:
            Message in log.

        Optional Outputs:
            None.

        Example:
            logger = JpmLogger()
            logger.critical('You done screwed up.')
        """

        calling_function = inspect.currentframe().f_back.f_code.co_name
        self.rootLogger.critical('[' + calling_function + '] ' + message)

    def error(self, message):
        """Generate error message in log.

        Inputs:
            message [string]: The message to add to the log.

        Optional Inputs:
            None.

        Outputs:
            Message in log.

        Optional Outputs:
            None.

        Example:
            logger = JpmLogger()
            logger.error('I got stuck =(')
        """

        calling_function = inspect.currentframe().f_back.f_code.co_name
        self.rootLogger.error('[' + calling_function + '] ' + message)

    def warning(self, message):
        """Generate warning message in log.

        Inputs:
            message [string]: The message to add to the log.

        Optional Inputs:
            None.

        Outputs:
            Message in log.

        Optional Outputs:
            None.

        Example:
            logger = JpmLogger()
            logger.critical('You might not want to do this.')
        """

        calling_function = inspect.currentframe().f_back.f_code.co_name
        self.rootLogger.warning('[' + calling_function + '] ' + message)

    def info(self, message):
        """Generate info message in log.

        Inputs:
            message [string]: The message to add to the log.

        Optional Inputs:
            None.

        Outputs:
            Message in log.

        Optional Outputs:
            None.

        Example:
            logger = JpmLogger()
            logger.info('I am doing a thing here.')
        """
        calling_function = inspect.currentframe().f_back.f_code.co_name
        self.rootLogger.info('[' + calling_function + '] ' + message)

    def debug(self, message):
        """Generate debug message in log.

        Inputs:
            message [string]: The message to add to the log.

        Optional Inputs:
            None.

        Outputs:
            Message in log.

        Optional Outputs:
            None.

        Example:
            logger = JpmLogger()
            logger.debug('This is a spot warranting some immediate attention.')
        """

        calling_function = inspect.currentframe().f_back.f_code.co_name
        self.rootLogger.debug('[' + calling_function + '] ' + message)
