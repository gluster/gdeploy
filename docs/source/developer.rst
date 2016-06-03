.. _rst_developerdoc:

Developer Documentation
========================


With gdeploy, the user get to remotely configure a lot of features in
multiple machines, without worrying dealing with the complexities of
writing Ansible Playbooks, modules, etc. It is the duty of the developer
to worry about all these things. Adding a new feature to gdeploy is
relatively easy, but comes with the cost of writing playbooks and
modules(if necessary) for Ansible. So this guide assumes that the
developer is comfortable with Python and has got the basic working
knowledge of Ansible.

gdeploy - Developer setup
^^^^^^^^^^^^^^^^^^^^^^^^^

To setup the development environment, refer :ref:`rst_sourceinstall`.

Proceed further once you are done with the setup.


gdeploy architecture
^^^^^^^^^^^^^^^^^^^^

gdeploy is a very lightweight, simple tool that efficiently make use of
Ansible, hiding the major complexities of it from the user, that does
numerous operations on remote machines sequentially. To do this, gdeploy
divides the logic to 3 parts:
1. Ansible module that implements the desired logic to be executed in
   the remote machine.
2. Ansible playbook that makes use of the already present Ansible module
   and specifies how a particular operation is to be performed.
3. A section independent from both the above sections that reads the
   user configuration file, parses it accordingly, sets default values
   for some if not provided by the user, and then populate all these
   data in variables that the Ansible playbook will then use. More
   about these variable can be found in the `Ansible documentation about
   them <http://docs.ansible.com/ansible/playbooks_variables.html>`_

   For this, gdeploy provide what we call the sections or features(:ref:`rst_features`).
   Each feature will have n-number of options for which the user will
   specify the value.

Adding your first feature to gdeploy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to add a new feature to Ansible, the developer has to make sure
the three above mentioned components or sections are written properly
and works as intended.

The development process can be started in the following order:

1. Write the Ansible module, if needed.
2. Write Ansible playbooks that does the necessary operations in the
   right order.
3. Add a feature with a suitable name matching your requirement to the
   gdeploy framework.

** Add a feature to gdeploy **

Use the gdeploy option --addfeature for this. To add a
feature names "myfeature":

    $ gdeploy --addfeature myfeature

This will create a directory <l>myfeature</l> under <l>features</l>
directory. If you look inside this directory, you will see that gdeploy
has created 3 files for you: an init file, a JSON file and a python
script. You need just edit the JSON file and the python script to make
gdeploy do what you want. The JSON file is used by gdeploy to validate
the user configuration provided for your feature(in this case,
'myfeature'). The necessary option for every feature in gdeploy is the
option named 'action'. Specify each one of your feature's action inside
the action hash in the JSON file. Each of these action keys will have a
list names 'options' which will specify the options that is to be
provided corresponding to each of these actions.  `This
<https://github.com/gluster/gdeploy/blob/master/gdeployfeatures/snapshot/snapshot.json>`_
is the JSON file written to implement the snapshot feature in gdeploy.

Once your JSON is ready, the next big task is to create playbooks to run
for each of these actions. This is where we cannot help you much.
Writing playbooks and modules depends on your feature. So put your
Python and Ansible skills to good use and write some cool playbooks.
Playbooks should go under the directory <l>playbooks</l> under the
working directory and modules should go under the directory
<l>modules</l> under the working directory. Once your playbooks are in,
add these playbook file names to the file `defaults.py
<https://github.com/gluster/gdeploy/blob/master/gdeploylib/defaults.py>`_,
just because it is cleaner.

Now you just have to let gdeploy know which playbook corresponds to
which feature action. This is where the python script comes into
picture. There should be a function corresponding to each feature action
inside this Python script. The function name should be in the format
'myfeature_actionname'. You need just edit the dummy method names
provided inside the script. I am sure you will figure it out. It is
pretty straight forward. As you will see inside the scripts, each
function will have a parameter being passed, 'section_dict'. This
dictionary holds the as keys and values, the options and their
corresponding values provided by the user in her configuration file
under the section 'myfeature'. Just print it out and see for yourself if
you are happy with the format. You can modify the keys and values in the
dictionary as per your needs. Each function should return 2 parameters:
One is the modified or not modified section_dict and other is the
playbook to be run for that particular section. Just edit the YML_NAME
and let the defaults be.




Testing your code
^^^^^^^^^^^^^^^^^


Guidelines for contribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^
