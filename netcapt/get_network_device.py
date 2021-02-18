from .cisco import CiscoIosDevice, CiscoXrDevice, CiscoNxosDevice, CiscoWlcDevice
import netmiko


DEVICE_MAPPER = {
    "cisco_ios": CiscoIosDevice,
    "cisco_xr": CiscoXrDevice,
    "cisco_nxos": CiscoNxosDevice,
    "cisco_wlc": CiscoWlcDevice

}

SUPPORTED_DEVICES_str = list(DEVICE_MAPPER.keys())
SUPPORTED_DEVICES_str = "\n".join(SUPPORTED_DEVICES_str)


class UnableToDetectDeviceType(Exception):
    pass


# TODO: Need to discuss how we are going to run this, do we have it return an empty if Value does not
#  exist or no match or raise an error
# noinspection PyPep8Naming
def GetNetworkDevice(**kwargs):
    """
    Dynamically detect the Network Device class to be utilized. if autodetect option is used it will default to SSH.
    :param kwargs: netmiko parameters and NetworkDevice class parameters
    :return: Network Device Class or None
    """
    # Auto Detect device type with netmiko or extract the device type from the device_type option

    auto_con_orig_val = None
    # TODO Need to move this unwanted_args function
    if 'auto_con_orig_val' in kwargs.keys():
        if not kwargs['auto_con_orig_val']:
            auto_con_orig_val = False
            kwargs['auto_con_orig_val'] = True

    if 'autodetect' in kwargs['device_type']:
        netmiko_args = kwargs.copy()
        net_dev_type = guess_device_type(**netmiko_args)
        if net_dev_type:
            kwargs['device_type'] = net_dev_type + '_ssh'
        else:
            return None
        # TODO: Need to consider what to do if we get back a None, currently it shouldn't be a problem. Needs to be
        #  resolved by the time we start the Network Crawl option.
    else:
        net_dev_type = kwargs['device_type'].split('_')
        net_dev_type = '_'.join(net_dev_type[:2])

    if net_dev_type not in DEVICE_MAPPER:
        raise ValueError('Unsupported Device Type, the following devices are currently supported:\n'
                         + SUPPORTED_DEVICES_str)
    network_device = DEVICE_MAPPER[net_dev_type]
    if not auto_con_orig_val:
        kwargs['auto_connect'] = False

    return network_device(**kwargs)


def guess_device_type(**kwargs):
    """
    Utilize the Netmiko SSHDetect class to detect the device type
    :param kwargs: netmiko connection parameters
    :return: String representing the detected device type
    :rtype: str or None
    """
    if kwargs['verbose']:
        print('Auto detecting device type for:', kwargs['host'])
    guesser = netmiko.SSHDetect(**kwargs)
    return guesser.autodetect()

def remove_unwanted_args(**kwargs):

    unwanted_args = ['auto_connect']
    for unwant_arg in unwanted_args:
        if unwant_arg in kwargs.keys():
            pass
