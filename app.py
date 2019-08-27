from flask import Flask, request, render_template, session,redirect,url_for
from datetime import datetime , date,time,timedelta
import sqlite3
from Crypto.Cipher import AES
from binascii import b2a_hex,a2b_hex
import random
import traceback
import importlib

app = Flask(__name__)
app.config['SECRET_KEY']=datetime.now().strftime('%b-%d-%Y %H:%M:%S')
waitinline =0
with open("key","r",encoding="utf-8") as keyf:
    encryptkey=keyf.read()
def getallpage(testname):
    conn=sqlite3.connect("DT.db")
    cursor=conn.cursor()
    cursor.execute("select id,username from userdata where usertype=0")
    userinfo=cursor.fetchall()
    sheet=[]
    for each in userinfo:
        cursor.execute("select * from user"+str(each[0])+" where testname='"+testname+"'")
        data=cursor.fetchall()
        if data!=[]:
            if data[0][3]==0:
                tj="否"
            else:
                tj='是'
            sheet.append((each[0],each[1],data[0][1],data[0][2],tj,data[0][4]))
    return sheet
def getest(testname):
    conn=sqlite3.connect("DT.db")
    cursor=conn.cursor()
    cursor.execute("select id from testdata where testname='"+testname+"'")
    id=cursor.fetchall()
    cursor.execute("select * from test"+str(id[0][0]))
    data=cursor.fetchall()
    test=[(("*",0),("",1),("",1),("10",1),(("添加",),0),("",0))]
    for each in data:
        if each[2]=="filling":
            tp="选择填空"
        else:
            tp="解答"
        test.append(((each[0],0),(tp,1),(each[1],1),(each[3],1),(("更新",),0),("载入成功",0)))
    cursor.close
    conn.close
    return [[("ID",25),("题目类型",100),("题目序号",100),("分值",100),("操作",200),("结果",100)],test]

def modifytest(testname,id,type,questionid,point):
    conn=sqlite3.connect("DT.db")
    cursor=conn.cursor()
    cursor.execute("select id from testdata where testname='"+testname+"'")
    testid=cursor.fetchall()[0][0]
    if type=="选择填空":
        typel="filling"
    else:
        typel="writting"
    if id=="*":
        try:cursor.execute("insert into test"+str(testid)+" (type,questionid,point) values ('"+typel+"',"+str(questionid)+","+str(point)+")")
        except:
            traceback.print_exc()
            result="添加失败"
        if cursor.rowcount!=0:
            result="添加成功"
        else:
            result="添加失败"
        try:
            print("select id from test"+str(testid)+" where questionid="+str(questionid)+" and type='"+typel+"' and point="+str(point))
            cursor.execute("select id from test"+str(testid)+" where questionid="+str(questionid)+" and type='"+typel+"' and point="+str(point))
        except:
            traceback.print_exc()
            result="添加异常"
        else:
            try:result=cursor.fetchall()
            except:result="添加失败"
            else:
                if result==[]:
                    result="添加失败"
                else:
                    column=[("ID",25),("题目类型",100),("题目序号",100),("分值",100),("操作",200),("结果",100)]
                    print(result)
                    result =render_template("search.html",data_list=[((result[0][0],0),(type,1),(questionid,1),(point,1),(("更新",),0),("载入成功",0))],column_list=column,len=len(column))
    else:
        print("update test",testid," set questionid=",questionid,",type='",typel,"point=",point," where id=",id)
        try:cursor.execute("update test"+str(testid)+" set questionid="+str(questionid)+",type='"+typel+"',point="+str(point)+" where id="+id)
        except:
            traceback.print_exc()
            result="添加失败"
        else:
            if cursor.rowcount!=0:
                result="添加成功"
            else:
                result="添加失败"
    try:conn.commit()
    except:pass
    cursor.close
    conn.close
    return result

def submitallpage(testname):
    conn=sqlite3.connect("DT.db")
    cursor=conn.cursor()
    cursor.execute("select id from userdata")
    id=cursor.fetchall()
    for each in id:
        cursor.execute("select submit from user"+str(each[0])+" where testname='"+testname+"'")
        issubmit=cursor.fetchall()
        if issubmit!=[]:
            if issubmit[0][0]==0:
                # savean(each[0],testname)
                scorecalc(str(each[0]),testname)
    cursor.close
    conn.close
    return 1
def encrypt(text,key):
    key=key+'\0'*(16-len(key)%16)
    cryptor=AES.new(key.encode('utf-8'),AES.MODE_CBC,key.encode('utf-8'))
    text=text+'\0'*(16-len(text.encode("utf-8"))%16)
    try:return b2a_hex(cryptor.encrypt(text.encode('utf-8'))).decode('utf-8')
    except:
        traceback.print_exc()
        return "ERROR"
def decrypt(text,key):
    key=key+'\0'*(16-len(key)%16)
    cryptor=AES.new(key.encode('utf-8'),AES.MODE_CBC,key.encode('utf-8'))
    try:return cryptor.decrypt(a2b_hex(text.encode('utf-8'))).decode('utf-8').rstrip('\0')
    except:return "ERROR"
