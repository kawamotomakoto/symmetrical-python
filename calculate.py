#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
##import numpy as np
import random
##import RPi.GPIO as GPIO
##import wiringpi2 as wiringpi
import sys
import Tkinter
import csv
##import Adafruit_PCA9685
import time
import itertools
from itertools import combinations
from collections import Counter
import wx
import time
import datetime
import threading
import pickle
import xlwt
import numpy as np
import matplotlib.pyplot as plt
import random
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties
import warnings;warnings.filterwarnings('ignore')

#------window------
class MyApp(wx.App):
	def OnInit(self):
		#フレーム
		width, height = 360, 400
		self.Frm = wx.Frame(None, -1,  u"計算式秤 v1",pos=(5,5), size=wx.Size(width, height))

		##def auto_save_data():
		##    #日付が一緒であれば同じセルに保存(上書き)。日付が異なる場合は次のセルに保存。
		##    #排出されたらオートセーブ
		##    datetime.date.today()
		##    
		##    log_list=[]
		##    log_list.append(datetime.date.today())
		##    log_list.append(today_weight)
		##    log_list.append(today_qty)
		##    log_list.append(ave_weight)
		##    log_list.append(working_min)
		##    log_list.append(ave_cyecle_time)
		##    log_list.append(ave_cyecle_cost)
		##    log_list.append(ave_coverweight_cost)
		##
		##    with open('log.csv', 'w') as f:
		##        writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
		##        writer.writerow(log_list)     # list（1次元配列）の場合

		#タブ
		self.notebook = wx.Notebook(self.Frm, wx.ID_ANY)

		#各タブのパネルの設定
		self.panel_1 = wx.Panel(self.notebook, wx.ID_ANY)
		self.panel_3 = wx.Panel(self.notebook, wx.ID_ANY)

		#各パネルの色設定
		self.panel_1.SetBackgroundColour("#fff9d3")
		self.panel_3.SetBackgroundColour("#d3fff0")

		#タブの文字
		self.notebook.InsertPage(0, self.panel_1, u"作業")
		self.notebook.InsertPage(1, self.panel_3, u"記録")

		#タブ1のテキスト
		self.s_text_1 = wx.StaticText(self.panel_1, wx.ID_ANY, u"回転速度(%)")
		self.s_text_2 = wx.StaticText(self.panel_1, wx.ID_ANY, u"平均重量(g)")
		self.s_text_3 = wx.StaticText(self.panel_1, wx.ID_ANY, u"上限重量(g)")
		self.s_text_4 = wx.StaticText(self.panel_1, wx.ID_ANY, u"下限重量(g)")
		#タブ1のスライダー
		g = file('set.dump', 'r')
		setting = pickle.load(g)		
		self.slider_1 = wx.Slider(self.panel_1, -1, setting[0], 60, 100,  size=(320, -1), style=wx.SL_LABELS)
		self.slider_2 = wx.Slider(self.panel_1, -1, setting[1], 100, 300, size=(320, -1), style=wx.SL_LABELS)
		self.slider_3 = wx.Slider(self.panel_1, -1, setting[2], 100, 300, size=(320, -1), style=wx.SL_LABELS)
		self.slider_4 = wx.Slider(self.panel_1, -1, setting[3], 100, 300, size=(320, -1), style=wx.SL_LABELS)
		g.close()		
		#タブ1のボタン
		self.Btn1 = wx.Button(self.panel_1, -1, u"開始")
		self.Btn2 = wx.Button(self.panel_1, -1, u"停止")
		self.Btn2.Disable()
		self.Btn1.Bind(wx.EVT_BUTTON, self.TimerStart)
		self.Btn2.Bind(wx.EVT_BUTTON, self.TimerStop)
		self.Bind(wx.EVT_TIMER, self.TimerTest)

		#タブ3のテキスト
		self.s_text_5 = wx.StaticText(self.panel_3, wx.ID_ANY, u"生産数(袋数)")
		self.TxtCtl_6 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.TxtCtl_6.SetBackgroundColour("#d3fff0")
		self.s_text_7 = wx.StaticText(self.panel_3, wx.ID_ANY, u"生産量(kg)")
		self.TxtCtl_8 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.TxtCtl_8.SetBackgroundColour("#d3fff0")
		self.s_text_9 = wx.StaticText(self.panel_3, wx.ID_ANY, u"平均重量(g/袋)")
		self.TxtCtl_10 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.TxtCtl_10.SetBackgroundColour("#d3fff0")
		self.s_text_11 = wx.StaticText(self.panel_3, wx.ID_ANY, u"作業時間")
		self.TxtCtl_12 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.TxtCtl_12.SetBackgroundColour("#d3fff0")
		self.s_text_13 = wx.StaticText(self.panel_3, wx.ID_ANY, u"作業時間(秒/袋)")
		self.TxtCtl_14 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.TxtCtl_14.SetBackgroundColour("#d3fff0")
		self.s_text_15 = wx.StaticText(self.panel_3, wx.ID_ANY, u"作業コスト(円/袋)")
		self.TxtCtl_16 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.TxtCtl_16.SetBackgroundColour("#d3fff0")
		self.s_text_17 = wx.StaticText(self.panel_3, wx.ID_ANY, u"重量コスト(円/袋)")
		self.TxtCtl_18 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.TxtCtl_18.SetBackgroundColour("#d3fff0")
		self.s_text_19 = wx.StaticText(self.panel_3, wx.ID_ANY, u"日付")
		self.TxtCtl_20 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.s_text_21 = wx.StaticText(self.panel_3, wx.ID_ANY, u"備考")
		self.TxtCtl_22 = wx.TextCtrl(self.panel_3, -1, "", size=(150,-1),
				   style=wx.TE_LEFT)
		self.Btn22 = wx.Button(self.panel_3, -1, u"保存＆リセット")
		self.Btn22.Bind(wx.EVT_BUTTON, self.Reset)

		g = file('log.dump', 'r')
		parametor = pickle.load(g)
		self.TxtCtl_20.SetValue(parametor[-1][0])
		g.close()

		#フォント
		self.font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.s_text_1.SetFont(self.font)
		self.s_text_2.SetFont(self.font)
		self.s_text_3.SetFont(self.font)
		self.s_text_4.SetFont(self.font)
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
		self.TxtCtl_20.SetFont(self.font)
		self.s_text_21.SetFont(self.font)
		self.TxtCtl_22.SetFont(self.font)
		self.Btn22.SetFont(self.font)
		self.Btn1.SetFont(self.font)
		self.Btn2.SetFont(self.font)

		#レイアウト
		self.layout_1 = wx.GridSizer(10,1)
		self.layout_1.Add(self.s_text_1)
		self.layout_1.Add(self.slider_1)
		self.layout_1.Add(self.s_text_2)
		self.layout_1.Add(self.slider_2)
		self.layout_1.Add(self.s_text_3)
		self.layout_1.Add(self.slider_3)
		self.layout_1.Add(self.s_text_4)
		self.layout_1.Add(self.slider_4)
		self.layout_1.Add(self.Btn1)
		self.layout_1.Add(self.Btn2)
		self.panel_1.SetSizer(self.layout_1)

		self.layout_3 = wx.GridSizer(10, 2)
		self.layout_3.Add(self.s_text_19)
		self.layout_3.Add(self.TxtCtl_20)
		self.layout_3.Add(self.s_text_5)
		self.layout_3.Add(self.TxtCtl_6)
		self.layout_3.Add(self.s_text_7)
		self.layout_3.Add(self.TxtCtl_8)
		self.layout_3.Add(self.s_text_9)
		self.layout_3.Add(self.TxtCtl_10)
		self.layout_3.Add(self.s_text_11)
		self.layout_3.Add(self.TxtCtl_12)
		self.layout_3.Add(self.s_text_13)
		self.layout_3.Add(self.TxtCtl_14)
		self.layout_3.Add(self.s_text_15)
		self.layout_3.Add(self.TxtCtl_16)
		self.layout_3.Add(self.s_text_17)
		self.layout_3.Add(self.TxtCtl_18)
		self.layout_3.Add(self.s_text_21)
		self.layout_3.Add(self.TxtCtl_22)
		self.layout_3.Add(self.Btn22)
		self.panel_3.SetSizer(self.layout_3)

		self.Frm.Show()
		return True

	def TimerStart(self, event):
		global start_time
		start_time=datetime.datetime.today()
		self.t1 = wx.Timer(self)
		self.t1.Start(900) # 数字の単位は msec
		self.Btn2.Enable()
		self.Btn1.Disable()

	def TimerStop(self, event):
		global stock_time
		stop_time=datetime.datetime.today()
		stock_time+=stop_time-start_time
		self.t1.Stop()
		del self.t1                # ちゃんとdelする。
		self.Btn2.Disable()
		self.Btn1.Enable()

	def TimerTest(self, event):
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
		dt = datetime.datetime.today()-start_time+stock_time        
		dt1 = str(dt)
		if today_qty>0:
			ave_weight=today_weight*1000/today_qty
		working_sec=dt.seconds
		if today_qty>0:
			ave_cyecle_time=working_sec/today_qty
		ave_cyecle_cost=37/60*ave_cyecle_time #日本人の平均分給を参照
		if ave_weight>0:
			ave_coverweight_cost=(ave_weight-setting[1])*496/1000 #kgあたりのほうれん草の単価を参照
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
		parametor[-1] = [self.TxtCtl_20.GetValue(),today_qty,today_weight,ave_weight,dt,ave_cyecle_time,ave_cyecle_cost,ave_coverweight_cost,self.TxtCtl_22.GetValue()]
		# 書き込みモードでpickle化したものを格納するファイル(.dump)を用意
