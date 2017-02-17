"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global

helpers = Helpers()

def pv_create(section_dict):
    global helpers
    section_dict['bricks'] = helpers.correct_brick_format(
            helpers.listify(section_dict['devices']))
    Global.ignore_errors = section_dict.get('ignore_pv_errors')
    helpers.perf_spec_data_write()
    Global.ignore_errors = section_dict.get('ignore_pv_errors')
    Global.logger.info("Creating pv on bricks %s"%section_dict['bricks'])
    return section_dict, defaults.PVCREATE_YML

def pv_resize(section_dict):
    global helpers
    devices = helpers.correct_brick_format(
            helpers.listify(section_dict['devices']))
    expand = section_dict.get('expand')
    shrink = section_dict.get('shrink')
    Global.ignore_errors = section_dict.get('ignore_pv_errors')
    if shrink is not None:
        shrink  = helpers.listify(shrink)
        devices  = helpers.listify(devices)
        data = []
        for disk, size in zip(devices, shrink):
            pvshrink = {}
            pvshrink['disk'] = disk
            pvshrink['size'] = size
            data.append(pvshrink)
            Global.logger.info("Resizing disk:%s with size:%s"%(disk,size))
        section_dict['pvshrink'] = data
        return section_dict, defaults.PVSHRINK_YML
    elif expand == 'yes':
        section_dict['pvexpand'] = 'true'
        section_dict['bricks'] = devices
        Global.logger.info("Extending pv on disks %s"%devices)
        return section_dict, defaults.PVEXTEND_YML
    # If you have reached here no proper values provided
    msg = "No valid value for resize, provide valid values for"\
          " expand or shrink in config"
    print "Error: %s"%msg
    Global.logger.error(msg)
    helpers.cleanup_and_quit()


