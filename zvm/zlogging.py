#
# Logging assistance. This provides a logging facility for the rest of
# the Z-Machine. As a Z-Machine is inherently I/O intensive, dumb screen
# dumping is no longer adequate. This logging facility, based on
# python's logging module, provides file logging.
#

import logging

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s : %(message)s',
    filename = 'debug.log',
    filemode = 'w')

def log(msg):
    logging.debug(msg)
