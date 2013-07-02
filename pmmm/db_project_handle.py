# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
class ProjecttableController:
    #查询出该项目经理下的所有项目
    def select_project_manager_pros(self,db,project_manager):
        cu=db.cursor()
        sql = "select proj_name from project where proj_manager_name='"+project_manager+"'"
        cu.execute(sql)
        projs=cu.fetchall()
        return projs
    #为项目添加项目经理的方法
    def add_project_manager(self,db,proj,u):
        cu=db.cursor()
        sql = "insert into project values(%s,%s)"
        cu.execute(sql,(proj,u))
        db.commit()
    #查询项目经理
    def select_proj_manager(self,db,proj):
        cu=db.cursor()
        sql = "select proj_manager_name from project where proj_name='"+proj+"'"
        cu.execute(sql)
        proj_mana=cu.fetchall()
        return proj_mana
    #删除项目经理(根据项目和项目经理删除)
    def delete_proj_manager(self,db,proj,proj_mana):
        cu=db.cursor()
        sql = "delete from project where proj_name=%s and proj_manager_name=%s"
        cu.execute(sql,(proj,proj_mana))
        db.commit()
      #删除项目
    def delete_project(self,db,proj_name):
        cu=db.cursor()
        sql = "delete from project where proj_name='"+proj_name+"'"
        cu.execute(sql)
        db.commit()
    #查询所有项目经理
    def select_all_proj_manager(self,db):
        cu=db.cursor()
        sql = "select distinct proj_manager_name from project"
        cu.execute(sql)
        proj_mana=cu.fetchall()
        return proj_mana
    #删除项目经理(根据项目经理删除)
    def delete_manager(self,db,proj_mana):
        cu=db.cursor()
        sql = "delete from project where proj_manager_name='"+proj_mana+"'"
        cu.execute(sql)
        db.commit()