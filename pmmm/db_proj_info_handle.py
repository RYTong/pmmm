# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
class ProjectInfoController:
    #查询项目信息
    def select_proj_info(self,db):
        cursor = db.cursor()
        cursor.execute("select proj_name,proj_name_zh from proj_info")
        project = cursor.fetchall()
        return project
    #查询项目中文名
    def select_projZh_name(self,db,proj_name):
        cursor = db.cursor()
        cursor.execute("select proj_name_zh from proj_info where proj_name='"+proj_name+"'")
        pZh = cursor.fetchone()
        return pZh
    #添加新项目
    def add_project(self,db,proj_name,proj_nameZh):
        cursor=db.cursor()
        sql = "insert into proj_info values(%s,%s)"
        cursor.execute(sql,(proj_name,proj_nameZh))
        db.commit()
    #删除项目
    def delete_project(self,db,proj_name):
        cursor=db.cursor()
        cursor.execute("delete from proj_info  where proj_name='"+proj_name+"'")
        db.commit()
    #删除表中数据
    def delete_data(self,db):
        cursor=db.cursor()
        cursor.execute("delete from proj_info")
        db.commit()
    #查询无中文名项目
    def select_no_projZh_name(self,db):
        cursor = db.cursor()
        sql = 'select proj_name,rowid from proj_info where proj_name_zh=""'
        cursor.execute(sql)
        pZh = cursor.fetchall()
        return pZh
    #查询有中文名项目
    def select_have_projZh_name(self,db):
        cursor = db.cursor()
        sql = 'select proj_name,rowid from proj_info where proj_name_zh<>""'
        cursor.execute(sql)
        pZh = cursor.fetchall()
        return pZh
    #添加项目中文名
    def add_project_zh_name(self,db,name,rid):
        cursor=db.cursor()
        sql = "update proj_info set proj_name_zh=%s where rowid=%s"
        cursor.execute(sql,(name,rid))
        db.commit()
    #删除用户中文名
    def delete_projzh_name(self,db,proj):
        cursor=db.cursor()
        sql = 'update proj_info set proj_name_zh="" where rowid="'+proj+'"'
        cursor.execute(sql)
        db.commit()