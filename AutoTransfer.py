#coding:utf-8
import re
import sys
import requests
import hashlib
import string

def MD5(src):
    m = hashlib.md5()
    m.update(src)
    return m.hexdigest()

    
class AutoTransfer():
    def __init__(self, user, password, tid):
        '''初始化表单和头部信息'''
        self.idList = []
        self.pidList = []
        self.pageList = []
        self.tid = tid
        self.address = 'http://rs.xidian.edu.cn/forum.php?mod=viewthread&tid=' + self.tid + '&extra=&page='
        self.s = requests.Session()
        self.loginData = {
            'username': user,
            'cookietime': '2592000',
            'password': MD5(password),
            'quickforward': 'yes',
            'handlekey': 'ls'
            }
        self.loginHeader = { 
            'Host': 'rs.xidian.edu.cn',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Origin': 'http://rs.xidian.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://rs.xidian.edu.cn/forum.php',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            }
        self.transferData = {
            'formhash':'',
            'transfersubmit':'true',
            'handlekey':'transfercredit',
            'transferamount':'',
            'to': '',
            'password': password,
            'transfermessage':u'猜番奖励',
            'transfersubmit_btn':'true'
            }
        self.transferHeader = self.loginHeader
        self.transferHeader['Referer'] = 'http://rs.xidian.edu.cn/home.php?mod=spacecp&ac=credit&op=transfer'
        self.commentData = {
            'formhash':'',
            'handlekey': 'comment',
            'message': '',
            'commentsubmit': 'true'
            }
        self.commentHeader = self.loginHeader
        self.commentHeader['Referer'] = 'http://rs.xidian.edu.cn/forum.php?mod=viewthread&tid=' + self.tid

    def Login(self):
        '''模拟登陆睿思'''
        login = self.s.post('http://rs.xidian.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1', data = self.loginData, headers = self.loginHeader)
        print login
        html = self.s.get('http://rs.xidian.edu.cn/forum.php').text
        reg = r'formhash=.*"'
        temp = re.compile(reg)
        query = re.findall(temp,html)
        self.transferData['formhash'] = query[0][9:len(query[0])-1]
        self.commentData['formhash'] = query[0][9:len(query[0])-1]

    def FetchInfo(self):
        '''获得回帖用户id，各楼层pid，楼层所在page'''
        self.Login()
        link = ''
        reg = r'xi2".*</a></s'
        pidReg = r'postnum[0-9]{8,9}'
        for i in range(1, 10):
            link = self.address + str(i)
            html = self.s.get(link).text           
            temp = re.compile(reg)
            pidTemp = re.compile(pidReg)
            query = re.findall(temp,html)
            pidQuery = re.findall(pidTemp,html)
            if(len(query) == 0):
                break
            self.pageList += [str(i) for j in range(0, len(query))]
            self.idList += [single[single.index('>') + 1:len(single) - 7] for single in query]
            self.pidList += [single[7:] for single in pidQuery]
            if(len(query) < 10):#已到最后一页
                break
        if len(self.idList) != 0:     
           self.idList.pop(0) #删掉楼主的相关信息
           self.pidList.pop(0)
           self.pageList.pop(0)

    def Transfer(self, to, amount):
        '''转账'''
        print type(amount)
        if(amount == '0' or amount == '1'): #输入为0或1则不转账
            return
        amount = string.atoi(amount) * 100
        self.transferData['transferamount'] = str(amount)
        self.transferData['to'] = to
        res = self.s.post('http://rs.xidian.edu.cn/home.php?mod=spacecp&ac=credit&op=transfer&inajax=1', data = self.transferData, headers = self.transferHeader)
        print res
    
    def Comment(self, pid, amount, page):
        '''点评'''
        if(amount == '0' or amount == '1'): #输入为0或1则不点评
            return
        self.commentData['message'] = amount + u'个~'
        commentAddress = 'http://rs.xidian.edu.cn/forum.php?mod=post&action=reply&comment=yes&tid='+self.tid+'&pid='+pid+'&extra=&page='+page+'&commentsubmit=yes&infloat=yes&inajax=1'
        res = self.s.post(commentAddress, data = self.commentData, headers = self.commentHeader)
        print res
        
    def Work(self):
        '''主要事件循环'''
        self.FetchId()
        if len(self.idList) == 0:
            print 'nobody, please check the tid'
            return
        for to,pid,page in zip(self.idList,self.pidList,self.pageList):
            print 'Next one is : %s\n' %(to)
            amount = raw_input('Right Num(0 means pass): ')
            self.Transfer(to, amount)
            self.Comment(pid, amount, page)
            print '-----------------------'
        print 'the end'

        
if __name__ == '__main__':
    with open('config.txt', 'r') as f:
        config = f.readlines()
    user = config[0][0:len(config[0]) - 1]
    user = unicode(user, 'gbk')
    password = config[1][0:len(config[1]) - 1]
    tid = config[2]
    trans = AutoTransfer(user, password, str(tid))
    trans.Work()
    
