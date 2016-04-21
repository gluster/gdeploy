#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global

helpers = Helpers()

def lv_create(section_dict):
    global helpers
    if not section_dict.get('vgname'):
        vg_section = Global.sections.get('vg')
        if not vg_section or not vg_section['vgname']:
            data_not_found('vgname')
        sections['vgname'] = vg_section['vgname']

    lvtype = section_dict.get('lvtype')
    if lvtype == 'thinlv':
        section_dict, yml = thin_lv_data(section_dict)
    elif lvtype == 'thick':
        section_dict, yml = get_lv_vg_names('lvname', section_dict)
    elif lvtype == 'thinpool':
         section_dict, yml = get_lv_vg_names('poolname', section_dict)
    else:
        print "Error: Unknown lvtype"
        helpers.cleanup_and_quit()
    return section_dict, yml

def lv_convert(section_dict):
    return section_dict, defaults.YML_NAME

def lv_setup_cache(section_dict):
    global helpers
    section_dict['ssd'] = helpers.correct_brick_format(
            helpers.listify(section_dict['ssd']))[0]
    helpers.perf_spec_data_write()
    return section_dict, defaults.SETUP_CACHE_YML

def lv_change(section_dict):
    return section_dict, defaults.LVCHANGE_YML

def get_lv_vg_names(name, section_dict):
    global helpers
    vgname = helpers.listify(section_dict['vgname'])
    lvname = helpers.listify(section_dict[name])
    size = helpers.listify(section_dict['size'])
    lvname, vgname = validate_the_numbers(lvname, vgname)
    lvname, size = validate_the_numbers(lvname, size)
    data = []
    for lv, vg, size in zip(lvname, vgname, size):
        lvnames = {}
        lvnames['lv'] = lv
        lvnames['vg'] = vg
        lvnames['size'] = size
        data.append(lvnames)
    ymls = []
    if name != 'poolname':
        section_dict, ymls = get_mount_data(section_dict, lvname, vgname)
    section_dict['lvnamelist'] = data
    ymls.insert(0, defaults.LVCREATE_YML)
    return section_dict, ymls

def thin_lv_data(section_dict):
    global helpers
    vgname = helpers.listify(section_dict.get('vgname'))
    lvname = helpers.listify(section_dict.get('lvname'))
    poolname = helpers.listify(section_dict.get('poolname'))
    virtualsize = helpers.listify(section_dict.get('virtualsize').strip())
    if not (vgname and lvname and poolname and virtualsize):
        print "Error: Provide vgname, lvname, poolname, virtualsize to create "\
                "thin lv"
        helpers.cleanup_and_quit()
    lvname, vgname = validate_the_numbers(lvname, vgname)
    lvname, virtualsize = validate_the_numbers(lvname, virtualsize)
    vgname, poolname = validate_the_numbers(vgname, poolname)
    data = []
    for lv, vg, pool, size in zip(lvname, vgname, poolname, virtualsize):
        lvpools = {}
        lvpools['lv'] = lv
        lvpools['vg'] = vg
        lvpools['pool'] = pool
        lvpools['virtualsize'] = size
        data.append(lvpools)
    section_dict['lvnamelist'] = data
    section_dict, ymls = get_mount_data(section_dict, lvname, vgname)
    ymls.insert(0, defaults.THINLVCREATE_YML)
    return section_dict, ymls


def get_mount_data(section_dict, devices, vgnames):
    fstype = helpers.listify(section_dict.get('mkfs'))
    if not fstype:
        fstype = 'xfs'
    else:
        if fstype[0].lower() == 'no':
            return section_dict, []
        else:
            fstype = fstype[0]
    section_dict['fstype'] = fstype
    lvols = ['/dev/%s/%s' % (i, j.split(':')[0]) for i, j in
                                  zip(vgnames, devices)]
    section_dict['lvols'] = lvols

    if section_dict.get('mkfs-opts'):
        section_dict['opts'] = section_dict['mkfs-opts']
    elif fstype == 'xfs':
        section_dict['opts'] = "-f -K -i size=512 -d sw=10,su=128k -n size=8192"

    mountpoint = helpers.listify(section_dict.get('mount'))
    if not mountpoint:
        path = ['/mnt/gluster' + str(i)  for i in range(1,
            len(devices)+1)]
    elif mountpoint[0].lower() == 'no':
        return section_dict, [defaults.FSCREATE_YML]
    else:
        path = mountpoint
        if len(path) != len(devices):
            if len(path) == 1:
                path *= len(devices)
            else:
                print "Error: Mountpoints number mismatch with lvnames"
                helpers.cleanup_and_quit()
    data = []
    for mnt, dev in zip(path, lvols):
        mntpath = {}
        mntpath['path'] = mnt
        mntpath['device'] = dev
        data.append(mntpath)
    section_dict['mntpath'] = data
    return section_dict, [defaults.FSCREATE_YML, defaults.MOUNT_YML]



def validate_the_numbers(validator, validatee):
    if len(validator) > 1 and len(validatee) == 1:
        validatee = validatee * len(validator)
    elif len(validatee) > 1 and len(validator) == 1:
        val = []
        for i in range(1, len(validatee) + 1):
            val.append(validator[0] + str(i))
        validator = val
    if len(validator) != len(validatee):
        print "Error: Provide same number of LVnames and VG names " \
                "or a common VG for all LVs mentioned."
        helpers.cleanup_and_quit()
    return validator, validatee

def data_not_found(item):
    global helpers
    print "Error: Value for option %s not found." % item
    helpers.cleanup_and_quit()
