from setuptools import setup
from distutils.command.install_scripts import install_scripts
from shutil import move

class strip_ext(install_scripts):
    def run(self):
        install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith('.py'):
                move(script, script[:-3])

setup(
    name="gdeploy",
    version="2.0",
    author="Nandaja Varma",
    author_email="nandaja.varma@gmail.com",
    packages=[  'gdeploylib', 'gdeploycore', 'gdeployfeatures',
                'gdeployfeatures/firewalld', 'gdeployfeatures/quota',
                'gdeployfeatures/rh_subscription',
                'gdeployfeatures/snapshot', 'gdeployfeatures/yum',
                'gdeployfeatures/update_file', 'gdeployfeatures/ctdb',
                'gdeployfeatures/geo_replication',
                'gdeployfeatures/service', 'gdeployfeatures/shell',
                'gdeployfeatures/nfs_ganesha'
             ],
    scripts=[
        'gdeploy/gdeploy.py'
    ],
    cmdclass = {
        "install_scripts": strip_ext
    },
    include_package_data=True,
    url="https://github.com/gluster/gdeploy",

    license="LICENSE",
    description="Tool to automatically setup and deploy " \
    "gluster using ansible",

    install_requires=[
        "ansible",
        "pyyaml",
        "eventlet",
    ],

)
