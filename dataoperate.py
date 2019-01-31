import sqlite3
import traceback
class database(object):
    #定义的对象名即为数据库名
    def __init__(self,file=None):
        self.conn=None
        self.cursor=None
        self.__name__=str(self)[str(self).find(".")+1:str(self).find(" ")]
        if file!=None:
            self.connect(file)
    def __del__(self):
        if self.chk_connect()==1:
            self.close()
    def close(self):
        try:self.conn.commit()
        except:
            traceback.print_exc()
        else:
            print(self.__class__.__name__,":提交修改")
        try:self.cursor.close()
        except:
            traceback.print_exc()
            print(self.__class__.__name__,":关闭数据库连接失败-1")
            return 0
        else:
            print("!!!")
            self.cursor=None
            print("!!!")
            print(self.cursor)
            try:self.conn.close()
            except:
                traceback.print_exc()
                print(self.__class__.__name__,":关闭数据库连接失败-2")
                return 0
            else:
                self.conn=None
                return 1

    def chk_connect(self):
        if self.conn==None and self.cursor==None:
            return 0
        else:
            return 1

    def connect(self,file):
        #file 数据库文件名
        self.conn=sqlite3.connect(file)
        self.cursor=self.conn.cursor()
        print(self.__class__.__name__,":创建数据库连接"+file)

    def createtable(self,*,tablename,column_obj,record_list=None,**kw):
        # tablename 表名 string
        # column_obj column对象或column对象的tuple()的返回值
        # record_list 若干个由record对象的values()方法的返回值组成的列表
        #所有参数可由table对象的sqlgenerator()方法返回
        if self.chk_connect()==0:
            print(self.__class__.__name__,":创建数据表%s失败，数据库连接已断开"%(tablename))
        else:
            if isinstance(column_obj,column):
                column_obj=column_obj.tuple()
            self.cursor.execute("create table "+tablename+" "+column_obj)
            for each in record_list:
                self.addrecord(tablename,column_obj,each)
        return 0
    def addrecord(self,*,tablename,cloumn_obj,record_string,**kw):
        #record_string由record对象的values()方法返回
        # column_obj column对象或column对象的tuple()的返回值
        if isinstance(column_obj,column):
            column_obj=column_obj.tuple()
        self.cursor.execute("insert into "+tablename+" "+column_obj+" values "+record_string)
        return 0
    
    def chgrecord(self,*,tablename,**kw)
    #提供多个关键字参数或者字典作为搜索依据，key为字段名，value为对应字段的值，第一对数据作为修改值，其余作为匹配依据
    
class table(object):
    #定义的对象名即为表名
    def __init__(self,*,column_obj=None,record_list=None):
        if column_obj!=None:
            if not(isinstance(column_obj,column)):
                raise "数据类型错误，column_obj应为column对象"
        self.column=column_obj
        self.field=record_list
        self.__name__=str(self)[str(self).find(".")+1:str(self).find(" ")]
        self.name=self.__name__
        self.info={"name":self.name,"column":self.column}
    def get_record(self,**kw):
        #提供一个关键字参数或者一个字典作为搜索依据，key为字段名，value为对应字段的值，函数返回一个record对象
        return 0
class record(object):
    def __init__(self,*,column_obj=None,):
        return None
    def append(self):
        return 0
class column(object):
    #字段列表
    def __init__(self,*arg):
        self.list=list(arg)
    def append(self,*arg):
        for each in arg:
            self.list.append(each)
        return 0
    def empty(self):
        self.list=[]
    def tuple(self):
        return str(tuple(self.list))

    


a=column()
print(a.list)
a.append(1,2,3,4,5)
print(a.list)