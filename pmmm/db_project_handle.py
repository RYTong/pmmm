# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()������ϵͳ����ʱ���ã���Ҫ����reload(sys)
reload(sys)
#����Ĭ�ϱ���Ϊutf-8�������̱�Ϊ����ʱ��������������
sys.setdefaultencoding('utf-8')
class ProjecttableController:
    #��ѯ������Ŀ�����µ�������Ŀ
    def select_project_manager_pros(self,db,project_manager):
        cu=db.cursor()
        sql = "select proj_name from project where proj_manager_name='"+project_manager+"'"
        cu.execute(sql)
        projs=cu.fetchall()
        return projs
    #Ϊ��Ŀ�����Ŀ����ķ���
    def add_project_manager(self,db,proj,u):
        cu=db.cursor()
        sql = "insert into project values(%s,%s)"
        cu.execute(sql,(proj,u))
        db.commit()
    #��ѯ��Ŀ����
    def select_proj_manager(self,db,proj):
        cu=db.cursor()
        sql = "select proj_manager_name from project where proj_name='"+proj+"'"
        cu.execute(sql)
        proj_mana=cu.fetchall()
        return proj_mana
    #ɾ����Ŀ����(������Ŀ����Ŀ����ɾ��)
    def delete_proj_manager(self,db,proj,proj_mana):
        cu=db.cursor()
        sql = "delete from project where proj_name=%s and proj_manager_name=%s"
        cu.execute(sql,(proj,proj_mana))
        db.commit()
      #ɾ����Ŀ
    def delete_project(self,db,proj_name):
        cu=db.cursor()
        sql = "delete from project where proj_name='"+proj_name+"'"
        cu.execute(sql)
        db.commit()
    #��ѯ������Ŀ����
    def select_all_proj_manager(self,db):
        cu=db.cursor()
        sql = "select distinct proj_manager_name from project"
        cu.execute(sql)
        proj_mana=cu.fetchall()
        return proj_mana
    #ɾ����Ŀ����(������Ŀ����ɾ��)
    def delete_manager(self,db,proj_mana):
        cu=db.cursor()
        sql = "delete from project where proj_manager_name='"+proj_mana+"'"
        cu.execute(sql)
        db.commit()