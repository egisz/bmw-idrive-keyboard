# carhack

Python script to capture BMW iDrive CANbus messages and simulate predefined keyboard strokes.
I used to integrate BMW F10 idrive rotary controller into OpenAuto ([Crankshaft project](https://github.com/opencardev/crankshaft)) Android auto solution.
Demo video in action on [youtube](https://www.youtube.com/watch?v=plySBRlPMZQ)

Script relies on: 

 - [python-can](https://github.com/hardbyte/python-can/blob/master/doc/index.rst)  library - for cature of CAN bus messages.
 - [uinput](https://pypi.org/project/python-uinput/) library - for simulation of keyboard input. This method acts as virtual keyboard.

Hardware:

- Raspberry pi board
- cheap [MCP2515 board](https://www.aliexpress.com/item/4000548754013.html?spm=a2g0s.9042311.0.0.27424c4dsagQ4T). Keep in mind that you need to connect board VCC  to Raspberry 3.3V pin, not 5V pin. It works fine. 
- [power supply](https://www.aliexpress.com/item/32909323470.html?spm=a2g0s.9042311.0.0.27424c4dGDPbPP) to power raspberry pi from car

Installing:

Run supplied `setup.sh` script or analyze it and do it manually.


Using:

Make sure to enable keyboard keys in Crankshaft Settings [Input tab]()

Idrive key bindings to OpenAuto keyboard keys:
<pre>
KEY_UP      # up
KEY_ESC     # up hold
KEY_DOWN,   # down
KEY_H,      # down hold (Home)
KEY_0,      # release
KEY_ENTER,  # press enter
KEY_1	    # rotary knob rotate counter clock
KEY_2       # rotary knob rotate clockwise
</pre>

Links:

 - Very detailed and nice [tutorial](https://www.raspberrypi.org/forums/viewtopic.php?t=141052) how to connect everything. Note, that board modification isn't needed. It works fine of 3.3V PIN.
