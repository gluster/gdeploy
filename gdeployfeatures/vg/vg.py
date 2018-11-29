"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global

helpers = Helpers()

def vg_create(section_dict):
    global helpers
    pvnames = get_pv_names(section_dict)
    vgnames = helpers.listify(section_dict['vgname'])
    Global.ignore_errors = section_dict.get('ignore_vg_errors')
    section_dict = set_default_values(section_dict, pvnames, vgnames)
    helpers.perf_spec_data_write()
    Global.logger.info("Creating volume groups %s"%vgnames)
    return section_dict, defaults.VGCREATE_YML

def vg_extend(section_dict):
    global helpers
    pvnames = get_pv_names(section_dict)
    vgnames = helpers.listify(section_dict['vgname'])
    Global.ignore_errors = section_dict.get('ignore_vg_errors')
    if len(vgnames) != 1:
        msg = "We can only extend one vg at a time"
        print "Error: %s"%msg
        Global.logger.error(msg)
        helpers.cleanup_and_quit()
    section_dict['vg'] = vgnames[0]
    section_dict['disk'] = pvnames
    Global.logger.info("Extending volume groups %s"%vgnames)
    return section_dict, defaults.VGEXTEND_YML

def set_default_values(section_dict, pvnames, vgnames):
    global helpers
    if len(pvnames) != len(vgnames):
        if len(vgnames) > len(pvnames):
            msg = "Insufficient number of values for pvname"
            print "Error: %s"%msg
            Global.logger.error(msg)
            helpers.cleanup_and_quit()
        else:
            if len(vgnames) != 1:
                msg = "Provide 1 value for vgname or " \
                      "one for each pvname"
                print "Error: %s"%msg
                Global.logger.error(msg)
                helpers.cleanup_and_quit()
    return dictify_pv_vg_names(section_dict, pvnames, vgnames)

def dictify_pv_vg_names(section_dict, pvnames, vgnames):
    data = []
    vglist = {}
    vglist['brick'] = ' '
    if len(vgnames) == 1 and len(pvnames) > 1:
        for p in pvnames:
            vglist['brick'] += p+' '
        vglist['vg'] = vgnames[0]
        data.append(vglist)
    else:
        for pv, vg in zip(pvnames, vgnames):
            vglist = {}
            vglist['brick'] = pv
            vglist['vg'] = vg
            data.append(vglist)
    section_dict['vgnames'] = data
    Global.vg_data.append(vglist)
    return section_dict

def get_pv_names(section_dict):
    global helpers
    pvnames = section_dict.get('pvname')
    if not pvnames:
        pv_section = Global.sections.get('pv')
        if not pv_section or not pv_section['devices']:
            msg = "'pvname' not specified to create " \
                  "volume group."
            print "Error: %s"%msg
            Global.logger.error(msg)
            helpers.cleanup_and_quit()
        pvnames = pv_section['devices']
    pvnames = helpers.correct_brick_format(helpers.listify(pvnames))
    return pvnames
