import os,sys
from moduleexception import ModuleException

from helper import Helper


class ModHandler:

    def __init__(self, url = None, password = None):

        self.url = url
        self.password = password

        self.__set_path_modules()

        self.interpreter = None
        self.modules_classes = {}
        self.modules = {}

        self.modules_names_by_group = {}

        self._first_load(self.path_modules)

        self.verbosity=[ 3 ]
        
        self._last_warns = ''
        

    def __set_path_modules(self):
    
    	try:
    		current_path = os.path.realpath( __file__ )
    		root_path = os.sep.join(current_path.split(os.sep)[:-2]) + os.sep
    		self.path_modules = root_path + 'modules'
    	except Exception, e :
    		raise Exception('Error finding module path: %s' % str(e))
    
        if not os.path.exists(self.path_modules):
		          raise Exception( "No module directory %s found." % self.path_modules )
    


    def _first_load(self, startpath, recursive = True):

        for file_name in os.listdir(startpath):

            file_path = startpath + os.sep + file_name

            if os.path.isdir(file_path) and recursive:
                self._first_load(file_path, False)
            
            if os.path.isfile(file_path) and file_path.endswith('.py') and file_name != '__init__.py':
                
                module_name = '.'.join(file_path[:-3].split(os.sep)[-2:])
                mod = __import__('modules.' + module_name, fromlist = ["*"])
                classname = module_name.split('.')[-1].capitalize()
                
                if hasattr(mod, classname):
                    modclass = getattr(mod, classname)
                    self.modules_classes[module_name] = modclass
                
                    module_g, module_n = module_name.split('.')
                    if module_g not in self.modules_names_by_group:
                        self.modules_names_by_group[module_g] = []
                    self.modules_names_by_group[module_g].append(module_name)

        self.ordered_groups = self.modules_names_by_group.keys()
        self.ordered_groups.sort()

    def load(self, module_name):

        if module_name not in self.modules_classes.keys():
            raise ModuleException(module_name, "Module '%s' not found in path '%s'." % (module_name, self.path_modules) )  
        elif not module_name:
            module_name = self.interpreter
        elif not module_name in self.modules:
            self.modules[module_name]=self.modules_classes[module_name](self)

        
        return self.modules[module_name]


    def set_verbosity(self, v = None):

        if not v:
            if self.verbosity:
                self.verbosity.pop()
            else:
                self.verbosity = [ 3 ]
        else:
            self.verbosity.append(v)

