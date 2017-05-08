#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
##import numpy as np
import random
##import RPi.GPIO as GPIO
##import wiringpi2 as wiringpi
import sys
import csv
##import Adafruit_PCA9685
import time
import itertools
from itertools import combinations
from collections import Counter
import wx
import datetime
import pickle
import xlwt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties
import warnings;warnings.filterwarnings('ignore')
import wx.lib.agw.flatnotebook as fnb
import threading



#初期化(普段はコメントアウト)
f = file('log.dump', 'w')
parametor=[[u"日付(年)","","",0,0.0,0.0,datetime.timedelta(0),0.0,0.0,0.0,""],[u"日付(年)","","",0,0.0,0.0,datetime.timedelta(0),0.0,0.0,0.0,""]]#parametor[-1] = [today_qty,today_weight,ave_weight,dt,ave_cyecle_time,ave_cyecle_cost,ave_coverweight_cost,self.TxtCtl_22.GetValue()]
pickle.dump(parametor, f)
f.close()
f = file('senbetu_log.dump', 'w')
senbetu_parametor=[[u"日付(年)","","",0,0.0,0.0,datetime.timedelta(0),0.0,0.0,0.0,"",u"日付(年)","","",0,0.0,0.0,datetime.timedelta(0),0.0,0.0,""],[u"日付(年)","","",0,0.0,0.0,datetime.timedelta(0),0.0,0.0,0.0,"",u"日付(年)","","",0,0.0,0.0,datetime.timedelta(0),0.0,0.0,""]]#parametor[-1] = [today_qty,today_weight,ave_weight,dt,ave_cyecle_time,ave_cyecle_cost,ave_coverweight_cost,self.TxtCtl_22.GetValue()]
pickle.dump(senbetu_parametor, f)
f.close()
f = file('set.dump', 'w')
setting=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,25,200,220,190,0,20,40,60,80,0]
#setting[16]からsetting[24]がsetting。setting[25]はロータリーエンコーダーのencoderの値
pickle.dump(setting, f)
f.close()

#各変数をlog.dumpから読み出す
g = file('log.dump', 'r')
parametor = pickle.load(g)
print parametor
#parametor=[[/0/u"日付(年)",/1/"",/2/"",/3/0,/4/0.0,/5/0.0,/6/datetime.timedelta(0),/7/0.0,/8/0.0,/9/0.0,/10/"",/11/u"日付(年)",/12/"",/13/"",/14/0,/15/0.0,/16/0.0,/17/datetime.timedelta(0),/18/0.0,/19/0.0,/20/""]
start_time=datetime.datetime.today()
today_qty=parametor[-1][3]
today_weight=parametor[-1][4]
ave_weight=parametor[-1][5]
stock_time=parametor[-1][6]
ave_cyecle_time=parametor[-1][7]
ave_cyecle_cost=parametor[-1][8]
ave_coverweight_cost=parametor[-1][9]
g.close()

g = file('senbetu_log.dump', 'r')
senbetu_parametor = pickle.load(g)
print senbetu_parametor
senbetu_start_time=datetime.datetime.today()
senbetu_today_qty=senbetu_parametor[-1][3]
senbetu_today_weight=senbetu_parametor[-1][4]
senbetu_ave_weight=senbetu_parametor[-1][5]
senbetu_stock_time=senbetu_parametor[-1][6]
senbetu_ave_cyecle_time=senbetu_parametor[-1][7]
senbetu_ave_cyecle_cost=senbetu_parametor[-1][8]
stop_time=datetime.datetime.today()
senbetu_stop_time=datetime.datetime.today()
g.close()
##fp = FontProperties(fname=r'C:\Users\2140022\Desktop\プログラム\ipaexg.ttf', size=14)#'C:\Users\USER\Downloads\ipaexg.ttf'
x_plot=[1]
y_plot=[0]
final_sumweight_a=0
final_sumweight_b=0
final_sumweight_c=0
final_sumweight_d=0
x_bar=[1,2,3,4]

g = file('set.dump', 'r')
setting = pickle.load(g)
#計量されたテーブルNo
table_num = []
#テーブルごとの計量結果
table_weight=[]
i=0
weight_ave=setting[17]/2
stdev=40
total_weight=4*setting[17]
count=0  #counter for user
NGcount=0
encoder = setting[25]
g.close()

#switch onで、190g以下の時の処理
discharge_list_a=[]
discharge_list_b=[]
discharge_list_c=[]
discharge_list_d=[]
discharge_i=10
discharge_a_offset=True
discharge_b_offset=True
discharge_c_offset=True
discharge_d_offset=True
spare_num_a=[]
spare_num_b=[]
spare_num_c=[]
spare_num_d=[]
spare_i=0
spare_sumweight_a=[]
spare_sumweight_b=[]
spare_sumweight_c=[]
spare_sumweight_d=[]
numbering=0
senbetu_discharge_list_a=[]
senbetu_discharge_list_b=[]
senbetu_discharge_list_c=[]
senbetu_discharge_list_d=[]
table_code=0#各テーブルの番号
stop_trigger=False
senbetu_stop_trigger=False
senbetu_table_code=0

##GPIO.setmode(GPIO.BCM)
###押しボタン
##GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #comment out for try


###------モーター用PWM設定------
##
### Simple demo of of the PCA9685 PWM servo/LED controller library.
### This will move channel 0 from min to max position repeatedly.
### Author: Tony DiCola
### License: Public Domain
##
##
### Import the PCA9685 module.
##
##
##
### Uncomment to enable debug output.
###import logging
###logging.basicConfig(level=logging.DEBUG)
##
### Initialise the PCA9685 using the default address (0x40).
##pwm = Adafruit_PCA9685.PCA9685()
##
### Alternatively specify a different address and/or bus:
###pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
##
### Configure min and max servo pulse lengths
##servo_down = 150  # Min pulse length out of 4096
##servo_up = 450  # Max pulse length out of 4096  90 deg at def=300 ##dc_min=0
##
### Helper function to make setting a servo pulse width simpler.
##def set_servo_pulse(channel, pulse):
##	pulse_length = 1000000    # 1,000,000 us per second
##	pulse_length //= 60       # 60 Hz
##	print('{0}us per period'.format(pulse_length))
##	pulse_length //= 4096     # 12 bits of resolution
##	print('{0}us per bit'.format(pulse_length))
##	pulse *= 1000
##	pulse //= pulse_length
##	pwm.set_pwm(channel, 0, pulse)
##
### Set frequency to 60hz, good for servos.
##pwm.set_pwm_freq(60)

###------排出------
##
def discharge_a():
        pass
##	pwm.set_pwm(0, 0, servo_down)

def discharge_b():
        pass
##	pwm.set_pwm(1, 0, servo_down)

def discharge_c():
        pass
##	pwm.set_pwm(2, 0, servo_down)

def discharge_d():
        pass
##	pwm.set_pwm(3, 0, servo_down)

###------回転------

##GPIO.setmode(GPIO.BCM)
##GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)　##for ロータリーエンコーダー
##GPIO.setup(18, GPIO.OUT,initial=0)　##for FET
##initPos=1200#原点になるように値を調整
##
##ロータリーエンコーダーを使う。Aの信号だけ拾って位置を判断する。
###スタート
##p = GPIO.PWM(18, 50)
### 初期化
##p.start(0)
def rotate_moter():#1/16回転する
	pass
##	global encoder
##	pwm.set_pwm(0, 0, servo_up)
##	pwm.set_pwm(1, 0, servo_up)
##	pwm.set_pwm(2, 0, servo_up)
##	pwm.set_pwm(3, 0, servo_up)
##	p.ChangeDutyCycle( 0 )
##	p.ChangeDutyCycle( 60 )
##	time.sleep(0.1)
##	if encoder==initPos:
##		p.ChangeDutyCycle( 0 )
##		time.sleep(0.1)
##		f = file('set.dump', 'w')
##		setting[25]=encoder
##		pickle.dump(setting, f)
##		f.close()

def moterEncode():
	global encoder
	while True:
		GPIO.wait_for_edge(17, GPIO.BOTH)
		encoder+=1
		if encoder==1800:#ギア比75*一周のパルス信号24
			encoder=0
	
	
	

#------組合せ------

