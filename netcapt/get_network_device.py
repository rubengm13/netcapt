from .cisco import CiscoIosDevice, CiscoXrDevice, CiscoNxosDevice, CiscoWlcDevice
import netmiko


DEVICE_MAPPER = {
    "cisco_ios": CiscoIosDevice,
    "cisco_xr": CiscoXrDevice,
    "cisco_nxos": CiscoNxosDevice,
    "cisco_wlc": CiscoWlcDevice

}


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

    if 'autodetect' in kwargs['device_type']:
        netmiko_args = kwargs.copy()
        # Need to enable Auto Connect otherwise it fails.
        netmiko_args['auto_connect'] = True
        net_dev_type = guess_device_type(**netmiko_args)
        if net_dev_type:
            kwargs['device_type'] = net_dev_type + '_ssh'
        else:
            return None
        # TODO: Need to consider what to do if we get back a None, currently it shouldn't be a problem. Needs to be
        #  resolved by the time we start the Network Crawl option.
    else:
        net_dev_type = kwargs['device_type']
        # Strip ssh or telnet tag
        if net_dev_type[-4:] == '_ssh':
            net_dev_type = net_dev_type[:-4]
        elif net_dev_type[-7:] == '_telnet':
            net_dev_type = net_dev_type[:-7]

    if net_dev_type not in DEVICE_MAPPER.keys():
        raise ValueError('Unsupported Device Type, the following devices are currently supported:\n'
                         + '\n'.join(DEVICE_MAPPER.keys()))
    network_device = DEVICE_MAPPER[net_dev_type]

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
