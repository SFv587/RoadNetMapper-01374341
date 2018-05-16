#-*- coding:utf-8 -*-
import pymysql
import pandas as pd
from sqlalchemy import create_engine

class DataBase(object):
    def __init__(self,**kwargs):
        self.name=None
        self.conn=None
        if kwargs.has_key("name"):
            self.name=kwargs["name"]
            self.conn=self._getConnection()

    def _getConnection(self):
        if self.name is None:
            print "Database name has not set yet!"
            raise ValueError
        else:
            if self.conn is None:
                self.CreateConnect()
            return self.conn

    def CreateConnect(self):
        pass

    def QureyTable(self,sql):
        try:
            DF=pd.read_sql(sql,self.conn)
            return DF
        except Exception,e:
            print e.message

    def InsertTable(self,Table,dataframe):
        try:
            cur=self.conn.cursor()
            pass
        except Exception,e:
            print e.message

    def UpdateTable(self,sql):
        try:
            cur=self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
        except Exception,e:
            print e.message

class MySQLdatabse(DataBase):
    def __init__(self,**kwargs):
        self.name=None
        self.conn=None
        self.engine=None
        if kwargs.has_key("name"):
            self.name=kwargs["name"]
            self.conn=self._getConnection()
            self.engine=self._getEngine()

    def _getEngine(self):
        if self.name is None:
            print "Database name has not set yet!"
            raise ValueError
        else:
            if self.engine is None:
                self.CreateEngine()
            return self.engine

    def CreateEngine(self):
        db_info = {'user': 'root',
                   'password': '12345678',
                   'host': 'localhost',
                   'database': self.name
                   }
        self.engine=create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info,encoding='utf-8')

    def CreateConnect(self):
        host="localhost"
        user="root"
        password="12345678"
        db=self.name
        port=3306
        charset="utf8"
        self.conn=pymysql.connect(host=host,user=user,password=password,port=port,database=db,charset=charset)




