#!/usr/bin/python
# -*- coding: UTF-8 -*-
import dbs
import mycrypto
import time
import cookie
from log import LogUtile

class UserService():
    def visitCount(self):
        try:
            sql = 'select count from visit where id =1'
            db = dbs.dbmanager()
            results = db.select(sql,'',1)
            return results[0]
        except Exception as e:
            LogUtile().info(str(e),'UserService.visitCount')
            return 'err'
    def iflogin(self,request):
        try:
            # 访问计数开始
            sql = 'update visit set count=count+1 where id=1'
            db = dbs.dbmanager()
            db.update(sql,'')
            # 访问计数结束
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
    def searchbook(self,utype,uvalue,currentpage):
        p=15
        args = '%' +uvalue+ '%'
        sql = "select * from books where bookname like %s order by chan desc limit %s,%s"
        if (utype=='1'): #按书名查询
            sql = "select * from books where bookname like %s order by chan desc limit %s,%s"
        elif (utype=='2'): #按作者查询
            sql = "select * from books where author like %s order by chan desc limit %s,%s"
        else:             # 按简介查询
            sql = "select * from books where introduction like %s order by chan desc limit %s,%s"
        values=[args,(int(currentpage)-1)*p,int(p)]
        try:
            db = dbs.dbmanager()
            results = db.select(sql,values,p)
            if(len(results)==0):
                return 'false'
            reslist = []
            for res in results:
                res['bookname']="《 "+res.get('bookname')+" 》"
                reslist.append(res)
            # 查询页数
            sqlco="select count(1) as countnum from books where bookname like %s"
            if (utype=='1'): #按书名查询
                sqlco = "select count(1) as countnum from books where bookname like %s"
            elif (utype=='2'): #按作者查询
                sqlco = "select count(1) as countnum from books where author like %s"
            else:             # 按简介查询
                sqlco = "select count(1) as countnum from books where introduction like %s"
            valuesco=[args]
            db = dbs.dbmanager()
            pcount=0
            resultco = db.select(sqlco,valuesco,1)
            if(len(resultco)>0):
                pcount=int(resultco[0].get('countnum'))
            # 查询页数结束
            ress ={'res':reslist,'pcount':pcount}
            return ress
        except Exception as e:
            LogUtile().info(str(e),'Bookservice.searchbook')
            return 'err'
    def getBooklist(self,menuid,currentpage):
        sql = 'select * from books where menuid=%s order by chan desc limit %s,%s'
        p=15
        values=[menuid,(int(currentpage)-1)*p,int(p)]
        try:
            db = dbs.dbmanager()
            results = db.select(sql,values,p)
            if(len(results)==0):
                return 'false'
            reslist = []
            for res in results:
                res['bookname']="《 "+res.get('bookname')+" 》"
                reslist.append(res)
            # 查询页数
            sqlco='select count(1) as countnum from books where menuid=%s'
            valuesco=[menuid]
            db = dbs.dbmanager()
            pcount=0
            resultco = db.select(sqlco,valuesco,1)
            if(len(resultco)>0):
                pcount=int(resultco[0].get('countnum'))
            # 查询页数结束
            ress ={'res':reslist,'pcount':pcount}
            return ress
        except Exception as e:
            LogUtile().info(str(e),'Bookservice.getBooklist')
            return 'err'
    def getBooklistByName(self,bookname):
        sql = 'select * from books where bookname=%s order by chan desc'
        values=[bookname]
        try:
            db = dbs.dbmanager()
            results = db.select(sql,values,10)
            reslist = []
            for res in results:
                reslist.append(res)
            ress ={'res':reslist}
            return ress
        except Exception as e:
            LogUtile().info(str(e),'Bookservice.getBooklistByName')
            return 'err'
    def addbook(self,param,username):
        #添加图书
        sql = 'insert into books(bookname,introduction,author,menuid,pan,createtime,owner,source) values (%s,%s,%s,%s,%s,%s,%s,%s)'
        t = time.time()
        n = int(t)
        values=[param.get('bookname'),param.get('introduction'),param.get('author'),param.get('menuid'),param.get('pan'),n,username,param.get('source')]
        try:
            db = dbs.dbmanager()
            db.insert(sql,values)
            return "success"
        except Exception as e:
            LogUtile().info(str(e),'Bookservice.addbook')
            return 'err'
    def addbookcomment(self,param,username):
        #添加图书评论
        sql = 'insert into comments(username,comment,bookid,createtime) values (%s,%s,%s,%s)'
        t = time.time()
        n = int(t)
        values=[username,param.get('comment'),param.get('bookid'),n]
        try:
            db = dbs.dbmanager()
            db.insert(sql,values)
            return "success"
        except Exception as e:
            LogUtile().info(str(e),'Bookservice.addbookcomment')
            return 'err'
    def addchan(self,bookid):
        #添加图书评论
        sql = 'update books set chan=chan+1,updatetime=%s where id=%s'
        t = time.time()
        n = int(t)
        values=[n,bookid]
        try:
            db = dbs.dbmanager()
            db.update(sql,values)
            return "success"
        except Exception as e:
            LogUtile().info(str(e),'Bookservice.addchan')
            return 'err'
    def getBookComments(self,bookid):
        sql = 'select t.*,(select nickname from user where username=t.username) as nickname from comments t where bookid=%s'
        values=[bookid]
        try:
            db = dbs.dbmanager()
            results = db.select(sql,values,10)
            if(len(results)==0):
                return 'false'
            reslist = []
            for res in results:
                res['createtime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res.get('createtime')))
                reslist.append(res)
            ress ={'res':reslist}
            return ress
        except Exception as e:
            LogUtile().info(str(e),'Bookservice.getBookComments')
            return 'err'
if __name__=='__main__':
    user = Bookservice()
    res = user.getBooklist('1-1',1)
    print res
