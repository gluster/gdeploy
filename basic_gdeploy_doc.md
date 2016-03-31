Introduction of gdeploy and how to use gdeploy to configure glusterfs: 
-----------------------------------------------------------------------------------------------

This document is intended to give a basic overview of the gdeploy tool like,
what is gdeploy, what does it do, and how you can use it.

What is glusterfs?

GlusterFS is a scale-out network-attached storage file system. It has found applications 
including cloud computing, streaming media services, and content delivery networks. GlusterFS 
was developed originally by Gluster, Inc., then by Red Hat, Inc., after their purchase of 
Gluster in 2011.

What is gdeploy?

gdeploy is an automation tool that uses Ansible to simplify setting up glusterfs 
file system for known configurations. You can easily deploy and configure glusterfs 
software across multiple machines using gdeploy tool. You must install ansible version 1.9.2 
or higher to use gdeploy.

Or


It's a python based automation tool that can be used to deploy and configure
glusterfs file system across multiples machines. Gdeploy must be run from a
machine that has ansible installed on it. Ansible is one of gdeploy's
dependencies. It only needs to installed on the machines from where you want to
manage glusterfs so no need to install on the servers that you are managing. You must install 
ansible version 1.9.2 or higher to use gdeploy.

How gdeploy works?

gdeploy depends on configuration file to make changes to machines which are listed 
inside the [host] section config file. Config file is defined by user.

Why gdeploy to install glusterfs?

Setting up a backend filesystem for glusterfs becomes a tedious task as the number of
servers/bricks increase. Glusterfs being is a highly scalable software solution provides 
the user ability to create a storage cluster with large number of nodes.

Why  gdeploy and not Ansible to deploy  glusterfs?

gdeploy automates deployment of glusterfs for known configurations while providing you with 
flexibility of tweaking important parameters tailored to your needs. This is a rather 
tedious and repetitive task even using ansible playbooks alone.

gdeploy configuration file can be used for:

    # [hosts] section includes ip addresses of all the machines which you want to peer probe.
    # Backend setup configurations on any number of machines or nodes.
    # Gluster cluster setup (Volume configuration)
    # Features configurations like:
        * NFS-Ganesha configuration
        * Samba configuration
          * Snapshot configuration.
          * Geo-replication configuration.
        * Quota configuration
        * RH-subscription
        * firewalld
        * yum
     * ctdb


Installation of gdeploy:

There are two ways to install gdeploy. This documentation is based on installation process
 on Fedora 23 on Virtual Machine Manager. 

#. Clone it via github repository
#. Using Operating System’s package manager (use rpm package manager for Fedora 23 OS)

1.) Installation procedure for gdeploy using github clone.

 Before we begin installing gdeploy, there are some prerequisites packages that you should 
 already have installed on your computer to use gdeploy.

The package dependencies for gdeploy may differ slightly across different operating systems 
and environments. Other platforms and quirks will be added as and when they are encountered.

This document is continuously being updated. The list of dependencies may not be exhaustive.
 We’ll update this section periodically and frequently.


Below is a known list of packages that you must have installed for gdeploy to work.
 You should be able to get all these using your Operating System’s package manager.

install python (No need to install pip exclusively if you are using python 2.7.10 or above)
install pip
install gcc
install python-devel package

These are commands that needs to be executed on Fedora 23 VM. They should also work fine 
if you are using any other version of Fedora.

    sudo dnf -y install python-pip
    dnf install gcc
    dnf install redhat-rpm-config
    dnf install python-devel

Or
Run the below mentioned packages to ensure gdeploy will run.

# yum install automake autoconf libtool flex bison openssl-devel libxml2-devel python-devel
 libaio-devel libibverbs-devel librdmacm-devel readline-devel lvm2-devel glib2-devel 
userspace-rcu-devel libcmocka-devel libacl-devel sqlite-devel redhat-rpm-config

It also depends on some other packages as well like ansible but those are 
taken care by requirements.txt file. You'll get to see when you’ll run it.

When you are done installing the above packages. We're good to go to the next step.

Here are quick rundown of steps that  you need to do to install gdeploy. If you
 are completely new to git and need some help here is the link.

1.) clone the gdeploy repository by running the below command in your preferred directory.

    [poo@poohostname ~]$ git clone git@github.com:gluster/gdeploy.git

2.) Go to inside gdeploy folder. Like this:
    
    $ cd gdeploy/

