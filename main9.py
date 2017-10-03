#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import random
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import time
from itertools import combinations
from collections import Counter
import wx
import datetime
import pickle
import xlwt
import warnings
warnings.filterwarnings('ignore')
from threading import (Event, Thread)
import serial #シリアル通信モジュールをインポート

#最初にやることでエラー回避
GPIO.cleanup()

# 初期化(普段はコメントアウト)
f = file('log.dump', 'w')
# parametor[-1] = [today_qty,today_weight,ave_weight,dt,ave_cyecle_time,ave_cyecle_cost,ave_coverweight_cost,self.TxtCtl_22.GetValue()]
parametor = [["", "", 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, "", 0.0, 0.0, 0.0, 0.0], [
    "", "", 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, "", 0.0, 0.0, 0.0, 0.0]]
pickle.dump(parametor, f)
f.close()
f = file('senbetu_log.dump', 'w')
senbetu_parametor = [["", "", 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, ""], [
    "", "", 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, ""]]  # parametor[-1] = [today_qty,today_weight,ave_weight,dt,ave_cyecle_time,ave_cyecle_cost,ave_coverweight_cost,self.TxtCtl_22.GetValue()]
pickle.dump(senbetu_parametor, f)
f.close()

f = file('set.dump', 'w')
setting = [0.6,0.6,-0.25,-0.4,2.8,0.6,4.05,0.8,2,-0.05,0.05,0.95,1.75,1.75,1.6,3.4, 10, 200, 220, 190, 500, 800, 1, 5, 0, 20, 40, 60, 80, 800, 1, 0]
## setting[16]からsetting[30]がsetting。setting[31]がtablecode
pickle.dump(setting, f)
f.close()

table_own_weight=[0.6,0.6,-0.25,-0.4,2.8,0.6,4.05,0.8,2,-0.05,0.05,0.95,1.75,1.75,1.6,3.4]

# fp = FontProperties(fname=r'C:\Users\2140022\Desktop\プログラム\ipaexg.ttf', size=14)#'C:\Users\USER\Downloads\ipaexg.ttf'
x_plot = [1]
y_plot = [0]
final_sumweight=[0,0,0,0]
final_sumweight_a = 0
final_sumweight_b = 0
final_sumweight_c = 0
final_sumweight_d = 0
x_bar = [1, 2, 3, 4]
g = file('set.dump', 'r')
setting = pickle.load(g)
g.close()
# 計量されたテーブルNo
table_num = []
# テーブルごとの計量結果
table_weight = []
i = 0
count = 0  # counter for user
NGcount = 0

# switch onで、190g以下の時の処理
discharge_list_a = []
discharge_list_b = []
discharge_list_c = []
discharge_list_d = []
discharge_i = 10
spare_num_a = []
spare_num_b = []
spare_num_c = []
spare_num_d = []
spare_i = 0
spare_sumweight_a = 0
spare_sumweight_b = 0
spare_sumweight_c = 0
spare_sumweight_d = 0
numbering = 0
senbetu_discharge_list_a = []
senbetu_discharge_list_b = []
senbetu_discharge_list_c = []
senbetu_discharge_list_d = []

kumiawase_event = Event()
senbetu_event = Event()

working_sec_sw=False
senbetu_working_sec_sw=False

GPIO.setmode(GPIO.BCM)
# 押しボタン
GPIO.setup(27, GPIO.IN)
#------モーター用PWM設定------
# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
# Import the PCA9685 module.
# Uncomment to enable debug output.
#import logging
# logging.basicConfig(level=logging.DEBUG)
# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()
# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
# Configure min and max servo pulse lengths
servo_down_0 = 300#220  # Min pulse length out of 4096
servo_up_0 = 200  # Max pulse length out of 4096  90 deg at def=300 ##dc_min=0

servo_down = 310#220  # Min pulse length out of 4096
servo_up = 210  # Max pulse length out of 4096  90 deg at def=300 ##dc_min=0
# Helper function to make setting a servo pulse width simpler.

def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
##    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
##    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

# ------排出------
def discharge_a():
    global servo_down
    pwm.set_pwm(0, 0, servo_down_0)
    time.sleep(0.3)

def discharge_b():
    global servo_down
    pwm.set_pwm(1, 0, servo_down_0)
    time.sleep(0.3)

def discharge_c():
    global servo_down
    pwm.set_pwm(2, 0, servo_down)
    time.sleep(0.3)

def discharge_d():
    global servo_down
    pwm.set_pwm(3, 0, servo_down)
    time.sleep(0.3)


time.sleep(2)
pwm.set_pwm(0, 0, servo_down_0)
time.sleep(0.3)
pwm.set_pwm(1, 0, servo_down_0)
time.sleep(0.3)
pwm.set_pwm(2, 0, servo_down)
time.sleep(0.3)
pwm.set_pwm(3, 0, servo_down)
time.sleep(1)
pwm.set_pwm(0, 0, servo_up_0)
time.sleep(0.3)
pwm.set_pwm(1, 0, servo_up_0)
time.sleep(0.3)
pwm.set_pwm(2, 0, servo_up)
time.sleep(0.3)
pwm.set_pwm(3, 0, servo_up)

## ------回転------
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)  # for switch
GPIO.setup(18, GPIO.OUT, initial=0)  # for FET
p = GPIO.PWM(18, 100)
p.start(0)

def rotate_moter():
    pwm.set_pwm(0, 0, servo_up)
    pwm.set_pwm(1, 0, servo_up)
    pwm.set_pwm(2, 0, servo_up)
    pwm.set_pwm(3, 0, servo_up)
    p.ChangeDutyCycle(20)
    time.sleep(1)
    GPIO.wait_for_edge(17, GPIO.RISING)
    time.sleep(0.1)
    p.ChangeDutyCycle(0)

#------組合せ------
sum_table_weight = []
allcombi_num = []
allcombi_weight = []
allcombi_weight_dif = []  # allcombi_weight_dif=[204.78022541534693, 88.19455714403786, 84.85081941624652, 31.734848855062552, 113.21724615959693, 3.3684221117121638, 6.712159839503499, 123.29782811081253, 84.85042555351703, 31.73524271779206, 35.0789804455834, 151.6646487168925, 6.712553702232981, 123.29822197354207, 126.6419597013334, 243.22762797264244, 123.55823768144668, 6.972569410137623, 3.628831682346288, 112.9568365889628, 31.995258425696676, 84.59040984561244, 87.93414757340378, 204.5198158447128, 3.628437819616778, 112.95723045169228, 116.30096817948362, 232.88663645079276, 87.9345414361332, 204.52020970744235, 207.86394743523368, 324.4496157065427, 119.66939029119577, 3.083722019886693, 0.26001570790464257, 116.84568397921373, 28.106411035445774, 88.47925723586332, 91.82299496365465, 208.40866323496368, 0.26040957063412407, 116.84607784194321, 120.18981556973455, 236.77548384104364, 91.82338882638413, 208.40905709769322, 211.75279482548456, 328.33846309679365, 38.447402557295504, 78.13826571401353, 81.48200344180486, 198.06767171311395, 53.115576698454504, 169.7012449697636, 173.04498269755493, 289.63065096886396, 81.4823973045344, 198.06806557584343, 201.41180330363477, 317.997471574944, 173.04537656028435, 289.6310448315935, 292.97478255938483, 409.5604508306939]
allcombi_weight_dif_order = []
# allcombi_order=[[4, 5], [2, 3], [3, 4], [0, 1], [2, 5], [0, 4], [1, 5], [1, 4]]
allcombi_order = []
leftover_order_allcombi = []
table_num_2 = []
n = 0  # n=4
combi_num = []
combi_weight_a = []
combi_weight_b = []
combi_weight_c = []
combi_weight_d = []
error_count = 0
counter = 0 # for analysis
choice_done = False

