#include <SoftwareSerial.h>
#include "ddr2ascii.h"
#include "ascii2ddr.h"

#define PC_BAUD 9600

#define RTS_PIN 3 // must be interupt able
#define ERIKA_RX 10
#define ERIKA_TX 11
#define ERIKA_BAUD 1200

SoftwareSerial erika(ERIKA_RX, ERIKA_TX); // RX, TX
volatile bool wait = false;

void setup()
{
	pinMode(RTS_PIN, INPUT);
	Serial.begin(PC_BAUD);
	erika.begin(ERIKA_BAUD);

	//pullup needed ? 
	//pinMode(RTS_PIN, INPUT_PULLUP);
	attachInterrupt(digitalPinToInterrupt(RTS_PIN), onRTS, FALLING);
}

void onRTS()
{
	wait = false;
}

void loop()
{ // run over and over
	//continue on falling edge
	if (wait == false)
	{
		//data from pc in serial buffer ?
		if (Serial.available())
		{
			//wait until next falling edge
			wait = true;
			//convert to raw (ddr-ascii)
			int result = ascii2ddr[Serial.read()];
			erika.write(result);
			//Serial.println(result,HEX);
		}
	}
	//erika has data to send
	if (erika.available())
	{
		//convert ddr-ascci to ascii and send to pc
		Serial.write(ddr2ascii[erika.read()]);
	}
}