def modifytk(basename,basekey,typel,id,question,answer,scorecalc):
    conn=sqlite3.connect(basename)
    cursor=conn.cursor()
    if id!="*":
        print("update "+typel+" set question='"+question+"',answer='"+encrypt(answer,basekey)+"',scorecalc='"+scorecalc+"' where id="+id)
        try:cursor.execute("update "+typel+" set question='"+question+"',answer='"+encrypt(answer,basekey)+"',scorecalc='"+scorecalc+"' where id="+id)
        except:
            traceback.print_exc()
            i="保存失败"
        else:i="保存成功"
    else:
        print("insert into "+typel+" (question,answer,scorecalc) values ('"+question+"','"+answer+"','"+scorecalc+"')")
        print(decrypt(encrypt(answer,basekey),basekey))
        try:cursor.execute("insert into "+typel+" (question,answer,scorecalc) values ('"+question+"','"+encrypt(answer,basekey)+"','"+scorecalc+"')")
        except:i="添加失败"
        else:
            cursor.execute("select * from "+typel+" where question='"+question+"'")
            u=cursor.fetchall()[0]
            cursor.execute("update info set maxquestionid="+str(u[0])+" where type='"+typel+"'")
            i=render_template("search-tk.html",i=[u[0],u[1],decrypt(u[2],basekey),u[3]])
    try:conn.commit()
    except:i="保存失败"
    cursor.close
    conn.close
    return i
def signin(username,password,encrypwd):
    conn=sqlite3.connect("DT.db")
    cursor= conn.cursor()
    if len(username)<=12:
        cursor.execute("select id,username,password,usertype from userdata where username='"+username+"'")
    userdata=cursor.fetchall()
    cursor.close
    conn.close
    if len(userdata)==0:
        return -1
    elif decrypt(userdata[0][2],encrypwd)==password:
        session['username']=username
        session['usertype']=userdata[0][3]
        return userdata[0][0]
    else:
        return -1
def gettesthistory():
    conn=sqlite3.connect("DT.db")
    cursor= conn.cursor()
    cursor.execute("select testname,answertime,submit from user"+str(session.get('id')))
    re=cursor.fetchall()
    rep=[]
    for each in re:
        if each[2]==0:
            info="正在进行"
        else:
            info="已提交"
        cursor.execute("select timelimit from testdata where testname='"+each[0]+"'")
        timelimit=cursor.fetchall()
        if timelimit!=[]:
            rep.append((each[0],each[1],timelimit[0][0],info))
    cursor.close
    conn.close
    return rep
def getestongoing():
    conn=sqlite3.connect("DT.db")
    cursor= conn.cursor()
    cursor.execute("select testname,createtime,timelimit from testdata where ongoing=1")
    re=cursor.fetchall()
    cursor.close
    conn.close
    return(re)
def testgenerator(userid,testname):
    conn=sqlite3.connect("DT.db")
    cursor= conn.cursor()
    try:cursor.execute("select answertime,submit from user"+userid+" where testname='"+testname+"'")
    except:teststatus=[]
    else:teststatus=cursor.fetchall()
    print(teststatus)
    try:cursor.execute("select id,testbase,timelimit,ongoing from testdata where testname='"+testname+"'" )
    except:
        cursor.close
        conn.close
        traceback.print_exc()
        return []
    else:  
        testinfo=cursor.fetchall()
        if teststatus == []:
            testquestion=getquestion(userid,testname)
            if testquestion==[]:
                cursor.close
                conn.close
                return []
        else:
            print(testinfo)
            if len(testinfo)>0:
                cursor.execute("select id,questionid,type,answer from user"+userid+"test"+str(testinfo[0][0]))
                testquestion=cursor.fetchall()
            else:
                cursor.close
                conn.close
                return []

    #生成试卷
    cursor.execute("select database from basedata where basename='"+testinfo[0][1]+"'")
    baseinfo=cursor.fetchall()
    conn2=sqlite3.connect(baseinfo[0][0])
    cursor2= conn2.cursor()
    test=[]
    print(testquestion)
    for each in testquestion:
        print("select question from "+each[2]+" where id="+str(each[1]))
        cursor2.execute("select question from "+each[2]+" where id="+str(each[1]))
        text=cursor2.fetchall()
        text=text[0][0].replace('<','&lt;')
        text=text.replace('>',"&gt;")
        text=text.replace('\n',"<br>")
        print("select point from test"+str(testinfo[0][0])+" where id="+str(each[0]))
        cursor.execute("select point from test"+str(testinfo[0][0])+" where id="+str(each[0]))
        point=cursor.fetchall()
        print(point)
        test.append((each[0],each[1],text,point[0][0],each[3]))
    cursor2.close
    conn2.close
    cursor.close
    conn.close
    return test
