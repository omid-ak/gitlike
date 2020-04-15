"""
-*- coding: utf-8 -*-
v1.0.2
gitlike project
copyright (c) 2020 GitLike, Omid Akhgary. all rights reserved.
licence: Gpl3
email: omid7798@gmail.com
"""

""" * Be Aware that This Module Should Be Run As Root Privileges.! """

# import system libs
import os
import socket
import sys
import logging
from threading import Thread

# import gitlike_server libs
from gitlike_server.users import User, User_Types
from gitlike_server.baseconf import Config, Group, Shell, Os_Type, Linux_Distro_Type
from gitlike_server.repositories import Repository
from gitlike_server._logging import Logger, Log_Type
from gitlike_server.main import handler

# import created instances from main 
from gitlike_server.main import  config, logger


__all__ = ["repositories", "_logging", "baseconf", "users", "main"]



__author__  = "omid akhgary <omid7798@gmail.com>"
__status__  = "Development"
__date__    = "09 Apr 2020"
__version__ = "1.0.2"
__license__ = "LGPLv3"





# check for root
if os.geteuid() != 0:
    print('Permission denied run only with root user')
    sys.exit(0)




def main():
    logger.main_logger(log_type=Log_Type.START, version=__version__)
    # Base config
    print('initializing...')
    if config.os_type is Os_Type.UNSUPPORTED:
        msg = "Unsupported Operation System .!"
        print(msg)
        logger.main_logger(Log_Type=Log_Type.START, log_msg=msg, level=logging.ERROR, version=__version__)
        sys.exit(1)

    if config.os_type is Os_Type.LINUX:
        if config.distro_type is Linux_Distro_Type.UNSUPPORTED:
            msg = f"Unsupported Linux Distribution {config.distro_type_detail}.!"
            print(msg)
            logger.main_logger(Log_Type=Log_Type.START, log_msg=msg, level=logging.ERROR, version=__version__)
            sys.exit(1)

    if config.os_type is Os_Type.FREE_BSD:
        msg = "GitLike Support for FreeBSD is Developing and will be release in next versions\nThank you for your patienece."
        print(msg)
        logger.main_logger(Log_Type=Log_Type.START, log_msg=msg, level=logging.INFO, version=__version__)
        sys.exit(0)

    print(f"{config.os_type.value} Operating System.")
    print(f"{config.distro_type_detail} Distribution.")
    config.company_name = input("Entenr Your Company Name: ")
    print('checking for dependencies...')

    # install dependencies
    if config.dependencies_installation_status is False:
        answer = input("You need to install some dependencies do you want to continues? [y/n]: ")
        if answer is "y" or answer is "Y":
            msg = "Dependencies Installed Successfully."
            config.install_dependencies()
            print(msg)
            logger.main_logger(Log_Type=Log_Type.START, log_msg=msg, version=__version__)

        elif answer is "n" or answer is "N":
            print("Operation aborted")
            logger.main_logger(Log_Type=Log_Type.START, log_msg="Dependencies Installation Operation Aborted.", version=__version__)
        else:
            print("Unknown!")
            sys.exit(0)
    else:
        logger.main_logger(log_type=Log_Type.START, log_msg="Dependencies Resolved.", version=__version__)
        print("Dependencies Resolved.")
    
    # connection
    
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.bind(('0.0.0.0', config.server_port))

    main_socket.listen()
    print("Waiting For connection...")

    try:
        while True:
            client, addr = main_socket.accept()
            thread = Thread(target=handler, args=(main_socket, client, addr))
            thread.setDaemon(True)
            thread.start()
    except OSError:
        print('closed')
