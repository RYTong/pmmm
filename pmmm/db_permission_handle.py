# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()������ϵͳ����ʱ���ã���Ҫ����reload(sys)
reload(sys)
#����Ĭ�ϱ���Ϊutf-8�������̱�Ϊ����ʱ��������������
sys.setdefaultencoding('utf-8')
class PermissionController:
    #��ѯ��Ŀ������
    def select_rowid(self,db,user,permission):
        cursor = db.cursor()
        sql = "select rowid from permission where username=%s and action=%s"
        cursor.execute(sql,(user,permission))
        rowid=cursor.fetchone()
        return rowid
    #ɾ��Ȩ��
    def delete_permission(self,db,user,permission):
        cursor = db.cursor()
        sql = "delete from permission where username=%s and action=%s"
        cursor.execute(sql,(user,permission))
        db.commit()
     #���Ȩ��
    def add_permission(self,db,user,permission):
        cursor=db.cursor()
        sql = "insert into permission values(%s,%s)"
        cursor.execute(sql,(user,permission))
        db.commit()