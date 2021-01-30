from .cisco import CiscoNetworkDevice
from unipath import Path
from .. import functions as hf


class TextFsmParseIssue(Exception):
    pass


class CiscoIosDevice(CiscoNetworkDevice):
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

    # Need to update this, as it does not always capture all the IPs
    # This template will work better
    def show_cdp_neigh_detailed(self, use_textfsm=True):
        """
        Captures the Detailed CDP output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed CDP Neighbors

        """
        txt_tmpl = Path("netcapt/ntc-templates/cisco_ios_show_cdp_neighbors_detail.textfsm")
        return self.send_command("show cdp neighbor detail", use_textfsm=use_textfsm, textfsm_template=txt_tmpl)