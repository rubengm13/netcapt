from netcapt.cisco import CiscoIosDevice, CiscoXrDevice, CiscoNxosDevice

DEVICE_MAPPER = {
    "cisco_ios": CiscoIosDevice,
    "cisco_xr": CiscoXrDevice,
    "cisco_nxos": CiscoNxosDevice
}

supported_devices = list(DEVICE_MAPPER.keys())
supported_devices = "\n".join(supported_devices)



def GetNetworkDevice(**kwargs):
    net_dev_type = kwargs["device_type"].split("_")
    net_dev_type = "_".join(net_dev_type[:2])
    if net_dev_type not in DEVICE_MAPPER:
        raise ValueError("Unsupported Device Type, the following devices are currently supported:\n"+supported_devices)
    network_device  = DEVICE_MAPPER[net_dev_type]
    return network_device(**kwargs)