def choice():  #4 dischargers
	#リセット
	sum_table_weight=[]
	allcombi_num=[]
	allcombi_weight=[]
	allcombi_weight_dif=[]                                  #allcombi_weight_dif=[204.78022541534693, 88.19455714403786, 84.85081941624652, 31.734848855062552, 113.21724615959693, 3.3684221117121638, 6.712159839503499, 123.29782811081253, 84.85042555351703, 31.73524271779206, 35.0789804455834, 151.6646487168925, 6.712553702232981, 123.29822197354207, 126.6419597013334, 243.22762797264244, 123.55823768144668, 6.972569410137623, 3.628831682346288, 112.9568365889628, 31.995258425696676, 84.59040984561244, 87.93414757340378, 204.5198158447128, 3.628437819616778, 112.95723045169228, 116.30096817948362, 232.88663645079276, 87.9345414361332, 204.52020970744235, 207.86394743523368, 324.4496157065427, 119.66939029119577, 3.083722019886693, 0.26001570790464257, 116.84568397921373, 28.106411035445774, 88.47925723586332, 91.82299496365465, 208.40866323496368, 0.26040957063412407, 116.84607784194321, 120.18981556973455, 236.77548384104364, 91.82338882638413, 208.40905709769322, 211.75279482548456, 328.33846309679365, 38.447402557295504, 78.13826571401353, 81.48200344180486, 198.06767171311395, 53.115576698454504, 169.7012449697636, 173.04498269755493, 289.63065096886396, 81.4823973045344, 198.06806557584343, 201.41180330363477, 317.997471574944, 173.04537656028435, 289.6310448315935, 292.97478255938483, 409.5604508306939]
	allcombi_weight_dif_order=[]
	allcombi_order=[]                                            #allcombi_order=[[4, 5], [2, 3], [3, 4], [0, 1], [2, 5], [0, 4], [1, 5], [1, 4]]
	leftover_order_allcombi=[]
	table_num_2=[]
	n=0	                                                #n=4
	combi_num=[]
	combi_weight_a=[]
	combi_weight_b=[]
	combi_weight_c=[]
	combi_weight_d=[]
	global NGcount
	error_count=0
	global table_num
	global table_weight
	global spare_num_a
	global spare_num_b
	global spare_num_c
	global spare_num_d
	global spare_sumweight_a
	global spare_sumweight_b
	global spare_sumweight_c
	global spare_sumweight_d
	global i
	global spare_i
	global today_weight
	global today_qty
	global setting

	spare_i=i

	#print "組合せ計算中"
	#べき集合の関数
	def powerset(s):
		return [[s[j] for j in xrange(len(s)) if (i&(1<<j))] for i in xrange(1<<len(s))]
	#全組合せのNumとweightのlist作成
	allcombi_num=powerset(table_num)                        #allcombi_num=[[], [0], [1], [0, 1], [2], [0, 2], [1, 2], [0, 1, 2], [3], [0, 3], [1, 3], [0, 1, 3], [2, 3], [0, 2, 3], [1, 2, 3], [0, 1, 2, 3], [4], [0, 4], [1, 4], [0, 1, 4], [2, 4], [0, 2, 4], [1, 2, 4], [0, 1, 2, 4], [3, 4], [0, 3, 4], [1, 3, 4], [0, 1, 3, 4], [2, 3, 4], [0, 2, 3, 4], [1, 2, 3, 4], [0, 1, 2, 3, 4], [5], [0, 5], [1, 5], [0, 1, 5], [2, 5], [0, 2, 5], [1, 2, 5], [0, 1, 2, 5], [3, 5], [0, 3, 5], [1, 3, 5], [0, 1, 3, 5], [2, 3, 5], [0, 2, 3, 5], [1, 2, 3, 5], [0, 1, 2, 3, 5], [4, 5], [0, 4, 5], [1, 4, 5], [0, 1, 4, 5], [2, 4, 5], [0, 2, 4, 5], [1, 2, 4, 5], [0, 1, 2, 4, 5], [3, 4, 5], [0, 3, 4, 5], [1, 3, 4, 5], [0, 1, 3, 4, 5], [2, 3, 4, 5], [0, 2, 3, 4, 5], [1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]]
	allcombi_weight=powerset(table_weight)                  #allcombi_weight=[[], [116.58566827130907], [119.92940599910041], [116.58566827130907, 119.92940599910041], [91.56297925575001], [116.58566827130907, 91.56297925575001], [119.92940599910041, 91.56297925575001], [116.58566827130907, 119.92940599910041, 91.56297925575001], [119.9297998618299], [116.58566827130907, 119.9297998618299], [119.92940599910041, 119.9297998618299], [116.58566827130907, 119.92940599910041, 119.9297998618299], [91.56297925575001, 119.9297998618299], [116.58566827130907, 91.56297925575001, 119.9297998618299], [119.92940599910041, 91.56297925575001, 119.9297998618299], [116.58566827130907, 119.92940599910041, 91.56297925575001, 119.9297998618299], [81.22198773390025], [116.58566827130907, 81.22198773390025], [119.92940599910041, 81.22198773390025], [116.58566827130907, 119.92940599910041, 81.22198773390025], [91.56297925575001, 81.22198773390025], [116.58566827130907, 91.56297925575001, 81.22198773390025], [119.92940599910041, 91.56297925575001, 81.22198773390025], [116.58566827130907, 119.92940599910041, 91.56297925575001, 81.22198773390025], [119.9297998618299, 81.22198773390025], [116.58566827130907, 119.9297998618299, 81.22198773390025], [119.92940599910041, 119.9297998618299, 81.22198773390025], [116.58566827130907, 119.92940599910041, 119.9297998618299, 81.22198773390025], [91.56297925575001, 119.9297998618299, 81.22198773390025], [116.58566827130907, 91.56297925575001, 119.9297998618299, 81.22198773390025], [119.92940599910041, 91.56297925575001, 119.9297998618299, 81.22198773390025], [116.58566827130907, 119.92940599910041, 91.56297925575001, 119.9297998618299, 81.22198773390025], [85.11083512415117], [116.58566827130907, 85.11083512415117], [119.92940599910041, 85.11083512415117], [116.58566827130907, 119.92940599910041, 85.11083512415117], [91.56297925575001, 85.11083512415117], [116.58566827130907, 91.56297925575001, 85.11083512415117], [119.92940599910041, 91.56297925575001, 85.11083512415117], [116.58566827130907, 119.92940599910041, 91.56297925575001, 85.11083512415117], [119.9297998618299, 85.11083512415117], [116.58566827130907, 119.9297998618299, 85.11083512415117], [119.92940599910041, 119.9297998618299, 85.11083512415117], [116.58566827130907, 119.92940599910041, 119.9297998618299, 85.11083512415117], [91.56297925575001, 119.9297998618299, 85.11083512415117], [116.58566827130907, 91.56297925575001, 119.9297998618299, 85.11083512415117], [119.92940599910041, 91.56297925575001, 119.9297998618299, 85.11083512415117], [116.58566827130907, 119.92940599910041, 91.56297925575001, 119.9297998618299, 85.11083512415117], [81.22198773390025, 85.11083512415117], [116.58566827130907, 81.22198773390025, 85.11083512415117], [119.92940599910041, 81.22198773390025, 85.11083512415117], [116.58566827130907, 119.92940599910041, 81.22198773390025, 85.11083512415117], [91.56297925575001, 81.22198773390025, 85.11083512415117], [116.58566827130907, 91.56297925575001, 81.22198773390025, 85.11083512415117], [119.92940599910041, 91.56297925575001, 81.22198773390025, 85.11083512415117], [116.58566827130907, 119.92940599910041, 91.56297925575001, 81.22198773390025, 85.11083512415117], [119.9297998618299, 81.22198773390025, 85.11083512415117], [116.58566827130907, 119.9297998618299, 81.22198773390025, 85.11083512415117], [119.92940599910041, 119.9297998618299, 81.22198773390025, 85.11083512415117], [116.58566827130907, 119.92940599910041, 119.9297998618299, 81.22198773390025, 85.11083512415117], [91.56297925575001, 119.9297998618299, 81.22198773390025, 85.11083512415117], [116.58566827130907, 91.56297925575001, 119.9297998618299, 81.22198773390025, 85.11083512415117], [119.92940599910041, 91.56297925575001, 119.9297998618299, 81.22198773390025, 85.11083512415117], [116.58566827130907, 119.92940599910041, 91.56297925575001, 119.9297998618299, 81.22198773390025, 85.11083512415117]]
	#全組合せweightと目標値の差分のlist作成
	sum_table_weight=sum(table_weight)                      #sum_table_weight=614.340676246
	for j in allcombi_weight:
		allcombi_weight_dif.append(abs(sum(j)-setting[17]))

	allcombi_weight_dif_allorder=sorted(range(len(allcombi_weight_dif)), key=allcombi_weight_dif.__getitem__)
	for j in allcombi_weight_dif_allorder:
		allcombi_order.append(allcombi_num[j]) #allcombi_order=[[0, 3], [1, 6], [6, 7], [0, 1], [3, 5], [3, 6], [0, 7], [1, 5], [4, 8], [5, 7], [2, 7], [1, 2], [0, 5], [2, 3], [5, 6], [1, 3], [0, 6], [3, 7], [2, 8], [4, 7], [1, 7], [1, 4], [2, 5], [3, 4], [0, 2], [6, 8], [2, 6], [0, 8], [2, 4, 6], [5, 8], [0, 2, 4], [4, 5], [2, 4, 5], [0, 4], [4, 6], [3, 8], [0, 4, 6], [1, 8], [4, 5, 6], [2, 3, 4], [7, 8], [0, 4, 5], [1, 2, 4], [2, 4], [2, 4, 7], [8], [0, 2, 6], [3, 4, 6], [2, 5, 6], [1, 4, 6], [0, 3, 4], [0, 2, 5], [4, 6, 7], [0, 1, 4], [3, 4, 5], [0, 4, 7], [1, 4, 5], [4, 5, 7], [2, 3, 6], [0, 5, 6], [1, 2, 6], [0, 2, 3], [2, 6, 7], [0, 1, 2], [2, 3, 5], [1, 3, 4], [0, 2, 7], [1, 2, 5], [3, 4, 7], [2, 4, 8], [2, 5, 7], [7], [1, 4, 7], [0, 3, 6], [1], [0, 1, 6], [3, 5, 6], [3], [0, 6, 7], [1, 5, 6], [0, 3, 5], [1, 2, 3], [4, 6, 8], [5, 6, 7], [2, 3, 7], [0, 1, 5], [0, 4, 8], [0, 5, 7], [1, 2, 7], [4, 5, 8], [5], [1, 3, 6], [0], [3, 6, 7], [0, 1, 3], [2, 6, 8], [6], [1, 6, 7], [0, 3, 7], [1, 3, 5], [0, 2, 8], [3, 4, 8], [0, 1, 7], [3, 5, 7], [2, 5, 8], [1, 4, 8], [1, 5, 7], [4, 7, 8], [2], [0, 6, 8], [5, 6, 8], [2, 3, 8], [0, 2, 4, 6], [1, 3, 7], [0, 5, 8], [1, 2, 8], [2, 4, 5, 6], [2, 7, 8], [0, 2, 4, 5], [4], [3, 6, 8], [1, 6, 8], [0, 3, 8], [2, 3, 4, 6], [6, 7, 8], [0, 1, 8], [3, 5, 8], [0, 4, 5, 6], [1, 2, 4, 6], [0, 2, 3, 4], [0, 7, 8], [2, 4, 6, 7], [1, 5, 8], [0, 1, 2, 4], [2, 3, 4, 5], [5, 7, 8], [0, 2, 4, 7], [1, 2, 4, 5], [2, 4, 5, 7], [0, 3, 4, 6], [0, 2, 5, 6], [1, 3, 8], [0, 1, 4, 6], [3, 4, 5, 6], [3, 7, 8], [0, 4, 6, 7], [1, 4, 5, 6], [0, 3, 4, 5], [1, 2, 3, 4], [1, 7, 8], [4, 5, 6, 7], [2, 3, 4, 7], [0, 1, 4, 5], [0, 4, 5, 7], [1, 2, 4, 7], [0, 2, 3, 6], [0, 1, 2, 6], [2, 3, 5, 6], [1, 3, 4, 6], [0, 2, 6, 7], [1, 2, 5, 6], [0, 2, 3, 5], [3, 4, 6, 7], [0, 1, 3, 4], [2, 4, 6, 8], [2, 5, 6, 7], [0, 1, 2, 5], [1, 4, 6, 7], [0, 3, 4, 7], [1, 3, 4, 5], [0, 2, 4, 8], [0, 2, 5, 7], [0, 1, 4, 7], [3, 4, 5, 7], [2, 4, 5, 8], [1, 4, 5, 7], [0, 3, 5, 6], [1, 2, 3, 6], [2, 3, 6, 7], [0, 1, 5, 6], [0, 1, 2, 3], [0, 4, 6, 8], [0, 5, 6, 7], [1, 2, 6, 7], [0, 2, 3, 7], [1, 2, 3, 5], [4, 5, 6, 8], [2, 3, 4, 8], [0, 1, 2, 7], [2, 3, 5, 7], [1, 3, 4, 7], [0, 4, 5, 8], [1, 2, 4, 8], [1, 2, 5, 7], [0, 1, 3, 6], [2, 4, 7, 8], [], [0, 3, 6, 7], [1, 3, 5, 6], [0, 2, 6, 8], [3, 4, 6, 8], [0, 1, 6, 7], [3, 5, 6, 7], [0, 1, 3, 5], [2, 5, 6, 8], [1, 4, 6, 8], [0, 3, 4, 8], [1, 5, 6, 7], [0, 3, 5, 7], [1, 2, 3, 7], [0, 2, 5, 8], [4, 6, 7, 8], [0, 1, 4, 8], [3, 4, 5, 8], [0, 1, 5, 7], [0, 4, 7, 8], [1, 4, 5, 8], [4, 5, 7, 8], [2, 3, 6, 8], [1, 3, 6, 7], [0, 5, 6, 8], [1, 2, 6, 8], [0, 2, 3, 8], [0, 1, 3, 7], [2, 6, 7, 8], [0, 1, 2, 8], [2, 3, 5, 8], [0, 2, 4, 5, 6], [1, 3, 4, 8], [1, 3, 5, 7], [0, 2, 7, 8], [1, 2, 5, 8], [3, 4, 7, 8], [2, 5, 7, 8], [1, 4, 7, 8], [0, 3, 6, 8], [0, 1, 6, 8], [3, 5, 6, 8], [0, 2, 3, 4, 6], [0, 6, 7, 8], [1, 5, 6, 8], [0, 3, 5, 8], [1, 2, 3, 8], [0, 1, 2, 4, 6], [2, 3, 4, 5, 6], [5, 6, 7, 8], [2, 3, 7, 8], [0, 2, 4, 6, 7], [0, 1, 5, 8], [1, 2, 4, 5, 6], [0, 2, 3, 4, 5], [0, 5, 7, 8], [1, 2, 7, 8], [2, 4, 5, 6, 7], [0, 1, 2, 4, 5], [0, 2, 4, 5, 7], [1, 3, 6, 8], [3, 6, 7, 8], [0, 1, 3, 8], [0, 3, 4, 5, 6], [1, 2, 3, 4, 6], [1, 6, 7, 8], [0, 3, 7, 8], [2, 3, 4, 6, 7], [1, 3, 5, 8], [0, 1, 4, 5, 6], [0, 1, 2, 3, 4], [0, 1, 7, 8], [3, 5, 7, 8], [0, 4, 5, 6, 7], [1, 2, 4, 6, 7], [0, 2, 3, 4, 7], [1, 2, 3, 4, 5], [1, 5, 7, 8], [0, 1, 2, 4, 7], [2, 3, 4, 5, 7], [1, 2, 4, 5, 7], [0, 2, 3, 5, 6], [0, 1, 3, 4, 6], [0, 1, 2, 5, 6], [0, 3, 4, 6, 7], [1, 3, 4, 5, 6], [0, 2, 4, 6, 8], [0, 2, 5, 6, 7], [1, 3, 7, 8], [0, 1, 4, 6, 7], [3, 4, 5, 6, 7], [0, 1, 3, 4, 5], [2, 4, 5, 6, 8], [1, 4, 5, 6, 7], [0, 3, 4, 5, 7], [1, 2, 3, 4, 7], [0, 2, 4, 5, 8], [0, 1, 4, 5, 7], [0, 1, 2, 3, 6], [0, 2, 3, 6, 7], [1, 2, 3, 5, 6], [2, 3, 4, 6, 8], [0, 1, 2, 6, 7], [2, 3, 5, 6, 7], [0, 1, 2, 3, 5], [1, 3, 4, 6, 7], [0, 4, 5, 6, 8], [1, 2, 4, 6, 8], [0, 2, 3, 4, 8], [1, 2, 5, 6, 7], [0, 2, 3, 5, 7], [0, 1, 3, 4, 7], [2, 4, 6, 7, 8], [0, 1, 2, 4, 8], [2, 3, 4, 5, 8], [0, 1, 2, 5, 7], [1, 3, 4, 5, 7], [0, 2, 4, 7, 8], [1, 2, 4, 5, 8], [0, 1, 3, 5, 6], [2, 4, 5, 7, 8], [0, 3, 4, 6, 8], [0, 3, 5, 6, 7], [1, 2, 3, 6, 7], [0, 2, 5, 6, 8], [0, 1, 4, 6, 8], [3, 4, 5, 6, 8], [0, 1, 5, 6, 7], [0, 1, 2, 3, 7], [0, 4, 6, 7, 8], [1, 4, 5, 6, 8], [0, 3, 4, 5, 8], [1, 2, 3, 4, 8], [1, 2, 3, 5, 7], [4, 5, 6, 7, 8], [2, 3, 4, 7, 8], [0, 1, 4, 5, 8], [0, 4, 5, 7, 8], [1, 2, 4, 7, 8], [0, 2, 3, 6, 8], [0, 1, 3, 6, 7], [0, 1, 2, 6, 8], [2, 3, 5, 6, 8], [1, 3, 4, 6, 8], [1, 3, 5, 6, 7], [0, 2, 6, 7, 8], [1, 2, 5, 6, 8], [0, 2, 3, 5, 8], [3, 4, 6, 7, 8], [0, 1, 3, 4, 8], [0, 1, 3, 5, 7], [2, 5, 6, 7, 8], [0, 1, 2, 5, 8], [1, 4, 6, 7, 8], [0, 3, 4, 7, 8], [1, 3, 4, 5, 8], [0, 2, 5, 7, 8], [0, 1, 4, 7, 8], [3, 4, 5, 7, 8], [1, 4, 5, 7, 8], [0, 3, 5, 6, 8], [1, 2, 3, 6, 8], [2, 3, 6, 7, 8], [0, 1, 5, 6, 8], [0, 1, 2, 3, 8], [0, 2, 3, 4, 5, 6], [0, 5, 6, 7, 8], [1, 2, 6, 7, 8], [0, 2, 3, 7, 8], [1, 2, 3, 5, 8], [0, 1, 2, 4, 5, 6], [0, 1, 2, 7, 8], [2, 3, 5, 7, 8], [0, 2, 4, 5, 6, 7], [1, 3, 4, 7, 8], [1, 2, 5, 7, 8], [0, 1, 3, 6, 8], [0, 3, 6, 7, 8], [1, 3, 5, 6, 8], [0, 1, 2, 3, 4, 6], [0, 1, 6, 7, 8], [3, 5, 6, 7, 8], [0, 2, 3, 4, 6, 7], [0, 1, 3, 5, 8], [1, 2, 3, 4, 5, 6], [1, 5, 6, 7, 8], [0, 3, 5, 7, 8], [1, 2, 3, 7, 8], [0, 1, 2, 4, 6, 7], [2, 3, 4, 5, 6, 7], [0, 1, 2, 3, 4, 5], [0, 1, 5, 7, 8], [1, 2, 4, 5, 6, 7], [0, 2, 3, 4, 5, 7], [0, 1, 2, 4, 5, 7], [1, 3, 6, 7, 8], [0, 1, 3, 4, 5, 6], [0, 1, 3, 7, 8], [0, 3, 4, 5, 6, 7], [1, 2, 3, 4, 6, 7], [0, 2, 4, 5, 6, 8], [1, 3, 5, 7, 8], [0, 1, 4, 5, 6, 7], [0, 1, 2, 3, 4, 7], [1, 2, 3, 4, 5, 7], [0, 1, 2, 3, 5, 6], [0, 2, 3, 4, 6, 8], [0, 2, 3, 5, 6, 7], [0, 1, 3, 4, 6, 7], [0, 1, 2, 4, 6, 8], [2, 3, 4, 5, 6, 8], [0, 1, 2, 5, 6, 7], [1, 3, 4, 5, 6, 7], [0, 2, 4, 6, 7, 8], [1, 2, 4, 5, 6, 8], [0, 2, 3, 4, 5, 8], [0, 1, 3, 4, 5, 7], [2, 4, 5, 6, 7, 8], [0, 1, 2, 4, 5, 8], [0, 2, 4, 5, 7, 8], [0, 1, 2, 3, 6, 7], [0, 3, 4, 5, 6, 8], [1, 2, 3, 4, 6, 8], [1, 2, 3, 5, 6, 7], [2, 3, 4, 6, 7, 8], [0, 1, 4, 5, 6, 8], [0, 1, 2, 3, 4, 8], [0, 1, 2, 3, 5, 7], [0, 4, 5, 6, 7, 8], [1, 2, 4, 6, 7, 8], [0, 2, 3, 4, 7, 8], [1, 2, 3, 4, 5, 8], [0, 1, 2, 4, 7, 8], [2, 3, 4, 5, 7, 8], [1, 2, 4, 5, 7, 8], [0, 2, 3, 5, 6, 8], [0, 1, 3, 4, 6, 8], [0, 1, 3, 5, 6, 7], [0, 1, 2, 5, 6, 8], [0, 3, 4, 6, 7, 8], [1, 3, 4, 5, 6, 8], [0, 2, 5, 6, 7, 8], [0, 1, 4, 6, 7, 8], [3, 4, 5, 6, 7, 8], [0, 1, 3, 4, 5, 8], [1, 4, 5, 6, 7, 8], [0, 3, 4, 5, 7, 8], [1, 2, 3, 4, 7, 8], [0, 1, 4, 5, 7, 8], [0, 1, 2, 3, 6, 8], [0, 2, 3, 6, 7, 8], [1, 2, 3, 5, 6, 8], [0, 1, 2, 6, 7, 8], [2, 3, 5, 6, 7, 8], [0, 1, 2, 3, 5, 8], [1, 3, 4, 6, 7, 8], [1, 2, 5, 6, 7, 8], [0, 2, 3, 5, 7, 8], [0, 1, 3, 4, 7, 8], [0, 1, 2, 5, 7, 8], [1, 3, 4, 5, 7, 8], [0, 1, 3, 5, 6, 8], [0, 3, 5, 6, 7, 8], [1, 2, 3, 6, 7, 8], [0, 1, 2, 3, 4, 5, 6], [0, 1, 5, 6, 7, 8], [0, 1, 2, 3, 7, 8], [0, 2, 3, 4, 5, 6, 7], [1, 2, 3, 5, 7, 8], [0, 1, 2, 4, 5, 6, 7], [0, 1, 3, 6, 7, 8], [1, 3, 5, 6, 7, 8], [0, 1, 2, 3, 4, 6, 7], [0, 1, 3, 5, 7, 8], [1, 2, 3, 4, 5, 6, 7], [0, 1, 2, 3, 4, 5, 7], [0, 2, 3, 4, 5, 6, 8], [0, 1, 3, 4, 5, 6, 7], [0, 1, 2, 4, 5, 6, 8], [0, 2, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 6, 8], [0, 1, 2, 3, 5, 6, 7], [0, 2, 3, 4, 6, 7, 8], [1, 2, 3, 4, 5, 6, 8], [0, 1, 2, 4, 6, 7, 8], [2, 3, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 5, 8], [1, 2, 4, 5, 6, 7, 8], [0, 2, 3, 4, 5, 7, 8], [0, 1, 2, 4, 5, 7, 8], [0, 1, 3, 4, 5, 6, 8], [0, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 6, 7, 8], [0, 1, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 7, 8], [1, 2, 3, 4, 5, 7, 8], [0, 1, 2, 3, 5, 6, 8], [0, 2, 3, 5, 6, 7, 8], [0, 1, 3, 4, 6, 7, 8], [0, 1, 2, 5, 6, 7, 8], [1, 3, 4, 5, 6, 7, 8], [0, 1, 3, 4, 5, 7, 8], [0, 1, 2, 3, 6, 7, 8], [1, 2, 3, 5, 6, 7, 8], [0, 1, 2, 3, 5, 7, 8], [0, 1, 3, 5, 6, 7, 8], [0, 1, 2, 3, 4, 5, 6, 7], [0, 1, 2, 3, 4, 5, 6, 8], [0, 2, 3, 4, 5, 6, 7, 8], [0, 1, 2, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8], [0, 1, 2, 3, 4, 5, 7, 8], [0, 1, 3, 4, 5, 6, 7, 8], [0, 1, 2, 3, 5, 6, 7, 8], [0, 1, 2, 3, 4, 5, 6, 7, 8]]

	def flatten(nested_list):
		"""2重のリストをフラットにする関数"""
		return [e for inner_list in nested_list for e in inner_list]

	table_num_1=table_num[:]

	try:
		for h in (8,15,25,40):
			lst=list(combinations(allcombi_order[:h],4))	#lst=[((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3)), ((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 4)), ((0, 1, 2), (0, 1, 3), (0, 2, 3), (0, 2, 4)), ((0, 1, 2), (0, 1, 4), (0, 2, 3), (0, 2, 4)), ((0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4))]
	##		print lst
			for j in lst:
				f=flatten(j)
	##			print f
				if [key for key,val in Counter(f).items() if val > 1]==[] and set(f)==set(table_num_1):
