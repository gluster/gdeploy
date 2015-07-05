import os
from generator_modules.helpers import Helpers
from generator_modules.yaml_writer import YamlWriter


class VarFileGenerator(Helpers, YamlWriter):

    def __init__(self, var_file, options, hosts, config, base_dir, group):
        self.options = options
        self.hosts = hosts
        self.config = config
        self.base_dir = base_dir
        self.var_file = var_file
        self.group = group
        vars_dir = self.get_file_dir_path(self.base_dir, var_file)
        dir_list = [self.base_dir, vars_dir]
        self.mk_dir(dir_list)
        output = {'host_vars': self.host_vars_gen,
                  'group_vars': self.group_vars_gen
                  }[var_file](vars_dir)
        self.move_templates_to_playbooks()

    def host_vars_gen(self, host_vars_path):
        for host in self.hosts:
            host_file = self.get_file_dir_path(host_vars_path, host)
            self.touch_file(host_file)
            device_names = filter(
                None,
                self.config_section_map(
                    self.config,
                    host,
                    'devices',
                    True).split(','))
            YamlWriter(device_names, self.config, host_file, self.var_file)

    def group_vars_gen(self, group_vars_path):
        group_file = self.get_file_dir_path(group_vars_path, self.group)
        self.touch_file(group_file)
        device_names = self.config_get_options(self.config,
                                               'devices', True)
        YamlWriter(device_names, self.config, group_file, self.var_file)

    def template_files_create(self, temp_file):
        if not os.path.isdir(temp_file):
            return False
        self.exec_cmds('cp %s/*' % temp_file, self.base_dir)
        return True

    def move_templates_to_playbooks(self):
        templates_path = '/usr/share/ansible/ansible-glusterfs/templates'
        templates_path_bk = self.get_file_dir_path('.', 'templates')
        if not (self.template_files_create(templates_path) or
                self.template_files_create(templates_path_bk)):
            print "Error: Template files not found at %s or %s. " \
                "Check your ansible-gluster " \
                "installation and try " \
                "again." % (templates_path, templates_path_bk)
            sys.exit(0)
