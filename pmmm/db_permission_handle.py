# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
class PermissionController:
    #查询项目中文名
    def select_rowid(self,db,user,permission):
        cursor = db.cursor()
        sql = "select rowid from permission where username=%s and action=%s"
        cursor.execute(sql,(user,permission))
        rowid=cursor.fetchone()
        return rowid
    #删除权限
    def delete_permission(self,db,user,permission):
        cursor = db.cursor()
        sql = "delete from permission where username=%s and action=%s"
        cursor.execute(sql,(user,permission))
        db.commit()
     #添加权限
    def add_permission(self,db,user,permission):
        cursor=db.cursor()
        sql = "insert into permission values(%s,%s)"
        cursor.execute(sql,(user,permission))
        db.commit()