##					print '4th start'
					combi_num=list(j)
					
					while True:
						if table_num[0] in combi_num[0] or table_num[-1] in combi_num[3]:
							random.shuffle(combi_num)
						else:
							break
					
					for j in combi_num[0]:
						combi_weight_a.append(table_weight[j])
					for j in combi_num[1]:
						combi_weight_b.append(table_weight[j])
					for j in combi_num[2]:
						combi_weight_c.append(table_weight[j])
					for j in combi_num[3]:
						combi_weight_d.append(table_weight[j])

					if sum(combi_weight_a)<setting[19] or sum(combi_weight_a)>setting[18]:
						error_count+=1
					if sum(combi_weight_b)<setting[19] or sum(combi_weight_b)>setting[18]:
						error_count+=1
					if sum(combi_weight_c)<setting[19] or sum(combi_weight_c)>setting[18]:
						error_count+=1
					if sum(combi_weight_d)<setting[19] or sum(combi_weight_d)>setting[18]:
						error_count+=1
					
					if error_count>=1:
						combi_num=[]
						combi_weight_a=[]
						combi_weight_b=[]
						combi_weight_c=[]
						combi_weight_d=[]
						error_count=0
						raise
					else:
						spare_num_a=combi_num[0]
						spare_num_b=map(lambda n:n+1,combi_num[1])
						spare_num_c=map(lambda n:n+2,combi_num[2])
						spare_num_d=map(lambda n:n+3,combi_num[3])
						spare_sumweight_a=sum(combi_weight_a)
						spare_sumweight_b=sum(combi_weight_b)
						spare_sumweight_c=sum(combi_weight_c)
						spare_sumweight_d=sum(combi_weight_d)
						print 'combi'
						print (combi_num)
						print (spare_sumweight_a)
						print (spare_sumweight_b)
						print (spare_sumweight_c)
						print (spare_sumweight_d)
						today_weight+=(spare_sumweight_a+spare_sumweight_b+spare_sumweight_c+spare_sumweight_d)/1000
						today_qty+=4
					break
			else:
				continue
			break

	except:
