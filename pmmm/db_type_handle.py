# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()������ϵͳ����ʱ���ã���Ҫ����reload(sys)
reload(sys)
#����Ĭ�ϱ���Ϊutf-8�������̱�Ϊ����ʱ��������������
sys.setdefaultencoding('utf-8')
class OtherTypeController:
    #����Ŀ��������(expend_type)��Ĳ���
    def add_expend_type(self,db,type):
        cursor=db.cursor()
        cursor.execute("insert into expend_type values ('"+type+"')")
        db.commit()
    def select_expend_type_name(self,db):
        cursor = db.cursor()
        sql = "select expend_type_name from expend_type"
        cursor.execute(sql)
        expend_type_name=cursor.fetchall()
        return expend_type_name
    #�Թ������ͱ�(proj_type)�Ĳ���
    def add_work_type(self,db,type):
        cursor=db.cursor()
        cursor.execute("insert into proj_type values ('"+type+"')")
        db.commit()
    def select_proj_type_name(self,db):
        cursor = db.cursor()
        sql = "select proj_type_name from proj_type"
        cursor.execute(sql)
        proj_type_name=cursor.fetchall()
        return proj_type_name
    def select_proj_type_table(self,db):
        cursor = db.cursor()
        sql = "select rowid,proj_type_name from proj_type"
        cursor.execute(sql)
        result=cursor.fetchall()
        return result
    def delete_proj_type(self,db,type):
        cursor = db.cursor()
        sql = "delete from proj_type where rowid="+type
        cursor.execute(sql)
        db.commit()
    #��Ա��������λ��(user_work_type)�Ĳ���
    def select_user_work_type_table(self,db):
        cursor = db.cursor()
        cursor.execute("select user_work_type_id,user_work_type from user_work_type")
        result=cursor.fetchall()
        return result
    def select_user_work_type(self,db,i):
        cursor = db.cursor()
        cursor.execute("select user_work_type from user_work_type where user_work_type_id='"+str(i)+"'")
        result=cursor.fetchone()
        return result
    def select_user_work_id(self,db,type):
        cursor = db.cursor()
        sql="select user_work_type_id from user_work_type where user_work_type='"+type+"'"
        cursor.execute(sql)
        result=cursor.fetchone()
        return result
    def add_user_work_type(self,db,type):
        cursor=db.cursor()
        cursor.execute("insert into user_work_type values (null,'"+type+"')")
        db.commit()