3.) You should be the root user to run the requirement.txt file. You can become root by running
    the following command at the command prompt and then entering your password.

    [poo@poohostname gdeploy]$ su
    Password:


4.)  Install the requirements.txt file.

    [root@poohostname gdeploy]# pip install -r requirements.txt

5.) Now we have to setup gdeploy by running below command.

    [root@poohostname gdeploy]# ./gdeploy_setup.sh
    
or

You can do the same manually as well.

#. Add ansible modules to ANSIBLE_LIBRARY environment variable by running the below command.

    echo "export Ansible_LIBRARY=$ANSIBLE_LIBRARY:'/path/to/gdeploy/modules'" >> ~/.bashrc

    In my case, this would be:

    echo "export Ansible_LIBRARY=$ANSIBLE_LIBRARY:'/home/poo/gdeploy/modules'" >> ~/.bashrc


    #. Add ansible playbooks(inside the templates directory) to GDEPLOY_TEMPLATES environment variable.
    

    echo "export GDEPLOY_TEMPLATES='path/to/gdeploy'" >> ~/.bashrc

    In my case, this would be:

    echo "export GDEPLOY_TEMPLATES='/home/poo/gdeploy'" >> ~/.bashrc

#. Install glusterlib module using setuptool.

    python setup.py install


6.) If you have properly followed all the steps, gdeploy should be installed on your machine. To
    check this, you can run command gdeploy --version. The output should look like this.

    [poo@poohostname /]$ gdeploy --version
    gdeploy 2.0





Installation of gdeploy using  operating system's package manager:
-------------------------------------------------------------------

Download gdeploy ( .rpm file for Fedora OS ) from here→ http://download.gluster.org/pub/gluster/gdeploy/2.0/

Prerequisites to install gdeploy:

    #. ansible>=1.9
    #. python>=2.6
    #. python(abi) = 2.7
    #. python-eventlet

These are the commands that needs to be executed to install the prerequisites on Fedora 23 VM.

    #. dnf install ansible
    #. dnf install python-eventlet

When you installed the above packages, go ahead and install the gdeploy by running the 
below command from the directory where you downloaded it. You need to be the root user 
to install gdeploy.

    [root@poo Downloads]# rpm -Uvh gdeploy-2.0-0.fc23.noarch.rpm


gdeploy should be installed without fail if you followed the steps properly. In case,
 if you happen to encounter any error even after following the above steps. 
Please do contact us here.
    
--------------------------

Now you can use gdeploy tool to configure glusterfs. Before you can use gdeploy to
configure glusterfs you need to have glusterfs-client installed on the machine from 
where you’ll be mounting the volume. And glusterfs-server installed on the machine 
where you’ll be storing your files/data.



Mandatory steps before you can configure glusterfs using gdeploy
-------------------------------------------------------------------------------------------

You need to have done all the below steps before you can begin writing your
first config file.

#. Should have glusterfs-client and glusterfs-servers running
#. Should have gdeploy installed
#. Create passwordless ssh login for all the nodes that will used as cluster.
  In simple words, create passwordless ssh login for all the machines which
  will be listed inside the [hosts] section.


Now we are ready to write our first configuration file. Config file names are
arbitrary.  We'll be writing very simple config file just to get an idea of how
this works. Once you are comfortable with this, you can go ahead and learn
writing more complicated config files (this would be a link). Config file is
basically split into different sections. You write specific data related to
each section under a header that is the section name. More details below.

Note: There shouldn't be any gap between section's name and section's content.
Otherwise, it wil throw an error.

Below are the section's names that we would need to write our config file.

#. [hosts]
#. [backend-setup]
#. [peer]
#. [volume]
#. [clients]


Below is the sample of 2*2 distributed replication config file.
---------------------------------------------------------------

   [hosts]
   10.70.47.17
   10.70.46.173
   10.70.47.97
   10.70.47.32

   [backend-setup]
   devices=/dev/vdb

   [peer]
   manage=probe

   [volume]
   action=create
   volname=volume1
   transport=tcp,rdma
   replica=yes
   replica_count=2
   force=yes

   [clients]
   action=mount
  volname=volume1
   hosts=192.168.124.1
   fstype=glusterfs
   client_mount_points=/home/poo/client_mount



Usage:
------

You can execute it by typing the below command:

  gdeploy -c <config file name>

In the case of this tutorial:

   gdeploy -c distri-repli.config
   
 

Where can I find more info?
---------------------------

For now: https://github.com/gluster/gdeploy

Later: this document would have a lot more info, probably all the info you'll
need about gdeploy.