##		print '3rd start'		
		for h in (8,15,25,40):
			lst=list(combinations(allcombi_order[:h],3))	#lst=[((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3)), ((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 4)), ((0, 1, 2), (0, 1, 3), (0, 2, 3), (0, 2, 4)), ((0, 1, 2), (0, 1, 4), (0, 2, 3), (0, 2, 4)), ((0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4))]
	##		print lst
			for j in lst:
				f=flatten(j)
	##			print f
				if [key for key,val in Counter(f).items() if val > 1]==[]:
					break
			else:
				continue
			break
		combi_num=list(j)

		while True:
			if table_num[0] in combi_num[0]:
				random.shuffle(combi_num)
			else:
				break
		
		for j in combi_num[0]:
			combi_weight_a.append(table_weight[j])
		for j in combi_num[1]:
			combi_weight_b.append(table_weight[j])
		for j in combi_num[2]:
			combi_weight_c.append(table_weight[j])

		if sum(combi_weight_a)<setting[19] or sum(combi_weight_a)>setting[18]:
			error_count+=1
		if sum(combi_weight_b)<setting[19] or sum(combi_weight_b)>setting[18]:
			error_count+=1
		if sum(combi_weight_c)<setting[19] or sum(combi_weight_c)>setting[18]:
			error_count+=1
		
		if error_count>=1:
			combi_num=[]
			combi_weight_a=[]
			combi_weight_b=[]
			combi_weight_c=[]
			error_count=0
##			print '2nd start'
			for h in (8,15,25,40):
				lst=list(combinations(allcombi_order[:h],2))	#lst=[((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3)), ((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 4)), ((0, 1, 2), (0, 1, 3), (0, 2, 3), (0, 2, 4)), ((0, 1, 2), (0, 1, 4), (0, 2, 3), (0, 2, 4)), ((0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4))]
		##		print lst
				for j in lst:
					f=flatten(j)
		##			print f
					if [key for key,val in Counter(f).items() if val > 1]==[]:
						break
				else:
					continue
				break
			combi_num=list(j)
			
			for j in combi_num[0]:
				combi_weight_a.append(table_weight[j])
			for j in combi_num[1]:
				combi_weight_b.append(table_weight[j])

			if sum(combi_weight_a)<setting[19] or sum(combi_weight_a)>setting[18]:
				error_count+=1
			if sum(combi_weight_b)<setting[19] or sum(combi_weight_b)>setting[18]:
				error_count+=1
			spare_num_a=combi_num[0]
			spare_num_b=map(lambda n:n+1,combi_num[1])
			spare_num_c=[]
			spare_num_d=[]
			spare_sumweight_a=sum(combi_weight_a)
			spare_sumweight_b=sum(combi_weight_b)
			spare_sumweight_c=0
			spare_sumweight_d=0
			print 'combi'
			print (combi_num)
			print (spare_sumweight_a)
			print (spare_sumweight_b)
			today_weight+=(spare_sumweight_a+spare_sumweight_b)/1000
			today_qty+=2

		else:
			spare_num_a=combi_num[0]
			spare_num_b=map(lambda n:n+1,combi_num[1])
			spare_num_c=map(lambda n:n+2,combi_num[2])
			spare_num_d=[]
			spare_sumweight_a=sum(combi_weight_a)
			spare_sumweight_b=sum(combi_weight_b)
			spare_sumweight_c=sum(combi_weight_c)
			spare_sumweight_d=0
			
			print 'combi'
			print (combi_num)
##			print 'spare_num_d'
##			print (spare_num_d)
			print (spare_sumweight_a)
			print (spare_sumweight_b)
			print (spare_sumweight_c)
			
			today_weight+=(spare_sumweight_a+spare_sumweight_b+spare_sumweight_c)/1000
			today_qty+=3


##	#組み合わせ失敗の場合は、番号割り当てないだけ
##	if sum(combi_weight_a_total)<parameter[3] or sum(combi_weight_a_total)>parameter[2]:
##		table_num.remove(0)
##		map(lambda n:n-1, table_num)
##		table_weight.remove(table_weight[0])
##

###------重量測定-----    #comment out for try

##
### MCP3208からSPI通信で12ビットのデジタル値を取得。0から7の8チャンネル使用可
##def readadc(adcnum, clockpin, mosipin, misopin, cspin):
##    if adcnum > 7 or adcnum < 0:
##        return -1
##    GPIO.output(cspin, GPIO.HIGH)
##    GPIO.output(clockpin, GPIO.LOW)
##    GPIO.output(cspin, GPIO.LOW)
##
##    commandout = adcnum
##    commandout |= 0x18  # スタートビット＋シングルエンドビット
##    commandout <<= 3    # LSBから8ビット目を送信するようにする
##    for i in range(5):
##        # LSBから数えて8ビット目から4ビット目までを送信
##        if commandout & 0x80:
##            GPIO.output(mosipin, GPIO.HIGH)
##        else:
##            GPIO.output(mosipin, GPIO.LOW)
##        commandout <<= 1
##        GPIO.output(clockpin, GPIO.HIGH)
##        GPIO.output(clockpin, GPIO.LOW)
##    adcout = 0
##    # 13ビット読む（ヌルビット＋12ビットデータ）
##    for i in range(13):
##        GPIO.output(clockpin, GPIO.HIGH)
##        GPIO.output(clockpin, GPIO.LOW)
##        adcout <<= 1
##        if i>0 and GPIO.input(misopin)==GPIO.HIGH:
##            adcout |= 0x1
##    GPIO.output(cspin, GPIO.HIGH)
##    return adcout
##
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
##inputVal0 = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)
sum1=0
weight=0.00
a=1
b=0
def measure(i):
	global weight
	global setting
	weight=110.5-random.uniform(1,20)-setting[i]
##	for j in range(1000):
##		inputVal0 = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)
##		sum1+=inputVal0
##	weight=(a*sum1/1000+b)-setting[i]########ここに係数,定数をかける。caliblationの値を引き算する。
####try:
####    while True:
####        inputVal0 = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)
####        print(inputVal0)
####        sleep(0.0001)
##



def calibration():
	global a
	global b
	global sum1
	global setting
	global table_code
	
	pass
	f = file('set.dump', 'w')
	for i in range(16):
		for j in range(1000):
			inputVal0 = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)
			sum1+=inputVal0
		setting[i]=a*sum1/1000+b
		rotate_moter()#for文の下に持ってくれば、最後の位置は0になる。
	pickle.dump(setting, f)
	f.close()
	table_code=0

#------回転------

def senbetu_rotate():
	global weight
	global senbetu_discharge_list_a
	global senbetu_discharge_list_b
	global senbetu_discharge_list_c
	global senbetu_discharge_list_d	
	
	#print "回転"
##	weight=random.gauss(102.5,25)#トライ用のコード。テーブルにワークが乗っかったと仮定。

	# 先頭に追加
	y_plot.insert(0, weight)
	del y_plot[1]
	table_weight.append(weight)
	
	if setting[20]<weight and weight<setting[21]:
		senbetu_discharge_list_a.append[9]
	if setting[21]<weight and weight<setting[22]:
		senbetu_discharge_list_b.append[10]
	if setting[22]<weight and weight<setting[23]:
		senbetu_discharge_list_c.append[11]
	if setting[23]<weight and weight<setting[24]:
		senbetu_discharge_list_d.append[12]

	#rotateしたらlistをすべて-1する。
	senbetu_discharge_list_a=map(lambda n:n-1, senbetu_discharge_list_a)
	senbetu_discharge_list_b=map(lambda n:n-1, senbetu_discharge_list_b)
	senbetu_discharge_list_c=map(lambda n:n-1, senbetu_discharge_list_c)
	senbetu_discharge_list_d=map(lambda n:n-1, senbetu_discharge_list_d)

##	print(discharge_i)
	#先頭が0だったらdischarge
	if len(senbetu_discharge_list_a)>0:
		if senbetu_discharge_list_a[0]==0:
			discharge_a()
			print "a排出"
			discharge_list_a.remove(0)#0を消す
	if len(senbetu_discharge_list_b)>0:
		if senbetu_discharge_list_b[0]==0:
			discharge_b()
			print "b排出"
			discharge_list_b.remove(0)
	if len(senbetu_discharge_list_c)>0:
		if senbetu_discharge_list_c[0]==0:
			discharge_c()
			print "c排出"
			discharge_list_c.remove(0)
	if len(senbetu_discharge_list_d)>0:
		if senbetu_discharge_list_d[0]==0:
			discharge_d()
			print "d排出"
			discharge_list_d.remove(0)


def rotate():
##	global discharge_a_offset
##	global discharge_b_offset
##	global discharge_c_offset
##	global discharge_d_offset
	global table_num
	global table_weight
	global discharge_list_a
	global discharge_list_b
	global discharge_list_c
	global discharge_list_d
	global spare_num_a
	global spare_num_b
	global spare_num_c
	global spare_num_d
	global spare_sumweight_a
	global spare_sumweight_b
	global spare_sumweight_c
	global spare_sumweight_d
	global count
	global spare_i
	global discharge_i
	global numbering
	global final_sumweight_a
	global final_sumweight_b
	global final_sumweight_c
	global final_sumweight_d
	
	#print "回転"
	table_num.append(i)
##	weight=random.gauss(102.5,25)#トライ用のコード。テーブルにワークが乗っかったと仮定。

	# 先頭に追加
	y_plot.insert(0, weight)
	del y_plot[1]
	
	time.sleep(1)#トライ用のコード。次のテーブルまでを表現
	table_weight.append(weight)

	#rotateしたらlistをすべて-1する。
	discharge_list_a=map(lambda n:n-1, discharge_list_a)
	discharge_list_b=map(lambda n:n-1, discharge_list_b)
	discharge_list_c=map(lambda n:n-1, discharge_list_c)
	discharge_list_d=map(lambda n:n-1, discharge_list_d)
	discharge_i-=1

##	print(discharge_i)
	#先頭が0だったらdischarge
	if len(discharge_list_a)>0:
		if discharge_list_a[0]==0:
##			#位置をずらして排出させることで山盛りになるのを防ぐ
##			if discharge_a_offset is True:
##				sleep(1)
			discharge_a()
			print "a排出"
			print (numbering+1)
			discharge_list_a.remove(0)#0を消す
##			#排出位置を交互にずらす
##			discharge_a_offset=not(discharge_a_offset)
	#	print "a排出"
	if len(discharge_list_b)>0:
		if discharge_list_b[0]==0:
			discharge_b()
			print "b排出"
			print (numbering)
			discharge_list_b.remove(0)
	if len(discharge_list_c)>0:
		if discharge_list_c[0]==0:
			discharge_c()
			print "c排出"
			print (numbering-1)
			discharge_list_c.remove(0)
	if len(discharge_list_d)>0:
		if discharge_list_d[0]==0:
			discharge_d()
			print "d排出"
			print (numbering-2)
			discharge_list_d.remove(0)

	numbering+=1
	
	#リストがなくなったらstop、袋詰後スイッチを押してstart
	if discharge_i==0:
##		if discharge_list_a==[] and discharge_list_b==[] and discharge_list_c==[] and discharge_list_d==[]:
		discharge_list_a=spare_num_a
		discharge_list_b=spare_num_b
		discharge_list_c=spare_num_c
		discharge_list_d=spare_num_d
		discharge_i=spare_i
		numbering=0
##			print(discharge_list_a)
##			print(discharge_list_b)
##			print(discharge_list_c)
##			print(discharge_list_d)
##			print(spare_sumweight_a)
##			print(spare_sumweight_b)
##			print(spare_sumweight_c)
##			print(spare_sumweight_d)
		final_sumweight_a=spare_sumweight_a
		final_sumweight_b=spare_sumweight_b
		final_sumweight_c=spare_sumweight_c
		final_sumweight_d=spare_sumweight_d
##		#switch on になるまでストップしている
##		GPIO.wait_for_edge(4, GPIO.RISING) #comment out for try
##		break



#------main------