def getquestion(stuid,testname):
    print("该考生首次进入，正在生成试卷")
    conn=sqlite3.connect("DT.db")
    cursor= conn.cursor()
    #获取测试相关信息
    cursor.execute("select id,testbase,timelimit,ongoing from testdata where testname='"+testname+"'" )
    testinfo=cursor.fetchall()
    if   testinfo==[]:
        cursor.close
        conn.close
        return []
    if testinfo[0][3] == 0:
        cursor.close
        conn.close
        return []
    #获取测试题目编号
    cursor.execute("select id,questionid,type from test"+str(testinfo[0][0]))
    questioninfo=cursor.fetchall()
    cursor.execute("select database from basedata where basename='"+testinfo[0][1]+"'")
    database=cursor.fetchall()[0][0]
    cursor.close
    conn.close
    if questioninfo==[]:
        return []
    #生成随机题目编号
    conn=sqlite3.connect(database)
    cursor= conn.cursor()
    testquestion=[]
    for each in questioninfo:
        if each[1]==0:
            cursor.execute("select maxquestionid from info where type='"+each[2]+"'")
            idmax=cursor.fetchall()
            testquestion.append((each[0],random.randint(1,idmax[0][0]),each[2],''))
        else:
            testquestion.append((each[0],each[1],each[2],''))
        
    cursor.close
    conn.close
    #保存试卷
    conn=sqlite3.connect("DT.db")
    cursor=conn.cursor()
    try:cursor.execute("create table user"+stuid+"test"+str(testinfo[0][0])+" (id integer primary key, questionid integer,answer text, type text,score integer)")
    except:pass
    for each in testquestion:
        cursor.execute("insert into user"+stuid+"test"+str(testinfo[0][0])+" (questionid,type,answer) values ("+str(each[1])+",'"+each[2]+"','')")
    #记录考生答卷开始
    cursor.execute("insert into user"+stuid+" (testname,answertime,submit) values ('"+testname+"','"+datetime.now().strftime('%b-%d-%Y %H:%M:%S')+"',0)")
    try:conn.commit()
    except:traceback.print_exc()
    cursor.close
    conn.close
    return testquestion
def scorecalc(id,testname):
    global waitinline
    waitinline=waitinline+1
    conn=sqlite3.connect('DT.db')
    cursor=conn.cursor()
    cursor.execute("select testbase,id from testdata where testname='"+testname+"'")
    testinfo=cursor.fetchall()
    if testinfo==[]:
        cursor.close
        conn.close
        return -1
    testbase=testinfo[0][0]
    cursor.execute("select database,basekey from basedata where basename='"+testbase+"'")
    baseinfo=cursor.fetchall()
    testbase=baseinfo[0][0]
    basekey=decrypt(baseinfo[0][1],encryptkey)
    print("select * from user",id,"test",str(testinfo[0][1]))
    cursor.execute("select * from user"+id+"test"+str(testinfo[0][1]))
    useranswer=cursor.fetchall()
    sum=0
    for each in useranswer:
        cursor.execute("select point from test"+str(testinfo[0][1]))
        point=cursor.fetchall()[0][0]
        score=getstdan(testbase,each[3],str(each[1]),basekey,each[2])
        if type(score)!=type(""):
            sum+=score*point
            score=str(score*point)
        cursor.execute("update user"+id+"test"+str(testinfo[0][1])+" set score="+score+" where id="+str(each[0]))
    cursor.execute("update user"+id+" set grade="+str(sum)+" where testname='"+testname+"'")
    cursor.execute("update user"+id+" set submit=1 where testname='"+testname+"'")
    conn.commit()
    cursor.close
    conn.close
    waitinline=waitinline-1
    return sum
def calc(answer,stdanswer):
    stdanswer=stdanswer.split("\n")
    answer=answer.split("\n")
    point=len(stdanswer)
    print(stdanswer,answer)
    score=0
    for i in range(0,min(len(answer),point)):
        if stdanswer[i].find('&&&')!=-1 or stdanswer[i].find('|||')!=-1 or stdanswer[i].find('!!!')!=-1:
            ptor=0
            print(stdanswer[i])
            for eachor in stdanswer[i].split('|||'):
                print("eachor:",eachor,"\tan:",answer[i])
                if eachor.find('&&&')!=-1  or eachor.find('!!!')!=-1:
                    ptand=1
                    for eachand in eachor.split("&&&"):
                        print("eachand:",eachand,"\tan:",answer[i])
                        a=eachand.replace("!!!","") in answer[i]
                        b="!!!" not in eachand
                        ptand*=(a*b+(not(a+b)))
                    ptor=ptor or ptand
                else:
                   ptor=ptor or (eachor in answer[i])
        else:
            ptor=stdanswer[i]==answer[i]
    score+=ptor
    print("score:",score,"\npoint:",point)
    return score/point

def getstdan(testbase,questiontype,questionid,decryptext,answer):
    conn=sqlite3.connect(testbase)
    cursor=conn.cursor()
    cursor.execute("select answer,scorecalc from "+questiontype+" where id="+questionid)
    data=cursor.fetchall()[0]
    stdanswer=decrypt(data[0],decryptext)
    cursor.close
    conn.close
    print(data[1])
    if data[1]=="standard":
        return calc(answer,stdanswer)
    else:
        try:module=importlib.import_module(data[1])
        except:
            traceback.print_exc()
            return 0
        else:return module.calc(answer,stdanswer)
