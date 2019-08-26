# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 18:56:03 2019

@author: solis
"""
import logging

LOGFILE = 'aemetDev.log'

if __name__ == "__main__":

    try:
        from datetime import datetime
        from time import time
        from aemetDev import menuMain

        logger = logging.getLogger('aemetDev')
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(LOGFILE, mode='w')
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

        now = datetime.now()

        startTime = time()

        menuMain()

        xtime = time() - startTime

    except ValueError as  err:
        logging.error("ValueError inesparado", exc_info=True)
    except Exception as err:
        logging.error("Error inesparado", exc_info=True)
    finally:
        # print('El script tardó {0}'.format(str(timedelta(seconds=xtime))))
        print('\nFin')
