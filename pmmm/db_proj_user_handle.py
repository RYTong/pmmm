# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()������ϵͳ����ʱ���ã���Ҫ����reload(sys)
reload(sys)
#����Ĭ�ϱ���Ϊutf-8�������̱�Ϊ����ʱ��������������
sys.setdefaultencoding('utf-8')
class PjuserController:
    #���Ա��������Ŀ��
    def select_user_proj_name(self,db,username):
        cu=db.cursor()
        cu.execute("select proj_name from proj_user where proj_user_name='"+username+"'")
        result = cu.fetchall()
        return result
    #�г���Ŀ�û��������е���Ŀ
    def select_projs(self,db):
        cu=db.cursor()
        sql = "select distinct proj_name from proj_user"
        cu.execute(sql)
        result=cu.fetchall()
        return result
    #������Ŀ���Ա����
    def select_proj_users(self,db,proj):
        cu=db.cursor()
        sql = "select proj_user_name from proj_user where proj_name='"+proj+"'"
        cu.execute(sql)
        names = cu.fetchall()
        return names
    #����Ŀ����ɾ���û�
    def delete_user(self,db,user):
        cu=db.cursor()
        cu.execute("delete from proj_user where proj_user_name='"+user+"'")
        db.commit()
     #ɾ���û��µ���Ŀ
    def delete_user_proj(self,db,p,user):
        cu=db.cursor()
        sql = "delete from proj_user where proj_name=%s AND proj_user_name=%s"
        cu.execute(sql,(p,user))
        db.commit()
    #Ϊ�û������Ŀ
    def add_user_proj(self,db,p,user):
        cu=db.cursor()
        sql = "insert into proj_user values(%s,%s)"
        cu.execute(sql,(p,user))
        db.commit()
    #Ϊ��Ŀ����û�
    def add_proj_user(self,db,proj,u):
        cu=db.cursor()
        sql ="insert into proj_user values(%s,%s)"
        cu.execute(sql,(proj,u))
        db.commit()
    #ɾ����Ŀ�û����е���������
    def delete_alldata(self,db):
        cu=db.cursor()
        sql ="delete from proj_user"
        cu.execute(sql)
        db.commit()
    #��ѯ��Ŀ�û���������Ա����
    def select_users(self,db):
        cu=db.cursor()
        sql ="select distinct proj_user_name from proj_user"
        cu.execute(sql)
        names = cu.fetchall()
        return names
    #�����Ŀ����������Ŀ�µ�Ա����
    def select_proj_manager_users(self,db,proj_manager_name):
        cu=db.cursor()
        sql ="select distinct proj_user_name from proj_user,project where proj_user.proj_name=project.proj_name AND proj_manager_name='"+proj_manager_name+"'"
        cu.execute(sql)
        names = cu.fetchall()
        return names
    #ɾ����Ŀ�û����е���Ŀ
    def _delete_project(self,db,pr):
        cu=db.cursor()
        sql ="delete from proj_user where proj_name='"+pr+"'"
        cu.execute(sql)
        db.commit()