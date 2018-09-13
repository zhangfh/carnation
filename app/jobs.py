import logging
from .utils import http_post
logging.basicConfig()

def job1(a, b):
    print(str(a) + ' ' + str(b))

def job2():
    print("it will run job2")
    url = "http://ultrasound.lonshinetech.cn/lscloud/api/PictureDoctor/testint"
    para = {'scantime':'1536741519'}
    ret = http_post(url, para)
    print('job2 %s ' % ret)

