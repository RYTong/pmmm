# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()������ϵͳ����ʱ���ã���Ҫ����reload(sys)
reload(sys)
#����Ĭ�ϱ���Ϊutf-8�������̱�Ϊ����ʱ��������������
sys.setdefaultencoding('utf-8')
class ProjectInfoController:
    #��ѯ��Ŀ��Ϣ
    def select_proj_info(self,db):
        cursor = db.cursor()
        cursor.execute("select proj_name,proj_name_zh from proj_info")
        project = cursor.fetchall()
        return project
    #��ѯ��Ŀ������
    def select_projZh_name(self,db,proj_name):
        cursor = db.cursor()
        cursor.execute("select proj_name_zh from proj_info where proj_name='"+proj_name+"'")
        pZh = cursor.fetchone()
        return pZh
    #�������Ŀ
    def add_project(self,db,proj_name,proj_nameZh):
        cursor=db.cursor()
        sql = "insert into proj_info values(%s,%s)"
        cursor.execute(sql,(proj_name,proj_nameZh))
        db.commit()
    #ɾ����Ŀ
    def delete_project(self,db,proj_name):
        cursor=db.cursor()
        cursor.execute("delete from proj_info  where proj_name='"+proj_name+"'")
        db.commit()
    #ɾ����������
    def delete_data(self,db):
        cursor=db.cursor()
        cursor.execute("delete from proj_info")
        db.commit()
    #��ѯ����������Ŀ
    def select_no_projZh_name(self,db):
        cursor = db.cursor()
        sql = 'select proj_name,rowid from proj_info where proj_name_zh=""'
        cursor.execute(sql)
        pZh = cursor.fetchall()
        return pZh
    #��ѯ����������Ŀ
    def select_have_projZh_name(self,db):
        cursor = db.cursor()
        sql = 'select proj_name,rowid from proj_info where proj_name_zh<>""'
        cursor.execute(sql)
        pZh = cursor.fetchall()
        return pZh
    #�����Ŀ������
    def add_project_zh_name(self,db,name,rid):
        cursor=db.cursor()
        sql = "update proj_info set proj_name_zh=%s where rowid=%s"
        cursor.execute(sql,(name,rid))
        db.commit()
    #ɾ���û�������
    def delete_projzh_name(self,db,proj):
        cursor=db.cursor()
        sql = 'update proj_info set proj_name_zh="" where rowid="'+proj+'"'
        cursor.execute(sql)
        db.commit()