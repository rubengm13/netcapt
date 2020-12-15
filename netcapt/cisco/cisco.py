from ..network_device import NetworkDevice

from ciscoconfparse import CiscoConfParse


class CiscoNetworkDevice(NetworkDevice):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vrf_names = None
        self.hostname = ''

    def __str__(self):
        return "<Cisco Device host: {self.host}>".format(self=self)

    # Gather Commands
    # TODO: add a gather all, that will gather all the Gather commands
    def gather_all(self):
        pass

    # Ready
    def gather_arp(self):
        """
        Developed on each individual class
        """
        pass

    # Ready
    def gather_bgp(self):
        # TODO: Check if NXOS and IOS needs to be VRF aware
        return self.show_ip_bgp()

    # Ready
    def gather_cdp(self):
        output = self.show_cdp_neigh_detailed(use_textfsm=True)
        output2 = self.show_cdp_neigh(use_textfsm=True)
        if len(output) != len(output2):
            print("ERROR:\n"
                  "\tThe detailed CDP count does not equal the regular CDP count, please check the TextFSM file")
        return output

    def gather_interface(self):
        pass
        # TODO: this to everything, double check GetInventory to make sure you transfer all the data.

    # Ready
    def gather_inventory(self):
        return self.show_inventory()

    # Ready
    def gather_lldp(self):
        output = self.show_lldp_neigh_detailed(use_textfsm=True)
        output2 = self.show_lldp_neigh(use_textfsm=True)
        if len(output) != len(output2):
            print("ERROR:\n"
                  "\tThe detailed LLDP count does not equal the regular LLDP count, please check the TextFSM file")
        return output

    def gather_mac(self):
        # TODO: Need to continue work on this for NXOS and XR
        return self.show_mac_address_table()

    def gather_route(self):
        pass
        # TODO: complete the gather_route for all devices

    # Ready
    def gather_version(self):
        output = self.show_version(use_textfsm=True)
        return output

    # Gather specific Data and parse it as needed
    def get_vrf_names(self):
        """
        Gathers the VRF names from the device
        """
        vrf_names = ["global"]
        output = self.show_vrf()
        if isinstance(output, list):
            for vrf in output:
                if vrf['name'] not in vrf_names:
                    vrf_names.append(vrf['name'])
        return vrf_names

    # Update Data from CLI interaction
    def update_hostname(self):
        """Gets Hostname from the Connection and saves it to the device."""
        self.hostname = self.connection.find_prompt()[:-1]

    # capture specific data that is not just a show command
    def configuration(self, cfg_location="run", use_parser=False):
        # check if startup or running config requested
        if cfg_location == "start":
            cfg = self.show_startup_configuration()
        else:
            cfg = self.show_running_configuration()
        # if use_parser is required then return it will parse with CiscoConfParser
        if use_parser:
            cfg = self.show_running_configuration()
            return CiscoConfParse(cfg.splitlines())
        return cfg

    def interface_configuration(self, cfg_location="run"):
        """
        Returns the Interface objects from the CiscoConfParse object
        :param cfg_location: 'run' to obtain running-configuration or 'start' for startup-configuration
        :return: List of Interface objects
        """
        cfg = self.configuration(cfg_location=cfg_location, use_parser=True)
        return cfg.find_objects('^interface')

    # Show commands with use_textfsm
    def show_inventory(self, use_textfsm=True):
        return self.send_command("show version", use_textfsm=use_textfsm)

    def show_ip_bgp(self, use_textfsm=True):
        return self.send_command("show ip bgp", use_textfsm=use_textfsm)

    def show_mac_address_table(self, use_textfsm=True):
        return self.send_command("show mac address-table", use_textfsm=use_textfsm)

    def show_vrf(self, use_textfsm=True):
        """
        Captures the show vrf output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed CDP Neighbors

        """
        return self.send_command("show vrf", use_textfsm=use_textfsm)

    def show_cdp_neigh_detailed(self, use_textfsm=True):
        """
        Captures the Detailed CDP output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed CDP Neighbors

        """
        return self.send_command("show cdp neighbor detail", use_textfsm=use_textfsm)

    def show_cdp_neigh(self, use_textfsm=True):
        """
        Captures the summary CDP output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed CDP Neighbors

        """
        return self.send_command("show cdp neighbor", use_textfsm=use_textfsm)

    def show_lldp_neigh_detailed(self, use_textfsm=True):
        """
        Captures the Detailed LLDP output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed LLDP Neighbors

        """
        return self.send_command("show lldp neighbor detail", use_textfsm=use_textfsm)

    def show_lldp_neigh(self, use_textfsm=True):
        """
        Captures the summary LLDP output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed LLDP Neighbors

        """
        return self.send_command("show lldp neighbor", use_textfsm=use_textfsm)

    def show_version(self, use_textfsm=True):
        return self.send_command("show version", use_textfsm=use_textfsm)

    def show_arp_vrf(self, vrf, use_textfsm=True):
        return self.send_command("show ip arp vrf " + vrf, use_textfsm=use_textfsm)

    def show_arp(self, use_textfsm=True):
        return self.send_command("show ip arp ", use_textfsm=use_textfsm)

    # show configuration commands with Cisco Config Parser option
    def show_startup_configuration(self, cisco_cfg_parse=False, factory=False):
        self.disable_paging()
        output = self.send_command("show startup-config")
        if cisco_cfg_parse:
            return CiscoConfParse(output.splitlines(), factory=factory)
        return output

    def show_running_configuration(self, cisco_cfg_parse=False, factory=False):
        self.disable_paging()
        output = self.send_command("show running-config")
        if cisco_cfg_parse:
            return CiscoConfParse(output.splitlines(), factory=factory)
        return output

    # show tech option that disables paging and increases the global_delay factor
    def show_tech(self, global_delay_factor=5):
        self.disable_paging()
        return self.send_command('show tech-support', global_delay_factor=global_delay_factor)

    # Enable/Disable Features
    def disable_paging(self):
        self.send_command('term len 0')
