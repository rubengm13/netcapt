from .cisco import CiscoNetworkDevice


class CiscoIosDevice(CiscoNetworkDevice):
    def __str__(self):
        return "<Cisco IOS Device> host: {self.host}".format(self=self)

    def gather_arp(self):
        # TODO: review this with team, do we want this in Cisco Devices, or here?
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

    def gather_interface(self):
        interface_list = self.show_interface()
        interface_status_list = self.show_interface_status()
        if isinstance(interface_status_list, str):
            switchport_data_found = True

