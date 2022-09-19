import os
import core.terminal
import atexit

try:
        import readline
except ImportError:
    try:
        import pyreadline as readline
    except ImportError: 
        print '[!] Error, readline or pyreadline python module required. In Ubuntu linux run\n[!] sudo apt-get install python-readline'
        sys.exit(1)

dirpath = '.weevely'
rcfilepath = 'weevely.rc'
historyfilepath = 'weevely_history'

class Configs:

    def _read_rc(self, rcpath):

        try:
            rcfile = open(rcpath, 'r')
        except Exception, e:
            self._tprint( "[!] Error opening '%s' file." % rcpath)
        else:
            return [c.strip() for c in rcfile.read().split('\n') if c.strip() and c[0] != '#']

        return []

    def _historyfile(self):
        return os.path.join(self.dirpath, historyfilepath)

    def _make_home_folder(self):

        self.dirpath = os.path.join(os.path.expanduser('~'),dirpath)
        
        if not os.path.exists(self.dirpath):
            os.mkdir(self.dirpath)


    def _init_completion(self):

    
            self.historyfile = self._historyfile()

            self.matching_words =  [':%s' % m for m in self.modhandler.modules_classes.keys()] + [core.terminal.help_string, core.terminal.load_string, core.terminal.set_string]
        
            try:
                readline.set_history_length(100)
                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind( 'tab: complete' )
                readline.set_completer( self._complete )
                readline.read_history_file( self.historyfile )

            except IOError:
                pass
            atexit.register( readline.write_history_file, self.historyfile )



    def _complete(self, text, state):
        """Generic readline completion entry point."""

        try:
            buffer = readline.get_line_buffer()
            line = readline.get_line_buffer().split()

            if ' ' in buffer:
                return []

            # show all commandspath
            if not line:
                all_cmnds = [c + ' ' for c in self.matching_words]
                if len(all_cmnds) > state:
                    return all_cmnds[state]
                else:
                    return []


            cmd = line[0].strip()

            if cmd in self.matching_words:
                return [cmd + ' '][state]

            results = [c + ' ' for c in self.matching_words if c.startswith(cmd)] + [None]
            if len(results) == 2:
                if results[state]:
                    return results[state].split()[0] + ' '
                else:
                    return []
            return results[state]

        except Exception, e:
            self._tprint('[!] Completion error: %s' % e)
