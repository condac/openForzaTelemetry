# openForzaTelemetry
Open source telemetry app for UDP output from Forza 7

## Enable Forza to send telemetry to same computer
in a windows command prompt with administrator rigths run:
 * CheckNetIsolation.exe LoopbackExempt -a -n=microsoft.apollobasegame_8wekyb3d8bbwe
## Gateway
The gateway module is capable of splitting the UDP data to multiple devices!

For the moment you edit gateway.py and add more lines for your devices and change ip and port manualy

## Android app
The android app is built with Kivy framework, to build your self run: buildozer android debug deploy run  
Download latest release at https://github.com/condac/openForzaTelemetry/releases  

The anrodid app is also runnable on PC see Python program  

## Python program
You should be able to run the sam android app on pc simply run:  
 python main.py