def init():
    greeting=""
    history=[]
    print(session.get('id'))
    if session.get('id')==None:
        session['id']=0
        print(session.get('id'))
    if session.get('usertype')==None:
        session['usertype']=0
    if session.get('id') != 0:
        statusvi='block'
        loginvi='none'
        nowtime=datetime.now().hour
        if 5<=nowtime<11:
            greeting="早上好"
        elif 11<=nowtime<13:
            greeting="中午好"
        elif 13<=nowtime<18:
            greeting="下午好"
        elif 18<=nowtime<23:
            greeting="晚上好"
        else :
            greeting="夜深了，注意休息"
        history=gettesthistory()
    else:
        statusvi='none'
        loginvi='block'
    if session.get('usertype')==0:
        typevi="none"
    else:
        typevi="block"
    try:testnow_list=getestongoing()
    except:testnow_list=[]
    return({'greeting':greeting,'statusvi':statusvi,'loginvi':loginvi,'testnow_list':testnow_list,'typevi':typevi,'testhistory_list':history})
def savean(id,testname):
    if id<=0:
        return "保存失败"
    conn=sqlite3.connect("DT.db")
    cursor= conn.cursor()
    cursor.execute("select id from testdata where testname='"+testname+"'")
    testid=cursor.fetchall()
    if testid==[]:
        cursor.close
        conn.close
        return "保存失败"
    else:
        cursor.execute("select id from test"+str(testid[0][0]))
        questionid=cursor.fetchall()
        print("mmm:::",questionid)
        for each in questionid:
            text=request.form.get(str(each[0]))
            text=text.replace("'","''")
            print("update user"+str(session.get('id'))+"test"+str(testid[0][0])+" set answer='"+text.replace("\r\n","\n")+"' where id="+str(each[0]))
            try:cursor.execute("update user"+str(session.get('id'))+"test"+str(testid[0][0])+" set answer='"+text.replace("\r\n","\n")+"' where id="+str(each[0]))
            except:
                traceback.print_exc()
                cursor.close
                conn.close
                return "保存失败"
            else: 
                result=cursor.rowcount
                # conn.commit()
                conn.commit()
                if result<=0:
                    cursor.close
                    conn.close
                    return "保存失败" 
    cursor.close
    conn.close
    return "保存成功"
def loadtk(database,basekey):
    conn=sqlite3.connect(database)
    print("database:",database)
    cursor=conn.cursor()
    cursor.execute("select * from info")
    typeinfo=cursor.fetchall()
    type_list=[]
    question_list=[]
    for each in typeinfo:
        if each[0]=="filling":
            typename="选择填空"
        elif each[0]=="writting":
            typename="解答"
        else:
            typename="Unknown"
        type_list.append((typename,each[0]))
        cursor.execute("select * from "+each[0])
        orgquestion=cursor.fetchall()
        questionintype_list=[]
        for i in orgquestion:
            questionintype_list.append((i[0],i[1],decrypt(i[2],basekey),i[3]))
        question_list.append(questionintype_list)
    cursor.close
    conn.close
    return (type_list,question_list)
@app.route('/testedit',methods=["POST"])
def testedit():
    questiontype=request.form.get('题目类型')
    questionid=request.form.get('题目序号')
    id=request.form.get('ID')
    point=request.form.get('分值')
    testname=request.form.get('testname')
    return modifytest(testname,id,questiontype,questionid,point)
@app.route('/istestongoing',methods=["POST"])
def istestongoing():
    testname=request.form.get('testname')
    conn=sqlite3.connect('DT.db')
    cursor=conn.cursor()
    cursor.execute("select ongoing from testdata where testname='"+testname+"'")
    a=cursor.fetchall()[0][0]
    cursor.close
    conn.close
    return str(a)
@app.route("/getwaitin",methods=["POST"])
def waitin():
    global waitinline
    return str(waitinline)    
@app.route('/tksave',methods=["POST"])
def tksave():
    questionid=request.form.get("id")
    question=request.form.get("question").replace("/$","&")
    print("QQQQ:",question)
    question=question.replace("'","''")
    print("Q322QQQ:",question)
    answer=request.form.get("answer").replace("/$","&")
    print("AAAA:",answer)
    answer=answer.replace("/$","&")
    print("AAt5433AA:",answer)
    typel=request.form.get("type")
    basename=request.form.get("basename")
    conn=sqlite3.connect("DT.db")
    scorecalc=request.form.get("scorecalc")
    cursor=conn.cursor()
    print("select database,basekey from basedata where basename='"+basename+"'")
    cursor.execute("select database,basekey from basedata where basename='"+basename+"'")
    data=cursor.fetchall()[0]
    database=data[0]
    basekey=decrypt(data[1],encryptkey)
    cursor.close
    conn.close
    print("tpl:",typel)
    if typel=="选择填空":
        questiontype="filling"
    else:
        questiontype="writting"
    return modifytk(database,basekey,questiontype,questionid,question,answer,scorecalc)

