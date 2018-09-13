import urllib,cookielib
import urllib2
import socket

def http_post(url, para):
    headers={'UserAgent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)','X-API-KEY':'lscloud'};
    values= para;
    data=urllib.urlencode(values);

    request=urllib2.Request(url,headers=headers,data=data);
    response=urllib2.urlopen(request);
    ret = response.read() #response.read() only is valid first
    print('http_post %s ' % ret)
    return ret


def get_hostname():
    return socket.gethostname().lower()

