import time
import logging
from .utils import http_post
logging.basicConfig()

def job1(a, b):
    print(str(a) + ' ' + str(b))


def job2():
    print("it will run job2")
    url = "xxx"
    para = {'scantime':'1536741519'}
    ret = http_post(url, para)
    print('job2 %s ' % ret)

def job3():
    print("job3 sleep 5 minutes ")
    time.sleep(5*60)
    print("job3 end")


