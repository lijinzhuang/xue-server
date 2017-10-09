#!/usr/bin/python
# -*- coding: UTF-8 -*-
import dbs
import mycrypto
import time
import cookie
from log import LogUtile

class UserService():
    def iflogin(self,request):
        try:
            co = cookie.CookieManager()
            username = co.getCookie(request,'xue-username')
            nickname = co.getCookie(request,'xue-nickname')
            if(not username == None and not nickname == None):
                return {'username':username,'nickname':nickname}
            else:
                return 'false'
        except Exception as e:
            LogUtile().info(str(e),'UserService.iflogin')
            return 'false'
    def logout(self,username,response):
        try:
            co = cookie.CookieManager()
            co.delCookie(response,'xue-username')
            co.delCookie(response,'xue-nickname')
        except Exception as e:
            LogUtile().info(str(e),'UserService.logout')
            return 'false'
    def getUser(self,username):
        sql='select * from user where username=%s'
        values=[username]
        try:
            db = dbs.dbmanager()
            results = db.select(sql,values,1)
            return results[0]
        except Exception as e:
            LogUtile().info(str(e),'UserService.getUser')
            return 'err'
    def login(self,username,password,response):
        sql = 'select * from user where username=%s'
        values=[username]
        try:
            db = dbs.dbmanager()
            results = db.select(sql,values,1)
            if(len(results)==0):
                return 'false'
            if(self.check_login(password,results[0].get('password'))):
                results[0].pop('password')
                co = cookie.CookieManager()
                co.setCookie(response,'xue-username',results[0].get('username'))
                co.setCookie(response,'xue-nickname',results[0].get('nickname'))
                return results[0]
            else:
                return 'false'
        except Exception as e:
            LogUtile().info(str(e),'UserService.login')
            return 'err'
    def regist(self,username,password,nickname,phone,response):
        db = dbs.dbmanager()
        try:
            #判断账户是否重复
            sql = 'select * from user where username=%s'
            values=[username]
            results = db.select(sql,values,1,False)
            if(len(results)>0):
                return 'existusername'
            #判断昵称是否重复
            sql = 'select * from user where nickname=%s'
            values=[nickname]
            results = db.select(sql,values,1,False)
            if(len(results)>0):
                return 'existnickname'
            #判断电话是否重复
            sql = 'select * from user where phone=%s'
            values=[phone]
            results = db.select(sql,values,1,False)
            if(len(results)>0):
                return 'existphone'
            #注册用户信息
            sql = 'insert into user(username,password,nickname,phone,createtime) values (%s,%s,%s,%s,%s)'
            mycc = mycrypto.mycrypto()
            dpassword = mycc.encrypt(password)
            t = time.time()
            n = int(t)
            values=[username,dpassword,nickname,phone,n]
            db.insert(sql,values,False)
            #查询是否注册成功
            sql = 'select * from user where username=%s'
            values=[username]
            results = db.select(sql,values,1)
            if(len(results)==0):
                return 'false'
            else:
                co = cookie.CookieManager()
                co.setCookie(response,'xue-username',results[0].get('username'))
                co.setCookie(response,'xue-nickname',results[0].get('nickname'))
                return results[0]
        except Exception as e:
            db.closeconn()
            LogUtile().info(str(e),'UserService.login')
            return 'err'
    def check_login(self,pass1,pass2):
        mycc = mycrypto.mycrypto()
        if(mycc.encrypt(pass1)==pass2):
            return True
        else:
            return False
class Bookservice():
    def getBooklist(self,menuid):
        sql = 'select * from books where menuid=%s order by chan desc'
        values=[menuid]
        try:
            db = dbs.dbmanager()
            results = db.select(sql,values,10)
            if(len(results)==0):
                return 'false'
            reslist = []
            for res in results:
                reslist.append(res)
            ress ={'res':reslist}
            return ress
        except Exception as e:
            LogUtile().info(str(e),'Bookservice.getBooklist')
            return 'err'
if __name__=='__main__':
    user = Bookservice()
    res = user.getBooklist('1-1')
    print res