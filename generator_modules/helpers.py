import os


class Helpers(object):

    def mk_dir(self, dirlists):
        for each in dirlists:
            if os.path.isdir(each):
                self.exec_cmds('rm -rf', each)
            self.exec_cmds('mkdir', each)

    def touch_file(self, filename):
        try:
            os.remove(filename)
        except OSError:
            pass
        self.exec_cmds('touch', filename)

    def get_file_dir_path(self, basedir, newdir):
        return os.path.join(os.path.realpath(basedir), newdir)

    def exec_cmds(self, cmd, opts):
        try:
            os.system(cmd + ' ' + opts)
        except:
            print "Error: Command %s failed. Exiting!" % cmd
            sys.exit()
