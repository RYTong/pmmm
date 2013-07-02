# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
class PjuserController:
    #查出员工所在项目名
    def select_user_proj_name(self,db,username):
        cu=db.cursor()
        cu.execute("select proj_name from proj_user where proj_user_name='"+username+"'")
        result = cu.fetchall()
        return result
    #列出项目用户表内所有的项目
    def select_projs(self,db):
        cu=db.cursor()
        sql = "select distinct proj_name from proj_user"
        cu.execute(sql)
        result=cu.fetchall()
        return result
    #根据项目查出员工名
    def select_proj_users(self,db,proj):
        cu=db.cursor()
        sql = "select proj_user_name from proj_user where proj_name='"+proj+"'"
        cu.execute(sql)
        names = cu.fetchall()
        return names
    #从项目表中删除用户
    def delete_user(self,db,user):
        cu=db.cursor()
        cu.execute("delete from proj_user where proj_user_name='"+user+"'")
        db.commit()
     #删除用户下的项目
    def delete_user_proj(self,db,p,user):
        cu=db.cursor()
        sql = "delete from proj_user where proj_name=%s AND proj_user_name=%s"
        cu.execute(sql,(p,user))
        db.commit()
    #为用户添加项目
    def add_user_proj(self,db,p,user):
        cu=db.cursor()
        sql = "insert into proj_user values(%s,%s)"
        cu.execute(sql,(p,user))
        db.commit()
    #为项目添加用户
    def add_proj_user(self,db,proj,u):
        cu=db.cursor()
        sql ="insert into proj_user values(%s,%s)"
        cu.execute(sql,(proj,u))
        db.commit()
    #删除项目用户表中的所有数据
    def delete_alldata(self,db):
        cu=db.cursor()
        sql ="delete from proj_user"
        cu.execute(sql)
        db.commit()
    #查询项目用户表中所有员工名
    def select_users(self,db):
        cu=db.cursor()
        sql ="select distinct proj_user_name from proj_user"
        cu.execute(sql)
        names = cu.fetchall()
        return names
    #查出项目经理所在项目下的员工名
    def select_proj_manager_users(self,db,proj_manager_name):
        cu=db.cursor()
        sql ="select distinct proj_user_name from proj_user,project where proj_user.proj_name=project.proj_name AND proj_manager_name='"+proj_manager_name+"'"
        cu.execute(sql)
        names = cu.fetchall()
        return names
    #删除项目用户表中的项目
    def _delete_project(self,db,pr):
        cu=db.cursor()
        sql ="delete from proj_user where proj_name='"+pr+"'"
        cu.execute(sql)
        db.commit()