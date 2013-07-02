# -*- coding: utf-8 -*-
import xlrd
import xlwt
import cStringIO
import smtplib 
import datetime
import time
import math
import sqlite
import urllib
import re
import calendar
import  sys
import httplib
import random
import os
import tempfile
import shutil
#setdefaultencoding()方法在系统启动时设置，需要加上reload(sys)
reload(sys)
#设置默认编码为utf-8，解决里程碑为中文时报编码错误的问题
sys.setdefaultencoding('utf-8')
from db_pm_hours_record_handle import PmtableController
from db_permission_handle import PermissionController
from db_type_handle import OtherTypeController
from db_proj_info_handle import ProjectInfoController
from db_proj_user_handle import PjuserController
from db_user_handle import UsertableController
from db_project_handle import ProjecttableController
from db_department_handle import Department_TableController
from trac.web import RequestDone
from xlwt.Utils import rowcol_to_cell
from smtplib import SMTP
from email.MIMEText import MIMEText
from time import strftime
from time import localtime
from datetime import timedelta,date
from trac.log import logger_factory
from trac.core import *
from trac.util import Markup
from trac.perm import IPermissionRequestor, PermissionSystem
from trac.web import IRequestHandler
from trac.web.chrome import add_stylesheet, add_script, \
    INavigationContributor, ITemplateProvider
