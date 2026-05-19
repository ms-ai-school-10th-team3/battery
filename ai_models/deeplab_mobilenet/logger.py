import os, logging
from logging.handlers import TimedRotatingFileHandler

class LoggerHelper:
    logger = None
    curr_dirname    = os.path.dirname(os.path.realpath(__file__))
    # os.chdir(curr_dirname) # Set working directory

    @staticmethod
    def create(
        level=10,
        filename="logs/eventlog.log",
        when="midnight",
        interval=1,
        backup_count=5,
        # formatter="%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s",
        formatter="%(asctime)s\t%(levelname)s\t%(message)s",
        suffix="%Y%m%d"
        ):

        # set up logger
        LoggerHelper.logger = logging.getLogger("scalawox.aihub.evaluator.logger")
        LoggerHelper.logger.setLevel(level)
        logger_dirname = os.path.dirname(filename)
        if not os.path.exists(logger_dirname):
            os.makedirs(logger_dirname)
        
        handler = TimedRotatingFileHandler(filename, when, interval, backup_count)
        handler.setFormatter(logging.Formatter(formatter))
        handler.suffix = suffix
        LoggerHelper.logger.addHandler(handler)

    
    @staticmethod
    def getLogger(filename=None):
        if not LoggerHelper.logger:
            if filename and len(filename):
                LoggerHelper.create(level=10, filename=filename)
            else:
                LoggerHelper.create(level=10)
        return LoggerHelper.logger
