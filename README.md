# openForzaTelemetry
Open source telemetry app for UDP output from Forza 7

## Enable Forza to send telemetry to same computer
in a windows command prompt with administrator rigths run:
 * CheckNetIsolation.exe LoopbackExempt -a -n=microsoft.apollobasegame_8wekyb3d8bbwe

## udpCloner
This program allows you to split the telemetry to multiple programs. If you run everything on the same computer you can just check the boxes for the programs to be activated. You must press Update for things to start working. 

## Analyzer
Rename the .csv file from your recordning to car1.csv and car2.csv to compare the results.

## Android app
The android app is built with Kivy framework, to build your self run: buildozer android debug deploy run  
Download latest release at https://github.com/condac/openForzaTelemetry/releases  

The anrodid app is also runnable on PC see Python program  

## Python program
You should be able to run the sam android app on pc simply run:  
 python main.py