def choice():  # 4 dischargers
    # リセットsum_table_weight = []
    global allcombi_num
    global allcombi_weight
    global allcombi_weight_dif  # allcombi_weight_dif=[204.78022541534693, 88.19455714403786, 84.85081941624652, 31.734848855062552, 113.21724615959693, 3.3684221117121638, 6.712159839503499, 123.29782811081253, 84.85042555351703, 31.73524271779206, 35.0789804455834, 151.6646487168925, 6.712553702232981, 123.29822197354207, 126.6419597013334, 243.22762797264244, 123.55823768144668, 6.972569410137623, 3.628831682346288, 112.9568365889628, 31.995258425696676, 84.59040984561244, 87.93414757340378, 204.5198158447128, 3.628437819616778, 112.95723045169228, 116.30096817948362, 232.88663645079276, 87.9345414361332, 204.52020970744235, 207.86394743523368, 324.4496157065427, 119.66939029119577, 3.083722019886693, 0.26001570790464257, 116.84568397921373, 28.106411035445774, 88.47925723586332, 91.82299496365465, 208.40866323496368, 0.26040957063412407, 116.84607784194321, 120.18981556973455, 236.77548384104364, 91.82338882638413, 208.40905709769322, 211.75279482548456, 328.33846309679365, 38.447402557295504, 78.13826571401353, 81.48200344180486, 198.06767171311395, 53.115576698454504, 169.7012449697636, 173.04498269755493, 289.63065096886396, 81.4823973045344, 198.06806557584343, 201.41180330363477, 317.997471574944, 173.04537656028435, 289.6310448315935, 292.97478255938483, 409.5604508306939]
    global allcombi_weight_dif_order
    # allcombi_order=[[4, 5], [2, 3], [3, 4], [0, 1], [2, 5], [0, 4], [1, 5], [1, 4]]
    global allcombi_order
    global leftover_order_allcombi
    global table_num_2
    global n  # n=4
    global combi_num
    global combi_weight_a
    global combi_weight_b
    global combi_weight_c
    global combi_weight_d
    global error_count
    global NGcount
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
    global choice_done
    sum_table_weight = []
    allcombi_num = []
    allcombi_weight = []
    allcombi_weight_dif = []  # allcombi_weight_dif=[204.78022541534693, 88.19455714403786, 84.85081941624652, 31.734848855062552, 113.21724615959693, 3.3684221117121638, 6.712159839503499, 123.29782811081253, 84.85042555351703, 31.73524271779206, 35.0789804455834, 151.6646487168925, 6.712553702232981, 123.29822197354207, 126.6419597013334, 243.22762797264244, 123.55823768144668, 6.972569410137623, 3.628831682346288, 112.9568365889628, 31.995258425696676, 84.59040984561244, 87.93414757340378, 204.5198158447128, 3.628437819616778, 112.95723045169228, 116.30096817948362, 232.88663645079276, 87.9345414361332, 204.52020970744235, 207.86394743523368, 324.4496157065427, 119.66939029119577, 3.083722019886693, 0.26001570790464257, 116.84568397921373, 28.106411035445774, 88.47925723586332, 91.82299496365465, 208.40866323496368, 0.26040957063412407, 116.84607784194321, 120.18981556973455, 236.77548384104364, 91.82338882638413, 208.40905709769322, 211.75279482548456, 328.33846309679365, 38.447402557295504, 78.13826571401353, 81.48200344180486, 198.06767171311395, 53.115576698454504, 169.7012449697636, 173.04498269755493, 289.63065096886396, 81.4823973045344, 198.06806557584343, 201.41180330363477, 317.997471574944, 173.04537656028435, 289.6310448315935, 292.97478255938483, 409.5604508306939]
    allcombi_weight_dif_order = []
    # allcombi_order=[[4, 5], [2, 3], [3, 4], [0, 1], [2, 5], [0, 4], [1, 5], [1, 4]]
    allcombi_order = []
    leftover_order_allcombi = []
    table_num_2 = []
    n = 0  # n=4
    combi_num = []
    combi_weight_a = []
    combi_weight_b = []
    combi_weight_c = []
    combi_weight_d = []
    error_count = 0
    spare_i = i
    
    g = file('set.dump', 'r')
    setting = pickle.load(g)

    # print "組合せ計算中"
    # べき集合の関数
    def powerset(s):
        return [[s[j] for j in xrange(len(s)) if (i & (1 << j))] for i in xrange(1 << len(s))]
    # 全組合せのNumとweightのlist作成
    allcombi_num = powerset(table_num)
    allcombi_weight = powerset(table_weight)
    # 全組合せweightと目標値の差分のlist作成
    for j in allcombi_weight:
        allcombi_weight_dif.append(abs(sum(j) - setting[17]))

    allcombi_weight_dif_allorder = sorted(
        range(len(allcombi_weight_dif)), key=allcombi_weight_dif.__getitem__)
    for k in allcombi_weight_dif_allorder:
        allcombi_order.append(allcombi_num[k])
        
    def flatten(nested_list):
        """2重のリストをフラットにする関数"""
        return [e for inner_list in nested_list for e in inner_list]
    
    choice_done = False
    
    def choice4():
        global combi_num
        global combi_weight_a
        global combi_weight_b
        global combi_weight_c
        global combi_weight_d
        global error_count
        global spare_num_a
        global spare_num_b
        global spare_num_c
        global spare_num_d
        global spare_sumweight_a
        global spare_sumweight_b
        global spare_sumweight_c
        global spare_sumweight_d
        global counter
        global choice_done
        #'4th start'
        lst = list(combinations(allcombi_order[:25], 4))
        # print lst
        for j in lst:
            f = flatten(j)
            # print f
            if [key for key, val in Counter(f).items() if val > 1] == [] :#かぶりなし、抜けなし
                # print '4th start'
                combi_num = list(j)
    
                while True:
                    if table_num[0] in combi_num[0] or table_num[-1] in combi_num[3]:
                        random.shuffle(combi_num)
                    else:
                        break
                
                #print combi_num
    
                for j in combi_num[0]:
                    combi_weight_a.append(table_weight[j])
                for j in combi_num[1]:
                    combi_weight_b.append(table_weight[j])
                for j in combi_num[2]:
                    combi_weight_c.append(table_weight[j])
                for j in combi_num[3]:
                    combi_weight_d.append(table_weight[j])
    
                if sum(combi_weight_a) < setting[19] or sum(combi_weight_a) > setting[18]:
                    error_count += 1
                if sum(combi_weight_b) < setting[19] or sum(combi_weight_b) > setting[18]:
                    error_count += 1
                if sum(combi_weight_c) < setting[19] or sum(combi_weight_c) > setting[18]:
                    error_count += 1
                if sum(combi_weight_d) < setting[19] or sum(combi_weight_d) > setting[18]:
                    error_count += 1
    
                if error_count == 0:
                    spare_num_a = [x for x in combi_num[0]]
                    spare_num_b = [x + 1 for x in combi_num[1]]
                    spare_num_c = [x + 2 for x in combi_num[2]]
                    spare_num_d = [x + 3 for x in combi_num[3]]
                    spare_sumweight_a = sum(combi_weight_a)
                    spare_sumweight_b = sum(combi_weight_b)
                    spare_sumweight_c = sum(combi_weight_c)
                    spare_sumweight_d = sum(combi_weight_d)
#                    print 'combi'
                    print(combi_num)
#                    print"a"
#                    print(spare_sumweight_a)
#                    print(spare_sumweight_b)
#                    print(spare_sumweight_c)
#                    print(spare_sumweight_d)
#                    print"d"
                    g = file('log.dump', 'r')
                    parametor = pickle.load(g)
                    parametor[-1][3] += 4
                    parametor[-1][4] += (spare_sumweight_a + spare_sumweight_b +
                                     spare_sumweight_c + spare_sumweight_d) / 1000
                    g.close()
                    
                    f = file('log.dump', 'w')
                    pickle.dump(parametor, f)
                    f.close()
                    choice_done = True
                    
#                    counter += 4
                    
                    break
    
                elif error_count > 1:
                    combi_weight_a = []
                    combi_weight_b = []
                    combi_weight_c = []
                    combi_weight_d = []
                    error_count = 0
    
    def choice3():
        global combi_num
        global combi_weight_a
        global combi_weight_b
        global combi_weight_c
        global combi_weight_d
        global error_count
        global spare_num_a
        global spare_num_b
        global spare_num_c
        global spare_num_d
        global spare_sumweight_a
        global spare_sumweight_b
        global spare_sumweight_c
        global spare_sumweight_d
        global counter
        global choice_done
        #print '3rd start'
        # lst=[((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3)), ((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 4)), ((0, 1, 2), (0, 1, 3), (0, 2, 3), (0, 2, 4)), ((0, 1, 2), (0, 1, 4), (0, 2, 3), (0, 2, 4)), ((0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4))]
        lst = list(combinations(allcombi_order[:25], 3))
        # print lst
        for j in lst:
            f = flatten(j)
            # print f
            if [key for key, val in Counter(f).items() if val > 1] == []:
                combi_num = list(j)
        
                while True:
                    if table_num[0] in combi_num[0]:
                        random.shuffle(combi_num)
                    else:
                        break
                            
        #                print combi_num
        
                for j in combi_num[0]:
                    combi_weight_a.append(table_weight[j])
                for j in combi_num[1]:
                    combi_weight_b.append(table_weight[j])
                for j in combi_num[2]:
                    combi_weight_c.append(table_weight[j])
        
                if sum(combi_weight_a) < setting[19] or sum(combi_weight_a) > setting[18]:
                    error_count += 1
                if sum(combi_weight_b) < setting[19] or sum(combi_weight_b) > setting[18]:
                    error_count += 1
                if sum(combi_weight_c) < setting[19] or sum(combi_weight_c) > setting[18]:
                    error_count += 1
        
                if error_count == 0:
                    spare_num_a = [x for x in combi_num[0]]
                    spare_num_b = [x + 1 for x in combi_num[1]]
                    spare_num_c = [x + 2 for x in combi_num[2]]
                    spare_num_d = []
                    spare_sumweight_a = sum(combi_weight_a)
                    spare_sumweight_b = sum(combi_weight_b)
                    spare_sumweight_c = sum(combi_weight_c)
                    spare_sumweight_d = 0
        
#                    print 'combi'
                    print(combi_num)
#                    # print 'spare_num_d'
#                    #print (spare_num_d)
#                    print "a"
#                    print(spare_sumweight_a)
#                    print(spare_sumweight_b)
#                    print(spare_sumweight_c)
#                    print "c"
        
                    g = file('log.dump', 'r')
                    parametor = pickle.load(g)
                    parametor[-1][3] += 3
                    parametor[-1][4] += (spare_sumweight_a +
                                     spare_sumweight_b + spare_sumweight_c) / 1000
                    g.close()
                    
                    f = file('log.dump', 'w')
                    pickle.dump(parametor, f)
                    f.close()
                    choice_done = True
                    
#                    counter += 3
                    
                    break
        
                elif error_count > 1:
                    combi_num = []
                    combi_weight_a = []
                    combi_weight_b = []
                    combi_weight_c = []
                    error_count = 0

    def choice2():
        global combi_num
        global combi_weight_a
        global combi_weight_b
        global combi_weight_c
        global combi_weight_d
        global error_count
        global spare_num_a
        global spare_num_b
        global spare_num_c
        global spare_num_d
        global spare_sumweight_a
        global spare_sumweight_b
        global spare_sumweight_c
        global spare_sumweight_d
        global counter
        global choice_done
        # print '2nd start'
        # lst=[((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3)), ((0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 4)), ((0, 1, 2), (0, 1, 3), (0, 2, 3), (0, 2, 4)), ((0, 1, 2), (0, 1, 4), (0, 2, 3), (0, 2, 4)), ((0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4))]
        lst = list(combinations(allcombi_order[:25], 2))
        # print lst
        for j in lst:
            f = flatten(j)
            # print f
            if [key for key, val in Counter(f).items() if val > 1] == []:
                combi_num = list(j)
        #                    print combi_num

                while True:
                    if table_num[-1] in combi_num[1]:
                        random.shuffle(combi_num)
                    else:
                        break        

                for j in combi_num[0]:
                    combi_weight_b.append(table_weight[j])
                for j in combi_num[1]:
                    combi_weight_c.append(table_weight[j])
        
                if sum(combi_weight_b) < setting[19] or sum(combi_weight_b) > setting[18]:
                    error_count += 1
                if sum(combi_weight_c) < setting[19] or sum(combi_weight_c) > setting[18]:
                    error_count += 1
                if error_count == 0:
                    spare_num_a = []
                    spare_num_b = [x + 1 for x in combi_num[0]]
                    spare_num_c = [x + 2 for x in combi_num[1]]
                    spare_num_d = []
                    spare_sumweight_a = 0
                    spare_sumweight_b = sum(combi_weight_b)
                    spare_sumweight_c = sum(combi_weight_c)
                    spare_sumweight_d = 0
