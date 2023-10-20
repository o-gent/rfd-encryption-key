# RFD Encryption key setter

## build
pip install pyserial
pip install pyinstaller

pyinstaller --noconfirm --onefile --windowed --icon logo.ico gui.pyw; pyarmor gen -O obfdist --pack dist/gui.exe gui.pyw

## User experience:
- open GUI program (text box, COM port dropdown, text explaining function, go button, success/fail)
- plug in RFD
- (option to select COM port explicitly)
- Enter encyrption key
- unplug RFD
- Repeat


## technical:
- poll COM ports
- When a new device is plugged in select that one
- display this port to user
- take encyrption key input from user
- button for user to press to start process
- display result (fail reason, or pass)



Mission planner sets the key here https://github.com/ArduPilot/MissionPlanner/blob/4f13e5afb1453e690548a76998c2df9a89237841/Radio/Sikradio.cs#L686C31-L686C31
