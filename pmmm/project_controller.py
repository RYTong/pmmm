'''
Created on Feb 22, 2010
Project actions for the PMMM main page.
@author: haoboy
'''
import sqlite
import os
import re
import urllib
import time


from trac.ticket import model
import pm_utils
from pm_utils import PMGeneralError
import user_list
from controller import Controller

class ProjectController(Controller):

    '''
    Handles project actions, called by the main page.
    '''

    def __init__(self, mainpage):
        Controller.__init__(self, mainpage)





    #----------------------------------------------------------------------
    # Action handlers
    #----------------------------------------------------------------------

    def _do_handle_action(self, req, action, data):

        if (not action or action == 'list'):
            return self._list(req, data)
        if (action == 'info'):
            # List detailed information about a project
            return self._info(req, data)
        if (action == 'minfo'):
            # List detailed information about a project
            return self._minfo(req, data)

        if (action == 'au'):
            return self._add_user(req, data)
        if (action == 'du'):
            return self._delete_user(req, data)

        if (action == 'aa'):
            return self._add_module_user(req, data)
        if (action == 'da'):
            return self._delete_module_user(req, data)

        if (action == 'mr'):
            return self._make_release(req, data)
        if (action == 'mb'):
            return self._make_branch(req, data)
        if (action == 'cp'):
            return self._clone_project(req, data)
        if (action == 'np'):
            return self._new_project(req, data)

        if (action == 'am'):
            return self._add_module(req, data)
        if (action == 'dm'):
            return self._del_module(req, data)

        if (action == 'ce'):
            return self._clone_experiment(req, data)
        if (action == 'ae'):
            return self._add_experiment(req, data)
        if (action == 'de'):
            return self._del_experiment(req, data)
        if (action == 'pml'):
            return self._view_mainList(req, data)
        if (action == 'pr'):
            return self._view_report(req,data)
        if (action == 'pc'):
            return self._view_check(req,data)
        if (action == 'pa'):
            return self._view_analysis(req,data)
        if (action == 'pra'):
            return self._info(req, data)
    def _view_analysis(self,req,data):
        data={'pm_href':req.href.pmmm()}
        return "pm_analysis.html",data,None
    def _view_check(self,req,data):
        data={'pm_href':req.href.pmmm()}
        return "pm_check.html",data,None
    def _view_mainList(self, req, data):
        trac_admin = req.perm.has_permission("TRAC_ADMIN")
        data={'pm_href':req.href.pmmm(),
              "pm_is_project_admin" : self.is_project_admin,
              "is_trac_admin":trac_admin}
        return "pm_main_list.html",data,None
    def _view_report(self,req,data):
        data={'pm_href':req.href.pmmm(),
              'pm_proj':"projName"}
        return "pm_report.html",data,None

    def _list_all_projects(self):
        projs = []
        for p in os.listdir(self.PROJROOT):
            if p in self.HIDDEN_DIRS:
                continue
            projs.append(p)
        return projs
    def _list(self, req, data):
        '''
        List all projects and all global users. NOTE: we require that
        /home/hg/acl/.htaccess holds a global user list.
        '''

        # Find a list of projects and a list of their modules
        mods = {}
        users = {}

        self.log.debug("Listing projects for user %s admin %d" %
                       (req.authname, self.is_project_admin))
        for p in os.listdir(self.PROJROOT):
            if p in self.HIDDEN_DIRS:
                continue
            # For an admin, list all projects; for a user, list
            # projects where she participates in.
            proj_users = self._list_users(p)
            if  self.is_trac_admin or (req.authname in proj_users):
                users[p] = proj_users
                mods[p] = self._list_modules(p)

        all_users = self._list_all_users()

        self.log.debug("found projects: %r" % mods.keys())
        self.log.debug("found users: %s" % all_users)
        mod_list = []
        projects = mods.keys()
        projects.sort()
        for p in projects:
            mod_list.append([p, mods[p], users[p]])
        trac_admin = req.perm.has_permission("TRAC_ADMIN")
        pm_user = req.authname
        # NOTE: we can't use 'href' as variable name. It's used by trac!
        data = {"pm_modlist": mod_list,
                "pm_is_project_admin" : self.is_project_admin,
                'pm_users' : all_users,
                'is_trac_admin':trac_admin,
                'pm_is_dep_admin':self.is_dep_admin,
                'pm_user':pm_user,
                'pm_href': req.href.pmmm()}
        
        return 'pm_projects.html', data, None

    def _info(self, req, proj):
        '''Show detailed information about a project'''
        mods = self._list_modules(proj)
        rels = self._list_releases(proj)
        branches = self._list_branches(proj)

        # Find all users that are and are not in this project.
        ulist = user_list.UserList()
        ulist.load_project(self._mainpage, proj)
        glist = user_list.UserList()
        glist.load_file(self.GLOBAL_ACL)
        users = ulist.to_list()
        not_users = []
        for u in glist.users():
            if not ulist.has_user(u):
                not_users.append(u)
        not_users.sort()

        # List all experiments of this user.
        exp_mods = self._list_experiments(proj)
        url = "https://%s/hg/proj/%s" % (req.server_name, proj)
        filePath="/home/trac/rytong/db/trac.db"
        is_current_project_admin=False
        cx = sqlite.connect(filePath)
        cu=cx.cursor()
        sql="select  proj_manager_name from project where proj_name='"+proj+"'"
        cu.execute(sql)
        proj_manager_name =cu.fetchall()
        user_name = req.authname
        list_managers = []
        trac_admin = req.perm.has_permission("TRAC_ADMIN")
        if trac_admin==True:
            is_current_project_admin=True
        else:
            for pmn in proj_manager_name:
                for pn in pmn:
                    if pn == user_name:
                        is_current_project_admin=True
        data = {'pm_proj' : proj,
                'pm_href' : req.href.pmmm(),
                'pm_modurl' : url,
                'pm_exprurl' : url + "/experiments",
                'pm_is_project_admin' : is_current_project_admin,
                'pm_modlist' : mods,
                'pm_users' : users,
                'pm_not_users' : not_users,
                'pm_releases' : rels,
                'pm_branches' : branches,
                'pm_experiments' : exp_mods
                }
        return 'pm_projinfo.html', data, None

    def _minfo(self, req, proj_mod):
        '''Show detailed information about a project'''
        [proj,module] = proj_mod.split()
        
        # Find all users that are and are not in this project.
        ulist = user_list.UserList()
        ulist.load_project(self._mainpage, proj)
        mlist = user_list.UserList()
        mlist.load_module(self._mainpage,proj,module)
        users = mlist.to_list()
        not_users = []
        for u in ulist.users():
            if not mlist.has_user(u):
                not_users.append(u)
        not_users.sort()

        # List all experiments of this user.
        exp_mods = self._list_experiments(proj)

        url = "https://%s/hg/proj/%s/%s" % (req.server_name, proj,module)
        data = {'pm_proj' : proj,
                'pm_module' : module,
                'pm_href' : req.href.pmmm(),
                'pm_modurl' : url,                
                'pm_is_project_admin' : self.is_project_admin,               
                'pm_users' : users,
                'pm_not_users' : not_users,         
                }
        return 'pm_moduleinfo.html', data, None

    
    def _add_user(self, req, data):
        '''
        Call proj-admin to add a new user.  Username is 
        required to pass from the request.
        '''
        self._check_post(req)
        self._check_name(req, 'project', 'No project.')
        self._check_name(req, 'user', 'No user name.')

        project = req.args['project']
        user = req.args['user']

        global_acl = user_list.UserList()
        global_acl.load_file(self.GLOBAL_ACL, False)

        if isinstance(user, list):
            out = ""
            for u in user:
                out += self._add_user_aux(global_acl, u, project)
        else:
            out = self._add_user_aux(global_acl, user, project)
            
        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Uesr %s added ' % user,
                'pm_out'  : out}
        return data

    def _add_user_aux(self, global_acl, user, project):
        if not global_acl.has_user(user):
            raise PMGeneralError("User %s does not exist." % user)
        return self._add_project_user(user, global_acl.password(user), project)
    
    def _delete_user(self, req, data):
        '''Call proj-admin to remove a user.'''
        self._check_post(req)
        self._check_name(req, 'project', 'No project.')
        self._check_name(req, 'user', 'No user name.')

        project = req.args['project']
        user = req.args['user']

        if isinstance(user, list):
            out = ""
            for u in user:
                cmd = "%s/proj-admin du %s --user %s" % \
                      (self.HGSCRIPT, project, u)
                out += pm_utils.run(cmd)
        else:
            cmd = "%s/proj-admin du %s --user %s" % \
                  (self.HGSCRIPT, project, user)
            out = pm_utils.run(cmd)

        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'User %s deleted' % user,
                'pm_out'  : out
                }
        return data

    def _add_module_user(self, req, data):
        '''
        Call proj-admin to add a new user.  Username is 
        required to pass from the request.
        '''
        self._check_post(req)
        self._check_name(req, 'project', 'No project.')
        self._check_name(req, 'module', 'No module name.')
        self._check_name(req, 'user', 'No user name.')
        
        project = req.args['project']
        user = req.args['user']
        module = req.args['module']

        if isinstance(user, list):
            out = ""
            for u in user:
                cmd = "%s/proj-admin aa %s --user %s --proj-mods %s" % \
                      (self.HGSCRIPT, project, u, module)
                out += pm_utils.run(cmd)
        else:
            cmd = "%s/proj-admin aa %s --user %s --proj-mods %s" % \
                  (self.HGSCRIPT, project, user, module)
            out = pm_utils.run(cmd)
            
        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Uesr %s added ' % user,
                'pm_out'  : out}
        return 'pm_release_done.html', data, None 

    def _delete_module_user(self, req, data):
        '''Call proj-admin to remove a user.'''
        self._check_post(req)
        self._check_name(req, 'project', 'No project.')
        self._check_name(req, 'module', 'No module name.')
        self._check_name(req, 'user', 'No user name.')

        project = req.args['project']
        user = req.args['user']
        module = req.args['module']

        if isinstance(user, list):
            out = ""
            for u in user:
                cmd = "%s/proj-admin da %s --user %s --proj-mods %s" % \
                      (self.HGSCRIPT, project, u, module)
                out += pm_utils.run(cmd)
        else:
            cmd = "%s/proj-admin da %s --user %s --proj-mods %s" % \
                  (self.HGSCRIPT, project, user, module)
            out = pm_utils.run(cmd)

        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'User %s deleted' % user,
                'pm_out'  : out
                }
        return 'pm_release_done.html', data, None 

    def _make_release(self, req, data):
        '''Call proj-admin to make a new release.'''
        self._check_post(req)
        self._check_name(req, 'project')
        self._check_version(req, 'version')

        project = req.args['project']
        ver = req.args['version']

        vlist = [v.name for v in model.Version.select(self._mainpage.env)]
        self.log.debug("versions = %s" % vlist)
        if ver in vlist:
            raise PMGeneralError("Version %s already exists in trac." % ver)
        
        cmd = self.HGSCRIPT + "/proj-admin mr "+project+" --version "+ver

        # If we have a branch string, release from a branch.
        if req.args.has_key('branch'):
            branch = req.args['branch']
            if re.match(self._re_badname, branch):
                return self._mainpage.return_error("Invalid name "+branch)
            if len(branch) > 0:
                cmd += " --branch " + branch

        out = pm_utils.run(cmd)
        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Release ' + ver + ' is done.',
                'pm_out'  : out
                }
        return 'pm_release_done.html', data, None 

    def _make_branch(self, req, data):
        '''Call proj-admin to make a new branch.'''
        self._check_post(req)
        self._check_name(req, 'project')
        self._check_name(req, 'name')

        project = req.args['project']
        ver = req.args['name']
        cmd = self.HGSCRIPT + "/proj-admin mb "+project+" --version "+ver
		
        # If we have a release string, make branch from a release.
        if req.args.has_key('release'):
            release = req.args['release']
            if re.match(self._re_badname, release):
                return self._mainpage.return_error("Invalid name "+release)
            if len(release) > 0:
                cmd += " --release " + release
				
        out = pm_utils.run(cmd)
        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Branch ' + ver + ' has been created.',
                'pm_out'  : out
                }
        return 'pm_release_done.html', data, None 

    def _add_module(self, req, data):
        self._check_post(req)
        self._check_name(req, 'project')
        self._check_name(req, 'name')

        project = req.args['project']
        name = req.args['name']

        # If the module spec does not contain '/', we consider this a
        # new module in the local project (branch/release/experiement
        # modules are created elsewhere.) Otherwise, we consider this
        # a module to be cloned.
        if name.find('/') > -1:
            modspec = "--src-mods %s" % name
        else:
            modspec = "--proj-mods %s" % name
        cmd = "%s/proj-admin am %s %s" % (self.HGSCRIPT, project, modspec)
        out = pm_utils.run(cmd)
        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Module ' + name + ' has been created.',
                'pm_out'  : out
                }
        return 'pm_release_done.html', data, None 

    def _del_module(self, req, data):
        self._check_post(req)
        self._check_name(req, 'project')
        self._check_name(req, 'module')

        project = req.args['project']
        name = req.args['module']
        cmd = "%s/proj-admin dm %s --proj-mods %s" % \
            (self.HGSCRIPT, project, name)
        out = pm_utils.run(cmd)
        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Module ' + name + ' has been deleted.',
                'pm_out'  : out
                }
        return 'pm_release_done.html', data, None 

    def _del_experiment(self, req, data):
        self._check_post(req)
        self._check_name(req, 'project')
        self._check_name(req, 'module')

        project = req.args['project']
        name = req.args['module']
        cmd = "%s/proj-admin dm %s --proj-mods experiments/%s" % \
            (self.HGSCRIPT, project, name)
        out = pm_utils.run(cmd)
        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Experiment module ' + name + ' has been deleted.',
                'pm_out'  : out
                }
        return 'pm_release_done.html', data, None

    def _add_experiment(self, req, data):
        '''
        Clone a module from the main project repository to the experiment
        directory inside the project.  This module is open to all project
        participants to manipulate.
        '''
        self._check_post(req)
        self._check_name(req, 'project')
        self._check_name(req, 'module')
        self._check_name(req, 'name')

        project = req.args['project']
        module = req.args['module']
        name = req.args['name']
        submitname=req.args['submit']
        if submitname=='Experiment':
            path = "%s/%s/experiments" % (self.PROJROOT, project)
            if not os.path.isdir(path):
                os.mkdir(path, 0750)

            cmd = "%s/proj-admin am %s --src-mods %s/%s=experiments/%s" % \
               (self.HGSCRIPT, project, project, module, name)
            out = pm_utils.run(cmd)
            data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Experiment module ' + name + ' has been created.',
                'pm_out'  : out
                }
            return 'pm_release_done.html', data, None 
        if submitname=='Rename':
            rname = req.args['name']
            path='/home/hg/repos/proj/'+project+'/'+module
            rpath='/home/hg/repos/proj/'+project+'/'+rname
            #modify the datebase
            filepath='home/trac/'+project+'/db/trac.db'
            cx = sqlite.connect(filepath)
            cursor = cx.cursor()
            sql="update repository set value=%s where value=%s"
            cursor.execute(sql,(rname,module))
            cx.commit()
            cursor.execute(sql,rpath,path)
            cx.commit()
            #modify the module folder name
            os.rename(path,rpath)
            #modify the module in branches
            dirname='/home/hg/repos/proj/'+project+'/branches/'
            bpathlist=os.listdir(dirname)
            for pt in bpathlist:
                if os.path.exists(dirname+pt+'/'+module)==True:
                    os.rename(dirname+pt+'/'+module,dirname+pt+'/'+rname)
            #modify the module in releases
            dirnamer='/home/hg/repos/proj/'+project+'/releases/'
            rpathlist=os.listdir(dirnamer)
            for rt in rpathlist:
                if os.path.exists(dirnamer+rt+'/'+module)==True:
                    os.rename(dirnamer+rt+'/'+module,dirnamer+rt+'/'+rname)
            #modify permission module name
            os.rename('/home/hg/acl/'+'.htaccess-proj'+'-'+project+'-'+module,'/home/hg/acl/'+'.htaccess-proj'+'-'+project+'-'+rname)
            outinfo='''Operation is successful:
modify the module foloder name;
modify the module in branches
modify the module in releases
modify the module name and module path in datebase
modify permission module name'''
            data = {'pm_href' : req.href.pmmm(),
                    'pm_proj':project,
                    'outinfo':outinfo
                }
            return 'pm_rename_done.html', data, None  
    def _clone_experiment(self, req, data):
        '''
        Clone one experiment module to another.
        '''
        self._check_post(req)
        self._check_name(req, 'project')
        self._check_name(req, 'module')
        self._check_name(req, 'name')

        project = req.args['project']
        module = req.args['module']
        name = req.args['name']
        cmd = "%s/proj-admin am %s --src-mods %s/experiments/%s=experiments/%s" % \
            (self.HGSCRIPT, project, project, module, name)
        out = pm_utils.run(cmd)
        data = {'pm_href' : req.href.pmmm(),
                'pm_proj' : project,
                'pm_msg'  : 'Experiment module ' + name + ' has been created.',
                'pm_out'  : out
                }
        return 'pm_release_done.html', data, None 

    def _new_project(self, req, data):
        '''
        Create a new project. Can clone initial modules using the
        given module spec. If nothing is given, create an empty project.
        Initial user list must be given, otherwise no user will be assigned
        to this project.
        '''
        self._check_post(req)
        self._check_name(req, 'name', 'No new project name.')
        self._check_name(req, 'user', 'No user name.')

        new_proj = req.args['name']

        if req.args.has_key('modules'):
            mod_str = req.args['modules']
        mod_str = mod_str[0:mod_str.find(' ')]
        if mod_str:
            mod_str = '--src-mods ' + mod_str

        global_acl = user_list.UserList()
        global_acl.load_file(self.GLOBAL_ACL, False)

        acl_file = '/var/tmp/%d' % int(time.time())
        if os.path.exists(acl_file):
            os.unlink(acl_file)
        f = user_list.UserList(acl_file)
        user = req.args['user']
        user_str = ""
        if isinstance(user, list):
            for u in user:
                if global_acl.has_user(u):
                    f.update_raw(u, global_acl.get_pwd(u))
        else:
            if global_acl.has_user(user):
                f.update_raw(user, global_acl.get_pwd(user))
        f.update_raw("zhao.zhengyu", global_acl.get_pwd("zhao.zhengyu"))
        f.update_raw("zhang.xueming", global_acl.get_pwd("zhang.xueming"))
        f.update_raw("haoboy", global_acl.get_pwd("haoboy"))
        f.save()
        user_str = "--acl " + acl_file
        
        cmd = "%s/proj-admin init %s %s %s" % (self.HGSCRIPT, new_proj, mod_str,
                                               user_str)
        try:
            out = pm_utils.run(cmd)
            msg = 'Project %s has been created.' % (new_proj)
            data = {'pm_href' : req.href.pmmm(),
                    'pm_proj' : new_proj,
                    'pm_msg'  : msg,
                    'pm_out'  : out
                    }
            os.unlink(acl_file)
            return data
        except Exception, e:
            os.unlink(acl_file)
            try:
                pm_utils.run(self.HGSCRIPT+"/proj-admin clean "+new_proj)
            except:
                # Ignore all exceptions.
                pass
            raise e
    def delete_file_folder(self,src):
        '''delete files and folders'''
        if os.path.isfile(src):
            try:
                os.remove(src)
            except:
                pass
        elif os.path.isdir(src):
            for item in os.listdir(src):
                itemsrc=os.path.join(src,item)
                self.delete_file_folder(itemsrc) 
            try:
                os.rmdir(src)
            except:
                pass 
    #def _delete_project(self,project):
    #    '''Call proj-admin to remove a user.'''
    #    proj_acl_file_name='.htaccess-proj-'+project
    #    proj_acl_file='/home/hg/acl/'+proj_acl_file_name
    #    proj_trac_file='/home/trac/'+project
    #    src='/home/hg/repos/proj/'+project
    #    if os.path.exists(proj_acl_file):
    #        os.remove(proj_acl_file)
    #    self.delete_file_folder(proj_trac_file)
    #    self.delete_file_folder(src)

    def _clone_project(self, req, data):
        '''
        Clone this project to another one with selected modules.
        '''
        self._check_post(req)
        self._check_name(req, 'project', 'No project.')
        self._check_name(req, 'modules', 'No modules.')
        self._check_name(req, 'name', 'No new project name.')

        project = req.args['project']
        new_proj = req.args['name']
        mod_str = req.args['modules']

        # Get modules from current project
        if not mod_str:
            mod_str = ','.join(self._list_modules(project))
        if not mod_str:
            raise PMGeneralError("No module in project %s" % project)
        mod_str = '--src-mods ' + mod_str
        
        # Root of this project
        root = '--root ' + self.PROJROOT + '/' + project
        
        # If we have a branch string, release from a branch.
        if req.args.has_key('branch'):
            branch = req.args['branch']
            if re.match(self._re_badname, branch):
                return self._mainpage.return_error("Invalid name "+branch)
            if len(branch) > 0:
                root += '/branches/' + branch  

        cmd = "%s/proj-admin init %s %s %s" % \
            (self.HGSCRIPT, new_proj, mod_str, root)
        try:
            out = pm_utils.run(cmd)
            msg = 'Project %s has been cloned to %s.' % (project, new_proj)
            data = {'pm_href' : req.href.pmmm(),
                    'pm_proj' : project,
                    'pm_msg'  : msg,
                    'pm_out'  : out
                    }
            return 'pm_release_done.html', data, None 
        except Exception, e:
            try:
                pm_utils.run(self.HGSCRIPT+"/proj-admin clean "+new_proj)
            except:
                pass
            raise e

    #----------------------------------------------------------------------
    # Private methods
    #----------------------------------------------------------------------

    def _list_users(self, proj):
        ulist = user_list.UserList()
        ulist.load_project(self._mainpage, proj)
        return ulist.to_list()
    
    def _list_all_users(self):
        file = self.GLOBAL_ACL 
        ulist = user_list.UserList()
        ulist.load_file(file) 
        return ulist.to_list()

    def _list_modules(self, proj):
        self.log.debug("Listing module for " + proj)
        mods = []
        for m in os.listdir(self.PROJROOT + "/" + proj):
            self.log.debug("checking module " + m)
            if m in self.HIDDEN_DIRS:
                continue
            mods.append(m)
        return mods

    def _list_submodules(self, proj, path):
        if not path:
            raise PMGeneralError('_list_submodules must has a valid path.')
        b = []
        subdir = self.PROJROOT + "/" + proj + "/" + path
        if not os.path.isdir(subdir):
            os.mkdir(subdir, 0750)
        for m in os.listdir(subdir):
            if m in self.HIDDEN_DIRS:
                continue
            b.append(urllib.quote(m))
        return b

    def _list_branches(self, proj):
        return self._list_submodules(proj, "branches")
    
    def _list_releases(self, proj):
        return self._list_submodules(proj, "releases")
    
    def _list_experiments(self, proj):
        return self._list_submodules(proj, "experiments")

