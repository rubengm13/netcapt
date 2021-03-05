from .cisco import CiscoNetworkDevice
from .. import functions as hf
from ..supported_attr import UnsupportSwitch
from ..netcapt_exceptions import GatherAttributeUnsupported


class CiscoIosDevice(CiscoNetworkDevice, UnsupportSwitch):
    def gather_arp(self):
        """
        Captures arp information and utilizing the vrf data it parses the
        output to prepare it for extraction to WB.
        """
        vrf_list = self.get_vrf_names()
        arp_list = list()
        for vrf in vrf_list:
            if vrf != "global":
                output = self.show_arp_vrf(vrf)
            else:
                output = self.show_arp()
            if isinstance(output, list):
                for arp in output:
                    arp["vrf"] = vrf
                    arp_list.append(arp)
            else:
                arp = {'vrf': vrf, 'address': "No ARP Data Found"}
                arp_list.append(arp)
        return arp_list

    def get_vrf_names(self):
        vrf_names = ['global']
        vrf_names += super(CiscoIosDevice, self).get_vrf_names()
        return vrf_names

    def gather_ip_mroute(self):
        output = super(CiscoIosDevice, self).gather_ip_mroute()
        if "% Invalid input detected at '^' marker." in output:
            raise GatherAttributeUnsupported(
                "{} object does not support attribute '{}'".format(str(self), 'gather_ip_mroute')
            )
