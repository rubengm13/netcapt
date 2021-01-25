from .cisco import CiscoNetworkDevice
from unipath import Path


class CiscoXrDevice(CiscoNetworkDevice):
    # Modified Gathered Commands
    def gather_bgp(self):
        vrf_names = self.get_vrf_names()
        bgp_data = list()
        for vrf in vrf_names:
            output = self.show_bgp_vrf(vrf)
            if isinstance(output, list):
                bgp_data += output
            else:
                bgp_data += [{'vrf': vrf, 'status': 'No BGP Data'}]
        return bgp_data

    # Modified other commands
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

    # Modified Show commands
    def show_vrf(self, use_textfsm=True):
        """
        Captures the show vrf output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed CDP Neighbors
        """
        command = 'show vrf all'
        txt_tmpl = Path("netcapt/ntc-templates/cisco_xr_show_vrf_all.textfsm")
        return self.send_command(command, use_textfsm=use_textfsm, textfsm_template=txt_tmpl)

    def show_arp_vrf(self, vrf, use_textfsm=True):
        textfsm_tmpl = Path("netcapt/ntc-templates/test_tmpl/cisco_xr_show_arp.textfsm")
        return self.send_command("show arp vrf " + vrf, use_textfsm=use_textfsm, textfsm_template=textfsm_tmpl)

    def show_arp(self, use_textfsm=True):
        textfsm_tmpl = Path("netcapt/ntc-templates/test_tmpl/cisco_xr_show_arp.textfsm")
        return self.send_command("show arp", use_textfsm=use_textfsm, textfsm_template=textfsm_tmpl)

    def show_bgp_vrf(self, vrf, use_textfsm=True):
        textfsm_tmpl = "netcapt/ntc-templates/test_tmpl/cisco_xr_show_bgp_vrf.textfsm"
        cmd = 'show bgp vrf {} ipv4 unicast'.format(vrf)
        return self.send_command(cmd, use_textfsm=use_textfsm, textfsm_template=textfsm_tmpl)

    def show_inventory(self, use_textfsm=True):
        textfsm_tmpl = "netcapt/ntc-templates/test_tmpl/cisco_ios_show_inventory.textfsm"
        cmd = 'show inventory'
        return self.send_command(cmd, use_textfsm=use_textfsm, textfsm_template=textfsm_tmpl)