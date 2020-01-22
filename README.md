# Erika3004

[![Build Status](https://travis-ci.org/Chaostreff-Potsdam/erika3004.svg?branch=master)](https://travis-ci.org/Chaostreff-Potsdam/erika3004)

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
![Erika Connector](http://hc-ddr.hucki.net/wiki/lib/exe/fetch.php/z9001/erweiterungen/s3004_anschluss.jpg?cache=)

More information can be found here (German):  
[http://hc-ddr.hucki.net/wiki/doku.php/z9001/erweiterungen/s3004](http://hc-ddr.hucki.net/wiki/doku.php/z9001/erweiterungen/s3004)

A schematic of our Raspberry Pi based interface can be found [on EasyEDA](https://easyeda.com/sirexeclp/erikaraspberrypiinterface).
![Schematic](https://raw.githubusercontent.com/Chaostreff-Potsdam/erika-docs/master/schematics/Schematic_ErikaRaspberryPiInterface.png)

[DDR-Halbleiter - Kurzdatenblätter und Vergleichsliste](https://www-user.tu-chemnitz.de/~heha/basteln/Konsumg%C3%BCter/DDR-Halbleiter/)

## Configure Hardware Controlflow

Hardware Controlflow is disribed in the wiki: [Hardware-control-flow-(RTS,-CTS)](https://github.com/Chaostreff-Potsdam/erika3004/wiki/Hardware-control-flow-(RTS,-CTS)).

## Installation 

```
# Install python3
sudo apt-get install python3

# Install pip package manager for python
sudo apt-get install python3-pip

# Install necessary packages
pip3 install -r requirements.txt
```

### Install tab autocompletion for erika.sh

If you want to use the command-line interface (CLI) of `erika.sh` with automated completion if you press the <Tab> character, 
run the install script:  
```
./activate_autocomplete_for_erika_sh.sh
```

The script may fail under certain circumstances - requiring SUDO permissions. In this case, try again like this: 
```
sudo ./activate_autocomplete_for_erika_sh.sh
```

## ASCII art

### Create ASCII art for printout

* install Imagemagick's convert tool
```
sudo apt install imagemagick 
```
* install jp2a
```
sudo apt install jp2a
```
* convert png files on the command line like this: 
  * leave one dimension unspecified to keep the original ratio
```
convert ubuntu-logo32.png jpg:- | jp2a - --width=80 --height=80 > ascii_art.txt
```

### Print ASCII art 

The `erika.sh` command-line utility provides convenience functions to have Erika print a given ASCII art file.

It offers the following built-in rendering strategies:
  * LineByLine
    * render the given image line by line 
  * Interlaced 
    * render the given image, every even line first (starting count at 0), every odd line later
  * PerpendicularSpiralInward 
    * render the given image, spiralling inward to the middle while going parallel to X or Y axis all the time
    * implementation goes clockwise, starting at the upper left corner
  * RandomDotFill
    * render the given image, printing one random letter at a time
  * ArchimedeanSpiralOutward
    * render the given image, starting from the middle, following an Archimedean spiral as closely as possible

For further information, simply call   
```./erika.sh -h```

### Print images

This works mostly just like for ASCII art images, described in the previous section.

If as a file parameter for the CLI you specify an image file, it will be printed pixel by pixel, according to the
specified rendering strategy, like before for ASCII art images.

### Play "Tic Tac Toe"

To run the Tic Tac Toe game in a simulated environment, call this in your shell:

```
 ./erika.sh tictactoe -d
```

Play against the real Erika machine (use the right port as parameter):
```
./erika.sh tictactoe -p "/dev/ttyACM0"
```

To control the game: 
* use the WASD keys to move
* use the space bar or enter key to make your mark at the current position

## Testing

### Run unit tests

For now, call this in bash: 
```
./run_unittests.sh
```


### Run integration tests

For now, call this in bash: 
```
./run_integrationtests.sh
```