@app.route('/')
@app.route('/signin', methods=['GET'])
def home():
    initatom=init()
    return render_template('home.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],testnow_list=initatom['testnow_list'],typevi=initatom['typevi'],testhistory_list=initatom['testhistory_list'])
@app.route('/admin',methods=["GET","POST"])
def admin():
    initatom=init()
    id=session.get('id')
    if id>0:
        if session.get('usertype')>0:
            return render_template('managecenter.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],testnow_list=initatom['testnow_list'],typevi=initatom['typevi'],manage_list=[("题库管理","添加、删除、查看和修改题库"),("考试管理","添加、开始和结束考试，查看考试结果"),("用户管理","添加、删除和修改学生信息，查看和修改学生答卷状态")])
        else:
            return render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info="权限不足",detail="妄图冒充管理员？门都没有！ˋ( ° ▽、° ) ")
    else:
        return redirect('/')
@app.route('/watch/<typename>',methods=['POST'])
def watch(typename):
    initatom=init()
    if typename=="题库管理":
        try:database=request.form.get('数据库文件名')
        except:
            traceback.print_exc()
            return redirect("/500")
        else:
            basekey=request.form.get('数据库密码')
            rec=loadtk(database,basekey)
            return render_template("tkedit.html",username=session.get('username'),greeting=initatom['greeting'],type_list=rec[0],question_list=rec[1],len=len(rec[0]),basename=request.form.get("题库名"))
    elif typename=="考试管理":
        print(request.form.get('operate'))
        if request.form.get("operate")=="查看":
            try:
                basename = request.form.get('题库')
            except:
                traceback.print_exc()
                return redirect("/500")
            else:
                conn = sqlite3.connect("DT.db")
                cursor = conn.cursor()
                cursor.execute("select database,basekey from basedata where basename='"+basename+"'")
                data = cursor.fetchall()
                rec = loadtk(data[0][0], decrypt(data[0][1], encryptkey))
                testname = request.form.get("测试名称")
                data = getest(testname)
                return render_template("testedit.html", username=session.get('username'), greeting=initatom['greeting'], type_list=rec[0], question_list=rec[1], len2=len(rec[0]), basename=basename, testname=testname, column_list=data[0], data_list=data[1], len1=len(data[0]))
        elif request.form.get('operate')=="成绩":
            getallpage(testname)
            return redirect("/404")


@app.route('/calc/<testname>',methods=['POST'])
def calcs(testname):

    id=session.get("id")
    print(savean(id,testname))
    if scorecalc(str(id),testname)<0:
        initatom=init()
        return  render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info="未知错误",detail="不存在此测试")
    else:
        return redirect('/result/'+testname)