#                    print 'combi'
                    print(combi_num)
#                    print "a"
#                    print(spare_sumweight_a)
#                    print(spare_sumweight_b)
#                    print "b"
                    g = file('log.dump', 'r')
                    parametor = pickle.load(g)
                    parametor[-1][3] += 2
                    parametor[-1][4] += (spare_sumweight_b + spare_sumweight_c) / 1000
                    g.close()
                    
                    f = file('log.dump', 'w')
                    pickle.dump(parametor, f)
                    f.close()
                    choice_done = True
                    
#                    counter += 2
                    
                    break
                
                elif error_count > 1:
                    combi_num = []
                    combi_weight_a = []
                    combi_weight_b = []
                    error_count = 0
                        
     
    def choice1():
        global combi_num
        global combi_weight_a
        global combi_weight_b
        global combi_weight_c
        global combi_weight_d
        global error_count
        global spare_num_a
        global spare_num_b
        global spare_num_c
        global spare_num_d
        global spare_sumweight_a
        global spare_sumweight_b
        global spare_sumweight_c
        global spare_sumweight_d
        global counter
        global choice_done
        # print '1st start'
        combi_num = allcombi_order[0]
#                        print combi_num

        for j in combi_num:
            combi_weight_b.append(table_weight[j])

        if sum(combi_weight_b) < setting[19] or sum(combi_weight_b) > setting[18]:
            error_count += 1
        if error_count == 0:
            spare_num_a = []#他と違ってcombi_numはlistではなくintになる。なので無理やりlistにする
            spare_num_b = [x + 1 for x in combi_num]
            spare_num_c = []
            spare_num_d = []
            spare_sumweight_a = 0
            spare_sumweight_b = sum(combi_weight_b)
            spare_sumweight_c = 0
            spare_sumweight_d = 0
#            print 'combi'
            print(combi_num)
#            print "a"
#            print(spare_sumweight_a)
#            print "a"
            g = file('log.dump', 'r')
            parametor = pickle.load(g)
            parametor[-1][3] += 1
            parametor[-1][4] += spare_sumweight_b  / 1000
            g.close()
            
            f = file('log.dump', 'w')
            pickle.dump(parametor, f)
            f.close()
            
#            counter += 1
                    
     
    choice4()
    if choice_done is False:
        choice3()
    if choice_done is False:
        choice2()
    if choice_done is False:
        choice1()
        


# ------重量測定-----    #comment out for try
weight = 0.0
a2=0.0
a3=0.0
def measure(setting_23,setting_setting_31):#setting[23]は測定時間、setting_setting[31]はweight of table
    global weight
    global a2
    global a3
#    weight=random.uniform(1,100)
#    pass
    times = int(7+setting_23/10*100/20 )#一回の測定が0.2sec程度。あと整数になるように回りくどく計算している
    for i in xrange(times):
        try:
            con=serial.Serial('/dev/ttyUSB0', 9600, timeout=0.6)#'S\xd4\xac-00000\xb1.\xb1\xa0\xa0\xe7\x00\x8d\n', 'S\xd4\xac-00\n'
            a=con.readlines(20)
        ##    print a
            con.close()
            val=[]
            a0=a[-1]
            a1=a0.replace('\xa0\xa0\xe7\x8d\n', '')
            a21=a1.replace('S\xd4\xac', '')
            a2=a21.replace('US\xac', '')
            if a2[-1].isdigit() ==False:#http://qiita.com/Arvelt/items/07c88411553fc0488ed8
                a2=a2.replace(a2[-1],chr(ord(a2[-1])-0x80))#なぜか0x80分大きな値になっていたので、それを修正している。ordで10→16進数に、chorで16→10進数にしている
        ##    if a2[-2].isdigit() ==False:
        ##        a2=a2.replace(a2[-2],chr(ord(a2[-2])-0x80))
            if a2[-3].isdigit() ==False: 
                a2=a2.replace(a2[-3],chr(ord(a2[-3])-0x80))#8
            if a2[-4].isdigit() ==False: 
                a2=a2.replace(a2[-4],chr(ord(a2[-4])-0x80))#8
            if a2[-5].isdigit() ==False: 
                a2=a2.replace(a2[-5],chr(ord(a2[-5])-0x80))#8
            if a2[-6].isdigit() ==False: 
                a2=a2.replace(a2[-6],chr(ord(a2[-6])-0x80))#8
            if a2[-7].isdigit() ==False: 
                a2=a2.replace(a2[-7],chr(ord(a2[-7])-0x80))#8
            if a2[-8].isdigit() ==False: 
                a2=a2.replace(a2[-8],chr(ord(a2[-8])-0x80))#8 
        ##    if a2.find('.')==-1:#こうしてあげないと08とかの値を8進数と勘違いする
        ##        a3=a2+'.0    
##            weight=float(a2)#重量小さいはかりのためにfloatにしておく 
            a3 = float(a2) - setting_setting_31
        except:
            pass
    print "a2"
    print a2
    weight=a3

def correction():#各テーブル重量の個体差分の補正を行う。
    global weight
    global a3
    con=serial.Serial('/dev/ttyUSB0', 1200, timeout=0.2)
    gcal = file('set.dump', 'r')
    setting = pickle.load(gcal)
    gcal.close()
    for i in xrange(16):
        times = 5 #一回の測定が0.2sec程度。あと整数になるように回りくどく計算している
        val=[]
        for i in xrange(times):
            try:
                a=con.readlines(20)
                con.close()
                a0=a[-1]
                a1=a0.replace('\xa0\xa0\xe7\x8d\n', '')
                a2=a1.replace('S\xd4\xac', '')
                if a2[-1].isdigit() ==False:#http://qiita.com/Arvelt/items/07c88411553fc0488ed8
                    a2=a2.replace(a2[-1],chr(ord(a2[-1])-0x80))#なぜか0x80分大きな値になっていたので、それを修正している。ordで10→16進数に、chorで16→10進数にしている
                if a2[-2].isdigit() ==False:
                    a2=a2.replace(a2[-2],chr(ord(a2[-2])-0x80))
                if a2[-3].isdigit() ==False: 
                    a2=a2.replace(a2[-3],chr(ord(a2[-3])-0x80))
                if a2.find('.')==-1:#こうしてあげないと08とかの値を8進数と勘違いする
                    a3=a2+'.0'
                val.append(float(a3))#重量小さいはかりのためにfloatにしておく
            except:
                pass
        weight = 1.0*sum(val)/len(val)
        setting[setting[31]]=weight
        rotate_moter()
        setting[31]+=1
        if setting[31]==16:
            setting[31]=0
        print weight
    print setting
    fcal = file('set.dump', 'w')
    pickle.dump(setting, fcal)
    fcal.close()

#------回転------
def senbetu_rotate():
    global weight
    global senbetu_discharge_list_a
    global senbetu_discharge_list_b
    global senbetu_discharge_list_c
    global senbetu_discharge_list_d
    global y_plot
    
    g = file('set.dump', 'r')
    setting = pickle.load(g)

    # print "回転"
# weight=random.gauss(102.5,25)#トライ用のコード。テーブルにワークが乗っかったと仮定。

    # 先頭に追加
    y_plot.insert(0, weight)
    del y_plot[1]
#    table_weight.append(weight)

    if setting[24] < weight and weight < setting[25]:
        senbetu_discharge_list_a.append(9)
    if setting[25] < weight and weight < setting[26]:
        senbetu_discharge_list_b.append(10)
    if setting[26] < weight and weight < setting[27]:
        senbetu_discharge_list_c.append(11)
    if setting[27] < weight and weight < setting[28]:
        senbetu_discharge_list_d.append(12)

    # rotateしたらlistをすべて-1する。
    senbetu_discharge_list_a = [x - 1 for x in senbetu_discharge_list_a]
    senbetu_discharge_list_b = [x - 1 for x in senbetu_discharge_list_b]
    senbetu_discharge_list_c = [x - 1 for x in senbetu_discharge_list_c]
    senbetu_discharge_list_d = [x - 1 for x in senbetu_discharge_list_d]

# print(discharge_i)
    # 先頭が0だったらdischarge
    if len(senbetu_discharge_list_a) > 0:
        if senbetu_discharge_list_a[0] == 0:
            discharge_a()
            print senbetu_discharge_list_a
            senbetu_discharge_list_a.remove(0)  # 0を消す
    if len(senbetu_discharge_list_b) > 0:
        if senbetu_discharge_list_b[0] == 0:
            discharge_b()
            print senbetu_discharge_list_b
            senbetu_discharge_list_b.remove(0)
    if len(senbetu_discharge_list_c) > 0:
        if senbetu_discharge_list_c[0] == 0:
            discharge_c()
            print senbetu_discharge_list_c
            senbetu_discharge_list_c.remove(0)
    if len(senbetu_discharge_list_d) > 0:
        if senbetu_discharge_list_d[0] == 0:
            discharge_d()
            print senbetu_discharge_list_d
            senbetu_discharge_list_d.remove(0)


