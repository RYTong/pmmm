# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
class OtherTypeController:
    #对项目财务类型(expend_type)表的操作
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
    #对工作类型表(proj_type)的操作
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
    #对员工工作岗位表(user_work_type)的操作
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