@app.route('/changepwd',methods=['GET','POST'])
def changpwd():
    initatom=init()
    id=session.get('id')
    info=""
    if id<=0:
        return redirect('/')
    try:request.form['Opassword']
    except:return render_template('changepwd.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'])
    else:
        Opassword=request.form.get('Opassword')
        Npassword=request.form.get('Npassword')
        Rpassword=request.form.get('Rpassword')
        if Npassword!=Rpassword or Npassword=='':
            return render_template('changepwd.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],cpwderror="新密码不能为空或两次输入的新密码不一致，请检查后重试")
        conn=sqlite3.connect("DT.db")
        cursor=conn.cursor()
        cursor.execute("select password from userdata where id="+str(id))
        password=decrypt(cursor.fetchall()[0][0],encryptkey)
        if password!=Opassword:
            detail="原密码有误，请检查后重试"
        else:
            try:cursor.execute("update userdata set password='"+encrypt(Npassword,encryptkey)+"' where id="+str(id))
            except:detail="未知错误，请检查后重试"
            else:
                if cursor.rowcount>0:
                    conn.commit()
                    session['id']=0
                    initatom=init()
                    info="修改密码"
                    detail="密码修改成功,请重新登录"
                else:
                    detail="未知错误，请检查后重试"
        if info!="":
            return render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info=info,detail=detail)
        else:
            return render_template('changepwd.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],cpwderror=detail)


@app.route('/result/<testname>',methods=['GET'])
def showresult(testname):
    conn=sqlite3.connect("DT.db")
    cursor=conn.cursor()
    id=str(session.get('id'))
    cursor.execute("select submit from user"+id+" where testname='"+testname+"'")
    submit=cursor.fetchall()
    if submit==[]:
        cursor.close
        conn.close
        return redirect('/test/'+testname)
    elif submit[0][0]==0:
        cursor.close
        conn.close
        return redirect('/test/'+testname)
    else:
        initatom=init()
        cursor.execute("select grade from user"+id+" where testname='"+testname+"'")
        grade=cursor.fetchall()[0][0]
        cursor.execute("select id from testdata where testname='"+testname+"'")
        testid=str(cursor.fetchall()[0][0])
        cursor.execute("select * from user"+id+"test"+testid)
        result=cursor.fetchall()
        test=testgenerator(id,testname)
        print("test:",test)
        cursor.close
        conn.close
        return render_template('result.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],question_list=test,testname=testname,result=result,grade=grade)

@app.route('/admin/<managetool>',methods=['GET','POST'])
def tools(managetool):
    initatom=init()
    id=session.get('id')
    print("managetool:",managetool)
    if id>0:
        if session.get('usertype')>0:
            conn=sqlite3.connect("DT.db")
            cursor=conn.cursor()
            column=[]
            
            if managetool=="题库管理":
                data=[(('*',0),('',1),('',1),('',1),(('添加',),0),('',0))]
                cursor.execute("select id,basename,database,basekey from basedata")
                dataget=cursor.fetchall()
                if dataget!=[]:
                    for each in dataget:
                        data.append(((each[0],0),(each[1],1),(each[2],1),(decrypt(each[3],encryptkey),1),(('更新','查看','删除'),0),('载入完毕',0)))
                column=[("ID",25),("题库名",100),("数据库文件名",150),("数据库密码",100),("操作",250),("结果",70)]
            elif managetool=="考试管理":
                data=[(('*',0),('',1),(datetime.now().strftime("%b-%d-%Y %H:%M:%S"),0),('',1),('',1),('未创建',0),(('添加',),0),('',0))]
                cursor.execute("select * from testdata")
                dataget=cursor.fetchall()
                if dataget!=[]:
                    for each in dataget:
                        if each[5]==0:
                            status="已结束"
                            op="开始"
                        else:
                            status="正在进行"
                            op="结束"
                        data.append(((each[0],0),(each[1],1),(each[2],0),(each[3],1),(each[4],1),(status,0),(('更新',op,'查看','成绩','删除'),0),('载入完毕',0)))
                column=[("ID",25),("测试名称",100),("创建时间",170),("题库",75),("时限",40),("状态",70),("操作",250),("结果",70)]
            elif managetool=="用户管理":
                data=[(('*',0),('',1),('',1),('学生',0),(('添加',),0),('',0))]
                cursor.execute("select * from userdata where usertype=0")
                dataget=cursor.fetchall()
                print("dataget:",dataget)
                if dataget!=[]:
                    for each in dataget:
                        if each[3]==0:
                            quanxian="学生"
                        else:
                            quanxian="管理员"
                        data.append(((each[0],0),(each[1],0),(decrypt(each[2],encryptkey),1),(quanxian,0),(('更新','查看','删除'),0),('载入完毕',0)))
                column=[("ID",25),("用户名",100),("密码",200),("权限",100),("操作",250),("结果",70)]
            print("data:",data)
            return render_template('managetool.html',managetool=managetool,statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],testnow_list=initatom['testnow_list'],typevi=initatom['typevi'],manage_list=[("题库管理","添加、删除、查看和修改题库"),("考试管理","添加、开始和结束考试，查看考试结果"),("用户管理","添加、删除和修改学生信息，查看和修改学生答卷状态")],column_list=column,data_list=data,len=len(data[0]))
        else:
            return render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info="权限不足",detail="妄图冒充管理员？门都没有!(￣▽￣)\"")
    else:
        return redirect('/')

@app.route('/calc/<testname>',methods=['GET'])
def calcwhat(testname):
    initatom=init()
    return  render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info="喵喵喵",detail="你希望我评啥分？")

@app.route('/save/<testname>',methods=['POST'])
def save(testname):
    init()
    return savean(session.get('id'),testname)


@app.route('/save/<testname>',methods=['GET'])
def saveget(testname):
    initatom=init()
    return  render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info="保存失败",detail="你自己知道为什么！")
@app.route('/test/<testname>', methods=['GET','POST'])
def testget(testname):
    initatom=init()
    id=session.get('id')
    conn=sqlite3.connect("DT.db")
    cursor= conn.cursor()  
    timeout=0
    width=0
    try:cursor.execute("select answertime,submit from user"+str(id)+" where testname='"+testname+"'")
    except:pass
    teststatus=cursor.fetchall()
    try:cursor.execute("select id,testbase,timelimit,ongoing from testdata where testname='"+testname+"'" )
    except:pass
    else:
        testinfo=cursor.fetchall() 
        time=testinfo[0][2]*60
        if testinfo!=[] and teststatus!=[]:
            if (datetime.now()-datetime.strptime(teststatus[0][0],'%b-%d-%Y %H:%M:%S'))>=timedelta(0,0,0,0,testinfo[0][2]) or teststatus[0][1]!=0:
                print("mmm",datetime.now()-datetime.strptime(teststatus[0][0],'%b-%d-%Y %H:%M:%S'),"yyy",timedelta(0,0,0,0,testinfo[0][2]))
                timeout=1
            else:
                time=(timedelta(0,0,0,0,testinfo[0][2])-(datetime.now()-datetime.strptime(teststatus[0][0],'%b-%d-%Y %H:%M:%S'))).seconds
        width=time/testinfo[0][2]*5
    cursor.close
    conn.close
    if id>0:
        test=testgenerator(str(id),testname)
        print(test)
        print(len(test))
        if len(test)>0 and timeout==0:
            return render_template('query.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],question_list=test,testname=testname,timeout=time,width=width)
        else:
            return  render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info="测试不存在",detail="当前无此测试或你已经完成此测试")
    else:
        return render_template('home.html',statusvi='none',loginvi='block',username=session.get('username'),greeting='',testnow_list=initatom['testnow_list'],typevi=initatom['typevi'],error="您尚未登录")
    