##		print 'parametor=', parametor
		g.close()
		
		f = file('log.dump', 'w')
		# pickle化する(dump()を使う)
		pickle.dump(parametor, f)
		f.close() # ちゃんと閉じましょう

		self.slider_1
		g = file('set.dump', 'r')
		setting=pickle.load(g)
		setting=[self.slider_1.GetValue(),self.slider_2.GetValue(),self.slider_3.GetValue(),self.slider_4.GetValue()]
		g.close()

		f = file('set.dump', 'w')
		pickle.dump(setting, f)
		f.close()



	#reset&add
	def Reset(self, event):
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

		dial = wx.MessageDialog(None, u'エクセルファイル　記録.xls　にデータを保存しリセットします。よろしいですか？', u'保存&リセット',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		res = dial.ShowModal()

		if res == wx.ID_YES:
			book = xlwt.Workbook()
			newSheet_1 = book.add_sheet('NewSheet_1')
			newSheet_1.write(0, 0, u"日付")
			newSheet_1.write(0, 1, u"生産数(袋数)")
			newSheet_1.write(0, 2, u"生産量(kg)")
			newSheet_1.write(0, 3, u"平均重量(g/袋)")
			newSheet_1.write(0, 4, u"作業時間")
			newSheet_1.write(0, 5, u"作業時間(秒/袋)")
			newSheet_1.write(0, 6, u"作業コスト(円/袋)")
			newSheet_1.write(0, 7, u"重量コスト(円/袋)")
			newSheet_1.write(0, 8, u"備考")
			
			g = file('log.dump', 'r')
			parametor = pickle.load(g)

			for i in range(len(parametor)):
				newSheet_1.write(i+1, 0, str(parametor[i][0]))
				newSheet_1.write(i+1, 1, parametor[i][1])
				newSheet_1.write(i+1, 2, '%.1f' % parametor[i][2])
				newSheet_1.write(i+1, 3, '%.1f' % parametor[i][3])
				newSheet_1.write(i+1, 4, str(str(parametor[i][4]).split('.')[0]))
				newSheet_1.write(i+1, 5, '%.1f' % parametor[i][5])
				newSheet_1.write(i+1, 6, '%.1f' % parametor[i][6])
				newSheet_1.write(i+1, 7, '%.1f' % parametor[i][7])
				newSheet_1.write(i+1, 8, str(parametor[i][8]))
			
			parametor.append([])
			print 'parametor=', parametor
			g.close()
			book.save(u'記録.xls')		
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
		
g = file('log.dump', 'r')
parametor = pickle.load(g)
stock_time=parametor[-1][4]
start_time=datetime.datetime.today()
today_qty=parametor[-1][1]
today_weight=parametor[-1][2]
ave_weight=parametor[-1][3]
ave_cyecle_time=parametor[-1][5]
ave_cyecle_cost=parametor[-1][6]
ave_coverweight_cost=parametor[-1][7]
g.close()


x_plot=[1]
y_plot=[0]
final_sumweight_a=0
final_sumweight_b=0
final_sumweight_c=0
final_sumweight_d=0
x_bar=[1,2,3,4]


##fp = FontProperties(fname=r'C:\Users\2140022\Desktop\プログラム\ipaexg.ttf', size=14)#'C:\Users\USER\Downloads\ipaexg.ttf'

def plot():
	global final_sumweight_a
	global final_sumweight_b
	global final_sumweight_c
	global final_sumweight_d
	final_sumweight=[final_sumweight_a,final_sumweight_b,final_sumweight_c,final_sumweight_d]

	fig = plt.figure(figsize=(4.5, 4.1))

	G = gridspec.GridSpec(1, 20)
	ax1 = fig.add_subplot(G[0,1:6])
	ax2 = fig.add_subplot(G[0,9:])

	lines, = ax1.plot(x_plot, setting[1]/2 ,color="r", marker="o",markersize=20,)
	lines1, = ax1.plot(x_plot, y_plot,color="k", marker="o",markersize=20,)
	lines2, = ax2.plot(x_bar, final_sumweight,color="b", marker="o",markersize=20, linewidth = 0)

	ax1.axis([0.9, 1.1, 0, 200])
	ax1.set_xticklabels([])
	ax1.set_title(u'個別重量')
	ax1.set_ylabel(u'重量(g)')
	ax2.axis([0, 5, 100, 300])
	ax2.set_title(u'組合せ重量')


	
	while True:
		lines1.set_data(x_plot, y_plot)
		final_sumweight=[final_sumweight_a,final_sumweight_b,final_sumweight_c,final_sumweight_d]
		lines2.set_data(x_bar, final_sumweight)
		plt.pause(0.1)
		
def window():
	app = MyApp()
	app.MainLoop()

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
##servo_min = 150  # Min pulse length out of 4096
##servo_max = 450  # Max pulse length out of 4096  90 deg at def=300 
##dc_min=0
##dc_max=4050
##
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
##	pwm.set_pwm(0, 0, servo_max)
##	time.sleep(0.6)  #0.9 sec at 135 deg      0.6 at 90 deg 
##	pwm.set_pwm(0, 0, servo_min)
##
def discharge_b():
	pass
##	pwm.set_pwm(1, 0, servo_max)
##	time.sleep(0.6)
##	pwm.set_pwm(1, 0, servo_min)
##
def discharge_c():
	pass
##	pwm.set_pwm(2, 0, servo_max)
##	time.sleep(0.6)
##	pwm.set_pwm(2, 0, servo_min)
##
def discharge_d():
	pass
##	pwm.set_pwm(3, 0, servo_max)
##	time.sleep(0.6)
##	pwm.set_pwm(3, 0, servo_min)

###------回転------
##
##GPIO.setmode(GPIO.BCM)
##GPIO.setup(17, GPIO.OUT)
##GPIO.setup(27, GPIO.OUT)
##p0 = GPIO.PWM(17, 50) 
##p1 = GPIO.PWM(27, 50) 
##
##
### 初期化
##p0.start(0)
##p1.start(0)
##
##
###速度の変数(%)
##a=setting[0]
##
##
###スタート
def rotate_moter():
	pass
##	p0.ChangeDutyCycle( 0 )
##	p1.ChangeDutyCycle( 0 )	#(in1,in2)を(1,1)→(0,0)にすることで、ブレーキ→フリーにする
##	for i in range(0,6):
##		new_duty = a*i/5
##		p0.ChangeDutyCycle( 0 )
##		p1.ChangeDutyCycle( new_duty )#(in1,in2)を(0,0)→(0,1)にする(あるいは(0,1))ことでフリー→回転
##		time.sleep(0.1)
##	
##
###ストップ
def stop_moter():
	pass
##	for i in range(5, -1, -1):
##		new_duty = a*i/5
##		p0.ChangeDutyCycle( 0 )
##		p1.ChangeDutyCycle( new_duty )#(in1,in2)を(0,1)→(0,0)にすることで、回転→フリーにする
##		time.sleep(0.1)
##	for i in range(0,6):
##		new_duty = 100*i/5
##		p0.ChangeDutyCycle( new_duty )
##		p1.ChangeDutyCycle( new_duty )#(in1,in2)を(0,0)→(1,1)にすることでフリー→ブレーキ
##		time.sleep(0.1)	


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
		allcombi_weight_dif.append(abs(sum(j)-setting[1]))

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

					if sum(combi_weight_a)<setting[3] or sum(combi_weight_a)>setting[2]:
						error_count+=1
					if sum(combi_weight_b)<setting[3] or sum(combi_weight_b)>setting[2]:
						error_count+=1
					if sum(combi_weight_c)<setting[3] or sum(combi_weight_c)>setting[2]:
						error_count+=1
					if sum(combi_weight_d)<setting[3] or sum(combi_weight_d)>setting[2]:
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

		if sum(combi_weight_a)<setting[3] or sum(combi_weight_a)>setting[2]:
			error_count+=1
		if sum(combi_weight_b)<setting[3] or sum(combi_weight_b)>setting[2]:
			error_count+=1
		if sum(combi_weight_c)<setting[3] or sum(combi_weight_c)>setting[2]:
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

			if sum(combi_weight_a)<setting[3] or sum(combi_weight_a)>setting[2]:
				error_count+=1
			if sum(combi_weight_b)<setting[3] or sum(combi_weight_b)>setting[2]:
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



##	
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
##
####try:
####    while True:
####        inputVal0 = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)
####        print(inputVal0)
####        sleep(0.0001)
##

#------回転------

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
	weight=random.gauss(102.5,25)#トライ用のコード。テーブルにワークが乗っかったと仮定。

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
		#stop
		stop_moter()
##		#switch on になるまでストップしている
##		GPIO.wait_for_edge(4, GPIO.RISING) #comment out for try
		#run
		rotate_moter()

g = file('set.dump', 'r')
setting = pickle.load(g)
g.close()
#計量されたテーブルNo
table_num = []
#テーブルごとの計量結果
table_weight=[]
i=0
weight_ave=setting[1]/2
stdev=40
total_weight=4*setting[1]
count=0  #counter for user
NGcount=0
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


#------main------

def main():
	global table_num
	global table_weight
	global total_weight
	global weight_ave
	global i
	global count
	
##	GPIO.setmode(GPIO.BCM)
##	#押しボタン
##	GPIO.setup(4, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN) #comment out for try

	thread1=threading.Thread(target=window)
	thread1.start()

	thread2=threading.Thread(target=plot)
	thread2.start()
     
	while True:
		rotate_moter()
		if sum(table_weight)>=(total_weight-weight_ave/2+10) or i>=9:
			choice()
			count+=1
			table_num = []
			table_weight=[]
			#print 'a'
			#print combi_num_a
			i=0
		else:
			rotate()
			i+=1
##	GPIO.cleanup()
			
if __name__ == '__main__':
	main()
