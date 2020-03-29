#!/usr/bin/env python3

import socket
import os
import sys
import json
import logging

def createlogger(currdir,silentmode):
    logger = logging.getLogger('backup')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(filename=f"{currdir}/backup.log",mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(handler)  

    if (not silentmode):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logger.addHandler(handler)    

    return logger

def backup(config,logger):    
    os.system(f"/bin/mount -t nfs {config['sharedrive']} {config['mountpoint']}")
    for folder in config['folders']:
        logger.info(f"backing up {folder['name']}")
        destdir = os.path.join(config['mountpoint'].rstrip('/'), folder['dest'].rstrip('/').lstrip('/'))
        if (not os.path.exists(destdir)):
            os.system(f"mkdir -p {destdir}")    
        os.system(f"rsync -azc --delete {folder['source']} {destdir}")
    os.system(f"/bin/umount {config['mountpoint']}")
    

def notify(currdir,config,logger):
    os.system(f"mailx -a 'From: {socket.gethostname()} Backup <{config['mailsender']}>' -s 'Backup | Success | {socket.gethostname()}' {config['mailreciver']} < {currdir}/backup.log")


def main(argv):
    silentmode = False

    for arg in argv:
        if (arg == "silent"):
            silentmode = True

    currdir = os.path.dirname(__file__)
    if (currdir == ""):
        currdir = "."

    logger = createlogger(currdir=currdir,silentmode=silentmode)
    try:
        logger.info('##########################################')
        logger.info('# easy rsync backup started...                      ')
        logger.info('')

        config_json = open(f"{currdir}/config.json")
        config = json.load(config_json)
        backup(config=config,logger=logger)

        logger.info('')        
        logger.info('# backup end...')
        logger.info('##########################################')

        notify(currdir=currdir,config=config,logger=logger)

    except OSError as err:
        logger.exception("OS error: {0}".format(err))    
    except:
        logger.exception("Unexpected error:", sys.exc_info()[0])


if __name__ == '__main__':
    main(sys.argv[1:])
