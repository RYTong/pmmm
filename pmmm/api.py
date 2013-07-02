# -*- coding: utf-8 -*-

from trac.log import logger_factory
from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor, PermissionSystem

from web_ui import *
#from admin import *
#from timeline_hook import *

'''Detects and initializes dabase and other environment settings for
this plugin.'''
class PMMMPlugin(Component) :
    implements(IEnvironmentSetupParticipant)

    DB_VERSION_KEY = 'pmmm_database_version'
    DB_VERSION = 13

    def __init__(self):
        '''Initializing database schemas for this plugin.'''
        self._db_installed_version = 0

        # Initialise database schema version tracking.
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("SELECT value FROM system WHERE name=%s",
                       (self.DB_VERSION_KEY,))
        try:
            self._db_installed_version = int(cursor.fetchone()[0])
        except:
            # If we failed to query the version from database, we should 
            # insert a 0 value there so that we may correctly upgrade 
            # the system later.
            cursor.execute("INSERT INTO system (name,value) VALUES (%s,%s)",
                           (self.DB_VERSION_KEY, 0))
            db.commit()
            self._db_installed_version = 0

    def environment_needs_upgrade(self, db):
        """Interface required by IEnvironmentSetupParticipant.
        Should return `True` if this participant needs an upgrade to be
        performed, `False` otherwise.
        """
        return (self.system_needs_upgrade())

    def environment_created(self):
        """Called when a new Trac environment is created."""
        if self.environment_needs_upgrade(None):
            self.upgrade_environment(None)
            
    def upgrade_environment(self, db):
        if self.system_needs_upgrade():
            self.log.debug("Upgrading PMMM.")
            self._do_db_upgrade()
            self.log.debug("Upgrade done.")

    def system_needs_upgrade(self):
        return self._db_installed_version < self.DB_VERSION

    # Private methods

    def _do_db_upgrade(self):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
 	if self._db_installed_version < 10:
			try:    
				sql1 = 'CREATE TABLE project ('\
					   ' proj_name text,'\
					   ' proj_manager_name text,'\
					   ' UNIQUE(proj_name,proj_manager_name)'\
					   ' )'
				sql2 = 'CREATE TABLE proj_user ('\
					   ' proj_name text,'\
					   ' proj_user_name text,'\
					   ' UNIQUE(proj_name,proj_user_name)'\
					   ' )'

				sql3='CREATE TABLE proj_type ('\
					' proj_type_name text PRIMARY KEY'\
					' )'

				sql4 = 'CREATE TABLE proj_hours_record ('\
					   ' proj_name text,'\
					   ' user_name text,'\
					   ' work_type text,'\
					   ' work_date date,'\
					   ' milestone text,'\
					   ' work_time_length text,'\
					   ' user_feedback text,'\
					   ' manager_feedback text,'\
					   ' check_status text,'\
					   ' checked_user text,'\
					   ' write_time DATETIME,'\
					   ' checked_time DATETIME'\
					   ' )'
				
				sql5 = 'CREATE TABLE proj_info ('\
	                                   ' proj_name text PRIMARY KEY,'\
					   ' proj_name_zh text'\
					   ')'
                                
                                sql6 = 'CREATE TABLE user('\
                                           ' user_id integer PRIMARY KEY,'\
                                           ' username text,'\
                                           ' username_zh text,'\
                                           ' dep_id integer,'\
                                           ' user_level integer,'\
                                           ' UNIQUE(username )'\
                                           ')'
                                #users表备份用户信息
				sql7 = 'CREATE TABLE users('\
                                           ' user_id integer PRIMARY KEY,'\
                                           ' username text,'\
                                           ' username_zh text,'\
                                           ' dep_id integer,'\
                                           ' user_level integer,'\
                                           ' UNIQUE(username )'\
                                           ')'
                                
                                sql8 = 'CREATE TABLE department('\
                                           ' dep_id integer PRIMARY KEY,'\
                                           ' dep_name text,'\
                                           ' dep_manager text,'\
                                           ' dep_deputy_manager text,'\
                                           ' leader_dep_id integer,'\
                                           ' dep_email varchar,'\
                                           'UNIQUE(dep_name,dep_manager)'\
                                           ')'
                                
                                sql9= 'CREATE TABLE leveltable('\
                                           ' Id INTEGER not null,'\
                                           ' level_value INTEGER,'\
                                           ' level_desc VARCHAR(400),'\
                                           ' cost NUMERIC'\
                                           ')'
                
				sqls=[sql1,sql2,sql3,sql4,sql5,sql6,sql7,sql8,sql9]
				for sql in sqls:
				   cursor.execute(sql)
				cursor.execute('UPDATE system set value=%s WHERE name=%s',
							   (10, self.DB_VERSION_KEY))
				db.commit()
				self._db_installed_version = 10
                        except Exception, e:
				self.log.error("PMMM failed to upgrade database schema: %s" % (e,))
				db.rollback()
				raise e
        if self._db_installed_version < 11:
			try:
		
				sql1 = 'CREATE TABLE expend_type ('\
                                           ' expend_type_name text PRIMARY KEY'\
					   ' )'
                                sql2 = 'create table  proj_expend('\
                                            ' proj_name text,'\
                                            ' expend_type text,'\
                                            ' expend text,'\
                                            ' time DATETIME,'\
                                            ' remarks text'\
                                            ')'
                                sql3 = 'alter table user add use_salary text'
				sql4 = 'alter table user add use_state integer'
                                sql5= 'update user set use_salary=""'
				sql6 = 'update user set use_state=0'
				sqls=[sql1,sql2,sql3,sql4,sql5,sql6]
				for sql in sqls:
				   cursor.execute(sql)
				cursor.execute('UPDATE system set value=%s WHERE name=%s',
							   (11, self.DB_VERSION_KEY))
				db.commit()
				self._db_installed_version = 11
			except Exception, e:
				self.log.error("PMMM failed to upgrade database schema: %s" % (e,))
				db.rollback()
				raise e
	if self._db_installed_version < 12:
			try:
                                sql = 'create table  attendance_record('\
				            ' record_id INTEGER PRIMARY KEY,'\
                                            ' dep_name text,'\
                                            ' user_number INTEGER,'\
                                            ' user_namezh text,'\
                                            ' date DATETIME,'\
                                            ' starttime DATETIME,'\
					    ' endtime1 DATETIME,'\
					    ' endtime2 DATETIME,'\
					    ' endtime3 DATETIME,'\
					    ' endtime4 DATETIME'\
                                            ')'
                                
				cursor.execute(sql)
				cursor.execute('UPDATE system set value=%s WHERE name=%s',
							   (12, self.DB_VERSION_KEY))
				db.commit()
				self._db_installed_version = 12
			except Exception, e:
				self.log.error("PMMM failed to upgrade database schema: %s" % (e,))
				db.rollback()
				raise e
	if self._db_installed_version < 13:
			try:
                                
				sql = 'create table  user_work_type('\
				            ' user_work_type_id integer PRIMARY KEY,'\
					    ' user_work_type text'\
                                            ')'
                                sql2 = 'alter table user add use_work_type integer'
				sql3 = 'update user set use_work_type=""'
				sqls=[sql,sql2,sql3]
				for sql in sqls:
				   cursor.execute(sql)
				cursor.execute('UPDATE system set value=%s WHERE name=%s',
							   (13, self.DB_VERSION_KEY))
				db.commit()
				self._db_installed_version = 13
			except Exception, e:
				self.log.error("PMMM failed to upgrade database schema: %s" % (e,))
				db.rollback()
				raise e