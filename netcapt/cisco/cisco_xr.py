from .cisco import CiscoNetworkDevice
from unipath import Path


class CiscoXrDevice(CiscoNetworkDevice):
    def __str__(self):
        return "<Cisco XR Device> host: {self.host}".format(self=self)

    # Modified Gathered Commands
    def gather_arp(self):
        """
        Captures arp information and utilizing the vrf data it parses the
        output to prepare it for extraction to WB.
        """
        vrf_list = self.get_vrf_names()
        arp_list = []
        for vrf in vrf_list:
            command = "show arp vrf " + vrf
            txt_tmpl = Path("ntc-templates/test_tmpl/cisco_xr_show_arp.textfsm")
            output = self.send_command(command, textfsm_template=txt_tmpl)
            if isinstance(output, list):
                for arp in output:
                    arp["vrf"] = vrf
                    arp_list.append(arp)
            else:
                arp = {'vrf': vrf, 'address': "No ARP Data Found"}
                arp_list.append(arp)
        return arp_list

    def get_vrf_names(self):
        """
        Gathers the VRF names from the connection. If the names were already
        gathered then it returns the list from the NetCapture variable of
        vrf_names.
        """
        vrf_names = ["default"]
        output = self.show_vrf()
        if isinstance(output, list):
            for vrf in output:
                if vrf['name'] not in vrf_names:
                    vrf_names.append(vrf['name'])
        elif isinstance(output, str):
            # Capture when the command is not supported
            if 'Invalid input detected' in output:
                pass
        return vrf_names

    def show_vrf(self, use_textfsm=True):
        """
        Captures the show vrf output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed CDP Neighbors
        """
        command = 'show vrf all'
        txt_tmpl = Path("ntc-templates/test_tmpl/cisco_xr_show_vrf_all.textfsm")
        return self.send_command(command, use_textfsm=use_textfsm, textfsm_template=txt_tmpl)
