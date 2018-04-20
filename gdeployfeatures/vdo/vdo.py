"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global
helpers = Helpers()

def vdo_create(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_vdo_errors')
    Global.vdo_device = True
    section_dict['state'] = 'present'
    disks = helpers.correct_brick_format(
        helpers.listify(section_dict['devices']))
    vdonames = helpers.listify(section_dict.get('names'))
    lsize = helpers.listify(section_dict.get('logicalsize'))

    # Zero-fill the lszie so that logicalsize defaults to disk size if not
    # provided.
    for fi in range(len(vdonames) - len(lsize)):
        lsize.append('')

    vdolist = []
    for d, n, lsize in zip(disks, vdonames, lsize):
        v = {}
        v['disk'] = d
        v['name'] = n
        v['logicalsize'] = lsize
        vdolist.append(v)
    section_dict['vdos'] = vdolist
    activate = section_dict.get('activate')

    if activate is None:
        data_not_found(activate)
    elif activate.lower() not in ['yes', 'no', 'true', 'false']:
        log_yes_no_error(activate)
    run = section_dict.get('run')
    if run is None:
        data_not_found(run)
    elif run.lower() not in ['yes', 'no', 'true', 'false']:
        log_yes_no_error(run)

    Global.logger.info("Creating vdo volume(s) %s" % vdonames)
    return section_dict, defaults.VDO_CREATE

def vdo_delete(section_dict):
    Global.ignore_errors = section_dict.get('ignore_vdo_errors')
    section_dict['state'] = 'absent'
    section_dict['vdonames'] = helpers.listify(section_dict.get('names'))
    Global.logger.info("Deleting vdo volume(s) %s"% section_dict['vdonames'])
    return section_dict, defaults.VDO_DELETE

def data_not_found(item):
    global helpers
    msg = "Value for option %s not found." % item
    print "Error: %s" % msg
    Global.logger.error(msg)
    helpers.cleanup_and_quit()

def log_yes_no_error(key):
    msg = "Error: invalid value for %s" % key
    print msg
    print "Possible values are 'yes', 'no', 'true', 'false'"
    Global.logger.error(msg)
