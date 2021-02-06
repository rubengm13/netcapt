import netmiko
from unipath import Path
import os
import traceback


class InitiatingConnectionException(Exception):
    pass


# TODO: Do we need to derive this class from the Netmiko Class?
#  This will have to be derived on a per device type basis. Might get Tricky with SSH
class NetworkDevice(object):
    # Location For TestFSM_templates
    _textfsm_templates_path = Path(os.path.dirname(__file__)).child('ntc_templates').child('textfsm_templates')

    def __init__(
            self,
            auto_connect=False,
            verbose=False,
            **kwargs
    ):
        # Added the netmiko class here
        # Note it will start the connection if auto_connect is set to True, Defaulted to False.
        self.connection = netmiko.ConnectHandler(auto_connect=auto_connect, verbose=verbose, **kwargs)

        self.host = kwargs['host']
        self.verbose = verbose
        self.model = None
        self.version = None
        self.serial_number = None
        self.hostname = None

    def __str__(self):
        return "<%s | host: %s>"% (self.classname, self.host)

    # Gather Functions
    # Most are Empty Place holders for respective Device Gathers
    def gather_version(self):
        """
        Gather the Version output, will return after it is parsed using TextFSM
        :return: List with Dictionary values
        """
        pass

    def gather_arp(self):
        pass

    def gather_mac(self):
        pass

    def gather_interfaces(self):
        pass

    def gather_cdp(self):
        """
        Gather the CDP output, will return after it is parsed using TextFSM. Checks the count of the
        CDP detailed neighbor and compares it to the count of the CDP neighbor to ensure that we get the
        same amount of neighbors. If count is incorrect it will return an error.
        :return: List with Dictionary values
        """
        pass

    def gather_lldp(self):
        pass

    def gather_route(self):
        pass

    def gather_bgp(self):
        pass

    def gather_inventory(self):
        pass

    def gather_commands(self, command_list):
        return_dict = dict()
        for command in command_list:
            return_dict[command] = self.send_command(command)
        return return_dict

    # Connection Commands
    def start_connection(self):
        """
        Starts Connection, if connection was started it will create connection with Netmiko ConnectHandler
        Otherwise it will reconnect if the connection is not alive.
        """
        if not self.connection.is_alive():
            self.connection.establish_connection()
            self.connection.session_preparation()

    def start_connect_w_retry(self, max_attempts=3):
        """
        Start Connection and handle attempts, This method will allow connection reattempts
        :param max_attempts: int default is 3
        """
        self.verbose_msg('Starting Connection')
        attempt = 0
        for attempt in range(max_attempts):
            try:
                self.start_connection()
                self.connection.session_preparation()
                return
            except Exception as e:
                self.verbose_msg('LOGIN FAILURE: Attempt to Establish Connection Failed, Attempt: ' + str(attempt))
        raise InitiatingConnectionException(
            'LOGIN FAILURE: Attempt to Establish Connection Failed, Attempt: ' + str(attempt)
        )

    def end_connection(self):
        self.connection.disconnect()

    def save_running_config(self):
        self.connection.save_config()

    def send_command(self, command, **kwargs):
        output = self.connection.send_command(command_string=command, **kwargs)
        return output

    def send_config_set(self, command_set, cmd_verify=False, **kwargs):
        if isinstance(command_set, str):
            command_set = command_set.splitlines()
        self.connection.send_config_set(command_set, cmd_verify=cmd_verify, **kwargs)

    def send_config_file(self, filename):
        self.connection.send_config_from_file(filename)

    def keep_alive(self, maintain_connection):
        if not maintain_connection:

            self.end_connection()

    def pretty_print_msg(self, msg):
        """
        Need to determine if we are going to print the XLS column,
        we will probably have to override it in a later function
        :param msg: msg to pretty print
        :return: None
        """
        line2 = str(self.host)
        if len(line2) < 15:
            line2 += (15 - len(line2)) * " "
        print(line2, "|", msg)

    @property
    def classname(self):
        return self.__class__.__name__

    def verbose_msg(self, msg):
        if self.verbose:
            line1 = str(self.host)
            if len(line1) < 15:
                line1 += (15 - len(line1)) * " "
            print(self, "verbose:", msg)

def test_print():
    print("This is a test of test broadcast system")
