#-*- using:utf-8 -*-
import time
import random
cdef float sum1,x
cdef int num,i

cpdef averaging():
	num=1000000
	start = time.time()
	sum1=0
	for i in xrange(num):
		sum1+=1
	x=sum1/num
	elapsed_time = time.time() - start
	print elapsed_time
	return x

