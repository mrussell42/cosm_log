#!/usr/bin/python


import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adc_num, adc_conf):

    clockpin = adc_conf['clockpin']
    mosipin = adc_conf['mosipin']
    misopin = adc_conf['misopin']
    cspin = adc_conf['cspin']

    if ((adc_num > 7) or (adc_num < 0)):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adc_num
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(14):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1       # first bit is 'null' so drop it
    return adcout


def adc_setup(SPI_conf)
	# set up the SPI interface pins
	GPIO.setwarnings(False)
	GPIO.setup(SPI_conf['SPIMOSI'], GPIO.IN)
	GPIO.setup(SPI_conf['SPIMISO'], GPIO.IN)
	GPIO.setup(SPI_conf['SPICLK'], GPIO.IN)
	GPIO.setup(SPI_conf['SPICS'], GPIO.IN)

	# Now set them as required
	GPIO.setup(SPI_conf['SPIMOSI'], GPIO.OUT)
	GPIO.setup(SPI_conf['SPIMISO'], GPIO.IN)
	GPIO.setup(SPI_conf['SPICLK'], GPIO.OUT)
	GPIO.setup(SPI_conf['SPICS'], GPIO.OUT)
