'''
Created on Feb 23, 2010
Utility functions and classes.
@author: haoboy
'''

class PMGeneralError(Exception):
    def __init__(self, str = ""):
        self.str = str
    def __str__(self):
        return self.str

class PMRunCommandError(PMGeneralError):
    def __init__(self, str = ""):
        PMGeneralError.__init__(self, str)

def run(str):
    '''Execute an external shell commands and print warning if failed.'''
    from subprocess import Popen, PIPE
    try:
        process = Popen(str, shell=True, stderr=PIPE, stdout=PIPE)
        (out_str, err_str) = process.communicate()
        out = out_str + '\n' + err_str
        retcode = process.wait()
        if retcode != 0:
            raise PMRunCommandError("Command '%s' failed with error code %d:\n%s" % 
                                    (str, retcode, out))
        return(out)
    except OSError, e:
        raise PMRunCommandError("Failed to execute '%s':\n%s" % (str, e))
    except PMRunCommandError, e:
        raise e
    except Exception, e:
        raise PMRunCommandError("Command '%s' failed:\n%s" % (str, e))

