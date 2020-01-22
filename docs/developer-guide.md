# WIP: Developer guide


This guide is made for the developers who might want add their cool
feature to gdeploy.

Why should you add your cool feature to gdeploy, you ask?

Well, If you want to automate your feature deployment using Ansible and
let users use it without editing the playbooks and what not, then adding
it to gdeploy is the way to go.

We expect the developers to know the following:

1. Python(Duh!)
2. Writing Ansible Playbooks(necessary) and modules(worst case)


To add a new feature, start with developer setup of gdeploy. Please
refer<a href="https://github.com/gluster/gdeploy/blob/master/docs/INSTALL.md">
INSTALL.md</a> for installation instructions.

Once you have gdeploy setup, get ready to make your feature gdeploy
compatible. Use the gdeploy option --addfeature for this. To add a
feature names "myfeature":

`gdeploy --addfeature myfeature`

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
provided corresponding to each of these actions. <a
href="https://github.com/gluster/gdeploy/blob/master/gdeployfeatures/snapshot/snapshot.json">
This</a> is the JSON file written to implement the snapshot feature in
gdeploy.

Once your JSON is ready, the next big task is to create playbooks to run
for each of these actions. This is where we cannot help you much.
Writing playbooks and modules depends on your feature. So put your
Python and Ansible skills to good use and write some cool playbooks.
Playbooks should go under the directory <l>playbooks</l> under the
working directory and modules should go under the directory
<l>modules</l> under the working directory. Once your playbooks are in,
add these playbook file names to the file <a
href="https://github.com/gluster/gdeploy/blob/master/gdeploylib/defaults.py">
defaults.py</a>, just because it is cleaner.

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
and let the defaults be(You will know what I mean when you see it. ;-))

