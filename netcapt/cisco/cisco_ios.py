from .cisco import CiscoNetworkDevice
from .. import functions as hf
from ..supported_attr import UnsupportSwitch


class TextFsmParseIssue(Exception):
    pass


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