from trac.web.href import Href
from project_controller import ProjectController
from user_controller import UserController
class PMMMPluginPage(Component):
    """Plugin for project management module for Mercurial."""
    implements(IPermissionRequestor, INavigationContributor, IRequestHandler,
               ITemplateProvider)
    #----------------------------------------------------------------------
    # Internal member variables
    #----------------------------------------------------------------------
    MODNAME = 'pmmm'
    HGROOT  = '/home/hg'
    HGSCRIPT = '/home/hg/scripts'
    HGREPO  = '/home/hg/repos'
    TRACROOT = '/home/trac'
    PROJROOT = HGREPO + "/proj"
    ACLROOT = HGROOT + "/acl"
    HIDDEN_DIRS = { 'branches' : 1, 'releases' : 1, '.hg' : 1, '.svn': 1,
                    'experiments' : 1 }
    #----------------------------------------------------------------------
    # Member functions
    #----------------------------------------------------------------------
    global gl_proj_hours_record
    gl_proj_hours_record=PmtableController()
    global gl_proj_user
    gl_proj_user=PjuserController()
    global gl_user
    gl_user=UsertableController()
    global  gl_project
    gl_project=ProjecttableController()
    global gl_department
    gl_department=Department_TableController()
    global gl_proj_info
    gl_proj_info=ProjectInfoController()
    global gl_permission
    gl_permission=PermissionController()
    #包括对的操作
    global gl_othertype
    gl_othertype=OtherTypeController()
    def __init__(self):
        pass
    # IPermissionRequestor methods   
    def get_permission_actions(self):
        """Permissions that PMMM needs to control projects."""
        return ['PROJECT_VIEW', 'PROJECT_CREATE', 
                'PROJECT_DELETE', 'PROJECT_MODIFY',
                ('PROJECT_ADMIN',
                 ['PROJECT_VIEW', 'PROJECT_CREATE', 'PROJECT_DELETE',
                  'PROJECT_MODIFY'])]
    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return self.MODNAME
    def get_navigation_items(self, req):
        url = req.href.pmmm()
        if req.perm.has_permission("PROJECT_VIEW"):
            yield 'mainnav', self.MODNAME, \
                Markup('<a href="%s">%s</a>' % (url , "Projects"))
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """ITemplateProvider"""
        from pkg_resources import resource_filename
        return [(self.MODNAME, resource_filename(__name__, 'htdocs'))]
    def get_templates_dirs(self):
        '''ITemplateProvider'''
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
    #----------------------------------------------------------------------
    # Request handlers
    #----------------------------------------------------------------------
    def match_request(self, req):
        if re.search('^/' + self.MODNAME, req.path_info):
            return True
        return None
    def process_request(self, req):
        '''Processing incoming requests. The main dispatcher.
        All paths must be in the form of /controller/action/data.
        Do not accept GET style parameters.
        For example:
        - /pmmm/project/lm
        - /pmmm/project/am
        - /pmmm/project/au
        ...
        Here, each action corresponds to a command of proj-admin.       
        We may have other actions as well, that corresponds to other tools.
        For example:
        - /pmmm/rel/tr
        These correspond to commands of rel-admin, etc.
        '''
        match = re.match('/' + self.MODNAME +'/*([^/]+)?/*([^/]+)?/*([^/]+)?',
                         req.path_info)
        if not match:
            return self.return_error('Wrong URL: ' + req.path_info)
        self.controller = match.group(1)
        self.action = match.group(2)
        self.data = match.group(3)
        if self.data:
            self.data = urllib.unquote(self.data)
        if self.controller == None:
            self.controller = ""
        if self.action == None:
            self.action = ""
        if self.data == None:
            self.data = ""
        self.log.debug("controller=%s action=%s data=%s" %
                       (self.controller, self.action, self.data))
        # Right now we only take one controller
        if not self.controller or self.controller == "project":
            # Default action is to list all projects
            p = ProjectController(self)
            return p.handle_action(req, self.action, self.data)        
        if self.controller == "user":
            c = UserController(self)
            return c.handle_action(req, self.action, self.data)
        if self.controller =="hours":
            if (self.action == 'prs'):
                return self._submit_report(req, self.data)
            if (self.action =='prajax'):
                return self._view_report(req,self.data)
            if (self.action == 'prlist'):
                return self._list_report(req,self.data)
            if (self.action == "pclist"):
                return self._list_check(req,self.data)
            if (self.action == "pglist"):
                return self._list_config(req,self.data)
            if (self.action == "pwlist"):
                return self._write_work_report(req,self.data)
            if (self.action == "sendreport"):
                return self._send_work_report(req,self.data)
            if (self.action == "prc"):
                return self._submit_check(req,self.data)
            if (self.action == "Synchronous"):
                return self._config_Synchronous(req,self.data)
            if (self.action =="project_proj_user"):
                return self._proj_user_Synchronous(req,self.data)
            if (self.action == "addWorkType"):
                return self._config_addWorkType(req,self.data)
            if (self.action == "du"):
                return self._add_manager(req,self.data)
            if (self.action == "dere"):
                return self._delete_record(req,self.data)
            if (self.action == "er"):
                return self._update_record(req,self.data)
            if (self.action == "editManager"):
                return self._edit_manager(req,self.data)
            if (self.action == "listProject"):
                return self._list_project(req,self.data)
            if (self.action == "ers"):
                return self._edit_report_submit(req,self.data)
            if (self.action == "plpl"):
                return self._list_project_users(req,self.data)
            if (self.action == "dpm"):
                return self._delete_proj_manager(req,self.data)
            if (self.action == "palist"):
                return self._analysis_list(req,self.data)
            if (self.action == "anaCount"):
                return self._analysis_count(req,self.data)
            if (self.action == "workdepCount"):
                return self._workdep_count(req,self.data)
            if (self.action == "viewReport2"):
                return self._view_report_form2(req,self.data)
            if (self.action == "viewReport3"):
                return self._view_report_form3(req,self.data)
            if (self.action == "listWorkType"):
                return self._list_workType(req,self.data)
            if (self.action == "deleWt"):
                return self._delete_workType(req,self.data)
            if (self.action == "pqlist"):
                return self._hour_query_list(req,self.data)
            if (self.action == "queryHour"):
                return self._hour_query_result(req,self.data)
            if (self.action == "queryHourX"):
                return self._hour_query_proj_result(req,self.data)
            if (self.action == "listUserZh"):
                return self._list_user_zh(req,self.data)
            if (self.action == "addUserZh"):
                return self._add_user_zh(req,self.data)
            if (self.action == "writeProjAndUser"):
                return self._write_proj_user(req,self.data)
            if (self.action == "addProjZh"):
                return self._add_proj_zh(req,self.data)
            if (self.action == "delUserZh"):
                return self._del_user_zh(req,self.data)
            if (self.action == "delProjZh"):
                return self._del_proj_zh(req,self.data)
            if (self.action == "np"):
                return self._new_project(req,self.data)
            if (self.action == "au"):
                return self._add_user(req,self.data)
            if (self.action == "duforP"):
                return self._del_user_forP(req,self.data)
            if (self.action == "auforP"):
                return self._add_user_forP(req,self.data)
            if (self.action == "apforU"):
                return self._add_proj_forU(req,self.data)
            if (self.action == "dpforU"):
                return self._del_proj_forU(req,self.data)
            if (self.action == "addDepView"):
                return self._add_dep_view(req,self.data)
            if (self.action == "addDepInfo"):
                return self._add_dep_info(req,self.data)
            if (self.action == "listDep"):
                return self._list_dep(req,self.data)
            if (self.action == "listDepUsers"):
                return self._list_dep_users(req,self.data)
            if (self.action == "doDelDep"):
                return self._do_del_dep(req,self.data)
            if (self.action == "doAddDep"):
                return self._do_add_dep(req,self.data)
            if (self.action == "addDepMana"):
                return self._add_dep_mana(req,self.data)
            if (self.action == "addDepViceMana"):
                return self._add_dep_vice_mana(req,self.data)
            if (self.action == "delDepMana"):
                return self._del_dep_mana(req,self.data)
            if (self.action == "delDepViceMana"):
                return self._del_dep_vice_mana(req,self.data)
            if (self.action == "delDep"):
                return self._del_dep(req,self.data)
            if (self.action =="delproject"):
                return self._del_project(req,self.data)
            if (self.action == "modifyDep"):
                return self._modify_dep(req,self.data)
            if (self.action == "delUser"):
                return self._del_user(req,self.data)
            if (self.action == "delDuser"):
                return self._del_database_user(req,self.data)
            if (self.action == "setuserlo"):
                return self._set_database_user_leave(req,self.data)
            if (self.action == "lufd"):
                return self._list_user_for_del(req,self.data)
            if (self.action == "wrdlist"):
                return self._work_record_distributed_list(req,self.data)
            if (self.action == "ajax"):
                return self._ajax(req,self.data)
            if (self.action == "userlevel"):
                return self._user_level(req,self.data)
            if (self.action =="usertype"):
                return self._add_user_type(req,self.data)
            if (self.action =="addUserworkType"):
                return self._add_user_workType(req,self.data)
            if (self.action == "addUserLevel"):
                return self._adduser_level(req,self.data)
            if (self.action == "exportUserData"):
                return self._export_userdate(req,self.data)
            if (self.action =="timeRecord"):
                return self._time_record(req,self.data)
            if (self.action == "workCount"):
                return self._work_count(req,self.data)
            if (self.action =="usersalary"):
                return self._user_salary_list(req,self.data)
            if (self.action =="addUsersalary"):
                return self._add_user_salary(req,self.data)
            if (self.action =="updateUsersalary"):
                return self._update_user_salary(req,self.data)
            if (self.action =="expend"):
                return self._add_spend(req,self.data)
            if (self.action =="addexpend"):
                return self._add_proj_expend(req,self.data)
            if (self.action =="addfinanceType"):
                return self._add_financeType(req,self.data)
            if (self.action =="expendcount"):
                return self._expend_count(req,self.data)
            if (self.action =="expender"):
                return self._expend_edit(req,self.data)
            if (self.action =="editexpend"):
                return self._expend_edits(req,self.data)
            if (self.action =="derexpend"):
                return self._dere_expend(req,self.data)
            if (self.action =="addleaofUserZh"):
                return self._add_leave_off_user(req,self.data)
            if (self.action =="import_view"):
                return self._import_view(req,self.data)
            if (self.action =="import"):
                return self._import_excel(req,self.data)
            if (self.action =="adduserworkType"):
                return self._add_user_work_type(req,self.data)
        return self.return_error('Wrong URL: ' + req.path_info)
    def return_error(self, str):
        self.log.debug("error: "+str)
        return 'pm_error.html', {'pm_errmsg' : str}, None
    #----------------------------------------------------------------------
    # Private methods
    #----------------------------------------------------------------------
    def _project(self, req):
        '''We implement project controller within this class.'''
        p = ProjectController(self)
        return p.handle_action(req, self.action, self.data)
    def _add_financeType(self,req,data):
        financetypes = req.args['financeType']
        db = self.env.get_db_cnx()
        #判断提交上来的工作类型是不是list,如果是则循环执行，不是则直接写入proj_type表
        if type(financetypes) is list:
            for w in financetypes:
                gl_othertype.add_expend_type(db,w)
        else:
            gl_othertype.add_expend_type(db,financetypes)
        data = {"pm_href":req.href.pmmm(),
                "pm_work":financetypes,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_configuration.html",data,None
    def _add_user_work_type(self,req,data):
        user_work_type=req.args['user_work_type']
        db = self.env.get_db_cnx()
        if type(user_work_type) is list:
            for w in user_work_type:
                gl_othertype.add_user_work_type(db,w)
        else:
            gl_othertype.add_user_work_type(db,user_work_type)
        data = {"pm_href":req.href.pmmm(),
                "pm_work":user_work_type,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_configuration.html",data,None
    def encrypt(self,s):
        tlist = []
        n = len(s)
        addsize = 10 - n -1
        data = [random.randint(0,10) for i in range(addsize)]
        slist = [n] + data + list(s)
        for element in slist:
            element = (int)(element)*8 + 32
            element = chr((int)(element))
            tlist = tlist + [element]
        tlist = ''.join(tlist)
        return tlist
    def decrypt(self,s):
        tlist = []
        for element in s:
            element = ord(element)
            element = ((int)(element)-32)/8
            element = str(element)
            tlist = tlist + [element]
        numsize = int(tlist[0])
        tlist = tlist[10-numsize:10:1]
        tlist = ''.join(tlist)
        return tlist
    def _dictUser(self):
        db = self.env.get_db_cnx()
        dictUser={}
        user_info=gl_user.select_user_name(db)
        for u_i in user_info:
            user_name=u_i[0]
            user_namezh=u_i[1]
            dictUser[u_i[0]]=user_namezh
        return dictUser
    def _dictProj(self):
        db = self.env.get_db_cnx()
        dictProj={}
        result=gl_proj_info.select_proj_info(db)
        for re in result:
            projname=re[0]
            projname_zh=re[1]
            dictProj[re[0]]=projname_zh
        return dictProj
    def _user_salarylist(self,req):
        dictU=self._dictUser()
        dictS={}
        db = self.env.get_db_cnx()
        nosalaryusers=gl_user.select_user_nosalary(db)
        salaryusers=gl_user.select_user_have_salary(db,str(0))
        leofsalaryusers=gl_user.select_user_have_salary(db,str(1))
        alluser=gl_user.select_all_user_have_salary(db)
        for un in alluser:
            for u in un:
                salary=gl_user.select_user_salary(db,str(u))
                for slr in salary:
                  for s in slr:
                    dictS[u]=self.decrypt(s)
        data = {"pm_href":req.href.pmmm(),
                "alluser":alluser,
                "salaryusers":salaryusers,
                "dictU":dictU,
                "dictS":dictS,
                "nosalaryusers":nosalaryusers,
                "leofsalaryusers":leofsalaryusers,
                "is_trac_admin": req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")
                }
        return data
    #导入考勤记录表
    def _import_view(self,req,data):
        data={'pm_href':req.href.pmmm(),
              'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
              'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_import_excel.html",data,None
    
    def _getdate(self,date):
        s_date = datetime.date(1899, 12, 31).toordinal() - 1
        if isinstance(date, float) and date > 1:
            date = int(date)
            d = datetime.date.fromordinal(s_date + date)
            return d.strftime("%Y-%m-%d")
        else:
            return '00000000'  
    #导入考勤记录表
    def _import_excel(self,req,data):
        upload = req.args['import-file']
        tempuploadedfile = tempfile.mktemp()
        flags = os.O_CREAT + os.O_WRONLY + os.O_EXCL
        if hasattr(os, 'O_BINARY'):
            flags += os.O_BINARY
        targetfile = os.fdopen(os.open(tempuploadedfile, flags), 'w')
        try:
            shutil.copyfileobj(upload.file, targetfile)
        finally:
            targetfile.close()
        book = xlrd.open_workbook(tempuploadedfile)
        sheet = book.sheet_by_index(0)
        db =  self.env.get_db_cnx()
        cursor = db.cursor()
        i=0
        anaWay=int(req.args['anaWay'])
        for r in range (1,len(sheet.col_values(0))):
            row_values0=sheet.row_values(r)[0]
            row_values1=sheet.row_values(r)[1]
            row_values2=sheet.row_values(r)[2]
            row_values3=sheet.row_values(r)[3]
            row_values4=sheet.row_values(r)[4]
            row_values5=sheet.row_values(r)[5]
            row_values6=sheet.row_values(r)[6]
            if anaWay==1:
                row_values8=sheet.row_values(r)[8]
                row_values7=sheet.row_values(r)[7]
                sql="select record_id from attendance_record where user_number='"+row_values1+"'and date='"+row_values3+"' and starttime='"+row_values4+"' and endtime1='"+row_values5+"' and endtime2='"+row_values6+"' and endtime3='"+row_values7+"' and endtime4='"+row_values8+"'"
                cursor.execute(sql)
                record_id=cursor.fetchone()
                if record_id!=None:
                    print 'the record is exist!'
                else:
                    cursor.execute("insert into attendance_record(record_id,dep_name,user_number,user_namezh,date,starttime,endtime1,endtime2,endtime3,endtime4) values(null,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(row_values0,row_values1,row_values2,row_values3,row_values4,row_values5,row_values6,row_values7,row_values8))
                    db.commit()
                    i+=1
            if anaWay==2:
                work_date=self._getdate(row_values3)
                record_id=gl_proj_hours_record.select_import_proj_hours_record(db,row_values0,row_values1,work_date,row_values6)
                if record_id!=None:
                    print 'the record is exist'
                else:
                        localtime=time.strftime('%Y-%m-%d',time.localtime(time.time()))
                        check_user=req.authname
                        work_date=self._getdate(row_values3)
                        write_time=self._getdate(row_values5)
                        gl_proj_hours_record.import_insert_into_table(db,row_values0,row_values1,row_values2,work_date,row_values5,row_values4,row_values6,"",1,check_user,work_date,localtime)
                        i+=1
        message='本次成功导入'
        message1='条数据!'
        data = {"pm_href":req.href.pmmm(),
                "message":message+str(i)+message1,
                "record_id":record_id,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status.html",data,None
    def _user_salary_list(self,req,data):
        data=self._user_salarylist(req)
        return "pm_user_salary.html",data,None
    def _add_user_salary(self,req,data):
        db = self.env.get_db_cnx()
        salary = req.args["salary"]
        rid = req.args["rid"]
        if isinstance(rid,list):
           for i in range(0,len(rid)):
              gl_user.add_user_salary(db,self.encrypt(salary[i]),rid[i])
              
        else:
              gl_user.add_user_salary(db,self.encrypt(salary),rid)
        data=self._user_salarylist(req)
        return "pm_user_salary.html",data,None
    def _update_user_salary(self,req,data):
        db =  self.env.get_db_cnx()
        users = req.args["user"]
        if isinstance(users,list):
            for i in range(0,len(users)):
                gl_user.delete_user_salary(db,users[i])
        else:
            gl_user.delete_user_salary(db,users)
        data=self._user_salarylist(req)
        return "pm_user_salary.html",data,None
    def _add_spend(self,req,data):
        add_stylesheet(req,"pmmm/css/datepicker.css")
        add_script(req,"pmmm/js/datepicker.js")
        add_script(req,"pmmm/js/eye.js")
        add_script(req,"pmmm/js/utils.js")
        add_script(req,"pmmm/js/layout.js")
        add_script(req,"pmmm/js/cookieHelper.js")
        db = self.env.get_db_cnx()
        result1 = gl_othertype.select_expend_type_name(db)
        dictP = self._dictProj()
        result=gl_proj_user.select_projs(db)
        is_proj_admin = req.perm.has_permission("PROJECT_ADMIN")
        is_trac_admin = req.perm.has_permission("TRAC_ADMIN")
        data={'pm_href':req.href.pmmm(),
              'proj_names':result,
              'proj_types':result1,
              'dictP':dictP,
              'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
              'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_add_expend.html",data,None
    def _proj_expend_list(self,req,startDate,endDate):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("select proj_name,expend_type,expend,time,remarks,rowid from proj_expend where time>='"+startDate+"' and time<='"+endDate+"' order by proj_name")
        listResult=cursor.fetchall()
        dictP=self._dictProj()
        queryList=[]
        for listRe in listResult:
            queryList.append({'pn':listRe[0],'et':listRe[1],'ex':listRe[2],'ti':listRe[3],'rm':listRe[4],'rd':listRe[5]})
        data = {"pm_href":req.href.pmmm(),
                "queryList":queryList,
                "dictP":dictP,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return data
    def _add_proj_expend(self,req,data):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        proj_name = req.args['proj']
        expend_type = req.args['expend_type']
        time = req.args['time']
        remarks = req.args['Remarks']
        expend = req.args['expend']
        cursor.execute("INSERT INTO proj_expend(proj_name,expend_type,expend,time,remarks) VALUES (%s,%s, %s, %s, %s)", (proj_name,expend_type,expend,time,remarks))
        db.commit()
        theYear = time.split("-")[0]
        theMonth = time.split("-")[1]
        startDate = theYear+"-"+theMonth+"-"+"01"
        endDate = theYear+"-"+theMonth+"-"+"31"
        data=self._proj_expend_list(req,startDate,endDate)
        return "pm_proj_expend_list.html",data,None
    def _expend_edit(self,req,data):
        add_stylesheet(req,"pmmm/css/datepicker.css")
        add_script(req,"pmmm/js/datepicker.js")
        add_script(req,"pmmm/js/eye.js")
        add_script(req,"pmmm/js/utils.js")
        add_script(req,"pmmm/js/layout.js")
        add_script(req,"pmmm/js/cookieHelper.js")
        proj_name = req.args['proj']
        expend_type = req.args['expend_type']
        time = req.args['time']
        remarks = req.args['Remarks']
        expend = req.args['expend']
        rowid = req.args['rowid']
        dictP = self._dictProj()
        db = self.env.get_db_cnx()
        result=gl_proj_user.select_user_proj_name(db,req.authname)
        result1 = gl_othertype.select_expend_type_name(db)
        data={'pm_href':req.href.pmmm(),
              'proj_name':proj_name,
              'time':time,
              'remarks':remarks,
              'expend':expend,
              'expend_type':expend_type,
              'rowid':rowid,
              'proj_names':result,
              'expend_types':result1,
              'dictP':dictP,
              'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
              'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_edit_expend.html",data,None
    def _expend_edits(self,req,data):
        is_proj_admin = req.perm.has_permission("PROJECT_ADMIN")
        is_trac_admin = req.perm.has_permission("TRAC_ADMIN")
        add_stylesheet(req,"pmmm/css/datepicker.css")
        add_script(req,"pmmm/js/datepicker.js")
        add_script(req,"pmmm/js/eye.js")
        add_script(req,"pmmm/js/utils.js")
        add_script(req,"pmmm/js/layout.js")
        add_script(req,"pmmm/js/cookieHelper.js")
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        proj_name = req.args['proj']
        expend_type = req.args['expend_type']
        time = req.args['time']
        remarks = req.args['Remarks']
        expend = req.args['expend']
        rowid = req.args['rowid']
        cursor.execute("update proj_expend set proj_name='"+proj_name+"',expend_type='"+expend_type+"',expend='"+expend+"',time='"+time+"',remarks='"+remarks+"' where rowid='"+rowid+"'")
        db.commit()
        theYear = time.split("-")[0]
        theMonth = time.split("-")[1]
        startDate = theYear+"-"+theMonth+"-"+"01"
        endDate = theYear+"-"+theMonth+"-"+"31"
        data=self._proj_expend_list(req,startDate,endDate)
        return "pm_proj_expend_list.html",data,None
    def _dere_expend(self,req,data):
        db=self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("select time from proj_expend where rowid='"+data+"'")
        dt=cursor.fetchone()
        for d in dt:
            time=d
        sql = "delete from proj_expend where rowid='"+data+"'"
        cursor.execute(sql)
        db.commit()
        theYear = time.split("-")[0]
        theMonth = time.split("-")[1]
        startDate = theYear+"-"+theMonth+"-"+"01"
        endDate = theYear+"-"+theMonth+"-"+"31"
        data=self._proj_expend_list(req,startDate,endDate)
        return "pm_proj_expend_list.html",data,None
    def _proj_hours_record_list(self,req,user_name,startDate,endDate):
        list1=[]
        dictP=self._dictProj()
        dictU=self._dictUser()
        dictC={}
        db=self.env.get_db_cnx()
        if type(user_name) is list:
            for name  in user_name:
                listResult=gl_proj_hours_record.select_list_table(db,name,startDate,endDate)
                for listRe in listResult:
                    arg2 = listRe[10]
                    if arg2 is None:
                        arg2 = ""
                    cZh=uZh=gl_user.select_userZh_name(db,arg2)
                    dictC[listRe[10]] = cZh
                    list1.append({'pn':listRe[0],'un':listRe[1],'wt':listRe[2],'wd':listRe[3],'mt':listRe[4],'wtl':listRe[5],'rw':listRe[6],'cs':listRe[7],'uf':listRe[8],'mf':listRe[9],'cu':listRe[10],'wti':listRe[11],'ct':listRe[12]})
        else:
            listResult=gl_proj_hours_record.select_list_table(db,user_name,startDate,endDate)
            for listRe in listResult:
                    arg2 = listRe[10]
                    if arg2 is None:
                        arg2 = ""
                    cZh=uZh=gl_user.select_userZh_name(db,arg2)
                    dictC[listRe[10]] = cZh
                    list1.append({'pn':listRe[0],'un':listRe[1],'wt':listRe[2],'wd':listRe[3],'mt':listRe[4],'wtl':listRe[5],'rw':listRe[6],'cs':listRe[7],'uf':listRe[8],'mf':listRe[9],'cu':listRe[10],'wti':listRe[11],'ct':listRe[12]})
        data = {"pm_href":req.href.pmmm(),
                "dictP":dictP,
                "dictU":dictU,
                "dictC":dictC,
                "queryList":list1,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return data
    #提交工时记录的方法，从form表单获取数据，将数据写入工时记录表中
    def _submit_report(self,req,data):
        proj_name = req.args['proj']
        milestone = req.args['milestone']
        work_type = req.args['proj_type']
        work_date = req.args['proj_date']
        work_date_length = req.args['proj_hour']
        user_remarks = req.args['userRemarks']
        #通过req对象获取当前登录的用户名
        user_name = req.authname
        #获取填报工时的时间
        write_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        anaMonth=time.strftime('%Y-%m',time.localtime(time.time()))
        theYear = anaMonth.split("-")[0]
        theMonth = anaMonth.split("-")[1]
        mr = calendar.monthrange(int(theYear),int(theMonth))[1]
        startDate = anaMonth+"-"+"01"
        endDate = anaMonth+"-"+str(mr)
        #插入新记录时，check_status状态为0即为未审核状态
        check_status = 0
        #插入新记录时，查看是否是重复提交
        username=""
        db=self.env.get_db_cnx()
        result=gl_proj_hours_record.select_table(db,proj_name,milestone,work_type,work_date,work_date_length,user_remarks)  
        if user_remarks=="":
            data = self._list_report1(req,data)
            data['errorinfo2'] = '工作内容为空,请填写工作内容！'
            return "pm_report.html",data,None 
        if write_time<work_date:
            data = self._list_report1(req,data)
            data['errorinfo1'] = '填写时间早于工作日期,请重新选择工作日期！'
            return "pm_report.html",data,None
        for  username in result:
            for u in username:
                if  user_name==u:
                    data = self._list_report1(req,data)
                    data['name']=result
                    data['name1']=username
                    data['name2']=user_name
                    data['errorinfo'] = '该条记录已存在,请不要提交重复的记录！'
                    return "pm_report.html",data,None
        else:
          gl_proj_hours_record.insert_into_table(db,proj_name,user_name,work_type,work_date,milestone,work_date_length,user_remarks,check_status,write_time)
        data=self._proj_hours_record_list(req,user_name,startDate,endDate)
        return "pm_query_hour_result1.html",data,None
    def today(self):
          return date.today()
    def getdayofday(self,n=0):
           if(n<0):
              n=abs(n)
              return date.today()-timedelta(days=n)
           else:
              return date.today()+timedelta(days=n)
    #统计工时记录填写时间不合格人员
    def _time_record(self,req,data):
        db=self.env.get_db_cnx()
        add_script(req,"pmmm/js/exportExcel.js")
        days=int(req.args["days"])
        anaMonth = req.args['anaMonth']
        theYear = anaMonth.split("-")[0]
        theMonth = anaMonth.split("-")[1]
        mr = calendar.monthrange(int(theYear),int(theMonth))[1]
        startDate = anaMonth+"-"+"01"
        endDate = anaMonth+"-"+str(mr)
        startDates = anaMonth+"-"+"01"
        d=self.getdayofday(-7)
        endDates=str(d)
        dictU=self._dictUser()
        dict1={}
        dict3={}
        dictD={}
        user_list=[]
        lostDay=[]
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        recordusers=gl_proj_hours_record.select_username_table(db,startDate,endDate)
        users_info=gl_user.select_users_dep_id(db)
        users=gl_user.select_users_state_zero(db)
        for us_id in users_info:
            user=us_id[0]
            user_id=us_id[1]
            user_list.append(user)
            id_name=gl_department.select_dep_name(db,str(user_id))
            dictD[user]=id_name
            dayout=gl_proj_hours_record.select_timeout_table(db,startDate,endDate,us_id[0])
            for day in dayout:
                dict1[us_id[0]]=day
            count=gl_proj_hours_record.select_sumworkdate_table(db,startDates,endDates,us_id[0])
            for c in count:
                if c!=None:
                    d=days-int(c)
                    if d>0:
                        dict3[us_id[0]]=d
                    else:
                        dict3[us_id[0]]=0          
        for user in users:
            if user not in recordusers:
                strUser = "".join(user)
                if strUser in dictU.keys():
                    theUser=dictU[strUser]
                lostDay.append(theUser)
        data={'pm_href':req.href.pmmm(),
              'dict1':dict1,
              'dict3':dict3,
              'dictD':dictD,
              'dictU':dictU,
              'lostDay':lostDay,
              'users_info':users_info,
              'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
              'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return  "pm_workdeuser_list.html",data,None
    #删除用户下的项目
    def _del_proj_forU(self,req,data):
        db = self.env.get_db_cnx()
        uc = UserController(self)
        result = uc._del_project(req,data)
        projs = req.args["proj"]
        user = data
        if isinstance(projs,list):
            for p in projs:
                gl_proj_user.delete_user_proj(db,p,user)
        else:
               gl_proj_user.delete_user_proj(db,projs,user)
        return  "pm_user_done.html",result,None
    #为用户添加项目
    def _add_proj_forU(self,req,data):
        db = self.env.get_db_cnx()
        uc = UserController(self)
        result = uc._add_project(req,data)
        projs = req.args["proj"]
        user = data
        if isinstance(projs,list):
            for  p in projs:
                gl_proj_user.add_user_proj(db,p,user)
        else:
                gl_proj_user.add_user_proj(db,projs,user)
        return "pm_user_done.html",result,None
    #为项目添加用户
    def _add_user_forP(self,req,data):
        db = self.env.get_db_cnx()
        pc = ProjectController(self)
        result = pc._add_user(req,data)
        proj = req.args["project"]
        users = req.args["user"]
        if isinstance(users,list):
            for u in users:
                gl_proj_user.add_proj_user(db,proj,u)
        else:
                gl_proj_user.add_proj_user(db,proj,users)
        return "pm_release_done.html",result,None
    #删除项目下的用户
    def _del_user_forP(self,req,data):
        db = self.env.get_db_cnx()
        pc = ProjectController(self)
        result = pc._delete_user(req,data)
        proj = req.args["project"]
        users = req.args["user"]
        if isinstance(users,list):
            for u in users:
                gl_proj_user.delete_user_proj(db,proj,u)
        else:
                gl_proj_user.delete_user_proj(db,proj,users)
        return "pm_release_done.html",result,None
    #添加新用户
    def _add_user(self,req,data):
        username = req.args["user"]
        username = username.strip()
        usernameZh = req.args["usernameZh"]
        usernameZh = usernameZh.strip()
        uc = UserController(self)
        result = uc._add_user(req,data)
        db = self.env.get_db_cnx()
        gl_user.add_user(db,username,usernameZh)
        return "pm_user_done.html",result,None
    #导出用户数据
    def _export_userdate(self,req,data):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("delete from users")
        db.commit()
        listResult = gl_user.select_user_info(db)
        for listRe in listResult:
                    username = listRe[0]
                    username_zh=listRe[1]
                    dep_id=listRe[2]
                    user_level=listRe[3]
                    use_salary=listRe[4]
                    use_state=listRe[5]
                    use_work_type =listRe[6]
                    sql="insert into users values(null,%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql,(username,username_zh,dep_id,user_level,use_salary,use_state,use_work_type ))
                    db.commit()
        data = {"pm_href":req.href.pmmm(),
                'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return 'pm_submit_status.html', data, None
    #创建新项目
    def _new_project(self,req,data):
        proj_name = req.args["name"]
        proj_name = proj_name.strip()
        proj_nameZh = req.args["nameZh"]
        proj_nameZh = proj_nameZh.strip()
        user_name = req.args["user"]
        pr = ProjectController(self)
        result = pr._new_project(req,data)
        db = self.env.get_db_cnx()
        gl_proj_info.add_project(db,proj_name,proj_nameZh)
        if isinstance(user_name,list):
            for u in user_name:
                gl_proj_user.add_user_proj(db,proj_name,u)
        else:
                gl_proj_user.add_user_proj(db,proj_name,user_name)
        return "pm_release_done.html",result,None
    #列出填报工时页面，从数据库获取该登录用户所在的项目，将项目写入页面下拉框供用户选择
    def _list_report(self,req,data):
        data=self._list_report1(req,data)
        return "pm_report.html",data,None
    def _list_report1(self,req,data):
        
        add_stylesheet(req,"pmmm/css/datepicker.css")
        add_script(req,"pmmm/js/datepicker.js")
        add_script(req,"pmmm/js/eye.js")
        add_script(req,"pmmm/js/utils.js")
        add_script(req,"pmmm/js/layout.js")
        add_script(req,"pmmm/js/cookieHelper.js")
        dictP = self._dictProj()
        dictU = {}
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        authZh=gl_user.select_userZh_name(db,req.authname)
        result=gl_proj_user.select_user_proj_name(db,req.authname)
        result1 = gl_othertype.select_proj_type_name(db)
        proj_nameDatas=[]
        ms=[]
        for proj_names in result:
            for proj_name in proj_names:
                proj_nameDatas.append(proj_name)
        #由于里程碑分别存放在各自项目的数据库中，所以通过项目路径访问获取各自的里程碑列表
        for proj_nameData in proj_nameDatas:
            list1 =[]
            filePath="/home/trac/"+proj_nameData+"/db/trac.db"
            cx = sqlite.connect(filePath)
            cu = cx.cursor()
            #只查询出未完成的里程碑
            cu.execute("select name from milestone where completed=0")
            ms.append(cu)
            db = self.env.get_db_cnx()
            listRes =gl_proj_hours_record.select_unreview_record_table(db,req.authname)
            for listRe in listRes:
                arg1 = listRe[9]
                if arg1 is None:
                    arg1 = ""
                uZh1=gl_user.select_userZh_name(db,arg1)
                dictU[listRe[9]] = uZh1
                list1.append({'pn':listRe[0],'un':listRe[1],'wt':listRe[2],'wd':listRe[3],'mt':listRe[4],'wtl':listRe[5],'rw':listRe[6],'cs':listRe[7],'mf':listRe[8],'cu':listRe[9],'uf':listRe[10]})
        data={'pm_href':req.href.pmmm(),
              'proj_names':result,
              'proj_types':result1,
              'milestones':ms,
              'check_list':list1,
              'dictP':dictP,
              'authZh':authZh,
              'dictU':dictU,
              'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
              'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return data
    #该方法用于列出该登录项目经理需要审核工时记录，列出的记录为该项目经理所在项目组下员工提交的状态为未审核的工时记录
    def _list_check(self,req,data):
        #查询出该项目经理下的所有项目
        dictP = self._dictProj()
        dictU = self._dictUser()
        #查询部门经理部门下的用户
        re_result1 = []
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        results2=gl_user.select_dep_user(db,req.authname)
        results =gl_project.select_project_manager_pros(db,req.authname)
        for proj in results:
            for pjt in proj:
                users=gl_proj_user.select_proj_manager_users(db,pjt)
        #根据部门用户查询待审核的记录
        for rs2 in results2:
             res2=gl_proj_hours_record.select_audit_table(db,rs2)
             for re2 in res2:
                 re_result1.append({'pn':re2[0],'un':re2[1],'wt':re2[2],'wd':re2[3],'mt':re2[4],'wtl':re2[5],'rw':re2[6],'uf':re2[7],'wti':re2[8]})
        #根据项目员工查询出待审核的记录
        for ur in users:
                res=gl_proj_hours_record.select_audit_table(db,ur)
                for re1 in res:
                    theRe = {'pn':re1[0],'un':re1[1],'wt':re1[2],'wd':re1[3],'mt':re1[4],'wtl':re1[5],'rw':re1[6],'uf':re1[7],'wti':re1[8]}
                    if theRe not in re_result1:
                        re_result1.append(theRe)
        #根据项目查询出待审核的记录
        for result0 in results:
            res1=gl_proj_hours_record.select_proj_audit_table(db,result0)
            for re1 in res1:
                theRe = {'pn':re1[0],'un':re1[1],'wt':re1[2],'wd':re1[3],'mt':re1[4],'wtl':re1[5],'rw':re1[6],'uf':re1[7],'wti':re1[8]}
                if theRe not in re_result1:
                    re_result1.append(theRe)
        data1 = {'pm_href':req.href.pmmm(),
                 're_result1':re_result1,
                 'dictP':dictP,
                 'dictU':dictU,
                 'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                 'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")
                }
        return "pm_check.html",data1,None
    #提交审核记录方法
    def _submit_check(self,req,data):
        rowid = req.args['rowid']
        db = self.env.get_db_cnx()
        #获取审核记录时间
        checked_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        #判断提交的记录是否为list，如果是多条则循环执行，否则直接根据id更新记录
        if (type(rowid) is list):
           for rw in rowid:
               rid = int(rw)
               check_name = "check_status"+rw
               manager_remark_name = "manaRemarks"+rw
               manager_remark = req.args[manager_remark_name]
               if int(req.args[check_name])>0:
                   check_status = str(req.args[check_name])
                   gl_proj_hours_record.submit_check_table(db,check_status,manager_remark,req.authname,checked_time,rid)
        else:
            rid = int(rowid)
            check_name = "check_status"+rowid
            manager_remark_name = "manaRemarks"+rowid
            manager_remark = req.args[manager_remark_name]
            if int(req.args[check_name])>0:
                check_status = str(req.args[check_name])
                gl_proj_hours_record.submit_check_table(db,check_status,manager_remark,req.authname,checked_time,rid)
        data1 = {'pm_href':req.href.pmmm(),
                 'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                 'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")
        }
        return "pm_submit_status.html",data1,None
    def _write_work_report(self,req,data):
        times=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        db = self.env.get_db_cnx()
        #获取当前用户名
        user_name = req.authname
        #获取当前用户的中文名
        username_zh=gl_user.select_userZh_name(db,user_name)
        dep_id=gl_user.select_user_depid(db,user_name)
        mail_rec=gl_department.select_dep_email(db,dep_id)
        #判断当前星期数
        daytime=datetime.datetime.now()
        day=daytime.weekday()
        if day<3:
            time1=time.strftime('%Y-%m',time.localtime(time.time()))
            t1=self.getdayofday(-7-day)
            t2=self.getdayofday(-1-day)
            startDate=str(t1)
            endDate=str(t2)
        else:
            time1=time.strftime('%Y-%m',time.localtime(time.time()))
            t1=self.getdayofday(-day)
            t2=self.getdayofday(6-day)
            startDate=str(t1)
            endDate=str(t2)
        work=gl_proj_hours_record.select_weekReport_table(db,startDate,endDate,user_name)
        list=[]
        dictP=self._dictProj()
        for listRe in work:
            list.append({'pj':listRe[0],'wt':listRe[1],'wd':listRe[2],'wk':listRe[3],'wl':listRe[4]})
        data={'pm_href':req.href.pmmm(),
              'mail_rec':mail_rec,
              'work':list,
              'times':times,
              'startDate':startDate,
              't2':t2,
              'username_zh':username_zh,
              'user_name':user_name,
              'dictP':dictP,
              'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
              'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_write_email.html",data,None
    def _time(self,year):
        startDate1=year+'-'+'01'+'-'+'01'
        endDate1=year+'-'+'01'+'-'+'31'
        startDate2=year+'-'+'02'+'-'+'01'
        endDate2=year+'-'+'02'+'-'+'29'
        startDate3=year+'-'+'03'+'-'+'01'
        endDate3=year+'-'+'03'+'-'+'31'
        startDate4=year+'-'+'04'+'-'+'01'
        endDate4=year+'-'+'04'+'-'+'30'
        startDate5=year+'-'+'05'+'-'+'01'
        endDate5=year+'-'+'05'+'-'+'31'
        startDate6=year+'-'+'06'+'-'+'01'
        endDate6=year+'-'+'06'+'-'+'30'
        startDate7=year+'-'+'07'+'-'+'01'
        endDate7=year+'-'+'07'+'-'+'31'
        startDate8=year+'-'+'08'+'-'+'01'
        endDate8=year+'-'+'08'+'-'+'31'
        startDate9=year+'-'+'09'+'-'+'01'
        endDate9=year+'-'+'09'+'-'+'30'
        startDate10=year+'-'+'10'+'-'+'01'
        endDate10=year+'-'+'10'+'-'+'31'
        startDate11=year+'-'+'11'+'-'+'01'
        endDate11=year+'-'+'11'+'-'+'30'
        startDate12=year+'-'+'12'+'-'+'01'
        endDate12=year+'-'+'12'+'-'+'31'
        timelist=[(startDate1,endDate1),(startDate2,endDate2),(startDate3,endDate3),(startDate4,endDate4),(startDate5,endDate5),(startDate6,endDate6),(startDate7,endDate7),(startDate8,endDate8),(startDate9,endDate9),(startDate10,endDate10),(startDate11,endDate11),(startDate12,endDate12)]
        return timelist
     #工作量统计汇总
    def _work_count(self,req,data):
        content, output_type = self._process_export(req) 
        req.send_response(200) 
        req.send_header('Content-Type', output_type) 
        req.send_header('Content-Length', len(content)) 
        req.send_header('Content-Disposition', 'filename=工作量汇总表.xls') 
        req.end_headers() 
        req.write(content) 
        raise RequestDone
    def _expend_count(self,req,data):
        content, output_type = self._process_expend_export(req) 
        req.send_response(200) 
        req.send_header('Content-Type', output_type) 
        req.send_header('Content-Length', len(content)) 
        req.send_header('Content-Disposition', 'filename=工作量汇总表.xls') 
        req.end_headers() 
        req.write(content) 
        raise RequestDone
    def _process_expend_export(self,req):
        localtime=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        year=req.args['year']
        titlelist=['费用名称','一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月','合计']
        costname=[]
        startDate1=year+'-'+'01'+'-'+'01'
        endDate12=year+'-'+'12'+'-'+'31'
        timelist=self._time(year)
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        dictP=self._dictProj()
        dictT={}
        dictS={}
        expendname=gl_othertype.select_expend_type_name(db)
        content = cStringIO.StringIO()
        headerStyle = xlwt.easyxf('font: bold on; pattern: pattern solid, fore-colour grey25; borders: top thin, bottom thin, left thin, right thin')
        wb = xlwt.Workbook()
        projs = gl_proj_hours_record.select_time_proj_name_table(db,startDate1,endDate12)
        for prj in projs:
            for pr in prj:
            #在excel文件中添加多个sheet，sheet的名以项目中文名为名
                ws = wb.add_sheet( dictP[pr],cell_overwrite_ok=True )
            #在excel中每个sheet的首行添加首行说明
            titlerow=0
            for title in titlelist:
                ws.write(0, titlerow, unicode(title),headerStyle)
                titlerow+=1
            costsumlist=[]
            for ti in timelist:
             if localtime<ti[0]:
                break
             else:
                #根据用户计算出项目每月的总工时数(group by user_name)
                costmounth=gl_proj_hours_record.select_user_month_work_length(db,pr,ti[0],ti[1])
                clist=[]
                for result in costmounth:
                    costtime=result[0]#员工的每月工作量
                    if costtime!=None:
                        ct=float(costtime)/8
                        if ct>22:
                            cts=22
                        else:
                            cts=round(ct,1)
                    else:
                        cts=""
                    user=result[1]#用户名
                    salary=gl_user.select_salary(db,user)
                    for cs in salary:
                      for c in cs:
                        if self.decrypt(c)!="":
                            hcost=float(self.decrypt(c))/22
                            usercost=hcost*cts
                            ucost=round(usercost,2)
                            dictS[user]=ucost
                        else:
                            dictS[user]=0.0
                        clist.append(dictS[user])
                costsum=sum(clist)
                costsumlist.append(costsum)
            r=0
            for uname in expendname:
                for name in uname:
                    r+=1
                    ws.write(r, 0,  name)
                usermtlist=[]
                for ti in timelist:
                 if localtime<ti[0]:
                    break
                 else:
                    sql="select sum(expend) from proj_expend where proj_name='"+str(pr)+"' AND time>='"+str(ti[0])+"' AND time<='"+str(ti[1])+"' and expend_type='"+str(name)+"'"
                    cursor.execute(sql)
                    expend=cursor.fetchone()
                    for t in expend:
                            if t!=None:
                                days=t
                            else:
                                days=""
                            usermtlist.append(days)
                    dictT[name]=usermtlist
                    sums=0
                    for umt in usermtlist:
                        if umt=='':
                            ut=0.0
                        else:
                            ut=umt
                        sums+=ut
                    c=0
                    for m in dictT[name]:
                        c+=1
                    ws.write(r, c, m)
                    ws.write(r, 13,sums)
            row=0
            sumcosts=0
            for cm in costsumlist:
                      row+=1
                      ws.write(r+1,row,cm)
            for c in costsumlist:
                    sumcosts+=c
            ws.write(r+1,13,sumcosts)
            ws.write(r+1, 0, unicode('人力成本'))
        wb.save(content) 
        return (content.getvalue(), 'application/excel')
    def _process_export(self, req):
        titlelist=['状态','人员','一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月','合计','员工级别','人力成本']
        #获取本地时间
        localtime=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        year=req.args['year']
        anaWay = int(req.args['anaWay'])
        startDate1=year+'-'+'01'+'-'+'01'
        endDate12=year+'-'+'12'+'-'+'31'
        timelist=self._time(year)#时间列表
        content = cStringIO.StringIO()
        db = self.env.get_db_cnx()
        headerStyle = xlwt.easyxf('font: bold on; pattern: pattern solid, fore-colour grey25; borders: top thin, bottom thin, left thin, right thin')
        wb = xlwt.Workbook()
        dictT={}#存放员工每月工作量信息(key为用户英文名,value为存放用户每月工作量的usermtlist)
        dictP=self._dictProj()#存放项目信息(key为项目英文名,value为项目中文名)
        dictU={}#存放用户信息(key为用户英文名,value为项目中文名
        dictS={}#存放用户是否在职(key为用户英文名,value为""或者'离职')
        result=gl_user.select_users_state(db)#在user表中查询用户在职状态和中文名
        for re in result:
            name=re[0]
            name_zh=re[1]#用户中文名
            state=re[2]#是否在职,0为在职,1为离职
            if state==0:
                dictS[re[0]]=""#如果在职，状态为空
            if state==1:
                dictS[re[0]]='离职'
            dictU[re[0]]=name_zh
        #查询数据库proj_hours_record表中在一段时间内(本系统得出的是在统计初输入的时间:例如2012,即时间为2012-01-01至2012-12-31)的所有项目名
        projs = gl_proj_hours_record.select_time_proj_name_table(db,startDate1,endDate12)
        for prj in projs:
            for pr in prj:
                #向excel文件中添加多个sheet，sheet的名以项目中文名为名，没有中文名则显示项目英文名
                ws = wb.add_sheet( dictP[str(pr)],cell_overwrite_ok=True )
            mlist=[]  
            sumlist=[]
            for ti in timelist:#timelist格式为[(2012-01-01,2012-01-31),......,(2012-12-01,2012-12-31)]
             if localtime<ti[0]:#判断当前时间如果小于时间表中的某月月初时间,则停止统计
                break
             else:
                mtlist=[]#当anaWay=2时,存放项目中每人每月的工作量(人天数)
                mtlists=[]#当anaWay=2时,存放项目中每人每月的工作量(人月数)
                if anaWay==1:#当anaWay=1时,统计pproj_hours_record表中实际填写的数据
                    monthtime=gl_proj_hours_record.select_sumtime_table(db,ti[0],ti[1],pr)#查询项目每月的总工作量(单位:小时)
                    for t in monthtime:
                        if t!=None:#项目某月工作量不为空,即不为0时
                            udays=float(t)/8#计算项目每月的工作量(人天)
                            days=round(udays,1)#round方法保留一位小数
                            mt=days
                            m=float(t)/(8*22)#计算项目每月的工作量(人月)
                            ms=round(m,1)
                        else:#项目某月总工作量为0时
                            mt=0.0
                            ms=0.0
                    sumlist.append(mt)#将每月工作量存放在列表中(人天数)
                    mlist.append(ms)#将每月工作量存放在列表中(人月数)
                if anaWay==2:
                    monthtime=gl_proj_hours_record.select_reality_work_length(db,pr,ti[0],ti[1])#查询项目每月m每人的总工作量(group by user_name)
                    for ti in monthtime:
                      for t in ti:
                        if t!=None:
                            udays=float(t)/8#计算项目每人每月的工作量(单位:天)
                            if udays>22:#超过每月实际工作量
                                mt=22#项目人员每月工作量(人天数)
                                ms=1#项目人员每月工作量(人月数)
                            else:
                                days=round(udays,1)
                                mt=days#项目人员每月工作量(人天数)
                                rtdays=float(udays)/22
                                rtday=round(rtdays,1)
                                ms=rtday#项目人员每月工作量(人月数)
                        else:
                            mt=0.0
                            ms=0.0
                        mtlist.append(mt)#将项目人员每月的工作量(人天数)存放在mtlist中
                        mtlists.append(ms)#将项目人员每月的工作量(人月数)存放在mtlists中
                    times=sum(mtlist)#求项目每月所有人的工作量总和(人天数)
                    sumlist.append(times)#将项目每月工作量存放在sumlist中(人天数)
                    times1=sum(mtlists)#求项目每月所有人的工作量总和(人月数)
                    mlist.append(times1)#将项目每月工作量存放在sumlist中(人月数)
            #在excel中每个sheet的首行添加首行说明
            titlerow=0
            for title in titlelist:
                ws.write(0, titlerow, unicode(title),headerStyle)
                titlerow+=1
            #查询每个项目中在时间段内的所有人员
            username=gl_proj_hours_record.select_proj_user_name_table(db,pr,startDate1,endDate12)
            r=0
            for uname in username:
                for name in uname:
                    r+=1
                ws.write(r, 0,  unicode(dictS[name]))#在excel表第一列写用户状态
                ws.write(r, 1,  dictU[name])#在excel表第二列写用户中文名
                #根据时间timelist循环j计算出每个项目中员工每月的工作量
                usermtlist=[]
                for ti in timelist:
                    #统计表包括两种统计方式,anaWay=1时：按数据库中proj_hours_record表实际添加的工时记录计算；anaWay=2时：如果用户每月的工时数超过22个工作日,则以22计算；
                    if anaWay==1:
                        times=gl_proj_hours_record.select_user_sumtime(db,ti[0],ti[1],name,pr)#计算项目中人员工作量(单位:小时/月)
                    if anaWay==2:
                        times=gl_proj_hours_record.select_sumtime(db,ti[0],ti[1],name,pr)
                    for t in times:
                        if t!=None:
                            udays=float(t)/8
                            if anaWay == 1:
                                days=round(udays,1)
                            if anaWay == 2:
                                if udays>22:
                                    days=22.0
                                else:
                                    days=round(udays,1)       
                        else:
                            days=""
                        usermtlist.append(days)#将员工每月工作量存放在usermtlist中(单位:人天)
                    dictT[name]=usermtlist#将员工每月工作量列表存放在字典中
                    sums=0
                    for umt in usermtlist:
                        if umt=='':
                            ut=0
                        else:
                            ut=umt
                        sums+=ut#根据计算出的员工每月的工作量(usermtlist)求其一年内的总工作量
                    c=1 #向excel表中添加员工工作量(sum(work_time_length))以及每月工作量总和
                    for m in dictT[name]:
                        c+=1
                    ws.write(r, c, m)
                    ws.write(r, 14,sums)
            ws.write(r+3, 0,unicode('合计(人天)'))
            ws.write(r+4,0,unicode('合计(人月)'))
            mtrow=1
            for mt in sumlist:
                mtrow+=1
                ws.write(r+3, mtrow,mt)
            mrow=1
            for m in mlist:
                mrow+=1
                ws.write(r+4,mrow,m)
        wb.save(content) 
        return (content.getvalue(), 'application/excel')
    def _send_work_report(self,req,data):
        user_name = req.authname
        nextwork = req.args['nextwork']
        works = req.args['works']
        message=works+nextwork
        mail_host = 'mail.rytong.com'
        mail_user = 'weeklyreport@rytong.com'
        mail_pwd = 'reportweek'
        mail_to=[]
        mail_to = req.args['mail_rec']
        subject = req.args['theme']
        msg = MIMEText(message.encode('utf-8'),_subtype='plain', _charset='utf-8')
        msg['To'] = mail_to
        msg['from'] = mail_user
        msg['subject'] = subject
        try:  
           s = smtplib.SMTP('mail.rytong.com',25)
           s.ehlo()
           s.starttls()
           s.ehlo()
           s.login(mail_user,mail_pwd)
           s.sendmail(mail_user,mail_to.split(','),msg.as_string())  
           s.quit()
        except Exception,e:  
           print e
        data={"pm_href":req.href.pmmm(),
              'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
              'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status.html",data,None
    #列出系统配置页面
    def _list_config(self,req,data):
        data = {'pm_href':req.href.pmmm(),
                'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_configuration.html",data,None
    #同步access文件到数据的方法
    def _config_Synchronous(self,req,data):
        db = self.env.get_db_cnx()
        #由于是全部导入，所以同步之前先删掉之前的记录
        gl_proj_user.delete_alldata(db)
        #实例化ProjectController
        pc = ProjectController(self)
        ss = []
        #调用ProjectController的方法列出所有项目
        projs = pc._list_all_projects()
        #列出每个项目下的用户
        for p in projs:
            ss.append(pc._list_users(p))
        #将项目和用户写入项目用户表
        for p in projs:
            for lu in pc._list_users(p):
                gl_proj_user.add_user_proj(db,p,lu)
        data = {'pm_href':req.href.pmmm(),
                'pm_users':ss,
                'pm_projs':projs,
                'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_configuration.html",data,None
    def _proj_user_Synchronous(self,req,data):
        lists=[]
        db = self.env.get_db_cnx()
        project_manager_user=gl_project.select_all_proj_manager(db)
        proj_users=gl_proj_user.select_users(db)
        for mana_user in project_manager_user:
            if mana_user not in proj_users:
                lists.append(mana_user)
        for m_user in lists:
            for m_u in m_user:
                gl_project.delete_manager(db,m_u)
        data = {'pm_href':req.href.pmmm(),
                'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")
        }
        return "pm_configuration.html",data,None
    #配置工作类型
    def _config_addWorkType(self,req,data):
        worktypes = req.args['workType']
        db = self.env.get_db_cnx()
        #判断提交上来的工作类型是不是list,如果是则循环执行，不是则直接写入proj_type表
        if type(worktypes) is list:
            for w in worktypes:
                gl_othertype.add_work_type(db,w)
        else:
            gl_othertype.add_work_type(db,worktypes)
        data = {"pm_href":req.href.pmmm(),
                "pm_work":worktypes,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_configuration.html",data,None
    #为项目添加项目经理的方法
    def _add_manager(self,req,data):
        
        proj = req.args['proj']
        user = req.args['user']
        db = self.env.get_db_cnx()
        #判断提交上来的数据是否为list，是则循环执行，不是则直接写入project表
        if type(user) is list:
            for u in user:
                gl_project.add_project_manager(db,proj,u)
        else:
            gl_project.add_project_manager(db,proj,user)
        data = {'pm_href':req.href.pmmm(),
                'proj':proj,
                'user':user,
                'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None
    #删除工时记录的方法，调用此方法根据rowid直接删除一条工时记录
    def _delete_record(self,req,data):
        db=self.env.get_db_cnx()
        gl_proj_hours_record.delete_record_table(db,data)
        data1 = {"pm_href":req.href.pmmm(),
                 "data":data,
                 "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                 "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status.html",data1,None
    #列出要重新填报的工时记录
    def _update_record(self,req,data):
        add_stylesheet(req,"pmmm/css/datepicker.css")
        add_script(req,"pmmm/js/datepicker.js")
        add_script(req,"pmmm/js/eye.js")
        add_script(req,"pmmm/js/utils.js")
        add_script(req,"pmmm/js/layout.js")
        rowid = req.args['rowid']
        proj = req.args['proj']
        milestone = req.args['milestone']
        work_type = req.args['work_type']
        work_time = req.args['work_time']
        work_date = req.args['work_date']
        userInfo = req.args["userInfo"]
        managerInfo = req.args["managerInfo"]
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        result=gl_proj_user.select_user_proj_name(db,req.authname)
        dictP = self._dictProj()
        result1 = gl_othertype.select_proj_type_name(db)
        proj_nameDatas=[]
        ms=[]
        for proj_names in result:
            for proj_name in proj_names:
                proj_nameDatas.append(proj_name)
        for proj_nameData in proj_nameDatas:
            list1 =[]
            filePath="/home/trac/"+proj_nameData+"/db/trac.db"
            cx = sqlite.connect(filePath)
            cu = cx.cursor()
            cu.execute("select name from milestone where completed=0")
            cu.fetchone
            ms.append(cu)
        data1={'pm_href':req.href.pmmm(),
              'proj_names':result,
              'proj_types':result1,
              'milestones':ms,
              'check_list':list1,
              'rowid':rowid,
              'proj1':proj,
              'milestone1':milestone,
              'work_type1':work_type,
              'work_time':work_time,
              'work_date':work_date,
              'dictP':dictP,
              'userInfo':userInfo,
              'managerInfo':managerInfo,
              'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
              'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_editReport.html",data1,None
    #更新工时记录，该方法用于对未审核通过的工时记录重新填写，改变记录的审核状态为未审核
    def _edit_report_submit(self,req,data):
        db = self.env.get_db_cnx()
        anaMonth=time.strftime('%Y-%m',time.localtime(time.time()))
        theYear = anaMonth.split("-")[0]
        theMonth = anaMonth.split("-")[1]
        mr = calendar.monthrange(int(theYear),int(theMonth))[1]
        startDate = anaMonth+"-"+"01"
        endDate = anaMonth+"-"+str(mr)
        #获取当前登录的用户
        user_name = req.authname
        proj_name = req.args['proj']
        milestone = req.args['milestone']
        work_type = req.args['proj_type']
        work_date = req.args['proj_date']
        work_date_length = req.args['proj_hour']
        rowid = req.args['rowid']
        user_remark = req.args['userRemarks']
        gl_proj_hours_record.update_pmhourecord_table(db,proj_name,user_name,work_type,work_date,milestone,work_date_length,user_remark,rowid)
        data=self._proj_hours_record_list(req,user_name,startDate,endDate)
        return "pm_query_hour_result1.html",data,None
    def _list_project_info(self,req,data):
        dict1 = self._dictProj()
        list1=[]
        db = self.env.get_db_cnx()
        result=gl_proj_user.select_projs(db)
        data1 = {
            'pm_href':req.href.pmmm(),
            'result':result,
            'dict1':dict1,
            'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
            'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")
        }
        return data1
    #列出项目用户表内所有的项目
    def _list_project(self,req,data):
        data1=self._list_project_info(req,data)
        return "pm_list_project.html",data1,None
      #删除项目
    def _del_project(self,req,data):
        db = self.env.get_db_cnx()
        proj_name=req.args['proj_name']
        #pr = ProjectController(self)
        #pr._delete_project(proj_name)
        if isinstance(proj_name,list):
            for pr in proj_name:
                gl_proj_user._delete_project(db,pr)
                gl_proj_info.delete_project(db,pr)
                gl_project.delete_project(db,pr)
        else:
                gl_proj_user._delete_project(db,proj_name)
                gl_proj_info.delete_project(db,proj_name)
                gl_project.delete_project(db,proj_name)
        data1=self._list_project_info(req,data)
        return "pm_list_project.html",data1,None
    #列出用户和项目经理
    def _list_project_users(self,req,data):
        db = self.env.get_db_cnx()
        dictU = self._dictUser()
        result=gl_proj_user.select_proj_users(db,data)
        result2=gl_project.select_proj_manager(db,data)
        data1 = {'pm_href':req.href.pmmm(),
                 'result':result,
                 'proj':data,
                 'managers':result2,
                 'dictU':dictU,
                 'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                 'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_list_proj_users.html",data1,None
    #该方法用于删除项目经理
    def _delete_proj_manager(self,req,data):
        db = self.env.get_db_cnx()
        proj = req.args['proj']
        userManager = req.args['manager']
        if type(userManager) is list:
            for u in userManager:
                gl_project.delete_proj_manager(db,proj,u)
        else:
            gl_project.delete_proj_manager(db,proj,userManager)
        data =  {"pm_href":req.href.pmmm(),
                 'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                 'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None
    #列出分析统计配置页面
    def _analysis_list(self,req,data):
        user_name = req.authname
        add_stylesheet(req,"pmmm/css/datepicker.css")
        add_script(req,"pmmm/js/datepicker.js")
        add_script(req,"pmmm/js/eye.js")
        add_script(req,"pmmm/js/utils.js")
        add_script(req,"pmmm/js/layout.js")
        add_script(req,"pmmm/js/monthpicker.js")
        add_script(req,"pmmm/js/cookieHelper.js")
        dict1 = self._dictUser()
        dict2 = self._dictProj()
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        is_proj_admin=req.perm.has_permission("PROJECT_ADMIN")
        if is_proj_admin:
           result=gl_project.select_project_manager_pros(db,user_name)
           result.sort()
        else:
            result=gl_proj_user.select_projs(db)
            result.sort()
        result2=gl_proj_user.select_users(db)
        anaway=["personel","into"]
        data1 = {'pm_href':req.href.pmmm(),
                 'proj_names':result,
                 'anaways':anaway,
                 'proj_uname':result2,
                 'dict1':dict1,
                 'dict2':dict2,
                 'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                 'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_analysis_list.html",data1,None
    #项目工时统计报表的计算方法
    def _analysis_count(self,req,data):
        add_script(req,"pmmm/js/exportExcel.js")
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        anaWay = int(req.args['anaWay'])
        projName = req.args['proj']
        dictP = self._dictProj()
        startTime = req.args['startTime']
        endTime = req.args['endTime']
        dictU = self._dictUser()
        user_resultsY = []
        work_typesY = []
        #判断统计方法，1为按人员划分，2为按投入划分
        if anaWay==1:
            user_results=gl_proj_hours_record.select_proj_user_table(db,projName)
            #定义字典类型变量，存放级别数据，key为用户名，value为该用户级别
            dict2={}
            dict3={}
            dict4={}
            #定义字典类型变量，存放工时数据，key为用户名，value为该用户在该项目下的工时
            dict1 = {}  
            for ur in user_results:
                for u in ur:
                     hourLength=gl_proj_hours_record.select_user_sumtime(db,startTime,endTime,u,str(projName),)
                     hour=0
                     days=0
                     for h in hourLength:
                      if h!=None:
                        hour=float(h)
                        day=float(h)/8
                        days=round(day,1)
                        dict1[str(ur)]=days
                        user_resultsY.append(ur)
                     level=gl_user.select_userlevel(db,u)
                     if level!=None:
                         sql3="select level_desc from leveltable where level_value=%s"
                         sql4="select cost from leveltable where level_value=%s"
                         cursor.execute(sql3,level)
                         leveldes=cursor.fetchone()
                         cursor.execute(sql4,level)
                         cost=cursor.fetchone()
                         for l in leveldes:
                            if l!=None:
                               dict2[str(ur)]=leveldes
                         for c in cost:
                            hcost=float(c)/22
                            if c!=None:
                               dict3[str(ur)]=hcost
                               usercost=hcost*days
                               ucost=round(usercost,2)
                               dict4[str(ur)]=ucost
                     else:
                         dictU[str(ur)] = u
                         sql3="select level_desc from leveltable where level_value=1"
                         sql4="select cost from leveltable where level_value=1"
                         cursor.execute(sql3)
                         leveldes=cursor.fetchone()
                         dict2[str(ur)]=leveldes
                         cursor.execute(sql4,level)
                         cost=cursor.fetchone()
                         for c in cost:
                            hcost=float(c)/22
                            if c!=None:
                               dict3[str(ur)]=hcost
                         usercost=hcost*days
                         ucost=round(usercost,2)
                         dict4[str(ur)]=ucost
                sum1=0
                for t in dict1:
                    sum1=dict1[t]+sum1
                sum=0
                for s in dict4:
                    sum=dict4[s]+sum
                data1 = {"pm_href":req.href.pmmm(),
                 "projName":projName,
                 "startTime":startTime,
                 "employees":user_resultsY,
                 "endTime":endTime,
                 "hourLength":dict1,
                 "anaWay":anaWay,
                 "dictU":dictU,
                 "level":dict2,
                 "dict3":dict3,
                 "cost":dict4,
                 "sum":sum,
                 "sum1":sum1,
                 "dictP":dictP,
                 "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                 "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        elif anaWay==2:
            work_types=gl_proj_hours_record.select_worktype_table(db)
            #定义字典类型变量，存放工时数据，key为工作类型，value为该工作类型在该项目下的工时
            dict2 ={}
            for wy in work_types:
                for w in wy:
                  hourLength2=gl_proj_hours_record.select_input_worktime_table(db,w,projName,startTime,endTime)   
                for h in hourLength2:
                    if h!=None:
                       dict2[w] = h
                       work_typesY.append(w)
                data1 = {"pm_href":req.href.pmmm(),
                         "projName":projName,
                         "startTime":startTime,
                         "work_types":work_typesY,
                         "endTime":endTime,
                         "hourLength2":dict2,
                         "anaWay":anaWay,
                         "dictP":dictP,
                         "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                         "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        elif anaWay==3:
            dictT ={}
            dictU={}
            dictH={}
            dictN={}
            dictP=self._dictProj()
            sum=0
            ids=[]
            projName = req.args['proj']
            result=gl_othertype.select_user_work_type_table(db)
            proj_users=gl_proj_user.select_proj_users(db,projName)
            for re in result:
                userlist=[]
                id = re[0]
                hourlist=[]
                users=gl_user.select_user_by_use_work_type(db,id)
                for us in proj_users:
                    if us in users:
                        userlist.append(us)
                dictT[id]=userlist
                userlist=[]
                for ul in dictT[id]:
                    for u in ul:
                        hours=gl_proj_hours_record.select_user_sumtime(db,startTime,endTime,u,projName)
                    userlist.append(hours)
                    dictU[id]=userlist
                    sum=0
                    for hour in dictU[id]:
                        for h in hour:
                            if h!=None:
                                hours=h
                            else:
                               hours=0.0
                            sum+=hours
                    dictH[id]=sum
                    ids=dictH.keys()
                    for i in ids:
                        iname=gl_othertype.select_user_work_type(db,i)
                    dictN[i]=iname
                data = {"pm_href":req.href.pmmm(),
                         "projName":projName,
                         "startTime":startTime,
                         "endTime":endTime,
                         "dictH":dictH,
                         "ids":ids,
                         "anaWay":anaWay,
                         "dictP":dictP,
                         "dictN":dictN}
            return "pm_work_analysis.html",data,None
        return "pm_analysisResult1.html",data1,None
    #按月统计所有员工工作量，这里的所有员工是指工时记录表里面提交过记录的员工
    def _view_report_form2(self,req,data):
        add_script(req,"pmmm/js/exportExcel.js")
        anaMonth = req.args['anaMonth']
        theYear = anaMonth.split("-")[0]
        theMonth = anaMonth.split("-")[1]
        mr = calendar.monthrange(int(theYear),int(theMonth))[1]
        startDate = anaMonth+"-"+"01"
        endDate = anaMonth+"-"+str(mr)
        db=self.env.get_db_cnx()
        user_results=gl_proj_hours_record.select_all_user_table(db)
        dictP = {}
        dictU = self._dictUser()
        projs_results = gl_proj_hours_record.select_proj_name_table(db)
        for p in projs_results:
          for pn in p:
            pZh = gl_proj_info.select_projZh_name(db,pn)
            if pZh!=None:
               dictP[str(p)] = pZh
            else:
               dictP[str(p)] = pn
        myDict= {}
        myDict1={}
        myDict2={}
        #循环所有用户，查询出每个用户在该月审核通过的记录时间总和
        for ur in user_results:
            for u in ur:
                tl=gl_proj_hours_record.select_user_monthtime_tabel(db,u,startDate,endDate)
                for t in tl:
                    for k in t:
                        if k==None:
                            k=0
        #将每个用户的时间存入字典类型对象，key为该用的用户名，value为时间
                        myDict1[str(ur)]=k
                        myDict1[str(ur)]=k
        #循环所有项目，查询每个项目在该月审核通过的记录的时间总和
        for pr in projs_results:
            for p in pr:
                tl=gl_proj_hours_record.select_sumtime_table(db,startDate,endDate,p)
                for t in tl:
                    if t==None:
                            t=0
        #将每个项目的时间存入字典类型对象，key为该项目项目名，value为时间
                    myDict2[str(pr)]=t
        #计算出每个人在每个项目的时间投入
        for ur in user_results:
            array1 =[]
            for pr in projs_results:
                for u in ur:
                    for p in pr:
                       timeLength=gl_proj_hours_record.select_user_sumtime(db,startDate,endDate,u,p)
                       for t in timeLength:
                         if t==None:
                             t=0
                       #将一个用户的所有项目时间分别存入数组
                         array1.append(t)
                       #将每个用户在所有项目下的时间分别存入字典对象，以用户名为key，数组数据为value
                       myDict[str(ur)]=array1
        data1 = {"pm_href":req.href.pmmm(),
                 "employees":user_results,
                 "projs":projs_results,
                 "dict":myDict,
                 "anaMonth":anaMonth,
                 "dict1":myDict1,
                 "dict2":myDict2,
                 "dictP":dictP,
                 "dictU":dictU,
                 "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                 "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_view_report2.html",data1,None
    #计算出部分人员在某月所有项目的工时记录，人员名可选，计算方法同上，添加了员工名限制
    def _view_report_form3(self,req,data):
        add_script(req,"pmmm/js/exportExcel.js")
        anaMonth = req.args['anaMonth']
        theYear = anaMonth.split("-")[0]
        theMonth = anaMonth.split("-")[1]
        mr = calendar.monthrange(int(theYear),int(theMonth))[1]
        startDate = anaMonth+"-"+"01"
        endDate = anaMonth+"-"+str(mr)
        dictP = {}
        dictU = self._dictUser()
        db=self.env.get_db_cnx()
        user_results =req.args['user']
        projs_results = gl_proj_hours_record.select_proj_name_table(db)
        for p in projs_results:
          for pn in p:
            pZh = gl_proj_info.select_projZh_name(db,pn)
            if pZh!=None:
                dictP[str(p)] = pZh
            else:
                dictP[str(p)] = pn
        myDict= {}
        myDict1={}
        if type(user_results) is list:
           for ur in user_results:
                tl=gl_proj_hours_record.select_user_monthtime_tabel(db,ur,startDate,endDate)
                for t in tl:
                    for k in t:
                        if k==None:
                            k=0
                    myDict1[ur]=k
        else:
             tl=gl_proj_hours_record.select_user_monthtime_tabel(db,user_results,startDate,endDate)
             for t in tl:
                 for k in t:
                     if k==None:
                        k=0
                 myDict1[user_results]=k
        if type(user_results) is list:
            for ur in user_results:
                array1 =[]
                for pr in projs_results:
                    for p in pr:
                       timeLength=gl_proj_hours_record.select_user_sumtime(db,startDate,endDate,ur,p)
                       for t in timeLength:
                         if t==None:
                              t=0
                         array1.append(t)
                       myDict[ur]=array1
        else:
             array1 =[]
             for pr in projs_results:
                    for p in pr:
                       timeLength=gl_proj_hours_record.select_user_sumtime(db,startDate,endDate,user_results,p)
                       for t in timeLength:
                         if t==None:
                              t=0
                         array1.append(t)
                       myDict[str(pr)]=array1
        data1 = {"pm_href":req.href.pmmm(),
                 "employees":user_results,
                 "projs":projs_results,
                 "dict":myDict,
                 "anaMonth":anaMonth,
                 "dict1":myDict1,
                 "dictU":dictU,
                 "dictP":dictP,
                 "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                 "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_view_report3.html",data1,None
    #该方法用于列出所有的工作类型，供查看和删除使用
    def _list_workType(self,req,data):
        db = self.env.get_db_cnx()
        result = gl_othertype.select_proj_type_table(db)
        ms = []
        for s in result:
            ms.append({'ri':s[0],'ptn':s[1]})
        data = {"pm_href":req.href.pmmm(),
                "workTypes":ms,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_list_workType.html",data,None
    #该方法用于删除工作类型
    def _delete_workType(self,req,data):
        db = self.env.get_db_cnx()
        rowid= req.args['workType']
        if type(rowid) is list:
            for w in rowid:
                gl_othertype.delete_proj_type(db,w)
        else:
            gl_othertype.delete_proj_type(db,rowid)
        data = {"pm_href":req.href.pmmm(),
                'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None
    #工时记录查询配置页面显示方法
    def _hour_query_list(self,req,data):
        db =self.env.get_db_cnx()
        dict1 = self._dictUser()
        resultU = []
        dictPZh={}
        add_stylesheet(req,"pmmm/css/datepicker.css")
        add_script(req,"pmmm/js/datepicker.js")
        add_script(req,"pmmm/js/eye.js")
        add_script(req,"pmmm/js/utils.js")
        add_script(req,"pmmm/js/layout.js")
        authname= req.authname
        projs = 0
        is_proj_amdin = req.perm.has_permission("PROJECT_ADMIN")
        #判断登录用户是否为项目经理，如果是则显示该项目经理项目下的员工名列表，否则不显示，即普通员工只能查询自己的记录
        if is_proj_amdin:
            projs=gl_project.select_project_manager_pros(db,req.authname)
            if isinstance(projs,list):
                for u in projs:
                  for uname in u:
                    projsZh=gl_proj_info.select_projZh_name(db,uname)
                  dictPZh[u]=projsZh
            else:
                projZh=gl_proj_info.select_projZh_name(db,projs)
                dictPZh[projs]=projZh
            result1=gl_proj_user.select_proj_manager_users(db,req.authname)
            for res in result1:
                resultU.append(res)
            #列出该部门经理部门下的用户
            result2=gl_user.select_dep_user(db,req.authname)
            for res2 in result2:
                if res2 not in resultU:
                    resultU.append(res2)
        data = {"pm_href":req.href.pmmm(),
                "pm_is_project_admin":is_proj_amdin,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "employees":resultU,
                "auth":authname,
                "dict1":dict1,
                "projs":projs,
                "dictPZh":dictPZh}
        return "pm_query_hour_list.html",data,None
    #根据项目查询工时记录
    def _hour_query_proj_result(self,req,data):
        db = self.env.get_db_cnx()
        person=[]
        days2=[]
        lostDay1=[]
        list1 = []
        dictP = self._dictProj()
        dictU = self._dictUser()
        dictC = {}
        proj = req.args["proj"]
        startDate = req.args["startTime"]
        endDate = req.args["endTime"]
        names=gl_proj_user.select_proj_users(db,proj)
        users = gl_proj_hours_record.select_proj_user_name_table(db,proj,startDate,endDate)
        for name in names:
          for n in name:
           days1 = gl_user.select_userZh_name(db,n)
           days2.append(days1)
        if type(users) is list:
         for user in users:
           for u in user:
            name=gl_user.select_userZh_name(db,u)
            person.append(name)
        for u in days2:
            if u not in person: 
                lostDay1.append(u)
        listResult=gl_proj_hours_record.select_projlist_table(db,proj,startDate,endDate)
        for listRe in listResult:
            arg2 = listRe[10]
            if arg2 is None:
                arg2 = ""
            cZh = gl_user.select_userZh_name(db,arg2)
            dictC[listRe[10]] = cZh
            list1.append({'pn':listRe[0],'un':listRe[1],'wt':listRe[2],'wd':listRe[3],'mt':listRe[4],'wtl':listRe[5],'rw':listRe[6],'cs':listRe[7],'uf':listRe[8],'mf':listRe[9],'cu':listRe[10],'wti':listRe[11],'ct':listRe[12]})
        data = {"pm_href":req.href.pmmm(),
                "queryList":list1,
                "dictP":dictP,
                "dictU":dictU,
                "dictC":dictC,
                "lostday":lostDay1,
                "days2":days2,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_query_hour_result.html",data,None
    #工时记录查询方法，根据时间跨度，项目经理可选择自己项目下用户来查询其工时记录，普通员工通过登录用户名查询自己的记录
    def _hour_query_result(self,req,data):
        db = self.env.get_db_cnx()
        dict1 = {}
        person=[]
        days1=[]
        days2=[]
        lostDay=[]
        startTime = req.args['startTime']
        endtime = req.args['endTime']
        is_proj_admin = req.perm.has_permission("PROJECT_ADMIN")
        if is_proj_admin:
            employees = req.args['employees']
            days=gl_proj_hours_record.select_username_table(db,startTime,endtime)
            for user in employees:
                username=gl_user.select_userZh_name(db,user)
                days1.append(username)
            for uns in days:
              for u in uns:
                uname=gl_user.select_userZh_name(db,u)
                days2.append(uname)
            for un in days1:
              if un not in days2:
                lostDay.append(un)
            if type(employees) is list:
                for e in employees:
                    print 'sss'
                data=self._proj_hours_record_list(req,employees,startTime,endtime)
                data['lostday']=lostDay
            else:
                employees = req.args['employees']
                days=gl_proj_hours_record.select_username_table(db,startTime,endtime)
                username = gl_user.select_userZh_name(db,employees)
                days1.append(username)
                for u in days:
                  for un in u:
                   uname = gl_user.select_userZh_name(db,un)
                days2.append(uname)
                for un in days1:
                   if un not in days2:
                     lostDay.append(un)
                data=self._proj_hours_record_list(req,employees,startTime,endtime)
                data['lostday']=lostDay
        else:
            employees = req.args['employee']
            data=self._proj_hours_record_list(req,employees,startTime,endtime)
        return "pm_query_hour_result.html",data,None
    #将htaccess文件中的用户名和项目名分别写入用户信息和项目信息表
    def _write_proj_user(self,req,data):
        #实例化ProjectController
        pc = ProjectController(self)
        db = self.env.get_db_cnx()
        #由于是全部导入，所以同步之前先删掉之前的记录
        gl_user.delete_all_date(db)
        gl_proj_info.delete_data(db)
        #调用ProjectController的方法列出所有项目
        projs = pc._list_all_projects()
        #调用ProjectController的方法列出所有用户
        users = pc._list_all_users()
        #将项目写入项目用户表
        for p in projs:
            gl_proj_info.add_project(db,p,"")
        #将用户写入用户表
        for u in users:
            gl_user.add_user(db,u,"")
        data = {"pm_href":req.href.pmmm(),
                'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status.html",data,None
    def _list_user_level_info(self,req,data):
        db = self.env.get_db_cnx()
        cjusers = gl_user.select_user_level(db,0)
        zjusers = gl_user.select_user_level(db,1)
        gjusers = gl_user.select_user_level(db,2)
        zjjusers = gl_user.select_user_level(db,3)
        data = {"pm_href":req.href.pmmm(),
                "pm_cjusers":cjusers,
                "pm_zjusers":zjusers,
                "pm_gjusers":gjusers,
                "pm_zajusers":zjjusers,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return data
    def _list_user_work_type_info(self,req,data):
        dictU={}
        db = self.env.get_db_cnx()
        user_work_type=gl_othertype.select_user_work_type_table(db)
        users=gl_user.select_user_by_use_work_type2(db)
        user=gl_user.select_user_by_use_work_type3(db)
        for u in user:
            username=u[0]
            user_type=u[2]
            uwt=gl_othertype.select_user_work_type(db,str(user_type))
            dictU[username]=uwt
        data = {"pm_href":req.href.pmmm(),
                "user_work_type":user_work_type,
                "users":users,
                "user":user,
                "dictU":dictU,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return data
    #显示用户界面，添加用户级别
    def _user_level(self,req,data):
        data=self._list_user_level_info(req,data)
        return "pm_user_level.html",data,None
    #显示用户工作类型界面，添加修改工作类型
    def _add_user_type(self,req,data):
        data=self._list_user_work_type_info(req,data)
        return "pm_user_work_type.html",data,None
    def _add_user_workType(self,req,data):
        db = self.env.get_db_cnx()
        rid=req.args['rid']
        type=req.args['type']
        if type=="未编辑":
            if isinstance(rid,list):
                for i in range(0,len(rid)):
                    gl_user.update_user_work_type(db,"",rid[i])
            else:
                    gl_user.update_user_work_type(db,"",rid)
        else:
            type=req.args['type']
            type_id=gl_othertype.select_user_work_id(db,type)
            for id in type_id:
                if isinstance(rid,list):
                    for i in range(0,len(rid)):
                        gl_user.update_user_work_type(db,id,rid[i])
                else:
                    gl_user.update_user_work_type(db,id,rid)
        data=self._list_user_work_type_info(req,data)
        return "pm_user_work_type.html",data,None
    #添加级别
    def _adduser_level(self,req,data):
        db = self.env.get_db_cnx()
        level = req.args["level"]
        rid = req.args["rid"]
        if (level=="设为初级级别"):
         if isinstance(rid,list):
           for i in range(0,len(rid)):
              gl_user.update_user_level(db,0,rid[i])
         else:
            gl_user.update_user_level(db,0,rid)
        elif (level=="设为中级级别"):
         if isinstance(rid,list):
           for i in range(0,len(rid)):
              gl_user.update_user_level(db,1,rid[i])
         else:
            gl_user.update_user_level(db,1,rid)
        elif (level=="设为高级级别"):
         if isinstance(rid,list):
           for i in range(0,len(rid)):
              gl_user.update_user_level(db,2,rid[i])
         else:
            gl_user.update_user_level(db,2,rid)
        else:
         if isinstance(rid,list):
           for i in range(0,len(rid)):
              gl_user.update_user_level(db,3,rid[i])
         else:
            gl_user.update_user_level(db,3,rid)
        data=self._list_user_level_info(req,data)
        return "pm_user_level.html",data,None
    #显示中英文用户名页面
    def _list_user_zh(self,req,data):
        dictP = self._dictProj()
        db = self.env.get_db_cnx()
        users=gl_user.select_no_userzh(db)
        projs=gl_proj_info.select_no_projZh_name(db)
        zh_users=gl_user.select_userzh(db)
        en_projs = gl_proj_info.select_have_projZh_name(db)
        allusers = gl_proj_hours_record.select_all_user_table(db)
        onusers= gl_user.select_users(db)
        listu=[]
        for u in allusers:
            if u not in onusers:
                listu.append(u)
        data = {"pm_href":req.href.pmmm(),
                "pm_users":users,
                "pm_projects":projs,
                "pm_en_projs":en_projs,
                "pm_users_zh":zh_users,
                "dictP":dictP,
                "listu":listu,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_list_zh.html",data,None
    #添加用户中文名
    def _add_user_zh(self,req,data):
        db = self.env.get_db_cnx()
        users = req.args["zh"]
        rid = req.args["rid"]
        if isinstance(rid,list):
           for i in range(0,len(rid)):
              gl_user.add_userzh(db,users[i],rid[i])
        else:
              gl_user.add_userzh(db,users,rid)
        data =  {"pm_href":req.href.pmmm(),
                 'is_trac_admin':req.perm.has_permission("TRAC_ADMIN"),
                 'pm_is_project_admin':req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None
    #添加离职员工
    def _add_leave_off_user(self,req,data):
        db = self.env.get_db_cnx()
        user_zh=req.args['user_zh']
        user=req.args['user']
        if isinstance(user,list):
           for i in range(0,len(user)):
              gl_user.add_lea_of_user(db,user[i],user_zh[i])
        else:
              gl_user.add_lea_of_user(db,user,user_zh)
        data =  {"pm_href":req.href.pmmm(),
                 "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                 "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None
    #添加项目中文名
    def _add_proj_zh(self,req,data):
        db = self.env.get_db_cnx()
        names = req.args["zh"]
        rid = req.args["rid"]
        if isinstance(rid,list):
           for i in range(0,len(rid)):
                gl_proj_info.add_project_zh_name(db,names[i],rid[i])
        else:
                gl_proj_info.add_project_zh_name(db,names,rid)
        data =  {"pm_href":req.href.pmmm(),
                 "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                 "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None
    #删除用户中文名
    def _del_user_zh(self,req,data):
        db =  self.env.get_db_cnx()
        users = req.args["users"]
        if type(users) is list:
            for i in range(0,len(users)):
                gl_user.delete_userzh(db,users[i])
        else:
            gl_user.delete_userzh(db,users)
        data = {"pm_href":req.href.pmmm(),
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None
    #删除项目中文名
    def _del_proj_zh(self,req,data):
        db =  self.env.get_db_cnx()
        projs = req.args["projs"]
        if type(projs) is list:
           for i in range(0,len(projs)):
                gl_proj_info.delete_projzh_name(db,projs[i])
        else:
                gl_proj_info.delete_projzh_name(db,projs)
        data =  {"pm_href":req.href.pmmm(),
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None
    def _list_update_dep_info(self,req,data):
        db = self.env.get_db_cnx()
        dictUser=self._dictUser()
        dictU = {}
        mods={}
        list2=[]
        #显示未编辑部门的人员名单
        nodepusers=gl_user.select_nodep_user(db,str(0))
        result = gl_department.select_dep_id(db)
        for re in result:
            for id in re:
                dep_name=gl_department.select_dep_name(db,str(id))
                mods[id]=dep_name
                username=gl_user.select_dep_user_zh(db,str(id))
            listUsers = []
            for u in username:
               for iu in u: 
                  listUsers.append(str(iu))    
            dictU[id] =listUsers   
        depids=mods.keys()
        depids.sort()
        for id in depids:
                list2.append([id, mods[id], dictU[id]])
        is_proj_admin = req.perm.has_permission("PROJECT_ADMIN")
        is_trac_admin = req.perm.has_permission("TRAC_ADMIN")
        data = {"pm_href":req.href.pmmm(),
                "nodepusers":nodepusers,
                "dictUser":dictUser,
                "list2":list2,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return data
    #显示添加部门息信页面
    def _add_dep_view(self,req,data):
        data=self._list_update_dep_info(req,data)
        return "pm_add_dep_info.html",data,None
    #执行添加部门信息操作
    def _add_dep_info(self,req,data):
        db = self.env.get_db_cnx()
        depId = int(req.args["depid"])
        depName = req.args["depname"]
        leaderdepId=req.args["depleadid"]
        depMana = ""
        depDeputyMana = ""
        depemail=req.args["depemail"]
        gl_department.add_dep(db,depId,depName,depMana,depDeputyMana,leaderdepId,depemail)
        data = self._list_update_dep_info(req,data)
        return "pm_add_dep_info.html",data,None
    #列出部门下的用户供操作
    def _list_dep_users(self,req,data):
        data=self._list_dep_info(req,data)
        return "pm_list_dep_users.html",data,None
    def _list_dep_info(self,req,data):
        dictUZ = self._dictUser()
        db = self.env.get_db_cnx()
        mana=gl_department.select_dep_manager(db,data)
        a = isinstance(mana,object)
        viceMana=gl_department.select_dep_deputy_manager(db,data)
        dep=gl_department.select_dep_name(db,data)
        users=gl_user.select_nodep_user(db,data)
        users2=gl_user.select_none_dep_user(db,data)
        s=gl_department.select_dep_info(db,data)
        data = {"pm_href":req.href.pmmm(),
                "users":users,
                "otherUsers":users2,
                "dictUZ":dictUZ,
                "dep":dep,
                "viceMana":viceMana,
                "mana":mana,
                "a":a,
                "depName":s[0],
                "leaderdepId":s[1],
                "depemail":s[2],
                "depId":data,
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return data
    #为部门添加员工
    def _do_add_dep(self,req,data):
        db = self.env.get_db_cnx()
        users = req.args["users"]
        depId =  req.args["dep"]
        if isinstance(users,list):
            for u in users:
                gl_user.update_user_dep_id(db,depId,u)
        else:
            gl_user.update_user_dep_id(db,depId,users)
        data=self._list_dep_info(req,depId)
        return "pm_list_dep_users.html",data,None
    #删除部门下的员工
    def _do_del_dep(self,req,data):
        depId =  req.args["dep"]
        db = self.env.get_db_cnx()
        usersn = req.args["depUsers"]
        if isinstance(usersn,list):
            for u in usersn:
                gl_user.update_user_dep_id(db,str(0),u)
        else:
            gl_user.update_user_dep_id(db,str(0),usersn)
        data=self._list_dep_info(req,depId)
        return "pm_list_dep_users.html",data,None
     #添加部门经理
    def _add_dep_mana(self,req,data):
        db = self.env.get_db_cnx()
        user = req.args["depUsers"]
        depId = req.args["dep"]
        rowid = gl_permission.select_rowid(db,user,'DEPARTMENT_ADMIN')
        if rowid!="":
            gl_permission.delete_permission(db,user,'DEPARTMENT_ADMIN')
        gl_department.update_dep_mana(db,user,depId)
        gl_permission.add_permission(db,user,'DEPARTMENT_ADMIN')
        data=self._list_dep_info(req,depId)
        return "pm_list_dep_users.html",data,None
    #添加部门副经理
    def _add_dep_vice_mana(self,req,data):
        db = self.env.get_db_cnx()
        user = req.args["depUsers"]
        depId = req.args["dep"]
        rowid = gl_permission.select_rowid(db,user,'DEPARTMENT_ADMIN')
        if rowid!="":
            gl_permission.delete_permission(db,user,'DEPARTMENT_ADMIN')
        gl_department.update_dep_vice_mana(db,user,depId)
        gl_permission.add_permission(db,user,'DEPARTMENT_ADMIN')
        data=self._list_dep_info(req,depId)
        return "pm_list_dep_users.html",data,None
    #删除部门经理
    def _del_dep_mana(self,req,data):
        db = self.env.get_db_cnx()
        user = req.args["depUsers"]
        depId = req.args["dep"]
        gl_department.delete_dep__mana(db,depId,user)
        gl_permission.delete_permission(db,user,'DEPARTMENT_ADMIN')
        data=self._list_dep_info(req,depId)
        return "pm_list_dep_users.html",data,None
    #删除部门副经理
    def _del_dep_vice_mana(self,req,data):
        db = self.env.get_db_cnx()
        user = req.args["depUsers"]
        depId = req.args["dep"]
        gl_department.delete_dep_vice__mana(db,depId,user)
        gl_permission.delete_permission(db,user,'DEPARTMENT_ADMIN')
        data=self._list_dep_info(req,depId)
        return "pm_list_dep_users.html",data,None
    #删除已有部门
    def _del_dep(self,req,data):
        depId = req.args["depId"]
        db = self.env.get_db_cnx()
        if isinstance(depId,list):
            for d in depId:
                gl_user.updata_deldep_user_depid(db,d)
                gl_department.delete_dep(db,d)
        else:
            gl_user.updata_deldep_user_depid(db,depId)
            gl_department.delete_dep(db,depId)
        data=self._list_update_dep_info(req,data)
        return "pm_add_dep_info.html",data,None
    #修改部门名
    def _modify_dep(self,req,data):
        depName = req.args["depName"]
        depId = req.args["depId"]
        leaderdepId=req.args["leaderdepId"]
        depemail=req.args["depemail"]
        name=req.args["depaction"]
        db = self.env.get_db_cnx()
        if (name=="修改部门名"):
            gl_department.update_dep_name(db,depName,depId)
        elif (name=="修改上属部门编号"):
            gl_department.update_updep_id(db,leaderdepId,depId)
        elif (name=="修改部门Email"):
            gl_department.update_dep_email(db,depemail,depId)
        db.commit()
        data=self._list_dep_info(req,depId)
        return "pm_list_dep_users.html",data,None
    #该方法用于删除用户，但工时记录任然保存在工时记录表中，该用户从项目和用户表中删除
    def _del_user(self,req,data):
        db = self.env.get_db_cnx()
        user = req.args["user"]
        gl_user.delete_user(db,user)
        gl_proj_user.delete_user(db,user)
        uc = UserController(self)
        data = uc._del_user(req,data)
        return 'pm_user_deleted.html', data, None
    #从数据库读出所有用户供删除操作使用
    def _list_user_for_del(self,req,data):
        db = self.env.get_db_cnx()
        results=gl_user.select_user_name(db)
        result=gl_user.select_leave_users(db)
        users=gl_user.select_users_noleave(db)
        data = {
           "pm_href":req.href.pmmm(),
           "results":results,
           "result":result,
           "user":users,
           "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
           "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")
        }
        return "pm_list_for_del.html",data,None
    #删除数据库里的用户
    def _del_database_user(self,req,data):
        db = self.env.get_db_cnx()
        user = req.args["users"]
        if isinstance(user,list):
            for u in user:
                gl_user.delete_user(db,u)
                gl_proj_user.delete_user(db,u)
        else:
            gl_user.delete_user(db,user)
            gl_proj_user.delete_user(db,user)
        data = {"pm_href":req.href.pmmm(),
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")
        }
        return "pm_submit_status1.html",data,None
    def _set_database_user_leave(self,req,data):
        db = self.env.get_db_cnx()
        user = req.args["users"]
        if isinstance(user,list):
            for u in user:
                gl_user._update_user_satae(db,u)
        else:
            gl_user._update_user_satae(db,user)
        data = {"pm_href":req.href.pmmm(),
                "is_trac_admin":req.perm.has_permission("TRAC_ADMIN"),
                "pm_is_project_admin":req.perm.has_permission("PROJECT_ADMIN")}
        return "pm_submit_status1.html",data,None