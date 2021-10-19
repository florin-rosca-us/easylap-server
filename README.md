easylap
=======

A server for an [EasyLAP](http://www.myezlap.com/store/index.html?language=en) RC timing device.

# Background
[Kyosho MiniZ](http://kyosho.com/mini-z-info/) are awesome remote control (RC) cars that [can race](https://www.youtube.com/watch?v=bLIlTpBr_Ls).

RC cars can be equipped with IR transponders that emit unique codes. When the RC cars pass the start line, the code is received by a timing system. A typical timing system sends the codes via a serial connection/USB to a Windows PC. The Windows PC runs a lap counter program such as [ZRound](https://www.zround.com/).

## Idea
Would like to run a lap counter on an phone or iPad, without having to connect a USB cable. Would like to use a Raspberry Pi Zero to send data.

## Building Blocks
The [EasyLAP USB digital counter](http://www.myezlap.com/store/set-with-transponders-c-114_162_166/easylap-usb-digital-lap-counter-with-transponders-p-331.html?language=en) is based on a [CP2110 USB to UART Bridge](https://www.silabs.com/interface/usb-bridges/classic/device.cp2110-f01-gm) and uses the [Robitronic serial protocol](http://www.flipsideracing.org/projects/fslapcounter/wiki/RobitronicSerial). There is a [pycp2110](https://github.com/rginda/pycp2110) Python library that can communicate with the CP2110 device.

# Implementation
The project consists of a Python server that can run on a Raspberry Pi and a iOS client. The server advertises a UDP service via Bonjour, reads from the EasyLAP device and sends data via UDP to registered clients. The client can register new racers and perform timing.

## Challenges
### UDP Broadcast
iOS 14 adds an extra level of security that makes it harder for iOS apps to send or listen to UDP broadcast. The workaround is to use unicast to send data to a list of active clients.

# Building
To build the server, run
```
python3 --m build
```

This will build a wheel that can be copied on the target Raspberry Pi device.

TODO: explain the installation process / how to start at boot time.