from ..network_device import NetworkDevice
from ciscoconfparse import CiscoConfParse
from unipath import Path
from .. import functions as hf
import re

class TextFsmParseIssue(Exception):
    pass


class CiscoNetworkDevice(NetworkDevice):

    _trunk_dict = {
        'vlans_native': 'cisco_ios_get_intf_native_vlan.textfsm',
        'vlans_allowed': 'cisco_ios_get_intf_allowed_vlan.textfsm',
        'vlans_forwarding': 'cisco_ios_get_intf_trunk_vlan.textfsm',
        'vlans_not_pruned': 'cisco_ios_get_intf_not_pruned_vlan.textfsm',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vrf_names = None

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
        output = self.show_cdp_neigh_detail(use_textfsm=True)

        output2 = self.show_cdp_neigh(use_textfsm=True)
        if len(output) != len(output2):
            raise TextFsmParseIssue(str(self) + " ERROR:\n"
                                    "\tThe detailed CDP count does not equal the regular CDP count, please check the TextFSM file")
        return output

    # Ready
    def gather_interfaces(self):
        """
        Capture the interface Data
        :return:
        """
        # Applies to all of them, will not go through interface_status section because no output
        intf_list = self.show_interface()
        intf_status_list = self.show_interface_status()
        vrf_info = self.get_vrf_info()

        # Gather additional trunk data
        trunk_detail = self.get_trunk_dict()
        switchport_data_found = False

        if isinstance(intf_list, list):
            for intf in intf_list:
                # Default values
                intf['vrf'] = 'global'
                intf['l2_l3'] = 'Layer 2'
                intf['trunk_access'] = 'Access'
                intf['native'] = str()
                intf['allowed'] = str()
                intf['not_pruned'] = str()
                intf['vlan'] = str()
                # Update Layer 3 Interface Data
                if intf['ip_address']:
                    intf['l2_l3'] = 'Layer 3'
                    intf['trunk_access'] = 'Routed'
                # Checking every interface not jus Layer 3
                if isinstance(vrf_info, list):
                    for vrf in vrf_info:
                        for intf_vrf in vrf['interface']:
                            if intf_vrf.lower() in hf.intf_abbvs(intf['interface']):
                                intf = vrf['name']
                # only proceed if Parsed by Textfsm, if a list was provided.
                # parses through
                if isinstance(intf_status_list, list):
                    intf_status = hf.find_intf_data(intf['interface'], intf_status_list, 'port')
                    # Only if a value was found
                    if intf_status and intf_status['vlan'] == 'trunk':
                        if intf_status['vlan'].isnumeric():
                            intf['vlan'] = intf_status['vlan']
                        intf['trunk_access'] = 'Trunk'
                        intf['native'] = hf.find_intf_data(
                            intf_status['port'], trunk_detail['vlans_native'], 'vlans', ''
                        )
                        intf['allowed'] = hf.find_intf_data(
                            intf_status['port'], trunk_detail['vlans_allowed'], 'vlans', ''
                        )
                        intf['not_pruned'] = hf.find_intf_data(
                            intf_status['port'], trunk_detail['vlans_not_pruned'], 'vlans', ''
                        )
            return intf_list

        elif isinstance(intf_list, str):
            raise TextFsmParseIssue("TextFSM failed to Parse 'show interface'. "
                                    "Please review and update the Template and output")

    # Ready
    def gather_inventory(self):
        return self.show_inventory()

    # Ready
    def gather_lldp(self):
        output = self.show_lldp_neigh_detailed(use_textfsm=True)
        output2 = self.show_lldp_neigh(use_textfsm=True)
        if len(output) != len(output2):
            raise TextFsmParseIssue(str(self) + " ERROR:\n"
                  "\tThe detailed LLDP count does not equal the regular LLDP count, please check the TextFSM file")
        return output

    def gather_mac(self):
        # TODO: Need to continue work on this for NXOS and XR
        return self.show_mac_address_table()

    # TODO: Need to improve this
    def gather_route(self):
        vrf_list = self.vrf_names
        route_list = list()
        route_table_present = False
        for vrf in vrf_list:
            vrf_string = ""
            if vrf != "global":
                vrf_string = " vrf " + vrf
            command = "show route" + vrf_string
            output = self.send_command(command, use_textfsm=True)
            if isinstance(output, list):
                for route in output:
                    route["cidr"] = route['network'] + "/" + route['mask']
                    if "vrf" not in list(route.keys()):
                        route["vrf"] = vrf
                    route_list.append(route)
                    route_table_present = True
            if not route_table_present:
                route = {}
                default_gateway = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", output)
                route["vrf"] = vrf
                route["protocol"] = "Layer 2 only"
                if default_gateway:
                    route["nexthop_ip"] = default_gateway[0]
                else:
                    output2 = self.send_command("show run | incl default-gateway")
                    default_gateway = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", output2)
                    if default_gateway:
                        route["nexthop_ip"] = default_gateway[0]
                route_list.append(route)
        return route_list

    # Ready
    def gather_version(self):
        output = self.show_version(use_textfsm=True)
        # Adding CPU Processes tp gather_version
        data = self.send_command('show processes cpu', use_textfsm=True)
        if isinstance(data, list):
            output[0].update(data[0])
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

    def interface_configuration(self, cfg_obj=None, cfg_location="run"):
        """
        Returns the Interface objects from the CiscoConfParse object
        :param cfg_obj:
        :param cfg_location: 'run' to obtain running-configuration or 'start' for startup-configuration
        :return: List of Interface objects
        """
        if cfg_obj is None:
            cfg_obj = self.configuration(cfg_location=cfg_location, use_parser=True)
        return cfg_obj.find_objects('^interface')

    # Show commands with use_textfsm
    def show_inventory(self, use_textfsm=True):
        return self.send_command("show inventory", use_textfsm=use_textfsm)

    def show_ip_bgp(self, use_textfsm=True):
        return self.send_command("show ip bgp", use_textfsm=use_textfsm)

    def show_mac_address_table(self, use_textfsm=True):
        return self.send_command("show mac address-table", use_textfsm=use_textfsm)

    def show_interface(self, use_textfsm=True):
        return self.send_command("show interface", use_textfsm=use_textfsm)

    def show_interface_status(self, use_textfsm=True):
        return self.send_command("show interface status", use_textfsm=use_textfsm)

    def show_vrf(self, use_textfsm=True):
        """
        Captures the show vrf output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed CDP Neighbors

        """
        return self.send_command("show vrf", use_textfsm=use_textfsm)

    def show_cdp_neigh_detail(self, use_textfsm=True):
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
        return self.send_command("show ip arp", use_textfsm=use_textfsm)

    def show_ip_mroute_summary(self, use_textfsm=True):
        return self.send_command("show ip mroute summary", use_textfsm=use_textfsm)

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

    # This is an intentional break

    def get_trunk_dict(self):
        """
        Parses the 'show int trunk' response, only works on cisco_ios
        """
        return_dict = self._trunk_dict.copy()
        def __parse_dictionary_data(list_of_dict):
            if isinstance(list_of_dict, str):
                return None

            return_dict = list()
            for line in list_of_dict:
                t_dict = dict()
                for key, value in line.items():
                    t_dict[key] = str().join(value)
                return_dict.append(t_dict)
            return return_dict

        def __get_vlan_list(txt_tmpl):
            vlans_list = self.send_command("show int trunk", use_textfsm=True, textfsm_template=txt_tmpl)
            vlans_list = __parse_dictionary_data(vlans_list)
            return vlans_list

        for key, val in return_dict.items():
            return_dict[key] = self._textfsm_templates_path.child(val)

        for vlan_list, template_path in return_dict.items():
            return_dict[vlan_list] = __get_vlan_list(template_path)

        return return_dict

    def get_sfp(self):
        """
        Obtain a list of SFP Inventory
        :return: list of SFP Inventory
        """
        inventory = self.gather_inventory()
        sfp_list = list()
        for item in inventory:
            if 'sfp' in item["description"].lower():
                sfp_list.append(item)
        return sfp_list

    def count_intf(self):
        intf_counts = dict()
        interface_list = self.show_interface()
        for intf in interface_list:
            # Strip the Interface Number
            intf_stripped = re.match(r'^([a-zA-Z]+)', intf['interface']).group(1)

            # Add Interface Type if it does not already exist
            if intf_stripped not in intf_counts.keys():
                intf_counts[intf_stripped] = {'count': 0, 'active': 0}

            # Add the Counts
            intf_counts[intf_stripped]['count'] += 1
            if intf['link_status'] == 'up':
                intf_counts[intf_stripped]['active'] += 1
        return intf_counts

    def get_vrf_info(self):
        return self.show_vrf()