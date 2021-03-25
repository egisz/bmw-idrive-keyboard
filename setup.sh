#!/bin/bash -e

CAN_INTERFACE=can0
CAN_BITRATE=100000
CAN_OSCILATOR=8000000
CAN_INTERRUPT=12

# install required packages:
apt-get install can-utils python-pip
pip install python-can python-uinput

# setup can interface to bring up automatically on reboot.
FILE_CAN_INTERFACE=/etc/network/interfaces.d/$CAN_INTERFACE
if [ -f "$FILE_CAN_INTERFACE" ]; then
    echo "can0 network interface found, skipping..."
else
    echo "Setting up can0 interface"
    cat > $FILE_CAN_INTERFACE <<EOF
auto $CAN_INTERFACE
iface $CAN_INTERFACE can static
        bitrate $CAN_BITRATE
EOF
    echo "File patched: $FILE_CAN_INTERFACE";
    cat $FILE_CAN_INTERFACE
fi

# patch config.txt
FILE_BOOT_CFG=/boot/config.txt
# detect Raspberry BCM chip
BCM_CHIP=`cat /proc/cpuinfo | grep -oE 'BCM[0-9]{4}' | tr '[:upper:]' '[:lower:]'`
if [ -z "$BCM_CHIP" ]; then
    echo "ERROR: Could not detect BCM chip. Exiting..."
    exit
fi
# check if config already patched
if grep -q ^dtoverlay=mcp2515-can "$FILE_BOOT_CFG"; then 
    echo "config.txt already patched, skipping..."
else    
    # check if file writable
    if [ ! -w "$FILE_BOOT_CFG" ]; then
        echo "/boot not writable, remounting"
        mount -o remount,rw /boot
    fi
    cat >> $FILE_BOOT_CFG <<EOF

# CAN bus
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=$CAN_OSCILATOR,interrupt=$CAN_INTERRUPT
dtoverlay=spi-$BCM_CHIP
EOF
    echo "File patched: $FILE_BOOT_CFG"; 
fi

# setup python-can library configuration file
FILE_PYCAN_CONFIG=/etc/can.conf
if [ -f "$FILE_PYCAN_CONFIG" ]; then
    echo "File $FILE_PYCAN_CONFIG found, skipping..."
else
    echo "Setting up can0 interface"
    cat > $FILE_PYCAN_CONFIG <<EOF
[default]
interface = socketcan
channel = $CAN_INTERFACE
bitrate = $CAN_BITRATE
EOF
    echo "File patched: $FILE_PYCAN_CONFIG"; 
    cat $FILE_PYCAN_CONFIG
fi

# install and configure uinput module to load on boot
FILE_MODULES=/etc/modules
if ! grep -q uinput "$FILE_MODULES"; then
    cat >> $FILE_MODULES <<EOF
uinput
EOF
    echo "File patched: $FILE_MODULES"; 
fi

# try to load module manually
modprobe uinput

FILE_SCRIPT=carhack.py
DIR_SCRIPT=`pwd`

FILE_KBD_SERVICE=/etc/systemd/system/can-kbd.service
if [ ! -f "$FILE_KBD_SERVICE" ]; then
    cat > $FILE_KBD_SERVICE <<EOF
[Unit]
Description=Start Can Keyboard

[Service]
ExecStart=/usr/bin/python $DIR_SCRIPT/$FILE_SCRIPT
Restart=always
RestartSec=60s
KillMode=process
TimeoutSec=infinity

[Install]
WantedBy=multi-user.target
EOF
    echo "File created: $FILE_KBD_SERVICE";
    systemctl daemon-reload
    systemctl enable can-kbd.service
    systemctl start can-kbd.service
fi
#show service status
systemctl status can-kbd.service


