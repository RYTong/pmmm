# -*- coding: utf-8 -*-
import sqlite
import sys
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
class PmtableController:
    #查出工时记录表中所有项目名
    def select_proj_name_table(self,db):
         cu=db.cursor()
         sql="select distinct proj_name from proj_hours_record"
         cu.execute(sql)
         projs=cu.fetchall()
         return projs
   #对工时记录表做查询,查看是否重复提交工时记录
    def select_table(self,db,proj_name,milestone,work_type,work_date,work_date_length,user_remarks):
         cu = db.cursor()
         sql="select user_name from proj_hours_record where proj_name=%s AND milestone=%s AND work_type=%s AND work_date=%s AND work_time_length=%s AND user_feedback=%s"     
         cu.execute(sql,(proj_name,milestone,work_type,work_date,work_date_length,user_remarks))
         result=cu.fetchall()
         return result
    #对工时记录表做查询,查看是否重复提交工时记录
    def select_import_proj_hours_record(self,db,proj_name,user_name,work_date,user_remarks):
         cu = db.cursor()
         sql="select rowid from proj_hours_record where proj_name=%s AND user_name=%s AND work_date=%s AND user_feedback=%s"     
         cu.execute(sql,(proj_name,user_name,work_date,user_remarks))
         result=cu.fetchone()
         return result
   #显示工时记录列表(根据人员)
    def select_list_table(self,db,user_name,startDate,endDate):
         list1=[]
         cu = db.cursor()
         sql="select proj_name,user_name,work_type,work_date,milestone,work_time_length,rowid,check_status,user_feedback,manager_feedback,checked_user,write_time,checked_time from proj_hours_record where user_name=%s AND work_date>=%s AND work_date<=%s order by work_date desc"
         cu.execute(sql,(user_name,startDate,endDate))
         listResult = cu.fetchall()
         return listResult
   #显示工时记录列表(根据项目)
    def select_projlist_table(self,db,pr,startDate,endDate):
         list1=[]
         cu = db.cursor()
         sql="select proj_name,user_name,work_type,work_date,milestone,work_time_length,rowid,check_status,user_feedback,manager_feedback,checked_user,write_time,checked_time from proj_hours_record  where proj_name=%s AND work_date>=%s AND work_date<=%s order by user_name,work_date"
         cu.execute(sql,(pr,startDate,endDate))
         listResult = cu.fetchall()
         return listResult
   #添加工时记录
    def insert_into_table(self,db,proj_name,user_name,work_type,work_date,milestone,work_date_length,user_remarks,check_status,write_time): 
         cu = db.cursor()
         cu.execute("INSERT INTO proj_hours_record(proj_name,user_name,work_type,work_date,milestone,work_time_length,user_feedback,check_status,write_time) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)", (proj_name,user_name,work_type,work_date,milestone,work_date_length,user_remarks,check_status,write_time))
         db.commit()
    #导入工时记录
    def import_insert_into_table(self,db,proj_name,user_name,work_type,work_date,milestone,work_date_length,user_remarks,manager_feedback,check_status,checked_user,write_time,checked_time): 
         cu = db.cursor()
         cu.execute("INSERT INTO proj_hours_record(proj_name,user_name,work_type,work_date,milestone,work_time_length,user_feedback,manager_feedback,check_status,checked_user,write_time,checked_time) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)", (proj_name,user_name,work_type,work_date,milestone,work_date_length,user_remarks,manager_feedback,check_status,checked_user,write_time,checked_time))
         db.commit()
   #查询工时记录表中工时填写时间超时的员工
    def select_timeout_table(self,db,startDate,endDate,u):
         cu = db.cursor()
         sql="select count(distinct work_date) from proj_hours_record where user_name='"+str(u)+"' and (julianday(write_time) - julianday(work_date))>7 and work_date>='"+startDate+"' and work_date<='"+endDate+"'"
         cu.execute(sql)
         day=cu.fetchone()
         return day
   #查询员工在一段时间内的工时记天数(distinct work_date)
    def select_sumworkdate_table(self,db,startDates,endDates,u):
         cu = db.cursor()
         sql="select count(distinct work_date) from proj_hours_record where user_name='"+str(u)+"' and work_date>='"+startDates+"' and work_date<='"+endDates+"'"
         cu.execute(sql)
         count=cu.fetchone()
         return count
    #显示周报中本周工作内容
    def select_weekReport_table(self,db,startDate,endDate,user_name):
         cu = db.cursor()
         sql="select proj_name,work_type,work_date,user_feedback,work_time_length from proj_hours_record where work_date>=%s AND work_date<=%s AND user_name=%s order by work_date"
         cu.execute(sql,(startDate,endDate,user_name))
         work = cu.fetchall()
         return work
   #查询出每个用户在该月审核通过的记录时间总和
    def select_user_monthtime_tabel(self,db,u,startDate,endDate):
        cu = db.cursor()
        sql4 = "select sum(work_time_length) from proj_hours_record where user_name='"+str(u)+"' AND work_date>='"+str(startDate)+"' AND work_date<='"+str(endDate)+"' AND work_type not in ('事假','病假','调休') AND check_status=1"
        cu.execute(sql4)
        t = cu.fetchall()
        return t
   #工作量总统计表中计算项目每月的工时总量
    def select_sumtime_table(self,db,startDate,endDate,pr):
         cu = db.cursor()
         sqls1="select sum(work_time_length) from proj_hours_record where proj_name='"+str(pr)+"' AND check_status=1 AND work_type not in ('事假','病假','调休') AND work_date>='"+str(startDate)+"' AND work_date<='"+str(endDate)+"'"
         cu.execute(sqls1)
         monthtime=cu.fetchone()
         return monthtime
   #工作量总统计表中员工每月的工作量(anaWay==1)
    def select_user_sumtime(self,db,startDate,endDate,u,pr):
         cu = db.cursor()
         sql="select sum(work_time_length) from proj_hours_record where proj_name='"+str(pr)+"' AND check_status=1 AND work_type not in ('事假','病假','调休') AND work_date>='"+str(startDate)+"' AND work_date<='"+str(endDate)+"' and user_name='"+str(u)+"'"
         cu.execute(sql)
         time=cu.fetchone()
         return time
    #工作量总统计表中员工每月的工作量(anaWay==2)
    def select_sumtime(self,db,startDate,endDate,u,pr):
         cu = db.cursor()
         sql="select sum(work_time_length) from proj_hours_record where proj_name='"+str(pr)+"' AND check_status=1 AND work_type not in ('事假','病假') AND work_date>='"+str(startDate)+"' AND work_date<='"+str(endDate)+"' and user_name='"+str(u)+"'"
         cu.execute(sql)
         time=cu.fetchone()
         return time
   #工作量总统计表中限制人员工时时合计
    def select_reality_work_length(self,db,pr,startDate,endDate):
         cu = db.cursor()
         sql="select sum(work_time_length) from proj_hours_record where proj_name='"+str(pr)+"' AND check_status=1 AND work_type not in ('事假','病假') AND work_date>='"+str(startDate)+"' AND work_date<='"+str(endDate)+"' group by user_name"
         cu.execute(sql)
         monthtime=cu.fetchall()
         return monthtime
        
    def select_user_month_work_length(self,db,pr,startDate,endDate):
         cu = db.cursor()
         sql="select sum(work_time_length),user_name from proj_hours_record where proj_name='"+str(pr)+"' AND check_status=1 AND work_type not in ('事假','病假','调休') AND work_date>='"+str(startDate)+"' AND work_date<='"+str(endDate)+"' group by user_name"
         cu.execute(sql)
         monthtime=cu.fetchall()
         return monthtime
   #根据部门用户查询待审核的记录
    def select_audit_table(self,db,username):
         cu =db.cursor()
         sql = "select proj_name,user_name,work_type,work_date,milestone,work_time_length,rowid,user_feedback,write_time from proj_hours_record where check_status=0 and user_name=%s order by work_date"
         cu.execute(sql,username)
         res = cu.fetchall()
         return res
   #根据项目查询出待审核的记录
    def select_proj_audit_table(self,db,proj_name):
         cu = db.cursor()
         sql = "select proj_name,user_name,work_type,work_date,milestone,work_time_length,rowid,user_feedback,write_time from proj_hours_record where check_status=0 and proj_name=%s order by user_name,work_date"
         cu.execute(sql,proj_name)
         res= cu.fetchall()
         return res
   #提交审核记录方法
    def submit_check_table(self,db,status,manager_feedback,check_user,check_time,rowid):
        cu =db.cursor()
        cu.execute('UPDATE proj_hours_record SET check_status=%s,manager_feedback=%s,checked_user=%s,checked_time=%s WHERE rowid=%s',(status,manager_feedback,check_user,check_time,rowid))
        db.commit()
   #更新工时记录，该方法用于对未审核通过的工时记录重新填写，改变记录的审核状态为未审核
    def update_pmhourecord_table(self,db,proj_name,user_name,work_type,work_date,milestone,work_date_length,user_remark,rowid):
        cu = db.cursor()
        cu.execute("update proj_hours_record set proj_name=%s,user_name=%s,work_type=%s,work_date=%s,milestone=%s,work_time_length=%s,user_feedback=%s,check_status=0,checked_user=%s,checked_time=%s where rowid=%s", (proj_name,user_name,work_type,work_date,milestone,work_date_length,user_remark,"","",rowid))
        db.commit()
   #按投入统计项目的工作量
    def select_input_worktime_table(self,db,w,projName,startTime,endTime):
        cu = db.cursor()
        sql = "select sum(work_time_length) from proj_hours_record where work_type=%s AND proj_name=%s AND check_status=1 AND work_date>=%s AND work_type not in ('事假','病假','调休') AND work_date<=%s"
        cu.execute(sql,(w,str(projName),startTime,endTime))
        hourLength = cu.fetchone()
        return hourLength
   #显示人员工时记录审核未通过的记录
    def select_unreview_record_table(self,db,u):
        cu = db.cursor()
        sqllist = "select proj_name,user_name,work_type,work_date,milestone,work_time_length,rowid,check_status,manager_feedback,checked_user,user_feedback from proj_hours_record where check_status>1 and user_name='"+u+"'"
        cu.execute(sqllist)
        listRes = cu.fetchall()
        return listRes
   #删除工时记录中的记录
    def delete_record_table(self,db,data):
        cu = db.cursor()
        sql = "delete from proj_hours_record where rowid="+data
        cu.execute(sql)
        db.commit()
  #查出工时记录表中工作类型
    def select_worktype_table(self,db):
        cu = db.cursor()
        sql = "select distinct work_type from proj_hours_record"
        cu.execute(sql)
        work_types = cu.fetchall()
        return work_types
  #根据项目查出一段时间内员工名
    def select_proj_user_name_table(self,db,proj,startDate,endDate):
        cu = db.cursor()
        sql="select distinct user_name from proj_hours_record  where proj_name=%s AND work_date>=%s AND work_date<=%s"
        cu.execute(sql,(proj,startDate,endDate))
        users = cu.fetchall()
        return users
  #根据项目名查出工时记录表中对应员工名
    def select_proj_user_table(self,db,projName):
        cu = db.cursor()
        sql = "select distinct user_name from proj_hours_record where proj_name='"+projName+"'"
        cu.execute(sql)
        user_results = cu.fetchall()
        return user_results
  #查询出工时系统中一段时间内员工名
    def select_username_table(self,db,startTime,endtime):
        cu =db.cursor()
        sql2 = "select distinct user_name from proj_hours_record where work_date>=%s and work_date<=%s"
        cu.execute(sql2,(startTime,endtime))
        days = cu.fetchall()
        return days
   #查询出工时系统中所有人员名单
    def select_all_user_table(self,db):
        cu = db.cursor()
        sql = "select distinct user_name from proj_hours_record"
        cu.execute(sql)
        user_results = cu.fetchall()
        return user_results
     #查出工时记录表在一段时间内中所有项目名
    def select_time_proj_name_table(self,db,startDate,endDate):
         cu=db.cursor()
         sql="select distinct proj_name from proj_hours_record where work_date>='"+startDate+"' and work_date<='"+endDate+"'"
         cu.execute(sql)
         projs=cu.fetchall()
         return projs