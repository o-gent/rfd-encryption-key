import time
import tkinter as tk
import tkinter.scrolledtext as st
from rfd_setting import RFD, logger
import os
import sys
import threading

key = os.urandom(32).hex()
logger.info(key)

# Set up the window
window = tk.Tk()
window.title("RFD pair tool")
window.resizable(width=False, height=False)

airside = False
groundside = False


def set_rfd_settings(rfd: RFD, airside:bool) -> list[bool]:
    check = rfd.enter_command_mode() and rfd.check_commands_work()
    enable_and_set = [
        rfd.send_setting(15, 1),
        rfd.send_setting(1, 57),
        rfd.send_setting(2,100),
        rfd.send_setting(3, int(id_entry.get())),
        rfd.send_setting(4, 30),
        rfd.send_setting(5, 0),
        rfd.send_setting(6, 1),
        rfd.send_setting(7, 0),
        rfd.send_setting(8, 865000),
        rfd.send_setting(9, 870000),
        rfd.send_setting(10, 8),
        rfd.send_setting(11, 100),
        rfd.send_setting(12, 0),
        rfd.send_setting(13, 0),
        rfd.send_setting(14, 50),
        rfd.send_setting(16, 0),
        rfd.send_setting(17, 0),
        rfd.send_setting(18, 0) if airside else rfd.send_setting(19, 2), # SBUS input (1)
        rfd.send_setting(19, 0) if airside else rfd.send_setting(18, 0), # SBUS output (2)
        rfd.send_setting(20, 0),
        rfd.send_setting(21, 0), # EXTRA LED output
        rfd.send_setting(22, 0),
        rfd.send_setting(23, 0), # rate and frequency band (only for 915)
        rfd.send_setting(24, 0),
        rfd.send_setting(25, 0),
        rfd.send_setting(25, 0),
        rfd.send_setting(28, 50),
        rfd.send_encryption_key(),
    ]
    return enable_and_set


def rfd_set_airside():
    incomplete = True
    while incomplete:
        try:
            air_side_pair.config(state="disabled")
            ground_side_pair.config(state="disabled")
            air_side_pair_status['text'] = "(re)connect the RFD!"; window.update()
            
            rfd = RFD(key)
            
            air_side_pair_status['text'] = "RFD found, processing.."; window.update()
            
            enable_and_set = set_rfd_settings(rfd, True)
            
            logger.info(enable_and_set)
            if all(enable_and_set):
                air_side_pair_status['text'] = "complete"
                ground_side_pair.config(state="disabled") if groundside else ground_side_pair.config(state="normal")
                incomplete = False
                del rfd
            else:
                air_side_pair_status['text'] = "failed, retrying.."
                time.sleep(1)
                del rfd
 
            global airside
            airside = True

        except:
            air_side_pair.config(state="normal")
            air_side_pair_status['text'] = "error! retrying.."; window.update()
            time.sleep(1)
    

def rfd_set_groundside():
    incomplete = True
    while incomplete:
        try:
            air_side_pair.config(state="disabled")
            ground_side_pair.config(state="disabled")
            ground_side_pair_status['text'] = "(re)connect the RFD!"; window.update()
            rfd = RFD(key)
            ground_side_pair_status['text'] = "RFD found, processing.."; window.update()
            
            enable_and_set = set_rfd_settings(rfd, False)

            logger.info(enable_and_set)
            if all(enable_and_set):
                ground_side_pair_status['text'] = "complete"
                air_side_pair.config(state="disabled") if airside else air_side_pair.config(state="normal")
                incomplete = False
                del rfd
            else:
                ground_side_pair_status['text'] = "config setting failed, retrying.."
                time.sleep(1)
                del rfd
            
            global groundside
            groundside = True

        except:
            ground_side_pair.config(state="normal")
            ground_side_pair_status['text'] = "error! retrying.."; window.update()
            time.sleep(1)


def restart_cmd():
    os.execl(sys.executable, sys.executable, *sys.argv)


restart = tk.Button(
    master=window,
    text="restart",
    command=restart_cmd
)


def start_ground_in_thread():
    threading.Thread(target=rfd_set_groundside).start()

def start_air_in_thread():
    threading.Thread(target=rfd_set_airside).start()

ground_side_pair = tk.Button(
    master=window,
    text="Set ground side radio",
    command=threading.Thread(target=start_ground_in_thread).start
)

ground_side_pair_status = tk.Label(master=window, text="unset")

air_side_pair = tk.Button(
    master=window,
    text="Set air side radio",
    command=threading.Thread(target=start_air_in_thread).start
)

air_side_pair_status = tk.Label(master=window, text="unset")


air_side_pair.config(state="disabled")
ground_side_pair.config(state="disabled")

def check_id(*args):
    id_ = id_entry.get()
    if id_.isdigit() and len(id_) == 1:
        air_side_pair.config(state="normal")
        ground_side_pair.config(state="normal")
        id_entry.config(state="disabled")
    else:
        air_side_pair.config(state="disabled")
        ground_side_pair.config(state="disabled")

stringvar1 = tk.StringVar(window)
stringvar1.trace("w", check_id)

# create ID input box
id_entry_box = tk.Frame(master=window)
id_entry = tk.Entry(master=id_entry_box, width=10, textvariable=stringvar1)
id_label = tk.Label(master=id_entry_box, text="ID")
id_entry.grid(row=0, column=0, sticky="e")
id_label.grid(row=0, column=1, sticky="w")

encrypt = tk.Label(master=window, text=key)

# Set up the layout using the .grid() geometry manager
id_entry_box.grid(row=1, column=0, padx=10)

ground_side_pair.grid(row=0, column=1, pady=10)
ground_side_pair_status.grid(row=1, column=1, pady=10)

air_side_pair.grid(row=0, column=2, pady=10)
air_side_pair_status.grid(row=1, column=2, pady=10)

restart.grid(row=0, column=0, pady=10)

encrypt.grid(row=2, column=0, pady=10, columnspan=3)

window.mainloop()