def rotate():
    global weight
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
    global y_plot

    # print "回転"
    table_num.append(i)
    # weight=random.gauss(102.5,25)#トライ用のコード。テーブルにワークが乗っかったと仮定。

    # 先頭に追加
    y_plot.insert(0, weight)
    del y_plot[1]

    table_weight.append(weight)

    # rotateしたらlistをすべて-1する。
    discharge_list_a = [x - 1 for x in discharge_list_a]
    discharge_list_b = [x - 1 for x in discharge_list_b]
    discharge_list_c = [x - 1 for x in discharge_list_c]
    discharge_list_d = [x - 1 for x in discharge_list_d]
    discharge_i -= 1

    

    # print(discharge_i)
    # 先頭が0だったらdischarge
    if len(discharge_list_a) > 0:
        if discharge_list_a[0] == 0:
            discharge_a()
            print "a discharge"
            print(numbering + 1)
            discharge_list_a.remove(0)  # 0を消す
    #	print "a排出"
    if len(discharge_list_b) > 0:
        if discharge_list_b[0] == 0:
            discharge_b()
            print "b discharge"
            print(numbering)
            discharge_list_b.remove(0)
    if len(discharge_list_c) > 0:
        if discharge_list_c[0] == 0:
            discharge_c()
            print "c discharge"
            print(numbering - 1)
            discharge_list_c.remove(0)
    if len(discharge_list_d) > 0:
        if discharge_list_d[0] == 0:
            discharge_d()
            print "d discharge"
            print(numbering - 2)
            discharge_list_d.remove(0)

    numbering += 1

    # リストがなくなったらstop、袋詰後スイッチを押してstart
    if discharge_i == 0:
        # if discharge_list_a==[] and discharge_list_b==[] and discharge_list_c==[] and discharge_list_d==[]:
        discharge_list_a = spare_num_a
        discharge_list_b = spare_num_b
        discharge_list_c = spare_num_c
        discharge_list_d = spare_num_d
        discharge_i = spare_i
        numbering = 0
#        print 'stop'
        #switch on になるまでストップしている
        GPIO.wait_for_edge(27, GPIO.RISING)#それか　GPIO.wait_for_edge(5, GPIO.FALLING)



