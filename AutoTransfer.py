#coding:utf-8
import re
import requests
import hashlib


def MD5(src):
    '''密码MD5加密'''
    m = hashlib.md5()
    m.update(src)
    return m.hexdigest()

class AutoTransfer():
    def __init__(self, user, password, address):
        '''初始化表单和头部信息'''
        self.address = address
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
            #'Content-Length': '107',
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
            'transfermessage':'',
            'transfersubmit_btn':'true'
            }
        self.transferHeader = { 
            'Host': 'rs.xidian.edu.cn',
            'Connection': 'keep-alive',
            #'Content-Length': '107',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Origin': 'http://rs.xidian.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://rs.xidian.edu.cn/home.php?mod=spacecp&ac=credit&op=transfer',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            }

        
    def Login(self):
        '''模拟登陆睿思'''
        login = self.s.post('http://rs.xidian.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1', data = self.loginData, headers = self.loginHeader)
        print login
        html = self.s.get('http://rs.xidian.edu.cn/forum.php').text
        reg = r'formhash=.*"'
        temp = re.compile(reg)
        query = re.findall(temp,html)
        self.transferData['formhash'] = query[0][9:len(query[0])-1]
        return

    def FetchId(self):
        '''获得回帖用户id'''
        self.Login()
        idList = []
        link = ''
        reg = r'xi2".*</a></s'
        for i in range(1, 6):
            link = self.address + str(i)
            html = self.s.get(link).text           
            temp = re.compile(reg)
            query = re.findall(temp,html)
            if(len(query) == 0):
                break
            idList += [single[single.index('>') + 1:len(single) - 7] for single in query]
            if(len(query) < 10):
                break
        if len(idList) != 0:     
           idList.pop(0) #删掉楼主
        return idList

    def Transfer(self, to, amount):
        '''转账'''
        if(amount == 0): #输入为0则不转
            return
        self.transferData['transferamount'] = str(amount)
        self.transferData['to'] = to
        res = self.s.post('http://rs.xidian.edu.cn/home.php?mod=spacecp&ac=credit&op=transfer&inajax=1', data = self.transferData, headers = self.transferHeader)
        print res
        
    def Work(self):
        '''主要事件循环'''
        toList = self.FetchId()
        if len(toList) == 0:
            print 'nobody, please check your config'
            return
        for to in toList:
            print 'Next one is : %s\n' %(to)
            amount = raw_input('Amount you want to give(0 means pass): ')
            self.Transfer(to, amount)
            print '-----------------------'
        print 'the end'

        
if __name__ == '__main__':
    with open('config.txt', 'r') as f:
        config = f.readlines()
    user = config[0][0:len(config[0]) - 1]
    password = config[1][0:len(config[1]) - 1]
    tid = config[2]
    print user,password,tid
    address = 'http://rs.xidian.edu.cn/forum.php?mod=viewthread&tid=' + str(tid) + '&extra=&page='
    trans = AutoTransfer(user, password, address)
    trans.Work()
