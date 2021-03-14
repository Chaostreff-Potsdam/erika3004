# Erika3004 - Minimal Software Branch

## Hardware Setup

To configure your pi you can use the following tool (at your own risk):

https://github.com/sirexeclp/pi-setup

Or follow the steps described in our wiki page:

https://github.com/Chaostreff-Potsdam/erika3004/wiki/RaspberryPI-Setup


## Assuming your hardware is working ...

You should be able to run:

```
./erika_print < example/fox.txt
```

Which should print the contents of `example/fox.txt`:

> The quick brown fox jumps over the lazy dog.

Did it work?
Congrats your Erika-Setup seems to be working just fine.

You could also try printing this file and see what happens...

## Use in your App

You can install this package as a dependency for your app using pip:

```
pip3 install git+https://github.com/Chaostreff-Potsdam/erika3004.git
```

## Encoding

The Erika3004 Typewriter uses a proprietary encoding NOT compatible with ASCII, Unicode, etc.  
Therefore, software is needed to convert the RAW encoding (or DDR ASCII (GDR ASCII) as we call it ;) ) 
into something more useful (by modern standands) like ASCII.

A table of all available characters and their hexadecimal value can be found in the 
manual ([Erika-IF2014_AnwenderHandbuch](https://raw.githubusercontent.com/Chaostreff-Potsdam/erika-docs/blob/master/Erika-IF2014_AnwenderHandbuch.pdf)) as Appendix E on page 10.    
It also has a list of the most used control characters on page 11 (Appendix F).  
A complete list can be found [here](http://hc-ddr.hucki.net/wiki/doku.php/z9001/erweiterungen/s3004).  

We implemented the conversion in python using a json-file which contains all characters and their hexadecimal values.  
Find it in the `erika` directory (that name was chosen because python module names are based on directory names). 
  
The implementation for Arduino uses hard-coded arrays instead.  
Find it in the `arduino` directory. 

## Hardware

> If you are a proud owner of an Erika 3004 Electronic Typewriter, you might want to check out this [`"ServiceManual"`](https://github.com/Chaostreff-Potsdam/erika-docs/blob/master/Felix'ServiceManual.md).

Description of the Erica connector:  
![Erika Connector](https://raw.githubusercontent.com/Chaostreff-Potsdam/erika-docs/master/img/erica-connector.png)

More information can be found here (German):  
[http://hc-ddr.hucki.net/wiki/doku.php/z9001/erweiterungen/s3004](http://hc-ddr.hucki.net/wiki/doku.php/z9001/erweiterungen/s3004)

A schematic of our Raspberry Pi based interface can be found [on EasyEDA](https://easyeda.com/sirexeclp/erikaraspberrypiinterface).
![Schematic](https://raw.githubusercontent.com/Chaostreff-Potsdam/erika-docs/master/schematics/Schematic_ErikaRaspberryPiInterface.png)

[DDR-Halbleiter - Kurzdatenblätter und Vergleichsliste](https://www-user.tu-chemnitz.de/~heha/basteln/Konsumg%C3%BCter/DDR-Halbleiter/)

## Configure Hardware Controlflow

Hardware Controlflow is disribed in the wiki: [Hardware-control-flow-(RTS,-CTS)](https://github.com/Chaostreff-Potsdam/erika3004/wiki/Hardware-control-flow-(RTS,-CTS)).

# Documentation

For documentation, check the wiki of this projekt:
https://github.com/Chaostreff-Potsdam/erika3004/wiki

Additional documentation of the Hardware can be found in:
https://github.com/Chaostreff-Potsdam/erika-docs