@app.route('/')
@app.route('/signin',methods=['POST'])
def inhomepost():
    error=''
    username=request.form.get('username')
    password=request.form.get('password')
    id=signin(username,password,encryptkey)
    if id<0:
        error="用户名或密码错误"
        username=''
    elif id>0:
        session['id']=id
        session['username']=username
    else:
        error="您尚未登录"
    initatom=init()
    return render_template('home.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],error=error,testnow_list=initatom['testnow_list'],typevi=initatom['typevi'],testhistory_list=initatom['testhistory_list'])
@app.route('/operate/<managetool>',methods=['POST'])
def operate(managetool):
    if managetool=="题库管理":
        table="basedata"
    elif managetool=="用户管理":
        table="userdata"
    elif managetool=="考试管理":
        table="testdata"
    else:
        return redirect("/404")
    try:opmethod=request.form.get('operate')
    except:return '操作失败'
    else:
        conn=sqlite3.connect("DT.db")
        cursor=conn.cursor()
        print(opmethod)
        if opmethod=="更新":
            if table=="basedata":
                data= "database='"+request.form.get('数据库文件名')+"',basekey='"+encrypt(request.form.get('数据库密码'),encryptkey)+"',basename='"+request.form.get('题库名')+"'"
            elif table=="userdata":
                data="password='"+encrypt(request.form.get('密码'),encryptkey)+"'"
            else:
                data="testname='"+request.form.get('测试名称')+"',timelimit="+request.form.get('时限')+",testbase='"+request.form.get('题库')+"'"
            cursor.execute("update "+table+" set "+data+" where id="+request.form.get("ID"))
            su=cursor.rowcount
            print(su)
            if su>0:
                returnstr="更新成功"
            else:
                returnstr="更新失败"
        elif opmethod==None:
            returnstr= "操作失败"
        elif opmethod=="删除":
            print("delete from "+table+" where id="+request.form.get("ID"))
            cursor.execute("delete from "+table+" where id="+request.form.get("ID"))
            su=cursor.rowcount
            cursor.execute("select name from sqlite_master where type='table' ")
            table_list=cursor.fetchall()
            for each in table_list:
                print("1:",table[0:4]+request.form.get("ID"))
                print("E:",each)
                print("D","drop table "+each[0])
                if each[0].find(table[0:4]+request.form.get("ID"))!=-1:
                    try:cursor.execute("drop table "+each[0])
                    except:traceback.print_exc()
            if su>0:
                returnstr="删除成功"
            else:
                returnstr="删除失败"
        elif opmethod=="添加" or opmethod=="添加并开始":
            if opmethod=="添加并开始": 
                ongoing=1
                ongostr="正在进行"
            else:
                ongoing =0
                ongostr="已结束"
            if table=="basedata":
                column_list=[("ID",25),("题库名",100),("数据库文件名",150),("数据库密码",100),("操作",250),("结果",70)]
                data_list=[(['*',0],[request.form.get('题库名'),1],[request.form.get('数据库文件名'),1],[request.form.get('数据库密码'),1],[('更新','查看','删除',),0],['',0])]
                data= "(basename,database,basekey)","('"+request.form.get('题库名')+"','"+request.form.get('数据库文件名')+"','"+encrypt(request.form.get('数据库密码'),encryptkey)+"')"
                conn2=sqlite3.connect(request.form.get('数据库文件名'))
                cursor2=conn2.cursor()
                try:cursor2.execute("create table filling (id integer primary key autoincrement,question text unique,answer BLOB,scorecalc text)")
                except:pass
                try:cursor2.execute("create table writting (id integer primary key autoincrement,question text unique,answer BLOB,scorecalc text)")
                except:pass
                try:cursor2.execute("create table info (type text unique,maxquestionid integer)")
                except:pass
                try:cursor2.execute("insert into info (type,maxquestionid) values ('filling',0)")
                except:pass
                try:cursor2.execute("insert into info (type,maxquestionid) values ('writting',0)")
                except:pass
                try:conn2.commit()
                except:pass
                cursor2.close
                conn2.close
            elif table=="userdata":
                sheet="(id integer primary key autoincrement,testname text unique,answertime text,submit integer,grade integer)"
                column_list=[("ID",25),("用户名",100),("密码",200),("权限",100),("操作",250),("结果",70)]
                data_list=[(['*',0],[request.form.get('用户名'),0],[request.form.get('密码'),1],["学生",0],[('更新','查看','删除'),0],['载入完毕',0])]
                data="(username,password,usertype)","('"+request.form.get('用户名')+"','"+encrypt(request.form.get('密码'),encryptkey)+"',0)"
            else:
                sheet="(id integer primary key autoincrement,questionid integer,type text,point integer)"
                column_list=[("ID",25),("测试名称",100),("创建时间",170),("题库",100),("时限",40),("状态",70),("操作",250),("结果",70)]
                data_list=[(['*',0],[request.form.get('测试名称'),1],[datetime.now().strftime("%b-%d-%Y %H:%M:%S"),0],[request.form.get('题库'),1],[str(request.form.get('时限')),1],[ongostr,0],[('更新','开始','查看','删除'),0],['',0])]
                data="(testname,createtime,testbase,timelimit,ongoing)","('"+request.form.get('测试名称')+"','"+datetime.now().strftime('%b-%d-%Y %H:%M:%S')+"','"+request.form.get('题库')+"',"+request.form.get('时限')+","+str(ongoing)+")"
            try:cursor.execute("insert into "+table+" "+data[0]+" values "+data[1])
            except:
                su=0
                traceback.print_exc()
            else:su=cursor.rowcount
            print(su)
            print("select id from "+table+" where "+data[0][1:9]+"='"+request.form.get(column_list[1][0])+"'")
            cursor.execute("select id from "+table+" where "+data[0][1:9]+"='"+request.form.get(column_list[1][0])+"'")
            data_list[0][0][0]=cursor.fetchall()[0][0]
            if table!="basedata":
                try:cursor.execute("create table "+table[0:4]+str(data_list[0][0][0])+" "+sheet)
                except:
                    su=0
                    try:cursor.execute("delete from "+table+" where id="+str(data_list[0][0][0]))
                    except:pass
            print(column_list,data_list)
            if su>0:
                returnstr=render_template("search.html",data_list=data_list,column_list=column_list,len=len(column_list),managetool=managetool)
            else:
                returnstr="添加失败"
        elif opmethod=="开始" or opmethod=="结束":
            if opmethod=="开始":
                ongoing=1
            else:
                ongoing=0
                submitallpage(request.form.get("测试名称"))
            cursor.execute("update "+table+" set ongoing="+str(ongoing)+" where id="+request.form.get("ID"))
            su=cursor.rowcount
            if su>0:
                returnstr="操作成功"
            else:
                returnstr="操作失败"
    try:conn.commit()
    except:pass
    cursor.close
    conn.close
    return returnstr
        



@app.route('/signout',methods=['POST','get'])
def outhome():
    session['id']=0
    session['usertype']=0
    initatom=init()
    return render_template('home.html',statusvi='none',loginvi='block',username=session.get('username'),greeting='',error='',testnow_list=initatom['testnow_list'],typevi=initatom['typevi'])
@app.route('/jquery-3.3.1.js',methods=['GET'])
def jq():
    return render_template('jquery-3.3.1.js')
@app.route("/style.css",methods=['get'])
def css():
    return render_template('style.css')
@app.route("/load.gif",methods=['get'])
def loadpic():
    with open("templates\load.gif","br") as pic:
        piccon=pic.read()
    return piccon
@app.errorhandler(404)
def page_not_found(e):
    initatom=init()
    return render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info="咦！(＃°Д°)怎么找不到了",detail="错误：404\n网页不存在，戳我找到回家的路"), 404
