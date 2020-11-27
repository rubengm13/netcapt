import netmiko
import netcapt.functions


class NetworkDevice(object):
    def __init__(
            self,
            host='',
            username='',
            password='',
            secret='',
            device_type='',
            global_delay_factor=2,
            verbose=False,
            **kwargs
    ):
        self.host = host
        self.username = username
        self.password = password
        self.secret = secret
        if not self.secret:
            self.secret = password
        self.device_type = device_type
        self.global_delay_factor = global_delay_factor
        # Gather netmiko connection requirements to start the connection at a later time
        self.connection_variables = vars(self).copy()
        self.connection = None
        self.verbose = verbose
        self.model = None
        self.version = None
        self.serial_number = None
        self.hostname = None

    # Gather Functions
    # Most are Empty Place holders for respective Device Gathers
    def gather_version(self):
        pass

    def gather_cdp(self):
        pass

    def gather_lldp(self):
        pass

    def gather_arp(self):
        pass

    def gather_commands(self, command_list):
        return_dict = dict()
        for command in command_list:
            return_dict[command_list] = self.send_command(command)
        return return_dict

    # Connection Commands
    def start_connection(self):
        """
        Starts Connection, if connection was started it will create connection with Netmiko ConnectHandler
        Otherwise it will reconnect if the connection is not alive.
        """
        if not self.connection:
            self.connection = netmiko.ConnectHandler(**self.connection_variables)
        elif not self.connection.is_alive():
            self.connection.establish_connection()

    def end_connection(self):
        self.connection.disconnect()

    def save_running_config(self):
        self.start_connection()
        self.connection.save_config()
        self.end_connection()

    def send_command(self, command, **kwargs):
        self.start_connection()
        output = self.connection.send_command(command_string=command, **kwargs)
        return output

    def send_config(self, command_set):
        if isinstance(command_set, str):
            command_set = command_set.splitlines()
        self.start_connection()
        self.connection.send_config_set(command_set, cmd_verify=False)

    def send_config_file(self, filename):
        self.start_connection()
        self.connection.send_config_from_file(filename)

    def keep_alive(self, maintain_connection):
        if not maintain_connection:
            self.end_connection()

    def pretty_print_msg(self, msg):
        """
        Need to determine if we are going to print the XLS column,
        we will probably have to overrride it in a later function
        :param msg: msg to pretty print
        :return: None
        """
        line2 = str(self.host)
        if len(line2) < 15:
            line2 += (15 - len(line2)) * " "
        print(line2, "|", msg)


def test_print():
    print("This is a test of test broadcast system")