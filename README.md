easylap
=======

A server for an [EasyLAP](http://www.myezlap.com/store/index.html?language=en) RC timing device.

# Background
[Kyosho MiniZ](http://kyosho.com/mini-z-info/) are awesome remote control (RC) cars that [can race](https://www.youtube.com/watch?v=bLIlTpBr_Ls).

RC cars can be equipped with IR transponders that emit unique codes. When the RC cars pass the start line, the code is received by a timing system. A typical timing system sends the codes via a serial connection/USB to a Windows PC. The Windows PC runs a lap counter program such as [ZRound](https://www.zround.com/).

### Idea
Would like to run a lap counter on an phone or iPad, without having to connect a USB cable. Would like to use a Raspberry Pi Zero to send data.

### Building Blocks
* The [EasyLAP USB digital counter](http://www.myezlap.com/store/set-with-transponders-c-114_162_166/easylap-usb-digital-lap-counter-with-transponders-p-331.html?language=en) is based on a [CP2110 USB to UART Bridge](https://www.silabs.com/interface/usb-bridges/classic/device.cp2110-f01-gm) and uses the [Robitronic serial protocol](http://www.flipsideracing.org/projects/fslapcounter/wiki/RobitronicSerial). There is a [pycp2110](https://github.com/rginda/pycp2110) Python library that can communicate with the CP2110 device.
* We can turn on and off LEDs for start lights with a [Adafruit GPIO Expander Bonnet - 16 Additional I/O over I2C](https://www.adafruit.com/product/4132).

# Implementation
The project consists of a Python server that can run on a Raspberry Pi, and a iOS client. The server advertises a UDP service via [Bonjour (mDNS)](https://en.wikipedia.org/wiki/Multicast_DNS), reads from the EasyLAP device and sends data via UDP to registered clients. The client can register new racers and perform timing. The client pings the server periodically so that the client is not discarded and also sends commands such as `LIGHTS ON` / `LIGHTS OFF` / `LIGHTS <value>` used for turning on or off 5 LEDS connected to a GPIO expander. The 5 LEDs mimic the [F1 start sequence](http://www.formula1-dictionary.net/start_sequence.html).

### Challenges
iOS 14 adds an extra level of security that makes it harder for iOS apps to send or listen to UDP broadcast. The workaround is to use unicast to send data to a list of active clients.

# Setup

To build the server, run

```
pipenv shell
python3 -m build
```

This builds a easylap-0.0.1.tar.gz file under dist. Copy the file to the Raspberry Pi device, then run

```
pip3 install easylap-0.0.1.tar.gz
```

To start at boot time, modify `/etc/rc.local`. See: [Run a program at startup](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/).