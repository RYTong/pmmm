'''
Created on Feb 28, 2010

@author: haoboy
'''

import os

from controller import Controller
from pm_utils import PMGeneralError
from user_list import UserList

import pm_utils

class UserController(Controller):
    '''
    Managing users.
    '''

    def __init__(self, mainpage):
        Controller.__init__(self, mainpage)

    #----------------------------------------------------------------------
    # Action handlers
    #----------------------------------------------------------------------
    
    def _do_handle_action(self, req, action, data):
        if action == "info":
            return self._info(req, data)

        if action == "au":
            return self._add_user(req, data)
        if action == "du":
            return self._del_user(req, data)
        if action == "cw":
            return self._change_password(req, data)
        if action == "ap":
            return self._add_project(req, data)
        if action == "dp":
            return self._del_project(req, data)

        raise PMGeneralError("Unknown action "+action)

    def _info(self, req, user):
        '''List all projects that this user belongs.'''
        ul = UserList()
        p_in = []
        p_out = []
        for p in self._foreach_project():
            self.log.debug("checking project %s" % p)
            ul.load_project(self._mainpage, p)
            if ul.has_user(user):
                p_in.append(p)
            else:
                p_out.append(p)
        data = {'pm_href' : req.href.pmmm(),
                'pm_user' : user,
                'pm_is_project_admin' : self.is_project_admin,
                'is_trac_admin':self.is_trac_admin,
                'pm_proj_in' : p_in,
                'pm_proj_out' : p_out}
        return 'pm_user_info.html', data, None
    
    def _add_user(self, req, data):
        '''Add a user to the global user list.'''
        self._check_post(req)
        self._check_name(req, 'user', 'No username.')
        self._check_name(req, 'passwd', 'No password.')

        user = req.args['user']
        user = user.strip()
        passwd = req.args['passwd']
        passwd = passwd.strip()
        
        ul = UserList()
        ul.load_file(self.GLOBAL_ACL)
        if ul.has_user(user):
            raise PMGeneralError("User %s already exists." % user)
        ul.update(user, passwd)
        ul.save()

        data = {'pm_href': req.href.pmmm(),
                'pm_msg' : "User %s has been created." % user,
                'pm_user': user}
        return data
    
    def _del_user(self, req, data):
        '''Delete a user from global user list, and from all projects.'''
        self._check_post(req)
        self._check_name(req, 'user', 'No username.')

        user = req.args['user']
        
        ul = UserList()
        ul.load_file(self.GLOBAL_ACL)
        if not ul.has_user(user):
            raise PMGeneralError("User %s does not exist." % user)
        ul.delete(user)
        ul.save()

        out = ""
        for p in self._foreach_project():
            ul.load_project(self._mainpage, p)
            if not ul.has_user(user):
                continue
            cmd = ("%s/proj-admin du %s --user %s" % 
                   (self.HGSCRIPT, p, user))
            out += pm_utils.run(cmd)
        
        data = {'pm_href' : req.href.pmmm(),
                'pm_out' : out,
                'pm_msg' : 'User %s has been deleted.' % user,
                'pm_user' : user}
        return 'pm_user_deleted.html', data, None
    
    def _add_project(self, req, user):
        '''Allow a user to access a project.'''
        self._check_post(req)
        self._check_name(req, 'proj', 'No projects selected.')

        global_acl = UserList()
        global_acl.load_file(self.GLOBAL_ACL)
        if not global_acl.has_user(user):
            raise PMGeneralError("User %s does not exist." % user)

        # Add this user to project ACL file.
        passwd = global_acl.password(user)
        out = self._add_project_user(user, passwd, req.args['proj'])
        
        data = {'pm_href' : req.href.pmmm(),
                'pm_out' : out,
                'pm_user' : user}
        return data
    
    def _del_project(self, req, user):
        '''Allow a user to access a project.'''
        self._check_post(req)
        self._check_name(req, 'proj', 'No projects selected.')

        global_acl = UserList()
        global_acl.load_file(self.GLOBAL_ACL)
        if not global_acl.has_user(user):
            raise PMGeneralError("User %s does not exist." % user)

        # Add this user to project ACL file.
        out = self._del_project_user(user, req.args['proj'])
        
        data = {'pm_href' : req.href.pmmm(),
                'pm_out' : out,
                'pm_user' : user}
        return data
    
    def _change_password(self, req, user):
        '''Change user password.'''
        self._check_post(req)
        self._check_name(req, 'pwd1', 'No password.')
        self._check_name(req, 'pwd2', 'No password.')

        pwd1 = req.args['pwd1']
        pwd2 = req.args['pwd2']
        if pwd1 != pwd2:
            raise PMGeneralError('Two passwords do not match.')

        ul = UserList()
        ul.load_file(self.GLOBAL_ACL)
        if not ul.has_user(user):
            raise PMGeneralError("User %s does not exist." % user)
        ul.update(user, pwd1)
        raw_passwd = ul.password(user)
        ul.save()
        u2 = UserList()

        for p in self._foreach_project():
            ul.load_project(self._mainpage, p)
            if ul.has_user(user):
                ul.update_raw(user, raw_passwd)
                ul.save()
                for m in os.listdir(self.PROJROOT + "/" + p):
                    self.log.debug("checking module " + m)
                    if m in self.HIDDEN_DIRS:
                        continue
                    u2.load_module(self._mainpage, p, m)
                    if u2.has_user(user):
                        u2.update_raw(user, raw_passwd)
                        u2.save()

        data = {'pm_href' : req.href.pmmm(),
                'pm_user' : user}
        return 'pm_user_done.html', data, None
