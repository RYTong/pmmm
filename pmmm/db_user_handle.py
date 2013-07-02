# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
class UsertableController:
    #查出某级别的用户名
    def select_user_level(self,db,level):
         cu=db.cursor()
         sql = "select username_zh,rowid from user where user_level=%s"
         cu.execute(sql,str(level))
         result=cu.fetchall()
         return result
    #查询出用户级别
    def select_userlevel(self,db,user):
         cu=db.cursor()
         sql = "select user_level from user where username='"+str(user)+"'"
         cu.execute(sql)
         result=cu.fetchone()
         return result
    #修改user级别
    def update_user_level(self,db,level,rid):
         cu=db.cursor()
         sql = 'update user set user_level=%s where rowid=%s'
         cu.execute(sql,(level,rid))
         db.commit()
    #查找没有中文名的用户
    def select_no_userzh(self,db):
         cu=db.cursor()
         sql = 'select username,rowid from user where username_zh=""'
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #查找用户中文名
    def select_userzh(self,db):
         cu=db.cursor()
         sql = 'select username_zh,rowid from user where username_zh<>""'
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #添加用户中文名
    def add_userzh(self,db,user,rid):
         cu=db.cursor()
         sql = "update user set username_zh=%s where rowid=%s"
         cu.execute(sql,(user,rid))
         db.commit()
    #删除用户中文名
    def delete_userzh(self,db,user):
         cu=db.cursor()
         sql = 'update user set username_zh="" where rowid="'+user+'"'
         cu.execute(sql)
         db.commit()
    #删除数据库里的用户
    def delete_user(self,db,user):
         cu=db.cursor()
         sql = "delete from user where username='"+str(user)+"'"
         cu.execute(sql)
         db.commit()
    #从数据库读出所有用户供删除操作使用
    def select_user_name(self,db):
         cu=db.cursor()
         sql = 'select username,username_zh from user'
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #添加用户
    def add_user(self,db,u,uzh):
         cu=db.cursor()
         sql = 'insert into user values(null,%s,%s,%s,%s,%s,%s,%s)'
         cu.execute(sql,(u,uzh,0,0,"",0,""))
         db.commit()
    #添加离职用户
    def add_lea_of_user(self,db,u,uzh):
        cu=db.cursor()
        sql = 'insert into user values(null,%s,%s,%s,%s,%s,%s,%s)'
        cu.execute(sql,(u,uzh,0,0,"",1,""))
        db.commit()
    #删除user表中数据
    def delete_all_date(self,db):
         cu=db.cursor()
         sql = 'delete from user'
         cu.execute(sql)
         db.commit()
    #查询用户部门id
    def select_user_depid(self,db,user):
         cu=db.cursor()
         sql = "select dep_id from user where username='"+user+"'"
         cu.execute(sql)
         result=cu.fetchone()
         return result
    #查询user用户表中员工
    def select_users(self,db):
         cu=db.cursor()
         sql = 'select distinct username from user'
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #查询user用户表中员工是否在职
    def select_users_state(self,db):
         cu=db.cursor()
         sql = "select username,username_zh,use_state from user"
         cu.execute(sql)
         result=cu.fetchall()
         return result
    ##查询user用户表中员工state为0的用户，即在职人员
    def select_users_state_zero(self,db):
         cu=db.cursor()
         sql = 'select distinct username from user where use_state=0'
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #查询user用户表中员工state为一的用户，即离职员工
    def select_users_state_one(self,db):
         cu=db.cursor()
         sql = 'select distinct username from user where use_state=1'
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #查出表中用户信息
    def select_user_info(self,db):
         cu=db.cursor()
         sql = 'select username,username_zh, dep_id, user_level,use_salary,use_state,use_work_type from user'
         cu.execute(sql)
         result=cu.fetchall()
         return result
     #查询部门经理部门下的用户
    def select_dep_user(self,db,user):
         cu=db.cursor()
         sql = "select username from user,department where user.dep_id=department.dep_id AND (dep_manager='"+user+"' OR dep_deputy_manager='"+user+"')"
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #根据部门id，查询用户
    def select_nodep_user(self,db,data):
         cu=db.cursor()
         sql = "select username from user where dep_id='"+data+"' and use_state=0"
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #根据部门id，查询用户中午名
    def select_dep_user_zh(self,db,data):
         cu=db.cursor()
         sql = "select username_zh from user where dep_id='"+data+"'"
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #查出用户表中不在某一部门的人员
    def select_none_dep_user(self,db,data):
         cu=db.cursor()
         sql = "select username from user where dep_id<>'"+data+"' and use_state=0"
         cu.execute(sql)
         result=cu.fetchall()
         return result
    #修改用户部门编号
    def update_user_dep_id(self,db,id,name):
         cu=db.cursor()
         sql = "update user set dep_id=%s where username=%s"
         cu.execute(sql,(id,name))
         db.commit()
    #删除已有部门时，修改删除部门用户的id为0
    def updata_deldep_user_depid(self,db,d):
         cu=db.cursor()
         sql = "update user set dep_id=0 where dep_id='"+d+"'"
         cu.execute(sql)
         db.commit()
    #查询用户中文名
    def select_userZh_name(self,db,arg):
        cu = db.cursor()
        cu.execute("select username_zh from user where username='"+arg+"'")
        uZh =cu.fetchone()
        return uZh
    #根据用户在职情况查询出用户有工资的人员
    def select_user_have_salary(self,db,state):
        cu = db.cursor()
        sql='select username from user where use_salary<>"" and use_state=%s'
        cu.execute(sql,state)
        users =cu.fetchall()
        return users
       #查询所有用户有工资的人员
    def select_all_user_have_salary(self,db):
        cu = db.cursor()
        sql='select username from user where use_salary<>""'
        cu.execute(sql)
        users =cu.fetchall()
        return users
    #查询出人员工资
    def select_user_salary(self,db,user):
        cu = db.cursor()
        cu.execute("select use_salary from user where username='"+user+"'")
        salary =cu.fetchall()
        return salary
     #查询出人员工资
    def select_salary(self,db,user):
        cu = db.cursor()
        cu.execute("select use_salary from user where username='"+user+"'")
        salary =cu.fetchall()
        return salary
    #添加员工工资
    def add_user_salary(self,db,salary,rid):
        cu=db.cursor()
        sql = "update user set use_salary=%s where rowid=%s"
        cu.execute(sql,(salary,rid))
        db.commit()
    #删除员工工资
    def delete_user_salary(self,db,user):
        cu=db.cursor()
        sql = 'update user set use_salary="" where username="'+user+'"'
        cu.execute(sql)
        db.commit()
    def _update_user_satae(self,db,user):
        cu=db.cursor()
        sql ="update user set use_state=1 where username='"+user+"'"
        cu.execute(sql)
        db.commit()
    def select_leave_users(self,db):
         cu=db.cursor()
         sql = 'select  username,username_zh from user where use_state=1'
         cu.execute(sql)
         result=cu.fetchall()
         return result
    def select_users_noleave(self,db):
         cu=db.cursor()
         sql = 'select  username,username_zh from user where use_state=0'
         cu.execute(sql)
         result=cu.fetchall()
         return result
     #查询出用户没有工资的人员
    def select_user_nosalary(self,db):
        cu = db.cursor()
        cu.execute('select username_zh,rowid from user where use_salary=""')
        users =cu.fetchall()
        return users
    def select_user_by_use_work_type(self,db,id):
        cu = db.cursor()
        sql="select username from user where use_work_type='"+str(id)+"'"
        cu.execute(sql)
        users =cu.fetchall()
        return users
    def select_user_by_use_work_type2(self,db):
        cu = db.cursor()
        sql='select username,username_zh from user where use_work_type=""'
        cu.execute(sql)
        users =cu.fetchall()
        return users
    def select_user_by_use_work_type3(self,db):
        cu = db.cursor()
        sql='select username,username_zh,use_work_type from user where use_work_type<>"" order by use_work_type'
        cu.execute(sql)
        users =cu.fetchall()
        return users
    def update_user_work_type(self,db,use_work_type,username):
        cu=db.cursor()
        sql="update user set use_work_type=%s where username=%s"
        cu.execute(sql,(use_work_type,username))
        db.commit()
    def select_users_dep_id(self,db):
        cu=db.cursor()
        sql = 'select username,dep_id from user where use_state=0 and dep_id<>0 and dep_id<>13 and dep_id<>15 and dep_id<>16 and dep_id<>20 and dep_id<>17 and dep_id<>18 order by dep_id'
        cu.execute(sql)
        result=cu.fetchall()
        return result