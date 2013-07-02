'''
Created on Feb 22, 2010
Packaging a .htaccess file.
@author: haoboy
'''

import os
import re

import sys
import random

# We need a crypt module, but Windows doesn't have one by default.  Try to find
# one, and tell the user if we can't.
try:
    import crypt
except ImportError:
    try:
        import fcrypt as crypt
    except ImportError:
        sys.stderr.write("Cannot find a crypt module.  "
                         "Possibly http://carey.geek.nz/code/python-fcrypt/\n")
        sys.exit(1)

from pm_utils import PMGeneralError

# Original author: Eli Carter

def salt():
    """Returns a string of 2 randome letters"""
    letters = 'abcdefghijklmnopqrstuvwxyz' \
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '0123456789/.'
    return random.choice(letters) + random.choice(letters)

class UserListNoFileError(PMGeneralError):
    def __init__(self, str = "UserList cannot find file."):
        PMGeneralError.__init__(self, str)
    
class UserListBadUsernameError(PMGeneralError):
    def __init(self, str = "Bad username in UserList."):
        PMGeneralError.__init__(self, str)

class UserList(object):
    '''
    Encapsulation of a .htaccess file of a project.
    '''
    _users = {}

    def __init__(self, filename = ''):
        self.filename = filename

    def load_project(self, mainpage, proj):
        acl_file = mainpage.ACLROOT + '/.htaccess-proj-' + proj
        self.load_file(acl_file)
        
    def load_module(self, mainpage, proj,module):
        acl_file = mainpage.ACLROOT + '/.htaccess-proj-' + proj + '-' + module
        self.load_file(acl_file)
        
    def load_file(self, acl_file, create=False):
        self._users = {}
        self.filename = acl_file
        if not os.path.exists(self.filename):
            if create:
                # We will save data to this class and save it later.
                return
            else:
                raise UserListNoFileError("%s does not exist" % self.filename)

        if not os.path.isfile(acl_file):
            raise UserListNoFileError('Cannot find file %s' % acl_file)
        try:
            f = open(acl_file, "r")
            for line in f:
                str = line.rstrip()
                match = re.match('([^:]+):(.*)', str)
                if not match:
                    continue
                if re.match('^#', str):
                    continue
                self._users[match.group(1)] = match.group(2)
            f.close()
        except:
            raise UserListNoFileError("Cannot read from file "+acl_file)

    def to_list(self):
        u = self._users.keys()
        u.sort()
        return u

    def save(self):
        """Write the htpasswd file to disk"""
        f = open(self.filename, 'w')
        users = self._users.keys()
        users.sort()
        for u in users:
            f.writelines("%s:%s\n" % (u, self._users[u]))
        f.close()

    def get_pwd(self, user):
        if user in self._users:
            return self._users[user]
        else:
            return None

    def empty(self):
        return len(self._users.keys()) > 0

    def users(self):
        return self._users.keys()
    
    def password(self, username):
        return self._users[username]

    def has_user(self, username):
        return self._users.has_key(username)

    def delete(self, username):
        """Remove the entry for the given user."""
        if self._users.has_key(username):
            del(self._users[username])

    def update(self, username, password):
        """Replace the entry for the given user, or add it if new."""
        if re.match('/^#/', username):
            raise UserListBadUsernameError("Bad username: "+username) 
        pwhash = crypt.crypt(password, salt())
        self._users[username] = pwhash

    def update_raw(self, username, passwd):
        if re.match('/^#/', username):
            raise UserListBadUsernameError("Bad username: "+username) 
        self._users[username] = passwd

def main():
    pass
    
if __name__ == '__main__':
    main()