@app.route('/500')
@app.errorhandler(500)
def server_error(e):
    initatom=init()
    return render_template('error.html',statusvi=initatom['statusvi'],loginvi=initatom['loginvi'],username=session.get('username'),greeting=initatom['greeting'],typevi=initatom['typevi'],info="抱歉！(⊙﹏⊙) 服务器开了个小差",detail="错误：500\n程序猿又要开始耕作了，让我们先离开这里"), 500
if __name__ == '__main__':
    conn=sqlite3.connect("DT.db")
    cursor= conn.cursor()
    try:cursor.execute("create table userdata (id integer primary key,username text unique,password BLOB,usertype integer)")
    except:print("Aleady exist!")
    else:
        print("检测到首次启动，正在初始化...")
        print("设置管理员账号：")
        name=input("请输入用户名：")
        pwd=input("请输入密码：")
        encryptkey=input("请输入数据库加密密匙：")
        with open("key","w",encoding="utf-8") as keyf:
            keyf.write(encryptkey)
        try:cursor.execute("insert into userdata (username,password,usertype) values ('"+name+"','"+encrypt(pwd,encryptkey)+"',1)")
        except:
            print("未知错误,请删除DT.db后重试")
            input()
            cursor.close
            conn.close
            exit()
        else:cursor.execute("create table user1 (id integer primary key autoincrement,testname text unique,answertime text,submit integer,grade integer)")
        print("创建测试数据库...")
        try:cursor.execute("create table testdata (id integer primary key autoincrement,testname text unique,createtime text,testbase text,timelimit integer,ongoing integer)")
        except:
            print("未知错误,请删除DT.db后重试")
            input()
            cursor.close
            conn.close
            exit()
        print("创建题库数据库...")
        try:cursor.execute("create table basedata (id integer primary key autoincrement,basename text unique,database text unique,basekey BLOB)")
        except:
            print("未知错误,请删除DT.db后重试")
            input()
            cursor.close
            conn.close
            exit()       
        conn.commit()
    cursor.close
    conn.close
    with open("key","r",encoding="utf-8") as keyf:
        encryptkey=keyf.read()
    while True:
        a=input("请输入服务器ip:")
        b=input("请输入服务器端口号:")
        try:app.run(host=a, port=int(b))
        except:
            print("ip或端口号不可用请重试")
    print("")



