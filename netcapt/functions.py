import json
import re


def print_json(json_data):
    print(json.dumps(json_data, indent=4))


def get_short_if_name(interface, device_type):
    """
    Returns short if name. for cisco_ios it returns first 2 char and the
    interface number. Everything else it returns the first 3 plus number.
    """
    number = re.compile(r"(\d.*)$")
    name = re.compile("([a-zA-Z]+)")
    number = number.search(interface).group(1)
    name = name.search(interface).group(1)
    short_name = ""
    if device_type == "cisco_ios":
        short_name = left(name, 2)
    elif device_type in ["cisco_nxos", "cisco_xr"]:
        port = left(name, 3).lower()
        if port == "eth":
            short_name = left(name, 3)
        elif port == "vla":
            short_name = left(name, 4)
        elif port == "mgm":
            short_name = left(name, 4)
        else:
            short_name = left(name, 2)
    if int(left(number, 1)) >= 0 or number is None:
        short_name = short_name + str(number)
    return short_name


def find_intf_data(intf_name, data_list, intf_key='interface', key=None, join_sep=None):
    """
    Find the list of
    :param data_list:
    :param join_sep:
    :param intf_name:
    :param key:
    :return:Value or None if None is found
    """
    for t_intf in data_list:
        if t_intf[intf_key].lower() in intf_abbvs(intf_name):
            if key is not None:
                if join_sep is not None:
                    return join_sep.join(t_intf[key])
                return t_intf[key]
            return t_intf
    return None


def intf_abbvs(intf_name):
    """
    Return interface abbreviations for a particular interface name
    Will lower all the abbreviation characters
    :param intf_name: Interface Name with port number
    :return: list of abbreviations in lower case
    """
    intf_name = intf_name.lower()
    return_list = list()
    re_match = re.match(r'([a-z]+)\s*(\S+)', intf_name)
    # print(re_match)
    for intf_len in range(len(re_match.group(1))):
        return_list.append(intf_name[:intf_len + 1] + ' ' + re_match.group(2))
        return_list.append(intf_name[:intf_len + 1] + re_match.group(2))
    return return_list


def left(s, amount):
    """
    Returns the left characters of amount size
    """
    return s[:amount]


def right(s, amount):
    """
    Returns the right characters of amount size
    """
    return s[-amount:]


def mid(s, offset, amount):
    """
    Returns the middle characters starting at offset of length amount
    """
    return s[offset:offset + amount]
