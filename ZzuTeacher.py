# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import urllib2

def request(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    contentLen = response.info().getheader('Content-Length')
    errInfoList = ['22', '6566']
    if contentLen in errInfoList:
        return None
    if response.getcode() != 200:
        return None
    return response.read()

path = raw_input('input the directory to save the pictures:')
os.chdir(path)
os.getcwd()
piccount = 0
urlPrefix = 'http://jw.zzu.edu.cn/scripts/newxkxt.dll/getphoto?userid='

for teacherID in range(20007, 600000):
    url = urlPrefix + '%06d' % int(teacherID)
    content = request(url)
    if content != None:
        f = open(str(teacherID) + '.jpg', 'wb')
        f.write(content)
        f.close()
        piccount += 1
        print piccount, ':', teacherID, 'saved!'

print 'Done! ' + piccount + ' pictures downloaded!'
