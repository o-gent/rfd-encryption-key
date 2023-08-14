import serial
import time
import logging 

KEY = "1231268"



logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s, [%(levelname)s], %(module)-5s, %(message)s",
    handlers=[
        logging.FileHandler(f"logs/log_{time.strftime('%Y%m%d-%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")


class RFD():

    def __init__(self):
        self.ser = serial.Serial("COM16", 56700, timeout=1)


    def get_ports(self):
        pass

    def wait_for_new_port(self):
        oldports = [portdetails[0] for portdetails in serial.tools.list_ports.comports()]
        while True:
            print("looking for new port....")
            ports = [portdetails[0] for portdetails in serial.tools.list_ports.comports()]

    def send_encryption_key(self, key: str):
        self.send(f"AT&E={key.ljust(32, '0')}")
        return True if self.read() == "key len 16" else False

    def send_setting(self, setting):
        echo = self.send(setting)
        confirmation = self.read()
        return True if echo and confirmation=="OK" else False

    def check_commands_work(self) -> bool:
        self.send("ATI")
        return True if self.read().startswith("RFD") else False

    def enter_command_mode(self) -> bool:
        """ entering command mode is just '+++' no '\r\n' """
        self.ser.write("+++".encode())
        time.sleep(1)
        return True if self.read() == "OK" else False

    def read(self) -> str:
        result = self.ser.read_until(b"\r\n").decode().strip("\r\n")
        logger.debug("READ " + result)
        return result

    def send(self, cmd: str) -> bool:
        """ each command requires '\r\n' afterwards and The RFD echos your command if correct """
        cmdbytes = f"{cmd}\r\n".encode()
        logging.debug( "SEND "+ cmd)
        self.ser.write(cmdbytes)
        time.sleep(1)
        return True if self.read() == cmd else False


import serial.tools.list_ports
ports = serial.tools.list_ports.comports()

for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))

rfd = RFD()

print(rfd.enter_command_mode())
print(rfd.check_commands_work())
print(rfd.send_setting("ATS15=1"))
print(rfd.send_encryption_key("011110"))