#! /usr/bin/env python
# -*- coding: utf-8 -*-
###------重量測定-----    #comment out for try
import RPi.GPIO as GPIO

cdef int adcnum,clockpin, mosipin, misopin, cspin,commandout,adcout,j,i,sum1,num

num=100000

# MCP3208からSPI通信で12ビットのデジタル値を取得。0から7の8チャンネル使用可
cpdef readadc(adcnum, clockpin, mosipin, misopin, cspin):
	if adcnum > 7 or adcnum < 0:
		return -1
	GPIO.output(cspin, GPIO.HIGH)
	GPIO.output(clockpin, GPIO.LOW)
	GPIO.output(cspin, GPIO.LOW)

	commandout = adcnum
	commandout |= 0x18  # スタートビット＋シングルエンドビット
	commandout <<= 3    # LSBから8ビット目を送信するようにする

	for j in xrange(num):
		for i in xrange(5):# LSBから数えて8ビット目から4ビット目までを送信
			if commandout & 0x80:
				GPIO.output(mosipin, GPIO.HIGH)
			else:
				GPIO.output(mosipin, GPIO.LOW)
			commandout <<= 1
			GPIO.output(clockpin, GPIO.HIGH)
			GPIO.output(clockpin, GPIO.LOW)
		adcout = 0# 13ビット読む（ヌルビット＋12ビットデータ）
		sum1=0
		for i in xrange(13):
			GPIO.output(clockpin, GPIO.HIGH)
			GPIO.output(clockpin, GPIO.LOW)
			adcout <<= 1
			if i>0 and GPIO.input(misopin)==GPIO.HIGH:
				adcout |= 0x1
		GPIO.output(cspin, GPIO.HIGH)
		sum1+=adcout
	return sum1/num

#code of main
##GPIO.setmode(GPIO.BCM)
### ピンの名前を変数として定義
##SPICLK = 11
##SPIMOSI = 10
##SPIMISO = 9
##SPICS = 8
### SPI通信用の入出力を定義
##GPIO.setup(SPICLK, GPIO.OUT)
##GPIO.setup(SPIMOSI, GPIO.OUT)
##GPIO.setup(SPIMISO, GPIO.IN)
##GPIO.setup(SPICS, GPIO.OUT)
##weight=sub.readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)


