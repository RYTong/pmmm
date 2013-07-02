'''
Created on Feb 28, 2010
@author: haoboy
'''

import re
import os
import time

from trac.web.chrome import add_stylesheet, add_script
from pm_utils import PMGeneralError
from user_list import UserList

import pm_utils

class ControllerUndefinedMethodError(PMGeneralError):
    def __init__(self, str = "Method not defined in Controller"):
        PMGeneralError.__init__(self, str)

class Controller(object):
    '''
    Base class for all controllers.
    '''

    #----------------------------------------------------------------------
    # Private data
    #----------------------------------------------------------------------

    _mainpage = None
    _re_badname = '.*[&|;\'\"\\\\].*'
    _re_version = '^[0-9]+\.[0-9]+\.[0-9]+(-[CBR])*$'

    def __init__(self, mainpage):
        self._mainpage = mainpage
        self.HGROOT = mainpage.HGROOT
        self.HGREPO = mainpage.HGREPO
        self.HIDDEN_DIRS = mainpage.HIDDEN_DIRS
        self.HGSCRIPT = mainpage.HGSCRIPT
        self.PROJROOT = mainpage.PROJROOT
        self.ACLROOT = mainpage.ACLROOT
        self.GLOBAL_ACL = self.ACLROOT+'/.htaccess'
        self.log = mainpage.log
        self.is_project_admin = False
        self.is_trac_admin = False

    
    def prepare_for_action(self, req):
        add_stylesheet(req, 'pmmm/pmmm.css')
        self.is_project_admin = req.perm.has_permission("PROJECT_ADMIN")
        self.is_trac_admin = req.perm.has_permission("TRAC_ADMIN")
        self.is_dep_admin = req.perm.has_permission("DEPARTMENT_ADMIN")
        self.log.debug("User %s is_admin %d" % (req.authname,
                                                 self.is_project_admin))

    def handle_action(self, req, action, data):
        '''
        Entrance point for all action processing.
        '''
        try:
            self.prepare_for_action(req)
            
            # Hook for derived classes to do the work.
            return self._do_handle_action(req, action, data)
        except PMGeneralError, e:
            # We simply ignore all exceptions and return an error.
            self.log.warn("Action %s error: %s" % (action, e))
            return self._mainpage.return_error("%s" % e)


    def _do_handle_action(self, req, action, data):
        '''This is a pure virtual function.'''
        raise ControllerUndefinedMethodError()

    def _check_post(self, req):
        if req.method != 'POST':

            raise PMGeneralError("Wrong request.")

    def _check_name(self, req, name = 'project', errstr = 'No name.'):
        if not req.args.has_key(name):
            raise PMGeneralError(errstr)
        project = req.args[name]
        if not project:
            raise PMGeneralError("Empty variable: "+name)
        # This argument can be a list or a string
        if isinstance(project, list):
            for p in project:
                self._check_name_aux1(p)
        else:
            self._check_name_aux1(project)

    def _check_name_aux1(self, project):
        if re.match(self._re_badname, project):
            raise PMGeneralError("Invalid name "+project)

    def _check_version(self, req, name):
        if not req.args.has_key(name):
            raise PMGeneralError("No version string.")
        ver = req.args[name]
        if not re.match(self._re_version, ver):
            raise PMGeneralError("Invalid version string "+ver)
    
    def _foreach_project(self):
        '''Iterate through all projects.'''
        for p in os.listdir(self.PROJROOT):
            if p in self.HIDDEN_DIRS:
                continue
            yield p


    def _add_project_user(self, user, raw_passwd, project):
        '''Add a user and a raw password to a project.'''
        if isinstance(project, list):
            out = ""
            for p in project:
                out += self._add_project_user_aux1(user, raw_passwd, p)
        else:
            out = self._add_project_user_aux1(user, raw_passwd, project)
        return out

    def _add_project_user_aux1(self, user, raw_passwd, project):
        acl_file = '/var/tmp/%d' % int(time.time())
        if os.path.exists(acl_file):
            os.unlink(acl_file)
        f = UserList()
        f.load_file(acl_file, True)
        f.update_raw(user, raw_passwd)
        f.save()
        cmd = ("%s/proj-admin au %s --acl %s" % 
               (self.HGSCRIPT, project, acl_file))
        out = pm_utils.run(cmd)
        os.unlink(acl_file)
        return out

    def _del_project_user(self, user, project):
        '''
        Remove a user from a project.
        '''
        if isinstance(project, list):
            out = ""
            for p in project:
                out += self._del_project_user_aux1(user, p)
        else:
            out = self._del_project_user_aux1(user, project)
        return out

    def _del_project_user_aux1(self, user, project):
        cmd = '%s/proj-admin du %s --user %s' % (self.HGSCRIPT, project, user)
        return pm_utils.run(cmd)
