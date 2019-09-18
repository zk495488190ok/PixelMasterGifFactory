# -*- coding: utf-8 -*-

import sqlite3
import threading
import os

class sqldb:

    __conn = None
    __cursor = None
    _instance_lock = threading.Lock()


    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(sqldb, "_instance"):
            with sqldb._instance_lock:
                if not hasattr(sqldb, "_instance"):
                    sqldb._instance = object.__new__(cls)
                    sql_path = os.path.abspath('../../db.sqlite3')
                    sqldb._instance.__conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
                    sqldb._instance.__cursor = sqldb._instance.__conn.cursor()
                    print('数据库连接成功')
                    #sqldb._instance.createTables()
        return sqldb._instance

    '''
    初始化数据库
    '''
    def createTables(self):

        print('---- 创建数据库表 Start----')


        self.__cursor = self.__conn.cursor()
        t_uinfo = '''create table if not exists t_uinfo(\'id\' INTEGER PRIMARY KEY AUTOINCREMENT,\'openid\' TEXT,\'nickName\' TEXT,\'icon\' TEXT,\'hot\' INTEGER DEFAULT 0)''';
        self.__cursor.execute(t_uinfo)
        print('创建用户信息表')



        t_func_hot = """CREATE
                        TABLE
                        if not exists 
                        t_func_hot
                        (
                            id int PRIMARY KEY,
                            openid TEXT,
                            func_id int,
                            func_use_count int
                        )"""
        self.__cursor.execute(t_func_hot)
        print('创建功能使用热度表')


        print('---- 创建数据库表 End----')

        self.__conn.commit()
        pass

    def getUsers(self):
        query_sql_str = 'select t_uinfo.*,hot.func_id,hot.func_use_count from t_uinfo left join t_func_hot as hot on t_uinfo.openid = hot.openid'
        self.__cursor.execute(query_sql_str)
        res = self.__cursor.fetchall()
        ret_arr = []
        for item in res:
            ret_arr.append({'id':item[0],'openid':item[1],'name':item[2],'icon':item[3],'func_id':item[5],'func_use_count':item[6]})
        return ret_arr


    '''
    记录用户登录信息
    '''
    def recoredLoginInfo(self,openid,nickname,icon):

        query_sql_str = 'select openid from t_uinfo where openid = :p_openid'
        self.__cursor.execute(query_sql_str,{'p_openid':openid})
        res = self.__cursor.fetchall()
        if len(res) > 0 :
            #udpate
            upd_sql_str = 'update t_uinfo set nickName = :p_nickname,icon = :p_icon where openid = :p_openid'
            self.__cursor.execute(upd_sql_str, {'p_nickname': nickname, 'p_icon': icon,'p_openid': openid})
            self.__conn.commit()
        else:
            #insert
            sqlstr = 'insert into t_uinfo (openid,nickName,icon) values (:p_openid,:p_nickName,:p_icon)'
            self.__cursor.execute(sqlstr, {'p_openid': openid, 'p_nickName': nickname, 'p_icon': icon})
            self.__conn.commit()
        pass


    '''
    记录功能使用次数
    '''
    def recoredFuncUse(self,openid,func_id):
        query_sql_str = 'select func_use_count from t_func_hot where openid = :p_openid and func_id = :p_func_id'
        self.__cursor.execute(query_sql_str, {'p_openid': openid,'p_func_id':func_id})
        res = self.__cursor.fetchall()
        if len(res) > 0 :
            #udpate
            count = res[0][0] + 1;
            upd_sql_str = 'update t_func_hot set func_use_count = :p_func_use_count where openid = :p_openid and func_id = :p_func_id'
            self.__cursor.execute(upd_sql_str, {'p_func_use_count': count, 'p_openid': openid,'p_func_id':func_id})
            self.__conn.commit()
            print("功能++")
        else:
            #insert
            sqlstr = 'insert into t_func_hot (openid,func_id,func_use_count) values (:p_openid,:p_func_id,:p_func_use_count)'
            self.__cursor.execute(sqlstr, {'p_openid': openid, 'p_func_id': func_id, 'p_func_use_count': 1})
            self.__conn.commit()
            print("记录功能使用")
        pass


db = sqldb()