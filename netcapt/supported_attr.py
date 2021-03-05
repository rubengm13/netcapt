
from .netcapt_exceptions import GatherAttributeUnsupported


class UnsupportWirelessControllerAttr(object):
    def __getattribute__(self, item):
        unsupported = ['gather_route', 'gather_mac', 'gather_bgp', 'gather_arp']
        if item in unsupported:
            raise GatherAttributeUnsupported("{} object does not support attribute '{}'".format(str(self), item))
        return object.__getattribute__(self, item)


class UnsupportSwitch(object):
    def __getattribute__(self, item):
        unsupported = ['gather_ap']
        if item in unsupported:
            raise GatherAttributeUnsupported("{} object does not support attribute '{}'".format(str(self), item))
        return object.__getattribute__(self, item)