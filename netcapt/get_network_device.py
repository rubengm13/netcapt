from .cisco import CiscoIosDevice, CiscoXrDevice, CiscoNxosDevice
import netmiko


DEVICE_MAPPER = {
    "cisco_ios": CiscoIosDevice,
    "cisco_xr": CiscoXrDevice,
    "cisco_nxos": CiscoNxosDevice
}

SUPPORTED_DEVICES_str = list(DEVICE_MAPPER.keys())
SUPPORTED_DEVICES_str = "\n".join(SUPPORTED_DEVICES_str)


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
    if kwargs['device_type'] == 'autodetect':
        netmiko_args = kwargs.copy()
        netmiko_args['auto_connect'] = True
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
