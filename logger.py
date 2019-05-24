# -*- coding: utf-8 -*-

import logging
import settings


class _Commmon_filter(logging.Filter):
    """ Class added additional records to logger formatter """
    def filter(self, record):
        record.component = LoggerOptions._COMPONENT
        return True


class LoggerOptions:
    """ Class to set up logger options """
    _COMPONENT = "Dispatcher"
    _PREVIOUS_COMPONENT = ""

    @staticmethod
    def set_component(arg):
        line_width = 12
        length = len(arg)
        if length > line_width:
            arg = arg[:line_width]
        elif length < line_width:
            nuls = line_width - length
            nuls_before = nuls // 2
            nuls_after = nuls_before + (nuls % 2)
            arg = " " * nuls_before + arg + " " * nuls_after
        LoggerOptions._PREVIOUS_COMPONENT = LoggerOptions._COMPONENT
        LoggerOptions._COMPONENT = arg

    @staticmethod
    def switchback_component():
        LoggerOptions._COMPONENT = LoggerOptions._PREVIOUS_COMPONENT

    @staticmethod
    def logger():
        """ Function setting options and return logger object """
        logger = logging.getLogger("Automation_Dispatcher")
        logger.setLevel(settings.LOGLEVEL)
        handler = logging.StreamHandler()
        logger.addFilter(_Commmon_filter())
        handler.setFormatter(logging.Formatter('%(asctime)s [%(component)s]'
                                               ' [%(levelname)s] %(message)s', "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        return logger


STREAM = LoggerOptions.logger()

# Some examples.
# STREAM.debug("this is a debugging message")
# STREAM.info("this is an informational message")
# STREAM.notice("this is an informational message")
# STREAM.success("this is an informational message")
# STREAM.warning("this is a warning message")
# STREAM.error("this is an error message")
# STREAM.critical("this is a critical message")
