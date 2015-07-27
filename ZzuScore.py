# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import urllib
import urllib2

import os
import pygame
from pygame.locals import *

class ZzuScore(object):
    tableHead, classList, termList, titleList, summaryList = [], [], [], [], []
    stuId, stuPwd, htmlText = '', '', ''
    isLogin = False

    def __init__(self, stuId, stuPwd):
        self.stuId = stuId
        self.stuPwd = stuPwd

    def login(self):
        url = 'http://jw.zzu.edu.cn/scripts/qscore.dll/search'
        params = {
            'nianji':self.stuId[:4],
            'xuehao':self.stuId,
            'mima'  :self.stuPwd,
            'selec' :url,
            u'登录'.encode('gb2312'):u'登录'.encode('gb2312')
        }
        data = urllib.urlencode(params).encode('utf-8')
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        resultText = response.read().decode('gb2312')
        keyword = 'href=\"../../glwj/xjgl.html\"'
        if resultText.find(keyword) == -1:
            return '登录失败😟\n请检查你的学号和密码是否正确'
        else:
            self.htmlText = resultText
            self.isLogin = True
        if self.isLogin:
            self.queryAllTerm()

    def parseTermTitle(self):
        rawTitle = re.findall('(?<="center">).*' + self.stuId + '.*(?=</p>)', self.htmlText)[0]
        titleList = rawTitle.split('&nbsp;&nbsp;')
        listLen = len(titleList)
        for i in range(listLen):
            separator = '：' if titleList[i].find('：') != -1 else ':'
            titleList[i] = titleList[i].split(separator)
        return titleList

    def parseTableHead(self):
        self.tableHead = re.findall('(?<=11pt">).*(?=</span>)', self.htmlText)

    def parseClassList(self):
        self.classList = []
        tmpClassList = re.findall('(?<=<tr>).*?(?=</tr>)', self.htmlText)
        for item in tmpClassList:
            self.classList.append(self.parseClassField(item))

    def parseClassField(self, classField):
        className = self.parseClassName(classField)
        classType = self.parseClassType(classField)
        classCredit = self.parseClassCredit(classField)
        classScore = self.parseClassScore(classField)
        classGP = self.parseClassGP(classField)
        return [className, classType, classCredit, classScore, classGP]

    def parseClassName(self, classField):
        return re.findall('(?<="40%">).*?(?=</td>)', classField)[0]

    def parseClassType(self, classField):
        return re.findall('(?<="17%" align="center">).*?(?=</td>)', classField)[0]

    def parseClassCredit(self, classField):
        return re.findall('(?<="15%" align="center">).*?(?=</td>)', classField)[0]

    def parseClassScore(self, classField):
        return re.findall('(?<="15%" align="center">).*?(?=</td>)', classField)[1]

    def parseClassGP(self, classField):
        return re.findall('(?<="15%" align="center">).*?(?=</td>)', classField)[2]

    def parseTermSummaryList(self):
        rawSummary = re.findall('(?<=<font size="2">).*(?=</font>)',self.htmlText)[0]
        summaryList = rawSummary.split('&nbsp;&nbsp;&nbsp;')
        listLen = len(summaryList)
        for i in range(listLen):
            summaryList[i] = summaryList[i].split('： ')
        return summaryList

    def parseOtherTermAddress(self):
        tmp = re.findall('(?<=<font size="2">).*(?=</font>)', self.htmlText)[1]
        termAddrList = re.findall('(?<=<a href=").*?(?=">)', tmp)
        return termAddrList

    def term(self):
        self.titleList.append(self.parseTermTitle())
        self.summaryList.append(self.parseTermSummaryList())
        self.parseClassList()
        return self.classList
    
    def queryTerm(self, termAddr):
        request = urllib2.Request(termAddr)
        response = urllib2.urlopen(request)
        self.htmlText = response.read().decode('gb2312')
        return self.term()

    def queryAllTerm(self):
        self.parseTableHead()
        self.termList.append(self.term())
        termAddrList = self.parseOtherTermAddress()
        listLen = len(termAddrList)
        for i in range(listLen-2, -1, -1):
           self.termList.append(self.queryTerm(termAddrList[i]))

    def getSpace(self, num):
        space = ''
        for i in range(num):
            space += ' '
        return space

    # length displayd on screen, full - width half - angle
    def realLen(self, string):
        strlen = len(string)
        for c in string:
            if ord(c) < 32 or ord(c) > 126:
                strlen += 1
            #if c == 'Ⅱ' or c == 'Ⅳ' or c == 'Ⅰ' or c == 'Ⅲ':
            #    strlen -= 1
        return strlen

    def getTableHead(self, maxLenCol):
        listLen = len(self.tableHead)
        tableHead = self.tableHead
        headResult = ''
        for i in range(listLen):
            padding = maxLenCol[i] - self.realLen(tableHead[i])
            if padding > 0:
                headResult = tableHead[i] + self.getSpace(padding)
        headResult += '\n'
        return headResult

    def list2Table(self, oriList, termNo):
        maxLenCol = [] # max length in column
        minCellLen = 10
        rows = len(oriList)
        cols = len(oriList[0])

        for col in range(cols):
            maxLen = minCellLen
            for row in range(rows):
                itemLen = self.realLen(oriList[row][col])
                maxLen = maxLen if maxLen > itemLen else itemLen
            maxLenCol.append(maxLen)

        for row in oriList:
            for i in range(cols):
                if self.realLen(row[i]) < maxLenCol[i]:
                    row[i] += (self.getSpace(maxLenCol[i] - self.realLen(row[i])))
        result = ''
        result += self.getTermTitle(termNo)
        result += self.getTableHead(maxLenCol)
        result += self.getTermClass(termNo)
        result += self.getTermSummary(termNo)
        return result

    def getTermTable(self, termNo):
        try:
            termNo = int(termNo)
        except:
            return '请输入正确的学期号😝'
        listLen = len(self.termList)
        if termNo > listLen or termNo < 1:
            return '学期号不存在😟'
        termNo = listLen - termNo
        return self.list2Table(self.termList[termNo], termNo)

    # get title by term number
    def getTermTitle(self, termNo):
        titleResult = ''
        termTitle = self.titleList[termNo]
        for item in termTitle:
            titleResult += item[0] + ':' + item[1] + ' '
        titleResult += '\n'
        return titleResult

    # get class by term number
    def getTermClass(self, termNo):
        classResult = ''
        listLen = len(self.termList[termNo])
        for i in range(listLen):
            for classItem in self.termList[termNo][i]:
                classResult += classItem + ' '
            classResult += '\n'
        return classResult

    # get term summary by term number
    def getTermSummary(self, termNo):
        summaryResult = ''
        termSummary = self.summaryList[termNo]
        for item in termSummary:
            summaryResult += item[0] + ':' + item[1] + ' '
        summaryResult += '\n'
        return summaryResult

    def saveTermPic(self, termNo):
        pygame.init()
        textLines = self.getTermTable(termNo).split('\n')
        font = pygame.font.SysFont('SimHei', 15)
        ftext = []
        width, height = 0, 0
        for line in textLines:
            tmp = font.render(line, True, (0, 0, 0), (255, 255, 255))
            tmpWidth, tmpHeight = tmp.get_size()
            width = max(width, tmpWidth)
            height = max(height, tmpHeight)
            ftext.append(tmp)
        surface = pygame.Surface((width, height*len(textLines)))
        surface.fill((255, 255, 255))
        count = 0
        for txt in ftext:
            surface.blit(txt, (0, count*height))
            count += 1
        pygame.image.save(surface, 'grade.jpg')
        
stuId = raw_input("Student ID:")
stuPwd = raw_input("Password:")
zzuScore = ZzuScore(stuId, stuPwd)
result = zzuScore.login()
if zzuScore.isLogin:
    while 1:
        stuTermNo =  input('Please input term number:')
        result = zzuScore.getTermTable(stuTermNo)
        print zzuScore.getTermTable(stuTermNo)
        zzuScore.saveTermPic(stuTermNo)
else:
    print result
