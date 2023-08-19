import tkinter as tk
import tkinter.scrolledtext as st
from rfd_setting import RFD, logger
import os
import sys

key = os.urandom(32).hex()
logger.info(key)

# Set up the window
window = tk.Tk()
window.title("RFD pair tool")
window.resizable(width=False, height=False)

def rfd_set_airside():
    air_side_pair_status['text'] = "(re)connect the RFD!"; window.update()
    rfd = RFD(key)
    air_side_pair_status['text'] = "RFD found, processing.."; window.update()
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
        rfd.send_setting(18, 0), # SBUS input (1)
        rfd.send_setting(19, 2), # SBUS output (2)
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
    logger.info(enable_and_set)
    if all(enable_and_set):
        air_side_pair_status['text'] = "complete"
    else:
        air_side_pair_status['text'] = "failed, retry"
        del rfd

def rfd_set_groundside():
    ground_side_pair_status['text'] = "(re)connect the RFD!"; window.update()
    rfd = RFD(key)
    ground_side_pair_status['text'] = "RFD found, processing.."; window.update()
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
        rfd.send_setting(19, 0), # SBUS output (2)
        rfd.send_setting(18, 1), # SBUS input (1)
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
    logger.info(enable_and_set)
    if all(enable_and_set):
        ground_side_pair_status['text'] = "complete"
    else:
        ground_side_pair_status['text'] = "failed, retry"
        del rfd

def restart_cmd():
    os.execl(sys.executable, sys.executable, *sys.argv)


restart = tk.Button(
    master=window,
    text="restart",
    command=restart_cmd
)


ground_side_pair = tk.Button(
    master=window,
    text="Set ground side radio",
    command=rfd_set_groundside
)

ground_side_pair_status = tk.Label(master=window, text="unset")

air_side_pair = tk.Button(
    master=window,
    text="Set air side radio",
    command=rfd_set_airside
)

air_side_pair_status = tk.Label(master=window, text="unset")


air_side_pair.config(state="disabled")
ground_side_pair.config(state="disabled")

def check_id(*args):
    id_ = id_entry.get()
    if id_.isdigit():
        air_side_pair.config(state="normal")
        ground_side_pair.config(state="normal")
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