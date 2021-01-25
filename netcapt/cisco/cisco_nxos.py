from .cisco import CiscoNetworkDevice


class CiscoNxosDevice(CiscoNetworkDevice):
    def gather_arp(self):
        """
        Captures arp information and utilizing the vrf data it parses the
        output to prepare it for extraction to WB.
        """
        vrf_list = self.get_vrf_names()
        arp_list = list()
        for vrf in vrf_list:
            command = "show ip arp"
            if vrf != "global":
                command += " vrf " + vrf
            output = self.send_command(command, use_textfsm=True)
            if isinstance(output, list):
                for arp in output:
                    assert isinstance(vrf, object)
                    arp["vrf"] = vrf
                    # this is NXOS specific
                    arp["type"] = "ARPA"
                    arp_list.append(arp)
            else:
                arp = {'vrf': vrf, 'address': "No ARP Data Found"}
                arp_list.append(arp)
        return arp_list
