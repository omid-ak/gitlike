"""
v1.0.2
GitLike Project
Copyleft (C) 2020 GitLike. All Rights Reserved.
Licence: GPL3
Email: omid7798@gmail.com
"""

"""
This module is log handler of whole  GitLike Project.
all logs store in GitLike_log.db :
tables:
start: logs of starting GitLike logging.
connection_received: logs of received connections
received_data: logs of received data
sent_data: logs of sent data
runtime_actions: logs of actions while GitLike is Running

**Data base GitLike_log.db will be store in log_DB Directory**

"""

__author__ = "omid <omid7798@gmail.com>"



import os
from getpass import getuser
import logging
from enum import Enum
import sqlite3
import threading
from datetime import datetime

class Log_Type(Enum):
    START               = "start"
    CONNECTION_RECEIVED = "connection_received"
    RECEIVED_DATA       = "received_data"
    SENT_DATA           = "sent_data"
    RUNTIME_ACTIONS     = "runtime_actions"

class Logger():

    def __init__(self):
        self.connection             = None
        self.cursor                 = None
        self.log_type               = None
        self.action_                = None
        self.stage                  = None
        self.ip                     = None
        self.port                   = None
        self.username               = None
        self.level_number           = None
        self.level_name             = None
        self.log_data               = None
        self.log_message            = None
        self.now_tostring           = None
        self.current_thread_name    = None
        self.user_                  = getuser()
        self.init_DB()

    def create_DB_connection(self):
        basedir = os.path.abspath((os.path.dirname(__file__)))
        DB_PATH = f"{os.path.join(basedir, 'log_DB')}"
        if os.path.exists(DB_PATH) is False:
            os.mkdir(DB_PATH)
        self.connection = sqlite3.connect(os.path.join(DB_PATH, 'GitLike_log.db'), check_same_thread=False)
        self.cursor     = self.connection.cursor()

    def calc_now_tostring(self):
        """ calc now to string """
        self.now_tostring = str(datetime.now())

    def calc_current_thread_name(self):
        """calculate current thread name"""
        self.current_thread_name = threading.current_thread().getName()

    def init_DB(self):

        """
        Tables Format:
        start:
        id|datetime|level_name|user|thread_name|message|
        connection_received:
        id|datetime|level_name|user|thread_name|ip|port|stage|message|
        received_data:
        id|datetime|level_name|user|thread_name|ip|port|stage|received_data|message|
        sent_data:
        id|datetime|level_name|user|thread_name|ip|port|stage|sent_data|message|
        runtime_actions:
        id|datetime|level_name|user|thread_name|ip|port|username|stage|action_|message
        """

        start_table                 = """CREATE TABLE IF NOT EXISTS start (
                                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                        date_time   VARCHAR (50),
                                        level_name  VARCHAR (20),
                                        user_       VARCHAR (50),
                                        thread_name VARCHAR (50),
                                        message     VARCHAR (1000)
                                                                            )"""

        connection_received_table   = """CREATE TABLE IF NOT EXISTS connection_received (
                                          id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                          date_time   VARCHAR (50),
                                          level_name  VARCHAR (20),
                                          user_       VARCHAR (50),
                                          thread_name VARCHAR (50),
                                          ip          VARCHAR (16),
                                          port        VARCHAR (10),
                                          stage       VARCHAR (50),
                                          message     VARCHAR (10000)
                                                                                          )"""

        received_data_table         = """CREATE TABLE IF NOT EXISTS received_data (
                                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                        date_time       VARCHAR (50),
                                        level_name      VARCHAR (20),
                                        user_           VARCHAR (50),
                                        thread_name     VARCHAR (50),
                                        ip              VARCHAR (16),
                                        port            VARCHAR (10),
                                        stage           VARCHAR (50),
                                        received_data   VARCHAR (1000),
                                        message         VARCHAR (1000)
                                                                                            )"""

        sent_data_table             = """CREATE TABLE IF NOT EXISTS sent_data (
                                        id              integer primary key autoincrement,
                                        date_time       varchar (50),
                                        level_name      varchar (20),
                                        user_           varchar (50),
                                        thread_name     varchar (50),
                                        ip              varchar (16),
                                        port            varchar (10),
                                        stage           varchar (50),
                                        sent_data       varchar (1000),
                                        message         varchar (1000)
                                                                                            )"""

        runtime_actions_table       = """CREATE TABLE IF NOT EXISTS runtime_actions (
                                        id              integer primary key autoincrement,
                                        date_time       varchar (50),
                                        level_name      varchar (20),
                                        user_           varchar (50),
                                        thread_name     varchar (50),
                                        ip              varchar (16),
                                        port            varchar (10),
                                        username        VARCHAR (50),
                                        stage           VARCHAR (50),
                                        action_         varchar (200),
                                        message         varchar (1000)
                                                                                            )"""

        self.create_DB_connection()
        self.cursor.execute(start_table)
        self.cursor.execute(connection_received_table)
        self.cursor.execute(received_data_table)
        self.cursor.execute(sent_data_table)
        self.cursor.execute(runtime_actions_table)
        self.connection.commit()
        self.connection.close()

    def insert_into_log_table(self, **kwargs):

        """ insert logs into appropriate table """

        self.calc_current_thread_name()
        self.calc_now_tostring()

        global query_

        if self.log_type is Log_Type.START:
            query_ = f"""INSERT INTO start (date_time, level_name, user_, thread_name, message)
                                VALUES ('{str(self.now_tostring)}', 
                                        '{str(self.level_name)}', 
                                        '{str(self.user_)}', 
                                        '{str(self.current_thread_name)}',
                                        '{str(self.log_message)}')"""

        elif self.log_type is Log_Type.CONNECTION_RECEIVED:
            query_ = f"""INSERT INTO connection_received (date_time,level_name,user_,thread_name,ip,port,stage,message)
                                VALUES ('{str(self.now_tostring)}', 
                                        '{str(self.level_name)}', 
                                        '{str(self.user_)}', 
                                        '{str(self.current_thread_name)}',
                                        '{str(self.ip)}',
                                        '{str(self.port)}',
                                        '{str(self.stage)}',
                                        '{str(self.log_message)}')"""

        elif self.log_type is Log_Type.RECEIVED_DATA:
            query_ = f"""INSERT INTO received_data (date_time,level_name,user_,thread_name,ip,port,stage,received_data ,message)
                                VALUES ('{str(self.now_tostring)}', 
                                        '{str(self.level_name)}',
                                        '{str(self.user_)}',
                                        '{str(self.current_thread_name)}',
                                        '{str(self.ip)}',
                                        '{str(self.port)}',
                                        '{str(self.stage)}',
                                        '{str(self.log_data)}',
                                        '{str(self.log_message)}')"""

        elif self.log_type is Log_Type.SENT_DATA:
            query_ = f"""INSERT INTO  sent_data (date_time,level_name,user_,thread_name,ip,port,stage,sent_data,message)
                                VALUES ('{str(self.now_tostring)}', 
                                        '{str(self.level_name)}',
                                        '{str(self.user_)}', 
                                        '{str(self.current_thread_name)}',
                                        '{str(self.ip)}',
                                        '{str(self.port)}',
                                        '{str(self.stage)}',
                                        '{str(self.log_data)}',
                                        '{str(self.log_message)}')"""

        elif self.log_type is Log_Type.RUNTIME_ACTIONS:
            query_ = f"""INSERT INTO  runtime_actions (date_time,level_name,user_,thread_name,ip,port,username,stage,action_,message)
                                VALUES ('{str(self.now_tostring)}', 
                                        '{str(self.level_name)}',
                                        '{str(self.user_)}', 
                                        '{str(self.current_thread_name)}',
                                        '{str(self.ip)}',
                                        '{str(self.port)}',
                                        '{str(self.username)}',
                                        '{str(self.stage)}',
                                        '{str(self.action_)}',
                                        '{str(self.log_message)}')"""

        self.create_DB_connection()
        self.cursor.execute(query_)
        self.connection.commit()
        self.connection.close()

    def main_logger(self, **kwargs):

        """ main method to deal with main controller """

        self.log_type = kwargs.get('log_type', None)   # log type enum
        self.ip = kwargs.get("ip", None)
        self.port = kwargs.get("port", None)
        self.action_ = kwargs.get("action", None)
        self.stage = kwargs.get('stage', None)
        l_d = str(kwargs.get("data", None))
        if l_d is not None:
            self.log_data = l_d.replace('\'', '`')
        self.level_number = kwargs.get("level", logging.INFO)
        if self.level_number is None:
            self.level_number = logging.INFO
        self.level_name = logging.getLevelName(self.level_number)

        if self.log_type is Log_Type.START:
            self.log_message = str(kwargs.get('log_msg', "GitLike started")).replace('\'', '`')
        elif self.log_type is Log_Type.CONNECTION_RECEIVED:
            self.log_message = str(kwargs.get('log_msg', f"connection received from {self.ip}:{self.port}")).replace('\'', '`')
        elif self.log_type is Log_Type.RECEIVED_DATA:
            self.log_message = str(kwargs.get('log_msg', f"from {self.ip}:{self.port} received {self.log_data}")).replace('\'', '`')
        elif self.log_type is Log_Type.SENT_DATA:
            self.log_message = str(kwargs.get('log_msg', f"data sent {self.log_data} to {self.ip}:{self.port}")).replace('\'', '`')
        elif self.log_type is Log_Type.RUNTIME_ACTIONS:
            self.username       = kwargs.get("username", None)
            self.log_message    = str(kwargs.get("log_msg", None)).replace('\'', '`')

        self.insert_into_log_table()