class MyApp(wx.App):
	def OnInit(self):
		def spin_value_change(event):
			obj = event.GetEventObject()
			self.TxtCtl_23.SetValue(str(obj.GetValue()/10))
			f = file('set.dump', 'w')
			setting[0]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()
		def spin_value_change_1(event):
			obj = event.GetEventObject()
			self.TxtCtl_24.SetValue(str(obj.GetValue()))
			f = file('set.dump', 'w')
			setting[17]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()
		def spin_value_change_2(event):
			obj = event.GetEventObject()
			self.TxtCtl_25.SetValue(str(obj.GetValue()))
			f = file('set.dump', 'w')
			setting[18]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()
		def spin_value_change_3(event):
			obj = event.GetEventObject()
			self.TxtCtl_26.SetValue(str(obj.GetValue()))
			f = file('set.dump', 'w')
			setting[19]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()

		self.stop_event = threading.Event() #停止させるかのフラグ
			
		#フレーム
		width, height = 720, 400
		self.Frm = wx.Frame(None, -1,  u"計算式秤 v1",pos=(5,5), size=wx.Size(width, height))

		#タブ
##		self.notebook = fnb.FlatNotebook(self.Frm, wx.ID_ANY, agwStyle=fnb.FNB_X_ON_TAB |
##						 fnb.FNB_NO_X_BUTTON)
		self.notebook = wx.Notebook(self.Frm, wx.ID_ANY)

		#各タブのパネルの設定
		self.panel_juryo = wx.Panel(self.notebook, wx.ID_ANY)
		self.panel_senbetu = wx.Panel(self.notebook, wx.ID_ANY)

		#各パネルの色設定
		self.panel_juryo.SetBackgroundColour("#fff9d3")
		self.panel_senbetu.SetBackgroundColour("#d3fff0")

		#タブの文字
		self.notebook.InsertPage(0, self.panel_juryo, u"重量")
		self.notebook.InsertPage(1, self.panel_senbetu, u"選別")

		#重量モード
		#設定欄のテキスト
		self.s_text_1 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"停止(秒)",size=(105,30),style=wx.TE_LEFT)
		self.s_text_2 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"平均重量(g)")
		self.s_text_3 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"上限重量(g)")
		self.s_text_4 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"下限重量(g)")
		#設定欄のスピンボタン
		g = file('set.dump', 'r')
		setting = pickle.load(g)
		self.spinbutton_1 = wx.SpinButton(self.panel_juryo, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.spinbutton_1.SetValue(setting[0])
		self.spinbutton_1.SetMin(0)
		self.spinbutton_1.SetMax(300)
		self.spinbutton_1.Bind(wx.EVT_SPIN, spin_value_change)
		self.spinbutton_2 = wx.SpinButton(self.panel_juryo, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.spinbutton_2.SetValue(setting[17])
		self.spinbutton_2.SetMin(0)
		self.spinbutton_2.SetMax(1000)
		self.spinbutton_2.Bind(wx.EVT_SPIN, spin_value_change_1)
		self.spinbutton_3 = wx.SpinButton(self.panel_juryo, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.spinbutton_3.SetValue(setting[18])
		self.spinbutton_3.SetMin(0)
		self.spinbutton_3.SetMax(1000)
		self.spinbutton_3.Bind(wx.EVT_SPIN, spin_value_change_2)
		self.spinbutton_4 = wx.SpinButton(self.panel_juryo, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.spinbutton_4.SetValue(setting[19])
		self.spinbutton_4.SetMin(0)
		self.spinbutton_4.SetMax(1000)
		self.spinbutton_4.Bind(wx.EVT_SPIN, spin_value_change_3)
		g.close()
		#開始、停止ボタン
		self.Btn1 = wx.Button(self.panel_juryo, -1, u"開始", size=(150,30))
		self.Btn2 = wx.Button(self.panel_juryo, -1, u"停止", size=(150,30))
		self.Btn1.Bind(wx.EVT_BUTTON, self.JuryoStart)
		self.Btn2.Bind(wx.EVT_BUTTON, self.JuryoStop)
		#記録欄のテキスト
		element_array_1 = ("",u"17年", u"18年", u"19年", u"20年", u"21年", u"22年", u"23年", u"24年", u"25年", u"26年")
		self.combobox_1 = wx.ComboBox(self.panel_juryo, wx.ID_ANY, u"年", choices=element_array_1, style=wx.CB_DROPDOWN)
		element_array_2 = ("",u"1月", u"2月",u"3月", u"4月",u"5月", u"6月",u"7月", u"8月",u"9月", u"10月",u"11月", u"12月")
		self.combobox_2 = wx.ComboBox(self.panel_juryo, wx.ID_ANY, u"月", choices=element_array_2, style=wx.CB_DROPDOWN)
		element_array_3 = ("",u"1日", u"2日",u"3日", u"4日",u"5日", u"6日",u"7日", u"8日",u"9日", u"10日",u"11日", u"12日",u"13日", u"14日",u"15日", u"16日",u"17日", u"18日",u"19日", u"20日",u"21日", u"22日",u"23日", u"24日",u"25日", u"26日",u"27日", u"28日",u"29日", u"30日", u"31日")
		self.combobox_3 = wx.ComboBox(self.panel_juryo, wx.ID_ANY, u"日", choices=element_array_3, style=wx.CB_DROPDOWN)
		self.s_text_5 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"生産数(袋数)")
		self.TxtCtl_6 = wx.TextCtrl(self.panel_juryo, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.TxtCtl_6.SetBackgroundColour("#d3fff0")
		self.s_text_7 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"生産量(kg)")
		self.TxtCtl_8 = wx.TextCtrl(self.panel_juryo, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.TxtCtl_8.SetBackgroundColour("#d3fff0")
		self.s_text_9 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"平均重量(g/袋)")
		self.TxtCtl_10 = wx.TextCtrl(self.panel_juryo, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.TxtCtl_10.SetBackgroundColour("#d3fff0")
		self.s_text_11 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"作業時間")
		self.TxtCtl_12 = wx.TextCtrl(self.panel_juryo, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.TxtCtl_12.SetBackgroundColour("#d3fff0")
		self.s_text_13 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"作業時間(秒/袋)")
		self.TxtCtl_14 = wx.TextCtrl(self.panel_juryo, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.TxtCtl_14.SetBackgroundColour("#d3fff0")
		self.s_text_15 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"作業コスト(円/袋)")
		self.TxtCtl_16 = wx.TextCtrl(self.panel_juryo, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.TxtCtl_16.SetBackgroundColour("#d3fff0")
		self.s_text_17 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"重量コスト(円/袋)")
		self.TxtCtl_18 = wx.TextCtrl(self.panel_juryo, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.TxtCtl_18.SetBackgroundColour("#d3fff0")
		self.s_text_19 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"日付")
		self.s_text_21 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"備考")
		self.TxtCtl_22 = wx.TextCtrl(self.panel_juryo, -1, u"じゃがいも", size=(150,-1),style=wx.TE_LEFT)
		self.s_text_27 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"市場価格(kg)")
		self.TxtCtl_28 = wx.TextCtrl(self.panel_juryo, -1, "500", size=(150,-1),style=wx.TE_LEFT)
		self.s_text_29 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"人件費(円)")
		self.TxtCtl_30 = wx.TextCtrl(self.panel_juryo, -1, "800", size=(150,-1),style=wx.TE_LEFT)
		self.s_text_31 = wx.StaticText(self.panel_juryo, wx.ID_ANY, u"作業者数(人)")
		self.TxtCtl_32 = wx.TextCtrl(self.panel_juryo, -1, "1", size=(150,-1),style=wx.TE_LEFT)
		#エクセルに書き込むボタン
		self.Btn22 = wx.Button(self.panel_juryo, -1, u"保存＆リセット", size=(300,30))
		self.Btn22.Bind(wx.EVT_BUTTON, self.JuryoReset)
		self.TxtCtl_23 = wx.TextCtrl(self.panel_juryo, -1, str(float(setting[0]/10)), size=(90,-1),style=wx.TE_LEFT)
		self.TxtCtl_24 = wx.TextCtrl(self.panel_juryo, -1, str(setting[17]), size=(90,-1),style=wx.TE_LEFT)
		self.TxtCtl_25 = wx.TextCtrl(self.panel_juryo, -1, str(setting[18]), size=(90,-1),style=wx.TE_LEFT)
		self.TxtCtl_26 = wx.TextCtrl(self.panel_juryo, -1, str(setting[19]), size=(90,-1),style=wx.TE_LEFT)
		self.s_text_white_6= wx.StaticText(self.panel_juryo, wx.ID_ANY, "")
		g = file('log.dump', 'r')
		parametor = pickle.load(g)
		g.close()

		#フォント
		self.font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.s_text_5.SetFont(self.font)
		self.TxtCtl_6.SetFont(self.font)
		self.s_text_7.SetFont(self.font)
		self.TxtCtl_8.SetFont(self.font)
		self.s_text_9.SetFont(self.font)
		self.TxtCtl_10.SetFont(self.font)
		self.s_text_11.SetFont(self.font)
		self.TxtCtl_12.SetFont(self.font)
		self.s_text_13.SetFont(self.font)
		self.TxtCtl_14.SetFont(self.font)
		self.s_text_15.SetFont(self.font)
		self.TxtCtl_16.SetFont(self.font)
		self.s_text_17.SetFont(self.font)
		self.TxtCtl_18.SetFont(self.font)
		self.s_text_19.SetFont(self.font)
		self.s_text_21.SetFont(self.font)
		self.TxtCtl_22.SetFont(self.font)
		self.Btn22.SetFont(self.font)
		self.Btn1.SetFont(self.font)
		self.Btn2.SetFont(self.font)
		self.notebook.SetFont(self.font)
		self.s_text_1.SetFont(self.font)
		self.s_text_2.SetFont(self.font)
		self.s_text_3.SetFont(self.font)
		self.s_text_4.SetFont(self.font)
		self.TxtCtl_23.SetFont(self.font)
		self.TxtCtl_24.SetFont(self.font)
		self.TxtCtl_25.SetFont(self.font)
		self.TxtCtl_26.SetFont(self.font)
		self.s_text_27.SetFont(self.font)
		self.TxtCtl_28.SetFont(self.font)
		self.s_text_29.SetFont(self.font)
		self.TxtCtl_30.SetFont(self.font)
		self.s_text_31.SetFont(self.font)
		self.TxtCtl_32.SetFont(self.font)
		self.font_1 = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.combobox_1.SetFont(self.font_1)
		self.combobox_2.SetFont(self.font_1)
		self.combobox_3.SetFont(self.font_1)
		
		#レイアウト
		self.layout_1 = wx.BoxSizer(wx.VERTICAL)
		self.layout_1_1 = wx.GridSizer(1, 2)
		self.layout_1_1.Add(self.Btn1, flag=wx.SHAPED | wx.ALIGN_CENTER)
		self.layout_1_1.Add(self.Btn2, flag=wx.SHAPED | wx.ALIGN_CENTER)
		self.layout_1_2 = wx.GridSizer(4,3)
		self.layout_1_2.Add(self.s_text_1)
		self.layout_1_2.Add(self.TxtCtl_23)
		self.layout_1_2.Add(self.spinbutton_1)
		self.layout_1_2.Add(self.s_text_2)
		self.layout_1_2.Add(self.TxtCtl_24)
		self.layout_1_2.Add(self.spinbutton_2)
		self.layout_1_2.Add(self.s_text_3)
		self.layout_1_2.Add(self.TxtCtl_25)
		self.layout_1_2.Add(self.spinbutton_3)
		self.layout_1_2.Add(self.s_text_4)
		self.layout_1_2.Add(self.TxtCtl_26)
		self.layout_1_2.Add(self.spinbutton_4)
		self.layout_1_3= wx.GridSizer(3,2)
		self.layout_1_3.Add(self.s_text_27)
		self.layout_1_3.Add(self.TxtCtl_28)
		self.layout_1_3.Add(self.s_text_29)
		self.layout_1_3.Add(self.TxtCtl_30)
		self.layout_1_3.Add(self.s_text_31)
		self.layout_1_3.Add(self.TxtCtl_32)
		self.layout_1.Add(self.layout_1_1)
		self.layout_1.Add(self.layout_1_2)
		self.layout_1.Add(self.layout_1_3)
		
		self.layout_3 = wx.BoxSizer(wx.VERTICAL)
		self.layout_3_1 = wx.GridSizer(1, 5)
		self.layout_3_1.Add(self.s_text_19)
		self.layout_3_1.Add(self.s_text_white_6)
		self.layout_3_1.Add(self.combobox_1)
		self.layout_3_1.Add(self.combobox_2)
		self.layout_3_1.Add(self.combobox_3)
		self.layout_3_2 = wx.GridSizer(8, 2)
		self.layout_3_2.Add(self.s_text_5)
		self.layout_3_2.Add(self.TxtCtl_6)
		self.layout_3_2.Add(self.s_text_7)
		self.layout_3_2.Add(self.TxtCtl_8)
		self.layout_3_2.Add(self.s_text_9)
		self.layout_3_2.Add(self.TxtCtl_10)
		self.layout_3_2.Add(self.s_text_11)
		self.layout_3_2.Add(self.TxtCtl_12)
		self.layout_3_2.Add(self.s_text_13)
		self.layout_3_2.Add(self.TxtCtl_14)
		self.layout_3_2.Add(self.s_text_15)
		self.layout_3_2.Add(self.TxtCtl_16)
		self.layout_3_2.Add(self.s_text_17)
		self.layout_3_2.Add(self.TxtCtl_18)
		self.layout_3_2.Add(self.s_text_21)
		self.layout_3_2.Add(self.TxtCtl_22)
		self.layout_3_3 = wx.GridSizer(1, 1)
		self.layout_3_3.Add(self.Btn22)
		self.layout_3.Add(self.layout_3_1)
		self.layout_3.Add(self.layout_3_2)
		self.layout_3.Add(self.layout_3_3)
		self.layout_1_3= wx.BoxSizer(wx.HORIZONTAL)
		self.layout_1_3.Add(self.layout_1, 0, flag=wx.EXPAND | wx.ALL,   border=10)
		self.layout_1_3.Add(self.layout_3, 1, flag=wx.EXPAND | wx.ALL,   border=10)
		self.panel_juryo.SetSizer(self.layout_1_3)

