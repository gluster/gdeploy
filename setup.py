from setuptools import setup, find_packages

setup(
    name="gluster-deploy",

    version="1.0.0",

    author="Nandaja Varma",
    author_email="nandaja.varma@gmail.com",

    packages=[  'glusterlib',
                'modules'
             ],

    scripts=[
        'bin/gluster-deploy'
        ],

    include_package_data=True,
    url="https://github.com/nandajavarma/gluster-deploy",

    license="LICENSE",
    description="Tool to automatically setup and deploy " \
    "gluster using ansible",

    long_description=open("README.md").read(),

    install_requires=[
        "ansible",
        "pyyaml",
    ],
)
