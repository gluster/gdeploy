"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global

helpers = Helpers()

def lv_create(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_lv_errors')
    if not section_dict.get('vgname'):
        vg_section = Global.sections.get('vg')
        if not vg_section or not vg_section['vgname']:
            data_not_found('vgname')
        section_dict['vgname'] = vg_section['vgname']

    lvtype = section_dict.get('lvtype')
    Global.logger.info("Create %s logical volume"%lvtype)
    if lvtype == 'thinlv':
        section_dict, yml = thin_lv_data(section_dict)
    elif lvtype == 'thick':
        section_dict, yml = get_lv_vg_names('lvname', section_dict)
    elif lvtype == 'thinpool':
        # If chunksize is not specified try to compute
        if section_dict['chunksize'].strip() == '':
            section_dict['chunksize'] = helpers.get_thin_pool_chunk_sz()
        section_dict, yml = get_lv_vg_names('poolname', section_dict)
    else:
        msg = "Unknown lvtype"
        print("Error: %s"%msg)
        Global.logger.error(msg)
        helpers.cleanup_and_quit()
    return section_dict, yml

def lv_convert(section_dict):
    if section_dict['chunksize'].strip() == '':
        section_dict['chunksize'] = helpers.get_thin_pool_chunk_sz()
    Global.ignore_errors = section_dict.get('ignore_lv_errors')
    Global.logger.info("Converting lv to cachepool/cachelv")
    return section_dict, defaults.LVCONVERT_YML

def lv_setup_cache(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_lv_errors')
    section_dict['ssd'] = helpers.correct_brick_format(
            helpers.listify(section_dict['ssd']))[0]
    helpers.perf_spec_data_write()
    Global.logger.info("Setting up SSD for caching.")
    return section_dict, defaults.SETUP_CACHE_YML

def lv_change(section_dict):
    Global.ignore_errors = section_dict.get('ignore_lv_errors')
    Global.logger.info("Changing logical volume attributes")
    return section_dict, defaults.LVCHANGE_YML

def get_lv_vg_names(name, section_dict):
    global helpers
    vgname = helpers.listify(section_dict['vgname'])
    lvname = helpers.listify(section_dict[name])
    size = helpers.listify(section_dict.get('size')) or ['']
    extend = helpers.listify(section_dict.get('extent')) or ['']
    lvname, vgname = validate_the_numbers(lvname, vgname)
    lvname, size = validate_the_numbers(lvname, size)
    lvname, extend = validate_the_numbers(lvname, extend)
    data = []
    for lv, vg, size, extend in zip(lvname, vgname, size, extend):
        lvnames = {}
        lvnames['lv'] = lv
        lvnames['vg'] = vg
        lvnames['size'] = size
        lvnames['extent'] = extend
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
        msg = "Error: Provide vgname, lvname, poolname, virtualsize to "\
              "create thin lv"
        print(msg)
        Global.logger.error(msg)
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
    Global.logger.info("Create thin logical volumes")
    ymls.insert(0, defaults.THINLVCREATE_YML)
    return section_dict, ymls

def get_mount_data(section_dict, devices, vgnames):
    fstype = helpers.listify(section_dict.get('mkfs'))
    Global.ignore_errors = section_dict.get('ignore_mount_errors')
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
        # If RAID data is provided use it to set the stripe_width and
        # stripe_unit_size from the config.
        disktype = helpers.config_get_options('disktype', False)
        if disktype and disktype[0].lower() != 'jbod':
            sw = helpers.config_get_options('diskcount', True)
            su = helpers.config_get_options('stripesize', False)
            if not su:
                # No stripe size given assuming 256
                su = [256]
            section_dict['opts'] = "-f -K -i size=512 -d sw=%s,su=%sk\
 -n size=8192"%(sw[0],su[0])
        else:
            section_dict['opts'] = "-f -K -i size=512 -n size=8192"

    Global.logger.info("Creating %s filesystem on %s with options %s"\
                       %(section_dict['fstype'],
                         section_dict['lvols'],
                         section_dict['opts']))


    mountpoint = helpers.listify(section_dict.get('mount'))
    if not mountpoint:
        path = ['/mnt/gluster' + str(i)  for i in
                range(1, len(devices)+1)]
    elif mountpoint[0].lower() == 'no':
        return section_dict, [defaults.FSCREATE_YML]
    else:
        path = mountpoint
        if len(path) != len(devices):
            if len(path) == 1:
                path *= len(devices)
            else:
                msg = "Mountpoints number mismatch with lvnames"
                print("Error: %s"%msg)
                Global.logger.error(msg)
                helpers.cleanup_and_quit()
    data = []
    for mnt, dev in zip(path, lvols):
        mntpath = {}
        mntpath['path'] = mnt
        mntpath['device'] = dev
        # Check if we have any VDO devices. We rely on pvnames provided in the
        # form /dev/mapper/<vdoname>. If this format changes, change the below
        # code appropriately. Also the lvols are built to be like
        # /dev/vgname/lvname if this changes please change the code below as
        # well.
        for vgdict in Global.vg_data:
            if vgdict['vg'] == dev.split('/')[2] and \
               vgdict['brick'].strip().startswith('/dev/mapper'):
                mntpath['vdodev'] = True
        data.append(mntpath)
    section_dict['mntpath'] = data

    selinux = helpers.config_get_options('selinux', False)
    ymls = [defaults.FSCREATE_YML, defaults.MOUNT_YML]
    if selinux:
        if selinux[0].lower() == 'yes':
            ymls.append(defaults.SELINUX_YML)
    return section_dict, ymls

def validate_the_numbers(validator, validatee):
    if len(validator) > 1 and len(validatee) == 1:
        validatee = validatee * len(validator)
    elif len(validatee) > 1 and len(validator) == 1:
        val = []
        for i in range(1, len(validatee) + 1):
            val.append(validator[0] + str(i))
        validator = val
    if len(validator) != len(validatee):
        msg = "Provide same number of LVnames and VG names " \
              "or a common VG for all LVs mentioned."
        print("Error: %s"%msg)
        Global.logger.error(msg)
        helpers.cleanup_and_quit()
    return validator, validatee

def data_not_found(item):
    global helpers
    msg = "Value for option %s not found." % item
    print("Error: %s"%msg)
    Global.logger.error(msg)
    helpers.cleanup_and_quit()