#################################################################################
		#選別モード
		#設定欄のテキスト
		def spin_value_change_senbetu(event):
			obj = event.GetEventObject()
			self.senbetu_TxtCtl_23.SetValue(str(obj.GetValue()))
			f = file('set.dump', 'w')
			setting[20]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()
		def spin_value_change_senbetu_1(event):
			obj = event.GetEventObject()
			self.senbetu_TxtCtl_24.SetValue(str(obj.GetValue()))
			f = file('set.dump', 'w')
			setting[21]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()
		def spin_value_change_senbetu_2(event):
			obj = event.GetEventObject()
			self.senbetu_TxtCtl_25.SetValue(str(obj.GetValue()))
			f = file('set.dump', 'w')
			setting[22]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()
		def spin_value_change_senbetu_3(event):
			obj = event.GetEventObject()
			self.senbetu_TxtCtl_26.SetValue(str(obj.GetValue()))
			f = file('set.dump', 'w')
			setting[23]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()
		def spin_value_change_senbetu_4(event):
			obj = event.GetEventObject()
			self.senbetu_TxtCtl_27.SetValue(str(obj.GetValue()))
			f = file('set.dump', 'w')
			setting[24]=obj.GetValue()
			pickle.dump(setting, f)
			f.close()	
		self.senbetu_s_text_0 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"規格")
		self.senbetu_s_text_1 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"重量範囲(g)")
		self.senbetu_s_text_S = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"S")
		self.senbetu_s_text_M = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"M")
		self.senbetu_s_text_L = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"L")
		self.senbetu_s_text_2L = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"2L")
		#設定欄のスピンボタン
		g = file('set.dump', 'r')
		setting = pickle.load(g)
		self.senbetu_spinbutton_1 = wx.SpinButton(self.panel_senbetu, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.senbetu_spinbutton_1.SetValue(setting[20])
		self.senbetu_spinbutton_1.SetMin(0)
		self.senbetu_spinbutton_1.SetMax(1000)
		self.senbetu_spinbutton_1.Bind(wx.EVT_SPIN, spin_value_change_senbetu)
		self.senbetu_spinbutton_2 = wx.SpinButton(self.panel_senbetu, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.senbetu_spinbutton_2.SetValue(setting[21])
		self.senbetu_spinbutton_2.SetMin(0)
		self.senbetu_spinbutton_2.SetMax(1000)
		self.senbetu_spinbutton_2.Bind(wx.EVT_SPIN, spin_value_change_senbetu_1)
		self.senbetu_spinbutton_3 = wx.SpinButton(self.panel_senbetu, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.senbetu_spinbutton_3.SetValue(setting[22])
		self.senbetu_spinbutton_3.SetMin(0)
		self.senbetu_spinbutton_3.SetMax(1000)
		self.senbetu_spinbutton_3.Bind(wx.EVT_SPIN, spin_value_change_senbetu_2)
		self.senbetu_spinbutton_4 = wx.SpinButton(self.panel_senbetu, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.senbetu_spinbutton_4.SetValue(setting[23])
		self.senbetu_spinbutton_4.SetMin(0)
		self.senbetu_spinbutton_4.SetMax(1000)
		self.senbetu_spinbutton_4.Bind(wx.EVT_SPIN, spin_value_change_senbetu_3)
		self.senbetu_spinbutton_5 = wx.SpinButton(self.panel_senbetu, wx.ID_ANY,size=(90,30), style=wx.SP_HORIZONTAL)
		self.senbetu_spinbutton_5.SetValue(setting[24])
		self.senbetu_spinbutton_5.SetMin(0)
		self.senbetu_spinbutton_5.SetMax(1000)
		self.senbetu_spinbutton_5.Bind(wx.EVT_SPIN, spin_value_change_senbetu_4)
		g.close()
		#開始、停止ボタン
		self.senbetu_Btn1 = wx.Button(self.panel_senbetu, -1, u"開始", size=(150,30))
		self.senbetu_Btn2 = wx.Button(self.panel_senbetu, -1, u"停止", size=(150,30))
		self.senbetu_Btn1.Bind(wx.EVT_BUTTON, self.SenbetuStart)
		self.senbetu_Btn2.Bind(wx.EVT_BUTTON, self.SenbetuStop)
		#記録欄のテキスト
		senbetu_element_array_1  = ("",u"17年", u"18年", u"19年", u"20年", u"21年", u"22年", u"23年", u"24年", u"25年", u"26年")
		self.senbetu_combobox_1 = wx.ComboBox(self.panel_senbetu, wx.ID_ANY, u"年", choices=element_array_1, style=wx.CB_DROPDOWN)
		senbetu_element_array_2 = ("",u"1月", u"2月",u"3月", u"4月",u"5月", u"6月",u"7月", u"8月",u"9月", u"10月",u"11月", u"12月")
		self.senbetu_combobox_2 = wx.ComboBox(self.panel_senbetu, wx.ID_ANY, u"月", choices=element_array_2, style=wx.CB_DROPDOWN)
		senbetu_element_array_3 = ("",u"1日", u"2日",u"3日", u"4日",u"5日", u"6日",u"7日", u"8日",u"9日", u"10日",u"11日", u"12日",u"13日", u"14日",u"15日", u"16日",u"17日", u"18日",u"19日", u"20日",u"21日", u"22日",u"23日", u"24日",u"25日", u"26日",u"27日", u"28日",u"29日", u"30日", u"31日")
		self.senbetu_combobox_3 = wx.ComboBox(self.panel_senbetu, wx.ID_ANY, u"日", choices=element_array_3, style=wx.CB_DROPDOWN)
		self.senbetu_s_text_3= wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"生産数(個)")
		self.senbetu_TxtCtl_4 = wx.TextCtrl(self.panel_senbetu, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_4.SetBackgroundColour("#d3fff0")
		self.senbetu_s_text_5 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"生産量(kg)")
		self.senbetu_TxtCtl_6 = wx.TextCtrl(self.panel_senbetu, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_6.SetBackgroundColour("#d3fff0")
		self.senbetu_s_text_7 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"平均重量(g/個)")
		self.senbetu_TxtCtl_8 = wx.TextCtrl(self.panel_senbetu, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_8.SetBackgroundColour("#d3fff0")
		self.senbetu_s_text_9 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"作業時間")
		self.senbetu_TxtCtl_10 = wx.TextCtrl(self.panel_senbetu, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_10.SetBackgroundColour("#d3fff0")
		self.senbetu_s_text_11 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"作業時間(秒/kg)")
		self.senbetu_TxtCtl_12 = wx.TextCtrl(self.panel_senbetu, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_12.SetBackgroundColour("#d3fff0")
		self.senbetu_s_text_13 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"作業コスト(円/kg)")
		self.senbetu_TxtCtl_14 = wx.TextCtrl(self.panel_senbetu, -1, "", size=(150,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_14.SetBackgroundColour("#d3fff0")
##		self.senbetu_s_text_15 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"作業コスト(円/袋)")
##		self.senbetu_TxtCtl_16 = wx.TextCtrl(self.panel_senbetu, -1, "", size=(150,-1),style=wx.TE_LEFT)
##		self.senbetu_TxtCtl_16.SetBackgroundColour("#d3fff0")
##		self.senbetu_s_text_17 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"作業時間")
##		self.senbetu_TxtCtl_18 = wx.TextCtrl(self.panel_senbetu, -1, "", size=(150,-1),style=wx.TE_LEFT)
##		self.senbetu_TxtCtl_18.SetBackgroundColour("#d3fff0")
		self.senbetu_s_text_19 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"日付")
		self.senbetu_s_text_21 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"備考")
		self.senbetu_TxtCtl_22 = wx.TextCtrl(self.panel_senbetu, -1, u"じゃがいも", size=(150,-1),style=wx.TE_LEFT)
		self.senbetu_s_text_27 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"人件費(円)")
		self.senbetu_TxtCtl_28 = wx.TextCtrl(self.panel_senbetu, -1, "500", size=(150,-1),style=wx.TE_LEFT)
		self.senbetu_s_text_29 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"作業者数(人)")
		self.senbetu_TxtCtl_30 = wx.TextCtrl(self.panel_senbetu, -1, "800", size=(150,-1),style=wx.TE_LEFT)
##		self.senbetu_s_text_31 = wx.StaticText(self.panel_senbetu, wx.ID_ANY, u"作業者数(人)")
##		self.senbetu_TxtCtl_32 = wx.TextCtrl(self.panel_senbetu, -1, "1", size=(150,-1),style=wx.TE_LEFT)
		#エクセルに書き込むボタン
		self.senbetu_Btn22 = wx.Button(self.panel_senbetu, -1, u"保存＆リセット", size=(300,30))
		self.senbetu_Btn22.Bind(wx.EVT_BUTTON, self.SenbetuReset)
		self.senbetu_TxtCtl_23 = wx.TextCtrl(self.panel_senbetu, -1, str(setting[20]), size=(90,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_24 = wx.TextCtrl(self.panel_senbetu, -1, str(setting[21]), size=(90,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_25 = wx.TextCtrl(self.panel_senbetu, -1, str(setting[22]), size=(90,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_26 = wx.TextCtrl(self.panel_senbetu, -1, str(setting[23]), size=(90,-1),style=wx.TE_LEFT)
		self.senbetu_TxtCtl_27 = wx.TextCtrl(self.panel_senbetu, -1, str(setting[24]), size=(90,-1),style=wx.TE_LEFT)
		self.senbetu_s_text_white_6= wx.StaticText(self.panel_senbetu, wx.ID_ANY, "")
		self.senbetu_s_text_white_7= wx.StaticText(self.panel_senbetu, wx.ID_ANY, "")
		self.senbetu_s_text_white_8= wx.StaticText(self.panel_senbetu, wx.ID_ANY, "")
		g = file('log.dump', 'r')
		parametor = pickle.load(g)
		g.close()

		#フォント
		self.senbetu_s_text_3.SetFont(self.font)
		self.senbetu_TxtCtl_4.SetFont(self.font)
		self.senbetu_s_text_5.SetFont(self.font)
		self.senbetu_TxtCtl_6.SetFont(self.font)
		self.senbetu_s_text_7.SetFont(self.font)
		self.senbetu_TxtCtl_8.SetFont(self.font)
		self.senbetu_s_text_9.SetFont(self.font)
		self.senbetu_TxtCtl_10.SetFont(self.font)
		self.senbetu_s_text_11.SetFont(self.font)
		self.senbetu_TxtCtl_12.SetFont(self.font)
		self.senbetu_s_text_13.SetFont(self.font)
		self.senbetu_TxtCtl_14.SetFont(self.font)
##		self.senbetu_s_text_15.SetFont(self.font)
##		self.senbetu_TxtCtl_16.SetFont(self.font)
##		self.senbetu_s_text_17.SetFont(self.font)
##		self.senbetu_TxtCtl_18.SetFont(self.font)
		self.senbetu_s_text_19.SetFont(self.font)
		self.senbetu_s_text_21.SetFont(self.font)
		self.senbetu_TxtCtl_22.SetFont(self.font)
		self.senbetu_Btn22.SetFont(self.font)
		self.senbetu_Btn1.SetFont(self.font)
		self.senbetu_Btn2.SetFont(self.font)
		self.senbetu_s_text_0.SetFont(self.font)
		self.senbetu_s_text_1.SetFont(self.font)
		self.senbetu_s_text_S.SetFont(self.font)
		self.senbetu_s_text_M.SetFont(self.font)
		self.senbetu_s_text_L.SetFont(self.font)
		self.senbetu_s_text_2L.SetFont(self.font)
		self.senbetu_TxtCtl_23.SetFont(self.font)
		self.senbetu_TxtCtl_24.SetFont(self.font)
		self.senbetu_TxtCtl_25.SetFont(self.font)
		self.senbetu_TxtCtl_26.SetFont(self.font)
		self.senbetu_TxtCtl_27.SetFont(self.font)
		self.senbetu_s_text_27.SetFont(self.font)
		self.senbetu_TxtCtl_28.SetFont(self.font)
		self.senbetu_s_text_29.SetFont(self.font)
		self.senbetu_TxtCtl_30.SetFont(self.font)
##		self.senbetu_s_text_31.SetFont(self.font)
##		self.senbetu_TxtCtl_32.SetFont(self.font)

		self.senbetu_combobox_1.SetFont(self.font_1)
		self.senbetu_combobox_2.SetFont(self.font_1)
		self.senbetu_combobox_3.SetFont(self.font_1)
		
		#レイアウト
		self.senbetu_layout_1 = wx.BoxSizer(wx.VERTICAL)
		self.senbetu_layout_1_1 = wx.GridSizer(1, 2)
		self.senbetu_layout_1_1.Add(self.senbetu_Btn1, flag=wx.SHAPED | wx.ALIGN_CENTER)
		self.senbetu_layout_1_1.Add(self.senbetu_Btn2, flag=wx.SHAPED | wx.ALIGN_CENTER)
		self.senbetu_layout_1_2 = wx.GridSizer(6,3)
		self.senbetu_layout_1_2.Add(self.senbetu_s_text_0)
		self.senbetu_layout_1_2.Add(self.senbetu_s_text_1)
		self.senbetu_layout_1_2.Add(self.senbetu_s_text_white_7)
		self.senbetu_layout_1_2.Add(self.senbetu_s_text_white_8)
		self.senbetu_layout_1_2.Add(self.senbetu_TxtCtl_23)
		self.senbetu_layout_1_2.Add(self.senbetu_spinbutton_1)
		self.senbetu_layout_1_2.Add(self.senbetu_s_text_S)
		self.senbetu_layout_1_2.Add(self.senbetu_TxtCtl_24)
		self.senbetu_layout_1_2.Add(self.senbetu_spinbutton_2)
		self.senbetu_layout_1_2.Add(self.senbetu_s_text_M)
		self.senbetu_layout_1_2.Add(self.senbetu_TxtCtl_25)
		self.senbetu_layout_1_2.Add(self.senbetu_spinbutton_3)
		self.senbetu_layout_1_2.Add(self.senbetu_s_text_L)
		self.senbetu_layout_1_2.Add(self.senbetu_TxtCtl_26)
		self.senbetu_layout_1_2.Add(self.senbetu_spinbutton_4)
		self.senbetu_layout_1_2.Add(self.senbetu_s_text_2L)
		self.senbetu_layout_1_2.Add(self.senbetu_TxtCtl_27)
		self.senbetu_layout_1_2.Add(self.senbetu_spinbutton_5)
		self.senbetu_layout_1_3= wx.GridSizer(2,2)
		self.senbetu_layout_1_3.Add(self.senbetu_s_text_27)
		self.senbetu_layout_1_3.Add(self.senbetu_TxtCtl_28)
		self.senbetu_layout_1_3.Add(self.senbetu_s_text_29)
		self.senbetu_layout_1_3.Add(self.senbetu_TxtCtl_30)
##		self.senbetu_layout_1_3.Add(self.senbetu_s_text_31)
##		self.senbetu_layout_1_3.Add(self.senbetu_TxtCtl_32)
		self.senbetu_layout_1.Add(self.senbetu_layout_1_1)
		self.senbetu_layout_1.Add(self.senbetu_layout_1_2)
		self.senbetu_layout_1.Add(self.senbetu_layout_1_3)
		
		self.senbetu_layout_3 = wx.BoxSizer(wx.VERTICAL)
		self.senbetu_layout_3_1 = wx.GridSizer(1, 5)
		self.senbetu_layout_3_1.Add(self.senbetu_s_text_19)
		self.senbetu_layout_3_1.Add(self.senbetu_s_text_white_6)
		self.senbetu_layout_3_1.Add(self.senbetu_combobox_1)
		self.senbetu_layout_3_1.Add(self.senbetu_combobox_2)
		self.senbetu_layout_3_1.Add(self.senbetu_combobox_3)
		self.senbetu_layout_3_2 = wx.GridSizer(7, 2)
		self.senbetu_layout_3_2.Add(self.senbetu_s_text_3)
		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_4)
		self.senbetu_layout_3_2.Add(self.senbetu_s_text_5)
		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_6)
		self.senbetu_layout_3_2.Add(self.senbetu_s_text_7)
		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_8)
		self.senbetu_layout_3_2.Add(self.senbetu_s_text_9)
		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_10)
		self.senbetu_layout_3_2.Add(self.senbetu_s_text_11)
		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_12)
		self.senbetu_layout_3_2.Add(self.senbetu_s_text_13)
		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_14)
##		self.senbetu_layout_3_2.Add(self.senbetu_s_text_15)
##		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_16)
##		self.senbetu_layout_3_2.Add(self.senbetu_s_text_17)
##		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_18)
		self.senbetu_layout_3_2.Add(self.senbetu_s_text_21)
		self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_22)
		self.senbetu_layout_3_3 = wx.GridSizer(1, 1)
		self.senbetu_layout_3_3.Add(self.senbetu_Btn22)
		self.senbetu_layout_3.Add(self.senbetu_layout_3_1)
		self.senbetu_layout_3.Add(self.senbetu_layout_3_2)
		self.senbetu_layout_3.Add(self.senbetu_Btn22)
		self.senbetu_layout_1_3= wx.BoxSizer(wx.HORIZONTAL)
		self.senbetu_layout_1_3.Add(self.senbetu_layout_1, 0, flag=wx.EXPAND | wx.ALL,   border=10)
		self.senbetu_layout_1_3.Add(self.senbetu_layout_3, 1, flag=wx.EXPAND | wx.ALL,   border=10)
		self.panel_senbetu.SetSizer(self.senbetu_layout_1_3)
		self.Frm.Show()		
		self.stop_event.set()
		self.Btn1.Enable()
		self.Btn2.Disable()
		self.senbetu_Btn1.Enable()
		self.senbetu_Btn2.Disable()
		return True
