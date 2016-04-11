#!/usr/bin/python
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
    section_dict = set_default_values(section_dict, pvnames, vgnames)
    helpers.perf_spec_data_write()
    return section_dict, defaults.VGCREATE_YML

def vg_extend(section_dict):
    global helpers
    pvnames = get_pv_names(section_dict)
    vgnames = helpers.listify(section_dict['vgname'])
    if len(vgnames) != 1:
        print "Error: We can only extend one vg at a time"
        helpers.cleanup_and_quit()
    section_dict['vg'] = vgnames[0]
    section_dict['disk'] = pvnames
    return section_dict, defaults.VGEXTEND_YML

def set_default_values(section_dict, pvnames, vgnames):
    global helpers
    if len(pvnames) != len(vgnames):
        if len(vgnames) > len(pvnames):
            print "Error: Insufficient number of values for pvname"
            helpers.cleanup_and_quit()
        else:
            if len(vgnames) != 1:
                print "Error: Provide 1 value for vgname or " \
                        "one for each pvname"
                helpers.cleanup_and_quit()
            if section_dict['one-to-one'] == 'no':
                vgnames *= len(pvnames)
            else:
                vgs = []
                for i in range(1, len(pvnames) + 1):
                    vgs.append(vgnames[0] + str(i))
                vgnames = vgs
    return dictify_pv_vg_names(section_dict, pvnames, vgnames)

def dictify_pv_vg_names(section_dict, pvnames, vgnames):
    data = []
    for pv, vg in zip(pvnames, vgnames):
        vglist = {}
        vglist['brick'] = pv
        vglist['vg'] = vg
        data.append(vglist)
    section_dict['vgnames'] = data
    return section_dict

def get_pv_names(section_dict):
    global helpers
    pvnames = section_dict.get('pvname')
    if not pvnames:
        pv_section = Global.sections.get('pv')
        if not pv_section or not pv_section['devices']:
            print "Error: 'pvname' not specified to create " \
                    "volume group."
            helpers.cleanup_and_quit()
        pvnames = pv_section['devices']
    pvnames = helpers.correct_brick_format(
            helpers.listify(pvnames))
    return pvnames
