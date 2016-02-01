#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
def quota_enable(section_dict):
    return section_dict, QUOTA_ENABLE

def quota_disable(section_dict):
    return section_dict, QUOTA_DISABLE

def quota_remove(section_dict):
    return section_dict, QUOTA_OPS

def quota_remove_objects(section_dict):
    return section_dict, QUOTA_OPS

def quota_default_soft_limit(section_dict):
    return section_dict, QUOTA_OPS

def quota_limit_usage(section_dict):
    section_dict = write_associated_data('size')
    return section_dict, QUOTA_LIMIT_USAGE

def quota_limit_objects(section_dict):
    section_dict = write_associated_data('number')
    return section_dict, QUOTA_LIMIT_OBJECTS

def quota_alert_time(section_dict):
    return section_dict, QUOTA_ALERT_TIME

def quota_soft_timeout(section_dict):
    return section_dict, QUOTA_OPS

def quota_hard_timeout(section_dict):
    return section_dict, QUOTA_OPS

def write_associated_data(section_dict, lmt):
    vals = self.section_dict[lmt]
    paths = self.section_dict['path']
    if len(vals) > len(paths):
        vals = vals[0:len(paths)]
    elif len(vals) < len(paths):
        vals.extend([vals[-1]] * (len(paths) - len(vals)))
    data = []
    for i, j in zip(vals, paths):
        values = {}
        values[lmt] = i
        values['path'] = j
        data.append(values)
    section_dict['limit'] = data
    return section_dict