#####################################################################################################	

	def JuryoStart(self, event):
		#メイン
		global table_num
		global table_weight
		global total_weight
		global weight_ave
		global i
		global count
		global final_sumweight_a
		global final_sumweight_b
		global final_sumweight_c
		global final_sumweight_d
		global start_time
		global start_time
		global stock_time
		global today_qty
		global today_weight
		global dt
		global ave_weight
		global working_sec
		global ave_cyecle_time
		global ave_cyecle_cost
		global ave_coverweight_cost
		global setting
		global table_code
		global stop_trigger
		print 'start'
		#senbetuを出来なくする
		self.Btn1.Disable()
		self.Btn2.Enable()
		self.senbetu_Btn1.Disable()
		self.senbetu_Btn2.Disable()
		#ストッパーの解除
		stop_trigger=False
		start_time=datetime.datetime.today()
		final_sumweight=[final_sumweight_a,final_sumweight_b,final_sumweight_c,final_sumweight_d]
		plt.close('all')
		fig = plt.figure(figsize=(4.5, 4.1))
		G = gridspec.GridSpec(1, 20)
		ax1 = fig.add_subplot(G[0,1:6])
		ax2 = fig.add_subplot(G[0,9:])

		lines, = ax1.plot(x_plot, setting[17]/2 ,color="r", marker="o",markersize=20,)
		lines1, = ax1.plot(x_plot, y_plot,color="k", marker="o",markersize=20,)
		lines2, = ax2.plot(x_bar, final_sumweight,color="b", marker="o",markersize=20, linewidth = 0)

		ax1.axis([0.9, 1.1, 0, 200])
		ax1.set_xticklabels([])
		ax1.set_title(u'個別重量')
		ax1.set_ylabel(u'重量(g)')
		ax2.axis([0, 5, 100, 300])
		ax2.set_title(u'組合せ重量')
		
		while True:
			#ストッパーで止める
			if senbetu_stop_trigger==True:
				while True:
					time.sleep(0.5)
					if senbetu_stop_trigger==False:
						break
			table_code+=1
			if table_code==16:
				table_code=0#0に戻す
			rotate_moter()
			measure(table_code)
			rotate()

			
			lines1.set_data(x_plot, y_plot)
			final_sumweight=[final_sumweight_a,final_sumweight_b,final_sumweight_c,final_sumweight_d]
			lines2.set_data(x_bar, final_sumweight)
			plt.pause(.01)
			i+=1
			#dtは作業時間
			dt = datetime.datetime.today()-start_time+stock_time        
			dt1 = str(dt)
			if today_qty>0:
				ave_weight=today_weight*1000/today_qty
			working_sec=dt.seconds
			if today_qty>0:
				ave_cyecle_time=working_sec/today_qty
			ave_cyecle_cost=float(self.TxtCtl_30.GetValue())*float(self.TxtCtl_32.GetValue())/3600*ave_cyecle_time #人件費と作業者数を参照
			if ave_weight>0:
				ave_coverweight_cost=(ave_weight-setting[17])*float(self.TxtCtl_28.GetValue())/1000 #kgあたりの野菜の単価を参照
			#today_qtyなどがtxtctlの欄に表示される(型を少し変更して)
			self.TxtCtl_6.SetValue('%d' % today_qty)
			self.TxtCtl_8.SetValue('%.1f' % today_weight)
			self.TxtCtl_10.SetValue('%.1f' % ave_weight)
			self.TxtCtl_12.SetValue(str(dt1.split('.')[0]))
			self.TxtCtl_14.SetValue('%.1f' % ave_cyecle_time)
			self.TxtCtl_16.SetValue('%.1f' % ave_cyecle_cost)
			self.TxtCtl_18.SetValue('%.1f' % ave_coverweight_cost)

			g = file('log.dump', 'r')
			# ファイルオブジェクトに対してload()を使う
			parametor = pickle.load(g)
			#save　というか置き換え
			parametor[-1] = [self.combobox_1.GetValue(),self.combobox_2.GetValue(),self.combobox_3.GetValue(),today_qty,today_weight,ave_weight,dt,ave_cyecle_time,ave_cyecle_cost,ave_coverweight_cost,self.TxtCtl_22.GetValue(),self.senbetu_combobox_1.GetValue(),self.senbetu_combobox_2.GetValue(),self.senbetu_combobox_3.GetValue(),senbetu_today_qty,senbetu_today_weight,senbetu_ave_weight,senbetu_stock_time,senbetu_ave_cyecle_time,senbetu_ave_cyecle_cost,self.senbetu_TxtCtl_22.GetValue()]#TxtCtl_22は備考の記入欄
			# 書き込みモードでpickle化したものを格納するファイル(.dump)を用意
			#print 'parametor=', parametor
			g.close()
			
			f = file('log.dump', 'w')
			# pickle化する(dump()を使う)
			pickle.dump(parametor, f)
			f.close() # ちゃんと閉じましょう

			f = file('set.dump', 'w')
			pickle.dump(setting, f)
			f.close()
			
			if sum(table_weight)>=(total_weight-weight_ave/2+10) or i>=9:
				choice()
				count+=1
				table_num = []
				table_weight=[]
				#print 'a'
				#print combi_num_a
				i=0
			time.sleep(float(setting[16]/10))
			#処理内容が多すぎる？のを改善するため


	def JuryoStop(self, event):
		global stop_trigger
		global stock_time
		#senbetuを出来るようにする
		self.Btn1.Enable()
		self.Btn2.Disable()
		self.senbetu_Btn1.Enable()
		self.senbetu_Btn2.Disable()
		print 'juryo_stop'
		#ストッパーをonにする
		stop_trigger=True
		#タイマーを止める
		stop_time=datetime.datetime.today()
		stock_time+=stop_time-start_time
		
	#Juryo&add
	def JuryoReset(self, event):
		global start_time
		global stock_time
		global today_qty
		global today_weight
		global dt
		global ave_weight
		global working_sec
		global ave_cyecle_time
		global ave_cyecle_cost
		global ave_coverweight_cost

		dial = wx.MessageDialog(None, u'エクセルファイル　log.xls　にデータを保存しリセットします。よろしいですか？', u'保存&リセット',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		res = dial.ShowModal()

		if res == wx.ID_YES:
			book = xlwt.Workbook()
			newSheet_1 = book.add_sheet('NewSheet_1')
			newSheet_1.write(0, 0, u"日付(年)")
			newSheet_1.write(0, 1, u"日付(月)")
			newSheet_1.write(0, 2, u"日付(日)")
			newSheet_1.write(0, 3, u"生産数(袋数)")
			newSheet_1.write(0, 4, u"生産量(kg)")
			newSheet_1.write(0, 5, u"平均重量(g/袋)")
			newSheet_1.write(0, 6, u"作業時間")
			newSheet_1.write(0, 7, u"作業時間(秒/袋)")
			newSheet_1.write(0, 8, u"作業コスト(円/袋)")
			newSheet_1.write(0, 9, u"重量コスト(円/袋)")
			newSheet_1.write(0, 10, u"備考")
			
			g = file('log.dump', 'r')
			parametor = pickle.load(g)

			for i in range(len(parametor)):
				newSheet_1.write(i+1, 0, parametor[i][0])
				newSheet_1.write(i+1, 1, parametor[i][1])
				newSheet_1.write(i+1, 2, parametor[i][2])
				newSheet_1.write(i+1, 3, parametor[i][3])
				newSheet_1.write(i+1, 4, '%.1f' % parametor[i][4])
				newSheet_1.write(i+1, 5, '%.1f' % parametor[i][5])
				newSheet_1.write(i+1, 6, str(str(parametor[i][6]).split('.')[0]))
				newSheet_1.write(i+1, 7, '%.1f' % parametor[i][7])
				newSheet_1.write(i+1, 8, '%.1f' % parametor[i][8])
				newSheet_1.write(i+1, 9, '%.1f' % parametor[i][9])
				newSheet_1.write(i+1, 10, parametor[i][10])
			
			parametor.append([])
			print 'parametor=', parametor
			g.close()
			book.save('log.xls')		
			f = file('log.dump', 'w')
			pickle.dump(parametor, f)
			f.close()

			start_time=datetime.datetime.today()
			stock_time=datetime.timedelta(0)
			today_qty=0
			today_weight=0
			ave_weight=0
			working_sec=0
			ave_cyecle_time=0
			ave_cyecle_cost=0
			ave_coverweight_cost=0
		
		elif res == wx.ID_NO:
			pass

		dial.Destroy()

###############################################################

	def SenbetuGo(self):
		#メイン
		global weight
		global senbetu_today_qty
		global senbetu_start_time
		global senbetu_stock_time
		global senbetu_today_weight
		global senbetu_dt
		global senbetu_ave_weight
		global senbetu_working_sec
		global senbetu_ave_cyecle_time
		global senbetu_ave_cyecle_cost
		global setting
		global senbetu_table_code
		global senbetu_stop_trigger
		global today_qty,today_weight
		global ave_weight
		global dt
		global ave_cyecle_time
		global ave_cyecle_cost
		global ave_coverweight_cost
		senbetu_start_time=datetime.datetime.today()
		plt.close('all')
		fig = plt.figure(figsize=(4.5, 4.1))
		G = gridspec.GridSpec(1, 20)
		ax3 = fig.add_subplot(G[0,1:])
		lines3, = ax3.plot(x_plot, y_plot,color="k", marker="o",markersize=20,)
		ax3.axis([0, 5, 0, 200])
		ax3.set_title(u'重量(g)')
		while not self.stop_event.is_set():
			senbetu_table_code+=1
			if senbetu_table_code==16:
				senbetu_table_code=0#0に戻す
			rotate_moter()
			measure(senbetu_table_code)
			print weight
			senbetu_today_weight+=weight/1000
			senbetu_today_qty+=1
			senbetu_rotate()
			
			lines3.set_data(x_plot, y_plot)
			plt.pause(.1)
			
			#dtは作業時間
			senbetu_dt = datetime.datetime.today()-senbetu_start_time+senbetu_stock_time
			senbetu_dt1 = str(senbetu_dt)
			working_sec=senbetu_dt.seconds
			if senbetu_today_qty>0:
				senbetu_ave_weight=senbetu_today_weight*1000/senbetu_today_qty
			senbetu_working_sec=senbetu_dt.seconds
			if senbetu_today_qty>0:
				senbetu_ave_cyecle_time=senbetu_working_sec/senbetu_today_qty
			senbetu_ave_cyecle_cost=float(self.senbetu_TxtCtl_28.GetValue())*float(self.senbetu_TxtCtl_30.GetValue())/3600*senbetu_ave_cyecle_time #人件費と作業者数を参照
			#today_qtyなどがtxtctlの欄に表示される(型を少し変更して)
			self.senbetu_TxtCtl_4.SetValue('%d' % senbetu_today_qty)
			self.senbetu_TxtCtl_6.SetValue('%.1f' % senbetu_today_weight)
			self.senbetu_TxtCtl_8.SetValue('%.1f' % senbetu_ave_weight)
			self.senbetu_TxtCtl_10.SetValue(str(senbetu_dt1.split('.')[0]))
			self.senbetu_TxtCtl_12.SetValue('%.1f' % senbetu_ave_cyecle_time)
			self.senbetu_TxtCtl_14.SetValue('%.1f' % senbetu_ave_cyecle_cost)

			g = file('senbetu_log.dump', 'r')
			# ファイルオブジェクトに対してload()を使う
			senbetu_parametor = pickle.load(g)
			#save　というか置き換え
			senbetu_parametor[-1] = [self.senbetu_combobox_1.GetValue(),self.senbetu_combobox_2.GetValue(),self.senbetu_combobox_3.GetValue(),senbetu_today_qty,senbetu_today_weight,senbetu_ave_weight,senbetu_dt,senbetu_ave_cyecle_time,senbetu_ave_cyecle_cost,self.senbetu_TxtCtl_22.GetValue()]#TxtCtl_22は備考の記入欄
			# 書き込みモードでpickle化したものを格納するファイル(.dump)を用意
			#print 'parametor=', parametor
			g.close()
			
			f = file('senbetu_log.dump', 'w')
			# pickle化する(dump()を使う)
			pickle.dump(senbetu_parametor, f)
			f.close() # ちゃんと閉じましょう

			f = file('set.dump', 'w')
			pickle.dump(setting, f)
			f.close()

			time.sleep(float(setting[20]/10))
			#処理内容が多すぎる？のを改善するため

	def SenbetuStart(self, event):
		global senbetu_stock_time
		global senbetu_stop_time
		global senbetu_start_time
		#juryoを出来なくする
		self.Btn1.Disable()
		self.Btn2.Disable()
		self.senbetu_Btn1.Disable()
		self.senbetu_Btn2.Enable()
		#"""スレッドをスタートさせる"""
		self.stop_event.clear()
		senbetu_stock_time+=(senbetu_stop_time-senbetu_start_time)
		self.SenbetuGo()
		
	def SenbetuStop(self, event):
		global senbetu_stock_time
		global senbetu_stop_time
		global senbetu_start_time
		#juryoを出来るようにする
		self.Btn1.Enable()
		self.Btn2.Disable()
		self.senbetu_Btn1.Enable()
		self.senbetu_Btn2.Disable()
		print 'senbetu_stop'
		#タイマーを止める
		senbetu_stop_time=datetime.datetime.today()
		#"""スレッドを停止させる"""
		self.stop_event.set()

	#Juryo&add
	def SenbetuReset(self, event):
		global senbetu_start_time
		global senbetu_stock_time
		global senbetu_today_qty
		global senbetu_today_weight
		global senbetu_ave_weight
		global senbetu_working_sec
		global senbetu_ave_cyecle_time
		global senbetu_ave_cyecle_cost
		
		dial = wx.MessageDialog(None, u'エクセルファイル　log.xls　にデータを保存しリセットします。よろしいですか？', u'保存&リセット',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		res = dial.ShowModal()

		if res == wx.ID_YES:
			book = xlwt.Workbook()
			newSheet_2 = book.add_sheet('NewSheet_2')
			newSheet_2.write(0, 0, u"日付(年)")
			newSheet_2.write(0, 1, u"日付(月)")
			newSheet_2.write(0, 2, u"日付(日)")
			newSheet_2.write(0, 3, u"生産数(個)")
			newSheet_2.write(0, 4, u"生産量(kg)")
			newSheet_2.write(0, 5, u"平均重量(g/個)")
			newSheet_2.write(0, 6, u"作業時間")
			newSheet_2.write(0, 7, u"作業時間(秒/kg)")
			newSheet_2.write(0, 8, u"作業コスト(円/kg)")
			newSheet_2.write(0, 9, u"備考")
			#parametor=[[/0/u"日付(年)",/1/"",/2/"",/3/0,/4/0.0,/5/0.0,/6/datetime.timedelta(0),/7/0.0,/8/0.0,/9/0.0,/10/"",/11/u"日付(年)",/12/"",/13/"",/14/0,/15/0.0,/16/0.0,/17/datetime.timedelta(0),/18/0.0,/19/0.0,/20/""]

			g = file('senbetu_log.dump', 'r')
			senbetu_parametor = pickle.load(g)

			for i in range(len(parametor)):
				newSheet_2.write(i+1, 0, senbetu_parametor[i][0])
				newSheet_2.write(i+1, 1, senbetu_parametor[i][1])
				newSheet_2.write(i+1, 2, senbetu_parametor[i][2])
				newSheet_2.write(i+1, 3, senbetu_parametor[i][3])
				newSheet_2.write(i+1, 4, '%.1f' % senbetu_parametor[i][4])
				newSheet_2.write(i+1, 5, '%.1f' % senbetu_parametor[i][5])
				newSheet_2.write(i+1, 6, str(str(senbetu_parametor[i][6]).split('.')[0]))
				newSheet_2.write(i+1, 7, '%.1f' % senbetu_parametor[i][7])
				newSheet_2.write(i+1, 8, '%.1f' % senbetu_parametor[i][8])
				newSheet_2.write(i+1, 9, senbetu_parametor[i][9])
			
			senbetu_parametor.append([u"日付(年)","","",0,0.0,0.0,datetime.timedelta(0),0.0,0.0,0.0,"",u"日付(年)","","",0,0.0,0.0,datetime.timedelta(0),0.0,0.0,""])
			g.close()
			book.save('log.xls')		
			f = file('senbetu_log.dump', 'w')
			pickle.dump(senbetu_parametor, f)
			f.close()

			senbetu_start_time=datetime.datetime.today()
			senbetu_stock_time=datetime.datetime.today()-senbetu_stop_time#####-1day とかになってしまうのを防ぐため、-senbetu_stop_timeを入れている。
			senbetu_today_qty=0
			senbetu_today_weight=0
			senbetu_ave_weight=0
			senbetu_working_sec=0
			senbetu_ave_cyecle_time=0
			senbetu_ave_cyecle_cost=0
		
		elif res == wx.ID_NO:
			pass

		dial.Destroy()


def main():
	thread1=threading.Thread(target=moterEncode)
	thread1.start()
	app = MyApp()
	app.MainLoop()

			
if __name__ == '__main__':
	main()