class MyApp(wx.App):
    def OnInit(self):
        def spin_value_change(event):#停止(秒)
            obj = event.GetEventObject()
            self.TxtCtl_23.SetValue(str(obj.GetValue() / 10))
            f = file('set.dump', 'w')
            setting[16] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_1(event):#平均重量(g)
            obj = event.GetEventObject()
            self.TxtCtl_24.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[17] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_2(event):#上限重量(g)
            obj = event.GetEventObject()
            self.TxtCtl_25.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[18] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_3(event):#下限重量(g)
            obj = event.GetEventObject()
            self.TxtCtl_26.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[19] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_4(event):#市場価格(円/kg)
            obj = event.GetEventObject()
            self.TxtCtl_28.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[20] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_5(event):#人件費(円)
            obj = event.GetEventObject()
            self.TxtCtl_30.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[21] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_6(event):#作業者数(人)
            obj = event.GetEventObject()
            self.TxtCtl_32.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[22] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        # フレーム
        width, height = 1200, 500
        self.Frm = wx.Frame(None, -1,  u"計算式秤 v1",
                            pos=(5, 5), size=wx.Size(width, height))

        # タブ
        self.notebook = wx.Notebook(self.Frm, wx.ID_ANY)

        # 各タブのパネルの設定
        self.panel_kumiawase = wx.Panel(self.notebook, wx.ID_ANY)
        self.panel_senbetu = wx.Panel(self.notebook, wx.ID_ANY)

        # 各パネルの色設定
        self.panel_kumiawase.SetBackgroundColour("#fff9d3")
        self.panel_senbetu.SetBackgroundColour("#d3fff0")

        # タブの文字
        self.notebook.InsertPage(0, self.panel_kumiawase, u"組合")
        self.notebook.InsertPage(1, self.panel_senbetu, u"選別")

        # 重量モード
        # 設定欄のテキスト
        self.s_text_1 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"停止(秒)", size=(105, 30), style=wx.TE_LEFT)
        self.s_text_2 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"平均重量(g)")
        self.s_text_3 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"上限重量(g)")
        self.s_text_4 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"下限重量(g)")
        # 設定欄のスピンボタン
        g = file('set.dump', 'r')
        setting = pickle.load(g)
        self.spinbutton_1 = wx.SpinButton(
            self.panel_kumiawase, wx.ID_ANY, size=(90, 30), style=wx.SP_VERTICAL)#linuxだとhorizontalでやるとspinctrlの表示になってしまうようだ
        self.spinbutton_1.SetMin(4)
        self.spinbutton_1.SetMax(600)
        self.spinbutton_1.SetValue(setting[16])
        self.spinbutton_1.Bind(wx.EVT_SPIN, spin_value_change)
        self.spinbutton_2 = wx.SpinButton(
            self.panel_kumiawase, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.spinbutton_2.SetRange(0,999)
        self.spinbutton_2.SetValue(setting[17])
        self.spinbutton_2.Bind(wx.EVT_SPIN, spin_value_change_1)
        self.spinbutton_3 = wx.SpinButton(
            self.panel_kumiawase, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.spinbutton_3.SetMin(0)
        self.spinbutton_3.SetMax(1000)
        self.spinbutton_3.SetValue(setting[18])
        self.spinbutton_3.Bind(wx.EVT_SPIN, spin_value_change_2)
        self.spinbutton_4 = wx.SpinButton(
            self.panel_kumiawase, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.spinbutton_4.SetMin(0)
        self.spinbutton_4.SetMax(1000)
        self.spinbutton_4.SetValue(setting[19])
        self.spinbutton_4.Bind(wx.EVT_SPIN, spin_value_change_3)
        self.spinbutton_5 = wx.SpinButton(
            self.panel_kumiawase, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.spinbutton_5.SetMin(0)
        self.spinbutton_5.SetMax(1000)
        self.spinbutton_5.SetValue(setting[20])
        self.spinbutton_5.Bind(wx.EVT_SPIN, spin_value_change_4)
        self.spinbutton_6 = wx.SpinButton(
            self.panel_kumiawase, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.spinbutton_6.SetMin(0)
        self.spinbutton_6.SetMax(1000)
        self.spinbutton_6.SetValue(setting[21])
        self.spinbutton_6.Bind(wx.EVT_SPIN, spin_value_change_5)
        self.spinbutton_7 = wx.SpinButton(
            self.panel_kumiawase, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.spinbutton_7.SetMin(0)
        self.spinbutton_7.SetMax(1000)
        self.spinbutton_7.SetValue(setting[22])
        self.spinbutton_7.Bind(wx.EVT_SPIN, spin_value_change_6)
        g.close()
        # 開始、停止ボタン
        self.Btn1 = wx.Button(self.panel_kumiawase, -1, u"開始", size=(150, 30))
        self.Btn2 = wx.Button(self.panel_kumiawase, -1, u"停止", size=(150, 30))
        self.Btn1.Bind(wx.EVT_BUTTON, self.KumiawaseStart)
        self.Btn2.Bind(wx.EVT_BUTTON, self.KumiawaseStop)
        # 記録欄のテキスト
        self.s_text_5 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"生産数(袋数)")
        self.TxtCtl_6 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_6.SetBackgroundColour("#d3fff0")
        self.s_text_7 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"生産量(kg)")
        self.TxtCtl_8 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_8.SetBackgroundColour("#d3fff0")
        self.s_text_9 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"平均重量(g/袋)")
        self.TxtCtl_10 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_10.SetBackgroundColour("#d3fff0")
        self.s_text_11 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"作業時間")
        self.TxtCtl_12 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_12.SetBackgroundColour("#d3fff0")
        self.s_text_13 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"作業時間(秒/袋)")
        self.TxtCtl_14 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_14.SetBackgroundColour("#d3fff0")
        self.s_text_15 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"作業コスト(円/袋)")
        self.TxtCtl_16 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_16.SetBackgroundColour("#d3fff0")
        self.s_text_17 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"重量コスト(円/袋)")
        self.TxtCtl_18 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_18.SetBackgroundColour("#d3fff0")
        self.s_text_21 = wx.StaticText(self.panel_kumiawase, wx.ID_ANY, u"備考")
        self.TxtCtl_22 = wx.TextCtrl(
            self.panel_kumiawase, -1, u"", size=(150, -1), style=wx.TE_LEFT)
        self.s_text_27 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"市場価格(円/kg)")
        self.TxtCtl_28 = wx.TextCtrl(
            self.panel_kumiawase, -1, str(setting[20]), size=(90, -1), style=wx.TE_LEFT)
        self.s_text_29 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"人件費(円/h)")
        self.TxtCtl_30 = wx.TextCtrl(
            self.panel_kumiawase, -1, str(setting[21]), size=(90, -1), style=wx.TE_LEFT)
        self.s_text_31 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"作業者数(人)")
        self.TxtCtl_32 = wx.TextCtrl(
            self.panel_kumiawase, -1, str(setting[22]), size=(90, -1), style=wx.TE_LEFT)
        self.s_text_33 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"日時")
        self.TxtCtl_34 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_34.SetBackgroundColour("#d3fff0")
        self.s_text_35 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"計測値(g)")
        self.TxtCtl_36 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_36.SetBackgroundColour("#d3fff0")
        self.s_text_37 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"組合せ1(g)")
        self.TxtCtl_38 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_38.SetBackgroundColour("#d3fff0")
        self.s_text_39 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"組合せ2(g)")
        self.TxtCtl_40 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_40.SetBackgroundColour("#d3fff0")
        self.s_text_41 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"組合せ3(g)")
        self.TxtCtl_42 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_42.SetBackgroundColour("#d3fff0")
        self.s_text_43 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, u"組合せ4(g)")
        self.TxtCtl_44 = wx.TextCtrl(
            self.panel_kumiawase, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.TxtCtl_44.SetBackgroundColour("#d3fff0")
        
        # エクセルに書き込むボタン
        self.Btn22 = wx.Button(self.panel_kumiawase, -1,
                               u"記録の保存＆リセット", size=(300, 30))
        self.Btn22.Bind(wx.EVT_BUTTON, self.KumiawaseReset)
        # 校正ボタン
        self.Btn23 = wx.Button(self.panel_kumiawase, -1,
                               u"ゼロ点補正", size=(300, 30))
        self.Btn23.Bind(wx.EVT_BUTTON, self.ZeroPointCorrection)
        self.TxtCtl_23 = wx.TextCtrl(
            self.panel_kumiawase, -1, str(float(setting[16] / 10)), size=(90, -1), style=wx.TE_LEFT)
        self.TxtCtl_24 = wx.TextCtrl(
            self.panel_kumiawase, -1, str(setting[17]), size=(90, -1), style=wx.TE_LEFT)
        self.TxtCtl_25 = wx.TextCtrl(
            self.panel_kumiawase, -1, str(setting[18]), size=(90, -1), style=wx.TE_LEFT)
        self.TxtCtl_26 = wx.TextCtrl(
            self.panel_kumiawase, -1, str(setting[19]), size=(90, -1), style=wx.TE_LEFT)
        self.s_text_white_6 = wx.StaticText(
            self.panel_kumiawase, wx.ID_ANY, "")

        # フォント
        self.font = wx.Font(14, wx.FONTFAMILY_DEFAULT,
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.font_1 = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.font_2 = wx.Font(18, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.font_3 = wx.Font(18, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
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
        self.s_text_21.SetFont(self.font)
        self.TxtCtl_22.SetFont(self.font)
        self.Btn22.SetFont(self.font)
        self.Btn23.SetFont(self.font)
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
        self.s_text_33.SetFont(self.font)
        self.TxtCtl_34.SetFont(self.font_1)
        self.s_text_35.SetFont(self.font_2)
        self.TxtCtl_36.SetFont(self.font_3)
        
        self.s_text_37.SetFont(self.font_2)
        self.TxtCtl_38.SetFont(self.font_3)
        self.s_text_39.SetFont(self.font_2)
        self.TxtCtl_40.SetFont(self.font_3)
        self.s_text_41.SetFont(self.font_2)
        self.TxtCtl_42.SetFont(self.font_3)
        self.s_text_43.SetFont(self.font_2)
        self.TxtCtl_44.SetFont(self.font_3)

        # レイアウト
        self.layout_1 = wx.BoxSizer(wx.VERTICAL)
        self.layout_1_2 = wx.GridSizer(7, 3, 5, 5)
        self.layout_1_2.Add(self.s_text_2)
        self.layout_1_2.Add(self.TxtCtl_24)
        self.layout_1_2.Add(self.spinbutton_2)
        self.layout_1_2.Add(self.s_text_3)
        self.layout_1_2.Add(self.TxtCtl_25)
        self.layout_1_2.Add(self.spinbutton_3)
        self.layout_1_2.Add(self.s_text_4)
        self.layout_1_2.Add(self.TxtCtl_26)
        self.layout_1_2.Add(self.spinbutton_4)
        self.layout_1_2.Add(self.s_text_1)
        self.layout_1_2.Add(self.TxtCtl_23)
        self.layout_1_2.Add(self.spinbutton_1)
        self.layout_1_2.Add(self.s_text_27)
        self.layout_1_2.Add(self.TxtCtl_28)
        self.layout_1_2.Add(self.spinbutton_5)
        self.layout_1_2.Add(self.s_text_29)
        self.layout_1_2.Add(self.TxtCtl_30)
        self.layout_1_2.Add(self.spinbutton_6)
        self.layout_1_2.Add(self.s_text_31)
        self.layout_1_2.Add(self.TxtCtl_32)
        self.layout_1_2.Add(self.spinbutton_7)
        self.layout_1.Add(self.layout_1_2)
        
        self.layout_2 = wx.BoxSizer(wx.VERTICAL)     
        self.layout_2_1 = wx.GridSizer(6, 2, 5, 5)
        self.layout_2_1.Add(self.Btn1, flag=wx.SHAPED | wx.ALIGN_CENTER)
        self.layout_2_1.Add(self.Btn2, flag=wx.SHAPED | wx.ALIGN_CENTER)
        self.layout_2_1.Add(self.s_text_35)
        self.layout_2_1.Add(self.TxtCtl_36)
        self.layout_2_1.Add(self.s_text_37)
        self.layout_2_1.Add(self.TxtCtl_38)
        self.layout_2_1.Add(self.s_text_39)
        self.layout_2_1.Add(self.TxtCtl_40)
        self.layout_2_1.Add(self.s_text_41)
        self.layout_2_1.Add(self.TxtCtl_42)
        self.layout_2_1.Add(self.s_text_43)
        self.layout_2_1.Add(self.TxtCtl_44)
        self.layout_2_2 = wx.GridSizer(2, 1, 5, 5)
        self.layout_2_2.Add(self.Btn22)
        self.layout_2_2.Add(self.Btn23)
        self.layout_2.Add(self.layout_2_1)
        self.layout_2.Add(self.layout_2_2)

        self.layout_3 = wx.BoxSizer(wx.VERTICAL)
        self.layout_3_2 = wx.GridSizer(9, 2, 5, 5)
        self.layout_3_2.Add(self.s_text_33)
        self.layout_3_2.Add(self.TxtCtl_34)
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
        self.layout_3.Add(self.layout_3_2)
        self.layout_1_2_3 = wx.BoxSizer(wx.HORIZONTAL)
        self.layout_1_2_3.Add(
            self.layout_2, 0, flag=wx.EXPAND | wx.ALL,   border=10)
        self.layout_1_2_3.Add(
            self.layout_1, 0, flag=wx.EXPAND | wx.ALL,   border=10)
        self.layout_1_2_3.Add(
            self.layout_3, 1, flag=wx.EXPAND | wx.ALL,   border=10)
        self.panel_kumiawase.SetSizer(self.layout_1_2_3)

#################################################################################
        # 選別モード
        # 設定欄のテキスト
        def spin_value_change_senbetu(event):
            obj = event.GetEventObject()
            self.senbetu_TxtCtl.SetValue(str(obj.GetValue() / 10))
            f = file('set.dump', 'w')
            setting[23] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_senbetu_1(event):
            obj = event.GetEventObject()
            self.senbetu_TxtCtl_23.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[24] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_senbetu_2(event):
            obj = event.GetEventObject()
            self.senbetu_TxtCtl_24.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[25] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_senbetu_3(event):
            obj = event.GetEventObject()
            self.senbetu_TxtCtl_25.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[26] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_senbetu_4(event):
            obj = event.GetEventObject()
            self.senbetu_TxtCtl_26.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[27] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_senbetu_5(event):
            obj = event.GetEventObject()
            self.senbetu_TxtCtl_27.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[28] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_senbetu_6(event):#人件費(円/h)
            obj = event.GetEventObject()
            self.senbetu_TxtCtl_28.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[29] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        def spin_value_change_senbetu_7(event):#作業者数(人)
            obj = event.GetEventObject()
            self.senbetu_TxtCtl_30.SetValue(str(obj.GetValue()))
            f = file('set.dump', 'w')
            setting[30] = obj.GetValue()
            pickle.dump(setting, f)
            f.close()

        self.senbetu_s_text = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"停止(秒)")
        self.senbetu_s_text_0 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"規格")
        self.senbetu_s_text_1 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"重量範囲(g)")
        self.senbetu_s_text_S = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"S")
        self.senbetu_s_text_M = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"M")
        self.senbetu_s_text_L = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"L")
        self.senbetu_s_text_2L = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"2L")
        # 設定欄のスピンボタン
        g = file('set.dump', 'r')
        setting = pickle.load(g)
        self.senbetu_spinbutton = wx.SpinButton(
            self.panel_senbetu, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.senbetu_spinbutton.SetMin(4)
        self.senbetu_spinbutton.SetMax(300)
        self.senbetu_spinbutton.SetValue(setting[23])
        self.senbetu_spinbutton.Bind(wx.EVT_SPIN, spin_value_change_senbetu)
        self.senbetu_spinbutton_1 = wx.SpinButton(
            self.panel_senbetu, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.senbetu_spinbutton_1.SetMin(0)
        self.senbetu_spinbutton_1.SetMax(1000)
        self.senbetu_spinbutton_1.SetValue(setting[24])
        self.senbetu_spinbutton_1.Bind(
            wx.EVT_SPIN, spin_value_change_senbetu_1)
        self.senbetu_spinbutton_2 = wx.SpinButton(
            self.panel_senbetu, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.senbetu_spinbutton_2.SetMin(0)
        self.senbetu_spinbutton_2.SetMax(1000)
        self.senbetu_spinbutton_2.SetValue(setting[25])
        self.senbetu_spinbutton_2.Bind(
            wx.EVT_SPIN, spin_value_change_senbetu_2)
        self.senbetu_spinbutton_3 = wx.SpinButton(
            self.panel_senbetu, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.senbetu_spinbutton_3.SetMin(0)
        self.senbetu_spinbutton_3.SetMax(1000)
        self.senbetu_spinbutton_3.SetValue(setting[26])
        self.senbetu_spinbutton_3.Bind(
            wx.EVT_SPIN, spin_value_change_senbetu_3)
        self.senbetu_spinbutton_4 = wx.SpinButton(
            self.panel_senbetu, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.senbetu_spinbutton_4.SetMin(0)
        self.senbetu_spinbutton_4.SetMax(1000)
        self.senbetu_spinbutton_4.SetValue(setting[27])
        self.senbetu_spinbutton_4.Bind(
            wx.EVT_SPIN, spin_value_change_senbetu_4)
        self.senbetu_spinbutton_5 = wx.SpinButton(
            self.panel_senbetu, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.senbetu_spinbutton_5.SetMin(0)
        self.senbetu_spinbutton_5.SetMax(1000)
        self.senbetu_spinbutton_5.SetValue(setting[28])
        self.senbetu_spinbutton_5.Bind(
            wx.EVT_SPIN, spin_value_change_senbetu_5)
        self.senbetu_spinbutton_6 = wx.SpinButton(
            self.panel_senbetu, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.senbetu_spinbutton_6.SetMin(0)
        self.senbetu_spinbutton_6.SetMax(1000)
        self.senbetu_spinbutton_6.SetValue(setting[29])
        self.senbetu_spinbutton_6.Bind(
            wx.EVT_SPIN, spin_value_change_senbetu_6)
        self.senbetu_spinbutton_7 = wx.SpinButton(
            self.panel_senbetu, wx.ID_ANY, size=(90, 30), style=wx.SP_HORIZONTAL)
        self.senbetu_spinbutton_7.SetMin(0)
        self.senbetu_spinbutton_7.SetMax(1000)
        self.senbetu_spinbutton_7.SetValue(setting[30])
        self.senbetu_spinbutton_7.Bind(
            wx.EVT_SPIN, spin_value_change_senbetu_7)
        g.close()
        # 開始、停止ボタン
        self.senbetu_Btn1 = wx.Button(
            self.panel_senbetu, -1, u"開始", size=(150, 30))
        self.senbetu_Btn2 = wx.Button(
            self.panel_senbetu, -1, u"停止", size=(150, 30))
        self.senbetu_Btn1.Bind(wx.EVT_BUTTON, self.SenbetuStart)
        self.senbetu_Btn2.Bind(wx.EVT_BUTTON, self.SenbetuStop)
        # 記録欄のテキスト
        self.senbetu_s_text_3 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"生産数(個)")
        self.senbetu_TxtCtl_4 = wx.TextCtrl(
            self.panel_senbetu, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_4.SetBackgroundColour("#d3fff0")
        self.senbetu_s_text_5 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"生産量(kg)")
        self.senbetu_TxtCtl_6 = wx.TextCtrl(
            self.panel_senbetu, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_6.SetBackgroundColour("#d3fff0")
        self.senbetu_s_text_7 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"平均重量(g/個)")
        self.senbetu_TxtCtl_8 = wx.TextCtrl(
            self.panel_senbetu, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_8.SetBackgroundColour("#d3fff0")
        self.senbetu_s_text_9 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"作業時間")
        self.senbetu_TxtCtl_10 = wx.TextCtrl(
            self.panel_senbetu, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_10.SetBackgroundColour("#d3fff0")
        self.senbetu_s_text_11 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"作業時間(秒/kg)")
        self.senbetu_TxtCtl_12 = wx.TextCtrl(
            self.panel_senbetu, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_12.SetBackgroundColour("#d3fff0")
        self.senbetu_s_text_13 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"作業コスト(円/kg)")
        self.senbetu_TxtCtl_14 = wx.TextCtrl(
            self.panel_senbetu, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_14.SetBackgroundColour("#d3fff0")
        self.senbetu_s_text_21 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"備考")
        self.senbetu_TxtCtl_22 = wx.TextCtrl(
            self.panel_senbetu, -1, u"", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_s_text_27 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"人件費(円)")
        self.senbetu_TxtCtl_28 = wx.TextCtrl(
            self.panel_senbetu, -1, str(setting[29]), size=(90, -1), style=wx.TE_LEFT)
        self.senbetu_s_text_29 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"作業者数(人)")
        self.senbetu_TxtCtl_30 = wx.TextCtrl(
            self.panel_senbetu, -1, str(setting[30]), size=(90, -1), style=wx.TE_LEFT)
        self.senbetu_s_text_33 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"日時")
        self.senbetu_TxtCtl_34 = wx.TextCtrl(
            self.panel_senbetu, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_34.SetBackgroundColour("#d3fff0")
        self.senbetu_s_text_35 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, u"計測値(g)")
        self.senbetu_TxtCtl_36 = wx.TextCtrl(
            self.panel_senbetu, -1, "", size=(150, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_36.SetBackgroundColour("#d3fff0")
        # エクセルに書き込むボタン
        self.senbetu_Btn22 = wx.Button(
            self.panel_senbetu, -1, u"記録の保存＆リセット", size=(300, 30))
        self.senbetu_Btn22.Bind(wx.EVT_BUTTON, self.SenbetuReset)
        self.senbetu_Btn23 = wx.Button(
            self.panel_senbetu, -1, u"ゼロ点補正", size=(300, 30))
        self.senbetu_Btn23.Bind(wx.EVT_BUTTON, self.ZeroPointCorrection)

        self.senbetu_TxtCtl = wx.TextCtrl(
            self.panel_senbetu, -1, str(float(setting[23] / 10)), size=(90, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_23 = wx.TextCtrl(
            self.panel_senbetu, -1, str(setting[24]), size=(90, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_24 = wx.TextCtrl(
            self.panel_senbetu, -1, str(setting[25]), size=(90, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_25 = wx.TextCtrl(
            self.panel_senbetu, -1, str(setting[26]), size=(90, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_26 = wx.TextCtrl(
            self.panel_senbetu, -1, str(setting[27]), size=(90, -1), style=wx.TE_LEFT)
        self.senbetu_TxtCtl_27 = wx.TextCtrl(
            self.panel_senbetu, -1, str(setting[28]), size=(90, -1), style=wx.TE_LEFT)
        self.senbetu_s_text_white_6 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, "")
        self.senbetu_s_text_white_7 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, "")
        self.senbetu_s_text_white_8 = wx.StaticText(
            self.panel_senbetu, wx.ID_ANY, "")

        # フォント
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
        self.senbetu_s_text_21.SetFont(self.font)
        self.senbetu_TxtCtl_22.SetFont(self.font)
        self.senbetu_Btn22.SetFont(self.font)
        self.senbetu_Btn23.SetFont(self.font)
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
        self.senbetu_s_text.SetFont(self.font)
        self.senbetu_TxtCtl.SetFont(self.font)
        self.senbetu_s_text_33.SetFont(self.font)
        self.senbetu_TxtCtl_34.SetFont(self.font_1)
        self.senbetu_s_text_35.SetFont(self.font_2)
        self.senbetu_TxtCtl_36.SetFont(self.font_3)

        # レイアウト
        self.senbetu_layout_1 = wx.BoxSizer(wx.VERTICAL)
        self.senbetu_layout_1_2 = wx.GridSizer(9, 3, 5, 5)
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
        self.senbetu_layout_1_2.Add(self.senbetu_s_text)
        self.senbetu_layout_1_2.Add(self.senbetu_TxtCtl)
        self.senbetu_layout_1_2.Add(self.senbetu_spinbutton)
        self.senbetu_layout_1_2.Add(self.senbetu_s_text_27)
        self.senbetu_layout_1_2.Add(self.senbetu_TxtCtl_28)
        self.senbetu_layout_1_2.Add(self.senbetu_spinbutton_6)
        self.senbetu_layout_1_2.Add(self.senbetu_s_text_29)
        self.senbetu_layout_1_2.Add(self.senbetu_TxtCtl_30)
        self.senbetu_layout_1_2.Add(self.senbetu_spinbutton_7)
        self.senbetu_layout_1.Add(self.senbetu_layout_1_2)
        
        self.senbetu_layout_2 = wx.BoxSizer(wx.VERTICAL)
        self.senbetu_layout_2_1 = wx.GridSizer(2, 2, 5, 5)
        self.senbetu_layout_2_1.Add(
            self.senbetu_Btn1, flag=wx.SHAPED | wx.ALIGN_CENTER)
        self.senbetu_layout_2_1.Add(
            self.senbetu_Btn2, flag=wx.SHAPED | wx.ALIGN_CENTER)
        self.senbetu_layout_2_1.Add(self.senbetu_s_text_35)
        self.senbetu_layout_2_1.Add(self.senbetu_TxtCtl_36)
        self.senbetu_layout_2_2 = wx.GridSizer(2, 1, 5, 5)
        self.senbetu_layout_2_2.Add(self.senbetu_Btn22)
        self.senbetu_layout_2_2.Add(self.senbetu_Btn23)
        self.senbetu_layout_2.Add(self.senbetu_layout_2_1)
        self.senbetu_layout_2.Add(self.senbetu_layout_2_2)
        
        self.senbetu_layout_3 = wx.BoxSizer(wx.VERTICAL)
        self.senbetu_layout_3_2 = wx.GridSizer(8, 2, 5, 5)
        self.senbetu_layout_3_2.Add(self.senbetu_s_text_33)
        self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_34)
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
        self.senbetu_layout_3_2.Add(self.senbetu_s_text_21)
        self.senbetu_layout_3_2.Add(self.senbetu_TxtCtl_22)
        self.senbetu_layout_3.Add(self.senbetu_layout_3_2)
        self.senbetu_layout_1_2_3 = wx.BoxSizer(wx.HORIZONTAL)
        self.senbetu_layout_1_2_3.Add(
            self.senbetu_layout_2, 0, flag=wx.EXPAND | wx.ALL,   border=10)
        self.senbetu_layout_1_2_3.Add(
            self.senbetu_layout_1, 0, flag=wx.EXPAND | wx.ALL,   border=10)
        self.senbetu_layout_1_2_3.Add(
            self.senbetu_layout_3, 1, flag=wx.EXPAND | wx.ALL,   border=10)
        self.panel_senbetu.SetSizer(self.senbetu_layout_1_2_3)
        self.Frm.Show()
        self.Btn1.Enable()
        self.Btn2.Disable()
        self.senbetu_Btn1.Enable()
        self.senbetu_Btn2.Disable()
        
        kumiawase_event.clear()
        senbetu_event.clear()

        self.Bind(wx.EVT_TIMER, self.Update)
        self.t1 = wx.Timer(self)
        self.t1.Start(1000)# 数字の単位は msec

        return True

#####################################################################################################

    def Update(self, event):
        global working_sec_sw
        global senbetu_working_sec_sw
        try:
            self.wg = file('log.dump', 'r')
            self.wparametor = pickle.load(self.wg)
            self.wparametor[-1][1]=datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")
            self.TxtCtl_34.SetValue(str(self.wparametor[-1][1]))
            self.TxtCtl_36.SetValue('%.1f' % self.wparametor[-1][2])
            self.TxtCtl_6.SetValue('%.1f' % self.wparametor[-1][3])
            self.TxtCtl_8.SetValue('%.1f' % self.wparametor[-1][4])
            self.TxtCtl_10.SetValue('%.1f' % self.wparametor[-1][5])
            h=self.wparametor[-1][6]//3600
            m=self.wparametor[-1][6]%3600//60
            s=self.wparametor[-1][6]%3600%60
            self.TxtCtl_12.SetValue(('%02d'%h)+":"+('%02d'%m)+":"+('%02d'%s))
            self.TxtCtl_14.SetValue('%.1f' % self.wparametor[-1][7])
            self.TxtCtl_16.SetValue('%.1f' % self.wparametor[-1][8])
            self.TxtCtl_18.SetValue('%.1f' % self.wparametor[-1][9])
            self.TxtCtl_38.SetValue('%.1f' % self.wparametor[-1][11])
            self.TxtCtl_40.SetValue('%.1f' % self.wparametor[-1][12])
            self.TxtCtl_42.SetValue('%.1f' % self.wparametor[-1][13])
            self.TxtCtl_44.SetValue('%.1f' % self.wparametor[-1][14])
            if working_sec_sw is True:
                self.wparametor[-1][6]+=1
            
            self.wf = file('log.dump', 'w')
            pickle.dump(self.wparametor, self.wf)
            self.wf.close()
            self.wg.close()
    
            self.wgs = file('senbetu_log.dump', 'r')
            self.wparametor_senbetu = pickle.load(self.wgs)
            self.wparametor_senbetu[-1][1]=datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")
            self.senbetu_TxtCtl_34.SetValue(str(self.wparametor_senbetu[-1][1]))
            self.senbetu_TxtCtl_36.SetValue('%.1f' % self.wparametor_senbetu[-1][2])
            self.senbetu_TxtCtl_4.SetValue('%.1f' % self.wparametor_senbetu[-1][3])
            self.senbetu_TxtCtl_6.SetValue('%.1f' % self.wparametor_senbetu[-1][4])
            self.senbetu_TxtCtl_8.SetValue('%.1f' % self.wparametor_senbetu[-1][5])
            hs=self.wparametor_senbetu[-1][6]//3600
            ms=self.wparametor_senbetu[-1][6]%3600//60
            ss=self.wparametor_senbetu[-1][6]%3600%60
            self.senbetu_TxtCtl_10.SetValue(('%02d'%hs)+":"+('%02d'%ms)+":"+('%02d'%ss))
            self.senbetu_TxtCtl_12.SetValue('%.1f' % self.wparametor_senbetu[-1][7])
            self.senbetu_TxtCtl_14.SetValue('%.1f' % self.wparametor_senbetu[-1][8])
            if senbetu_working_sec_sw is True:
                self.wparametor_senbetu[-1][6]+=1
    
            self.wfs = file('senbetu_log.dump', 'w')
            pickle.dump(self.wparametor_senbetu, self.wfs)
            self.wfs.close()       
            self.wgs.close()
        except:
            pass

    def KumiawaseStart(self, event):
        global working_sec_sw
        # Kumiawaseを出来なくする
        self.Btn1.Disable()
        self.Btn2.Enable()
        self.senbetu_Btn1.Disable()
        self.senbetu_Btn2.Disable()
        self.Btn22.Disable()
        self.Btn23.Disable()
        self.senbetu_Btn22.Disable()
        self.senbetu_Btn23.Disable()
        
        working_sec_sw=True
        kumiawase_event.set()

    def KumiawaseStop(self, event):
        global working_sec_sw
        # Kumiawaseとsenbetuを出来るようにする
        self.Btn1.Enable()
        self.Btn2.Disable()
        self.senbetu_Btn1.Enable()
        self.senbetu_Btn2.Disable()
        self.Btn22.Enable()
        self.Btn23.Enable()
        self.senbetu_Btn22.Enable()
        self.senbetu_Btn23.Enable()
        working_sec_sw=False
        print 'Kumiawase_stop'
        kumiawase_event.clear()

    # reset&add
    def KumiawaseReset(self, event):
        dial = wx.MessageDialog(None, u'エクセルファイル　log.xls　にデータを保存しリセットします。よろしいですか？', u'保存&リセット',
                                wx.YES_NO | wx.NO_DEFAULT)
        res = dial.ShowModal()

        if res == wx.ID_YES:
            book = xlwt.Workbook()
            newSheet_1 = book.add_sheet('NewSheet_1')
            newSheet_1.write(0, 0, u"")
            newSheet_1.write(0, 1, u"日時")
            newSheet_1.write(0, 2, u"気温(℃)")
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

            for i in range(len(parametor)-1):
#                newSheet_1.write(i + 1, 0, parametor[i][0])
                newSheet_1.write(i + 1, 1, parametor[i+1][1])
                newSheet_1.write(i + 1, 2, parametor[i+1][2])
                newSheet_1.write(i + 1, 3, parametor[i+1][3])
                newSheet_1.write(i + 1, 4, '%.1f' % parametor[i+1][4])
                newSheet_1.write(i + 1, 5, '%.1f' % parametor[i+1][5])
                newSheet_1.write(
                    i + 1, 6, str(str(parametor[i+1][6]).split('.')[0]))
                newSheet_1.write(i + 1, 7, '%.1f' % parametor[i+1][7])
                newSheet_1.write(i + 1, 8, '%.1f' % parametor[i+1][8])
                newSheet_1.write(i + 1, 9, '%.1f' % parametor[i+1][9])
                newSheet_1.write(i + 1, 10, parametor[i+1][10])

            parametor.append(["", "", 25.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, ""])
            print 'parametor=', parametor
            g.close()
            book.save('kumiawase_log.xls')
            f = file('log.dump', 'w')
            pickle.dump(parametor, f)
            f.close()


        elif res == wx.ID_NO:
            pass

        dial.Destroy()

###############################################################

    def SenbetuStart(self, event):
        global senbetu_event
        global senbetu_working_sec_sw
        # Kumiawaseを出来なくする
        self.Btn1.Disable()
        self.Btn2.Disable()
        self.senbetu_Btn1.Disable()
        self.senbetu_Btn2.Enable()
        self.Btn22.Disable()
        self.Btn23.Disable()
        self.senbetu_Btn22.Disable()
        self.senbetu_Btn23.Disable()
        senbetu_working_sec_sw=True
        senbetu_event.set()

    def SenbetuStop(self, event):
        global senbetu_event
        global senbetu_working_sec_sw
        global i
        global table_num
        global table_weight
        table_num = []
        table_weight = []
        i=0
        # Kumiawaseを出来るようにする
        self.Btn1.Enable()
        self.Btn2.Disable()
        self.senbetu_Btn1.Enable()
        self.senbetu_Btn2.Disable()
        self.Btn22.Enable()
        self.Btn23.Enable()
        self.senbetu_Btn22.Enable()
        self.senbetu_Btn23.Enable()
        senbetu_working_sec_sw=False
        print 'senbetu_stop'
        senbetu_event.clear()

    # reset&add
    def SenbetuReset(self, event):
        dial = wx.MessageDialog(None, u'エクセルファイル　log.xls　にデータを保存しリセットします。よろしいですか？', u'保存&リセット',
                                wx.YES_NO | wx.NO_DEFAULT)
        res = dial.ShowModal()

        if res == wx.ID_YES:
            book = xlwt.Workbook()
            newSheet_2 = book.add_sheet('NewSheet_1')
            newSheet_2.write(0, 0, u"")
            newSheet_2.write(0, 1, u"日時")
            newSheet_2.write(0, 2, u"気温(℃)")
            newSheet_2.write(0, 3, u"生産数(個)")
            newSheet_2.write(0, 4, u"生産量(kg)")
            newSheet_2.write(0, 5, u"平均重量(g/個)")
            newSheet_2.write(0, 6, u"作業時間")
            newSheet_2.write(0, 7, u"作業時間(秒/kg)")
            newSheet_2.write(0, 8, u"作業コスト(円/kg)")
            newSheet_2.write(0, 9, u"備考")

            g = file('senbetu_log.dump', 'r')
            senbetu_parametor = pickle.load(g)

            for i in range(len(parametor)-1):
#                newSheet_2.write(i + 1, 0, senbetu_parametor[i][0])
                newSheet_2.write(i + 1, 1, senbetu_parametor[i+1][1])
                newSheet_2.write(i + 1, 2, senbetu_parametor[i+1][2])
                newSheet_2.write(i + 1, 3, senbetu_parametor[i+1][3])
                newSheet_2.write(i + 1, 4, '%.1f' % senbetu_parametor[i+1][4])
                newSheet_2.write(i + 1, 5, '%.1f' % senbetu_parametor[i+1][5])
                newSheet_2.write(
                    i + 1, 6, str(str(senbetu_parametor[i+1][6]).split('.')[0]))
                newSheet_2.write(i + 1, 7, '%.1f' % senbetu_parametor[i+1][7])
                newSheet_2.write(i + 1, 8, '%.1f' % senbetu_parametor[i+1][8])
                newSheet_2.write(i + 1, 9, senbetu_parametor[i+1][9])

            senbetu_parametor.append(["", "", 25.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, ""])
            g.close()
            book.save('senbetu_log.xls')
            f = file('senbetu_log.dump', 'w')
            pickle.dump(senbetu_parametor, f)
            f.close()

        elif res == wx.ID_NO:
            pass

        dial.Destroy()
        
    def ZeroPointCorrection(self, event):
        global weight
        gcal = file('set.dump', 'r')
        setting = pickle.load(gcal)
        gcal.close()
        for i in xrange(16):
            times = 7 #一回の測定が0.2sec程度。あと整数になるように回りくどく計算している
            for i in xrange(times):
                try:
                    con=serial.Serial('/dev/ttyUSB0', 9600, timeout=0.6)
                    a=con.readlines(20)
                    print a
                    con.close()
                    a0=a[-1]
                    a1=a0.replace('\xa0\xa0\xe7\x8d\n', '')
                    a21=a1.replace('S\xd4\xac', '')
                    a2=a21.replace('US\xac', '')
                    if a2[-1].isdigit() ==False:#http://qiita.com/Arvelt/items/07c88411553fc0488ed8
                        a2=a2.replace(a2[-1],chr(ord(a2[-1])-0x80))#なぜか0x80分大きな値になっていたので、それを修正している。ordで10→16進数に、chorで16→10進数にしている
                ##    if a2[-2].isdigit() ==False:
                ##        a2=a2.replace(a2[-2],chr(ord(a2[-2])-0x80))
                    if a2[-3].isdigit() ==False: 
                        a2=a2.replace(a2[-3],chr(ord(a2[-3])-0x80))#8
                    if a2[-4].isdigit() ==False: 
                        a2=a2.replace(a2[-4],chr(ord(a2[-4])-0x80))#8
                    if a2[-5].isdigit() ==False: 
                        a2=a2.replace(a2[-5],chr(ord(a2[-5])-0x80))#8
                    if a2[-6].isdigit() ==False: 
                        a2=a2.replace(a2[-6],chr(ord(a2[-6])-0x80))#8
                    if a2[-7].isdigit() ==False: 
                        a2=a2.replace(a2[-7],chr(ord(a2[-7])-0x80))#8
                    if a2[-8].isdigit() ==False: 
                        a2=a2.replace(a2[-8],chr(ord(a2[-8])-0x80))#8 
                ##    if a2.find('.')==-1:#こうしてあげないと08とかの値を8進数と勘違いする
                ##        a3=a2+'.0    
        ##            weight=float(a2)#重量小さいはかりのためにfloatにしておく 
                    a3 = float(a2)
                except:
                    pass
            weight = a3
            setting[setting[31]]=weight
            rotate_moter()
            setting[31]+=1
            if setting[31]==16:
                setting[31]=0
            print weight
            time.sleep(1)
        print setting
        fcal = file('set.dump', 'w')
        pickle.dump(setting, fcal)
        fcal.close()


##fig = plt.figure(figsize=(4.5, 4.1))
##G = gridspec.GridSpec(1, 20)
##ax1 = fig.add_subplot(G[0, 1:6])
##ax2 = fig.add_subplot(G[0, 9:])
##lines, = ax1.plot(
##    x_plot, setting[17] / 2, color="r", marker="o", markersize=20,)
##lines1, = ax1.plot(x_plot, y_plot, color="k",
##                   marker="o", markersize=20,)
##lines2, = ax2.plot(x_bar, final_sumweight, color="b",
##                   marker="o", markersize=20, linewidth=0)
##ax1.axis([0.9, 1.1, 0, 200])
##ax1.set_xticklabels([])
##ax1.set_title(u'個別重量')
##ax1.set_ylabel(u'重量(g)')
##ax2.axis([0, 5, 100, 300])
##ax2.set_title(u'組合せ重量')

#------main------
def KumiawaseRun():
    global i
    global table_num
    global table_weight
    global weight
    global final_sumweight
##    global lines1
##    global lines2

##    lines1.set_data(x_plot, y_plot)
##    lines2.set_data(x_bar, final_sumweight)
##    plt.draw()
##    plt.pause(.01)
    
    while True:
        kumiawase_event.wait()
        final_sumweight = [
            spare_sumweight_a, spare_sumweight_b, spare_sumweight_c, spare_sumweight_d]

        g2 = file('set.dump', 'r')
        setting = pickle.load(g2)
        measure(setting[16],setting[setting[31]])
##        print "setting[31]"
##        print setting[31]
##        print "setting[setting[31]]"
##        print setting[setting[31]]
##        print "weight"
##        print weight
        
        rotate_moter()
        setting[31]+=1
        if setting[31]==16:
            setting[31]=0
        g2.close()
        f2 = file('set.dump', 'w')
        pickle.dump(setting, f2)
        f2.close()
        
        rotate()
        i += 1

        if i>=9:
            print "choice start"
            choice()
#            count += 1
            table_num = []
            table_weight = []
            i=0

##        lines1.set_data(x_plot, y_plot)
##        lines2.set_data(x_bar, final_sumweight)
##        plt.pause(.01)
        try:
            g = file('log.dump', 'r')
            parametor = pickle.load(g)
            g1 = file('set.dump', 'r')
            setting = pickle.load(g1)
            parametor[-1][2] = weight
            if parametor[-1][3] > 0:
                parametor[-1][5] = parametor[-1][4] * 1000 / parametor[-1][3]
            if parametor[-1][3] > 0:
                parametor[-1][7] = parametor[-1][6] / parametor[-1][3]
            if parametor[-1][3] > 0:        
                parametor[-1][8] = setting[21] * setting[22] / 3600 * parametor[-1][7]
            if parametor[-1][3] > 0:
                parametor[-1][9] = setting[20] / 1000 * (parametor[-1][5]-setting[17])
            parametor[-1][11] = final_sumweight[0]
            parametor[-1][12] = final_sumweight[1]
            parametor[-1][13] = final_sumweight[2]
            parametor[-1][14] = final_sumweight[3]
    
            g.close()
            g1.close()
            
            f = file('log.dump', 'w')
            pickle.dump(parametor, f)
            f.close()
        except:
            pass

#parametor[0]=self.combobox_1.GetValue()
#parametor[1]=self.combobox_2.GetValue()
#parametor[2]=self.combobox_3.GetValue()
#today_qty = parametor[3]
#today_weight = parametor[4]
#ave_weight = parametor[5]
#stock_time = parametor[6]
#ave_cyecle_time = parametor[7]
#ave_cyecle_cost = parametor[8]
#ave_coverweight_cost = parametor[9]
#parametor[10]=self.TxtCtl_22.GetValue()
#setting[16]#停止(秒)
#setting[17]平均重量(g)
#setting[18]上限重量(g)
#setting[19]下限重量(g)
#setting[20]#市場価格(円/kg)
#setting[21]#人件費(円/h)
#setting[22]#作業者数(人)
    
def SenbetuRun():
##    global lines1
##    global lines2
    
    while True:
        senbetu_event.wait()

        gs2 = file('set.dump', 'r')
        setting = pickle.load(gs2)
        measure(setting[23],setting[setting[31]])
##        print "setting[31]"
##        print setting[31]
##        print "setting[setting[31]]"
##        print setting[setting[31]]
##        print "weight"
##        print weight
        
        rotate_moter()
        setting[31]+=1
        if setting[31]==16:
            setting[31]=0
        gs2.close()
        fs2 = file('set.dump', 'w')
        pickle.dump(setting, fs2)
        fs2.close()
        senbetu_rotate()

##        lines1.set_data(x_plot, y_plot)
##        lines2.set_data(x_bar, [0,0,0,0])
##        plt.pause(.01)
        try:
            gs = file('senbetu_log.dump', 'r')
            parametor_senbetu = pickle.load(gs)
            gs1 = file('set.dump', 'r')
            setting = pickle.load(gs1)
            parametor_senbetu[-1][2] = weight
            parametor_senbetu[-1][3] += 1
            parametor_senbetu[-1][4] += weight / 1000
            if parametor_senbetu[-1][3] > 0:
                parametor_senbetu[-1] [5] = parametor_senbetu[-1] [4] * 1000 / parametor_senbetu[-1] [3]        
            if parametor_senbetu[-1] [3] > 0:
                parametor_senbetu[-1] [7] = parametor_senbetu[-1] [6] / parametor_senbetu[-1] [3]
            if parametor_senbetu[-1] [3] > 0:        
                parametor_senbetu[-1] [8] = setting[29] * setting[30] / 3600 * parametor_senbetu[-1] [7]
    
            gs.close()
            gs1.close()
            
            fs = file('senbetu_log.dump', 'w')
            pickle.dump(parametor_senbetu, fs)
            fs.close()
        except:
            pass
    
#setting[16]#停止(秒)
#setting[17]平均重量(g)
#setting[18]上限重量(g)
#setting[19]下限重量(g)
#setting[20]#市場価格(円/kg)
#setting[21]#人件費(円/h)
#setting[22]#作業者数(人)
#senbetu_s_text 停止(秒) setting[23]
#senbetu_s_text_S S setting[24]
#senbetu_s_text_S S setting[25]
#senbetu_s_text_M M setting[26]
#senbetu_s_text_L L setting[27]
#senbetu_s_text_2L 2L setting[28]
#setting[29]#人件費(円/h)
#setting[30]#作業者数(人)
    
#parametor [0]=self.combobox_1.GetValue()
#parametor [1]=self.combobox_2.GetValue()
#parametor [2]=self.combobox_3.GetValue()
#self.TxtCtl_6.SetValue('%d' % parametor [3])
#self.TxtCtl_8.SetValue('%.1f' % parametor [4])
#self.TxtCtl_10.SetValue('%.1f' % parametor [5])
#self.TxtCtl_12.SetValue(str(parametor [6].split('.')[0]))
#self.TxtCtl_14.SetValue('%.1f' % parametor [7])
#self.TxtCtl_16.SetValue('%.1f' % parametor [8])
#parametor [9]=self.TxtCtl_22.GetValue()           

##correction()
#補正値作成

def main():
    kumiawase_thread = Thread(target=KumiawaseRun)
    kumiawase_thread.start()
    
    senbetu_thread = Thread(target=SenbetuRun)
    senbetu_thread.start()
    
    app = MyApp()
    app.MainLoop()


if __name__ == '__main__':
    main()
