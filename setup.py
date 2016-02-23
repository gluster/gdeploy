from setuptools import setup

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
        'gdeploy/gdeploy'
    ],
    include_package_data=True,
    url="https://github.com/gluster/gdeploy",

    license="LICENSE",
    description="Tool to automatically setup and deploy " \
    "gluster using ansible",

    long_description=open("README.md").read(),

    install_requires=[
        "ansible",
        "pyyaml",
        "eventlet",
    ],

)
