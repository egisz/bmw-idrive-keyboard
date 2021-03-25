import can
import time
import os
import uinput

# ----- Open auto key bindings --------
# Enter -> [Enter]
# Left -> [Left]
# Right -> [Right]
# Up -> [Up]
# Down -> [Down]
# Back -> [Esc]
# Home -> [H]
# Phone -> [P]
# Call end -> [O]
# Play -> [X]
# Pause -> [C]
# Previous track -> [V] / [Media Previous]
# Next track -> [N] / [Media Next]
# Toggle play -> [B] / [Media Play]
# Voice command -> [M]
# Wheel left -> [1]
# Wheel right -> [2]
# ----- Open auto key bindings --------


# ----- CAN key bindings --------
# byte:   3     4     5
keys={
#    0x81: {0xDD: {0x01: 'left'}},   # left
#    0x21: {0xDD: {0x01: 'right'}},  # right
    0x11: {0xDD: uinput.KEY_UP},     # up
    0x12: {0xDD: uinput.KEY_ESC},      # up hold
    0x41: {0xDD: uinput.KEY_DOWN},   # down
    0x42: {0xDD: uinput.KEY_H},    # down hold 
    0x00: {0xDD: uinput.KEY_0},      # release
    0x01: {0xDE: uinput.KEY_ENTER},  # press enter
#        0x01: {0xC0: {0x02: 'h'}},      # back
#    0x01: {0xC0: {0x04: 'h'}},      # option
#    0x02: {
#         0xC0: {
#              0x02: 'esc',        # back hold
#              0x04: 'return'},     # option hold
#         0xDE: {0x01: 'h'}},     # menu hold
}

events = (
    uinput.KEY_ESC, # KEY_ESC https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
    uinput.KEY_1,
    uinput.KEY_2,
    uinput.KEY_H,
    uinput.KEY_UP,
    uinput.KEY_DOWN,
    uinput.KEY_ENTER,
    uinput.KEY_B
)

try:
    bus = can.interface.Bus()
except AttributeError:
    print('Cannot find CAN board.')
    exit()
    
print('Ready')

c0 = -1
c = -1
c2 = 0x00
lastKey = uinput.KEY_0
inReverse = 0

with uinput.Device(events) as device:
    time.sleep(1)
    try:
        while True:
            message = bus.recv()    # Wait until a message is received.
            
            # idrive rotation check, http://www.loopybunny.co.uk/CarPC/can/264.html
            if (message.arbitration_id == 0x264 and message.data[0] == 0xE1 and message.data[1] == 0xFD and message.data[5] == 0x1E):
                c0 = c
                c = message.data[4] * 256 + message.data[3]
                if (c < c0 and c0 != -1):
                    device.emit_click(uinput.KEY_1)
                    print("SCROLL LEFT")
                elif (c > c0 and c0 != -1):
                    device.emit_click(uinput.KEY_2)
                    print("SCROLL RIGHT")

            # if not rotation, then check if idrive buttons, http://www.loopybunny.co.uk/CarPC/can/267.html
            elif (message.arbitration_id == 0x267 and message.data[0] == 0xE1 and message.data[1] == 0x0FD and message.data[2] > c2):
                try:
                    # print(c2)
                    # print(message.data[3] == 0x11 + ' ' + message.data[4] == 0xDD)
                    #if (message.data[3] == 0x11 and message.data[4] == 0xDD):
                    #    print('UP')
                    val = keys[message.data[3]][message.data[4]]
                    #print(val)
                    if (val == uinput.KEY_ENTER):
                        print('ENTER')
                        device.emit_click(val)
                    # check if key is pressed
                    if (val != uinput.KEY_0):
                        print('Key pressed')
                        print(val)
                        lastKey = val
                    # check if key released and last key is not release (duplicate)
                    else: #f (lastKey != uinput.KEY_0):
                        print('Key realeased')
                        print(lastKey)
                        device.emit_click(lastKey)
                        lastKey = uinput.KEY_0
                except KeyError:
                    # do nothing
                    print('Unrecognized key')
                c2 = message.data[2]
            # if in reverse gear
            elif (message.arbitration_id == 0x21A and message.data[1] % 2 == 1 and inReverse == 0):
                print('IN REVERSE')
                inReverse = 1
                os.system("crankshaft rearcam show& ")
            elif (message.arbitration_id == 0x21A and message.data[1] % 2 == 0 and inReverse == 1):
                print('NOT REVERSE')
                inReverse = 0
                os.system("crankshaft rearcam hide& ")

    except KeyboardInterrupt:
        #Catch keyboard interrupt
        print('\n\rKeyboard interrtupt')    
