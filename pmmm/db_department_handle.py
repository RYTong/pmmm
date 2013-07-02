#-*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
class Department_TableController:
    def select_dep_email(self,db,dep_id):
        cu=db.cursor()
        sql="select dep_email from department where dep_id=%s"
        cu.execute(sql,dep_id)
        dep_email=cu.fetchone()
        return dep_email
    def select_dep_name(self,db,dep_id):
        cu=db.cursor()
        sql = "select dep_name from department where dep_id='"+dep_id+"'"
        cu.execute(sql)
        dep_name=cu.fetchone()
        return dep_name
    def select_dep_id(self,db):
        cu=db.cursor()
        sql = "select dep_id from department"
        cu.execute(sql)
        dep_id=cu.fetchall()
        return dep_id
    def add_dep(self,db,depId,depName,depMana,depDeputyMana,leaderdepId,depemail):
        cursor =db.cursor()
        sql = "insert into department values(%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,(depId,depName,depMana,depDeputyMana,leaderdepId,depemail))
        db.commit()
    def select_dep_manager(self,db,dep_id):
        cu=db.cursor()
        sql = "select dep_manager from department where dep_id='"+dep_id+"'"
        cu.execute(sql)
        dep_manager=cu.fetchone()
        return dep_manager
    def select_dep_deputy_manager(self,db,dep_id):
        cu=db.cursor()
        sql = "select dep_deputy_manager from department where dep_id='"+dep_id+"'"
        cu.execute(sql)
        dep_deputy_manager=cu.fetchone()
        return dep_deputy_manager
    def select_dep_info(self,db,dep_id):
        cu=db.cursor()
        cu.execute("select dep_name,leader_dep_id,dep_email from department where dep_id='"+dep_id+"'")
        dep_info=cu.fetchone()
        return dep_info
    def update_dep_mana(self,db,user,depId):
        cu=db.cursor()
        sql = "update department set dep_manager=%s where dep_id=%s"
        cu.execute(sql,(user,depId))
        db.commit()
    def update_dep_vice_mana(self,db,user,depId):
        cu=db.cursor()
        sql = "update department set dep_deputy_manager=%s where dep_id=%s"
        cu.execute(sql,(user,depId))
        db.commit()
    def delete_dep__mana(self,db,depId,user):
        cu=db.cursor()
        sql = "update department set dep_manager=%s where dep_id=%s AND dep_manager=%s"
        cu.execute(sql,("",depId,user))
        db.commit()
    def delete_dep_vice__mana(self,db,depId,user):
        cu=db.cursor()
        sql = "update department set dep_deputy_manager=%s where dep_id=%s AND dep_deputy_manager=%s"
        cu.execute(sql,("",depId,user))
        db.commit()
    def delete_dep(self,db,depId):
        cu=db.cursor()
        cu.execute("delete from department where dep_id='"+depId+"'")
        db.commit()
    def update_dep_name(self,db,depName,depId):
        cu=db.cursor()
        cu.execute("update department set dep_name=%s where dep_id=%s",(depName,depId))
        db.commit()
    def update_updep_id(self,db,leaderdepId,depId):
        cu=db.cursor()
        cu.execute("update department set leader_dep_id=%s where dep_id=%s",(leaderdepId,depId))
        db.commit()
    def update_dep_email(self,db,depemail,depId):
        cu=db.cursor()
        cu.execute("update department set dep_email=%s where dep_id=%s",(depemail,depId))
        db.commit()