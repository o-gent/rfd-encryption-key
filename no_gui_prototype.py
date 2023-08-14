import logging
import time
import re
import sys
from pathlib import Path

import serial
import serial.tools.list_ports


Path("./logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s, [%(levelname)s], %(message)s",
    handlers=[
        logging.FileHandler(f"logs/log_{time.strftime('%Y%m%d-%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")


class RFD():

    def __init__(self, key):
        """ Manage connecting to and changing RFD settings """
        self.__ser_open = False
        self.__key = self.set_user_key(key)
        self.__ser = serial.Serial(self.wait_for_new_port(), 56700, timeout=1)
        self.__ser_open = True

    def set_user_key(self, key):
        isvalid = re.match(r"\A\b[0-9a-fA-F]+\b\Z", key)
        if not isvalid:
            logger.info("Not a valid key")
            raise Exception("Invalid encryption key supplied, must be hexidecimal")
        return key

    def get_ports(self) -> set[str]:
        """ return a set of port strings """
        return set([portdetails[0] for portdetails in serial.tools.list_ports.comports()])

    def wait_for_new_port(self) -> str:
        """ periodically check availible ports, if port count increases, grab that new port string """
        oldports = self.get_ports()
        logger.info("now looking for a new port, connect the RFD")
        while True:
            ports = self.get_ports()
            if len(ports) > len(oldports):
                selected_port = ports.difference(oldports).pop()
                logger.info(f"Found a new port ({selected_port}), connecting...")
                return selected_port
            oldports = ports
            time.sleep(0.5)

    def send_encryption_key(self):
        """ send the encryption key, pad to 32 integers or 16 hex """
        self.send(f"AT&E={self.__key.ljust(32, '0')}")
        return True if self.read() == "key len 16" else False

    def send_setting(self, setting):
        """ send a setting and check for OK response """
        echo = self.send(setting)
        confirmation = self.read()
        return True if echo and confirmation=="OK" else False

    def check_commands_work(self) -> bool:
        """ sanity check that commands are working """
        self.send("ATI")
        return True if self.read().startswith("RFD") else False

    def enter_command_mode(self) -> bool:
        """ entering command mode is just '+++' no '\r\n' """
        self.__ser.write("+++".encode())
        time.sleep(1)
        return True if self.read() == "OK" else False

    def read(self) -> str:
        """ read the serial port and sanitise """
        result = self.__ser.read_until(b"\r\n").decode().strip("\r\n")
        logger.debug("READ " + result)
        return result

    def send(self, cmd: str) -> bool:
        """ each command requires '\r\n' afterwards and The RFD echos your command if correct """
        cmdbytes = f"{cmd}\r\n".encode()
        logging.debug( "SEND "+ cmd)
        self.__ser.write(cmdbytes)
        time.sleep(0.5)
        return True if self.read() == cmd else False
    
    def __del__(self):
        if self.__ser_open:
            logger.info("closing serial port")
            self.__ser.close()


if __name__ == "__main__":

    while True:
        try:
            rfd = RFD(input("Input your encryption key -> "))
            logger.info("starting task, this could take a few seconds")
            check = rfd.enter_command_mode() and rfd.check_commands_work()
            enable_and_set = rfd.send_setting("ATS15=1") and rfd.send_encryption_key()
            if enable_and_set:
                logger.info("Encryption key set!")
            else:
                logger.info(f"command mode initialisation {'passed' if check else 'failed'}, the encyrption key was not set. Remove power from the RFD then try again")
            del rfd
        except KeyboardInterrupt:
            print("stopped")
            time.sleep(2)
            raise Exception()
        except Exception as e:
            print("Error encountered:")
            print(e)
