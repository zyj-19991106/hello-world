#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pymssql
import json
from flask import Flask, request, jsonify
from flask_cors import *

def get_connection():
    book_data=pymssql.connect(host='localhost', user='sa', password='123456', database='book_data_base', charset='utf8')
    return book_data
def close_connection(conn):
    conn.close()

global val
app = Flask(__name__)                                               #Flask框架
CORS(app)                                                           #解决跨域问题不能缺少

@app.route('/register/', methods=['POST'])                          #注册
def regiest():
    data = request.get_json('data')
    S_ID=data['S_ID']
    Psw=data['Psw']
    Psw1=data['Psw1']
    if(Psw!=Psw1):
        return jsonify({"statue": 1})       #两次密码不相等
    if(len(Psw)<6 or len(Psw)>20):
        return jsonify({"statue": 2})       #密码在6-20位之间
    sql = "select IsLogin from Student where S_ID = " + "'"+S_ID+"'"
    print(sql)
    cursor.execute(sql)
    data = cursor.fetchone()
    print(data)
    if data==None:
        return jsonify({"statue": 3})       #用户学号不存在
    print(data[0])
    if data[0]=='1':
        return  jsonify({"statue": 4})     #用户已注册
    sql = "update Student set IsLogin = '1',Psw = " +"'" + Psw +"'" + " where S_ID = " + "'" + S_ID + "'"
    print(sql)
    cursor.execute(sql)
    book_data.commit()
    return jsonify({"statue": 2001})        #注册成功


@app.route('/login/', methods=['POST'])                             #登陆
def login():
    data = request.get_json('data')
    global val
    S_ID = data['S_ID']
    val = S_ID
    Psw = data['Psw']
    print(data)
    sql = "select * from Student where S_ID = " + "'" + S_ID + "'"
    print(sql)
    cursor.execute(sql)
    data = cursor.fetchone()
    print(data)
    if data == None:
        return jsonify({"statue": 1})                               #用户学号不存在
    if data[6]=='0':
        return jsonify({"statue": 2})                               #用户未注册
    if data[7] != Psw:
        return jsonify({"statue": 3})                               #密码错误
    else:
        return jsonify({"statue": 2001})                            #登陆成功

@app.route('/approve/',methods=['Post'])                            #教务处绑定
def approve():
    data = request.get_json('data')
    S_ID=data['S_ID']
    Office_ID=data['Office_ID']
    Office_psw=data['Office_psw']
    sql = "update Student set Office_Id =" + "'"+Office_ID+"'," + "Office_psw =" + "'"+Office_psw+"'" + "where S_Id = " + "'" + S_ID + "'"
    print(sql)
    cursor.execute(sql)
    book_data.commit()
    return jsonify({"statue": 2001})                                #绑定成功

@app.route('/changepsw/',methods=['Post'])                          #修改密码
def changepsw():
        data = request.get_json('data')
        S_ID=data['S_ID']
        Psw=data['Opsw']
        Psw1=data['Npsw']
        sql = "select Psw from Student WHERE S_ID =" + "'" + S_ID + "'"
        cursor.execute(sql)
        data = cursor.fetchone()
        if Psw!=data[0]:
            return jsonify({"statue": 1})                           #密码错误
        if Psw==Psw1:
            return jsonify({"statue": 2})                           #新旧密码相同
        Psw=Psw1
        sql = "update Student set Psw =" +"'" + Psw + "'" +" where S_ID = " + "'" + S_ID + "'"
        print(sql)
        cursor.execute(sql)
        book_data.commit()
        return jsonify({"statue": 2001})                            #修改密码成功

@app.route('/findpsw/',methods=['Post'])                            #找回密码
def findpsw():
    data = request.get_json('data')
    Office_ID=data['Office_ID']
    Office_psw=data['Office_psw']
    sql="select Psw,Office_ID,Office_psw from Student WHERE Office_ID="+ "'"+Office_ID+"'" + "and IsLogin='1'"
    # print(sql)
    cursor.execute(sql)
    data = cursor.fetchone()
    # print(data)
    if data==None:
        return jsonify({"statue": 1})                               #学号验证失败
    if data[2]!=Office_psw:
        return jsonify({"statue": 2})                               #教务处密码验证失败
    data=data[0]
    return jsonify({"data":data})

@app.route('/getshopcar_data/',methods=['post'])                            #拿取购物车数据
def getshopcar_data():
    original_data = request.get_json('data')
    SID=original_data['S_ID']
    sql="select * from Shoopcar WHERE Buy_ID="+"'"+SID+"'"
    cursor.execute(sql)
    data=cursor.fetchall()
    if (data == None):
        final_data = {"statue": 2}
        return jsonify(final_data)
    i=0
    final_data={"statue":1}                                                         #正常返回
    list=[]
    if(len(data)==0):
        final_data={"statue":2}                                       #没有搜索到该用户购物车数据
        return jsonify(final_data)
    while i<len(data):
        sql = "select Student.Photo,Sex,Nick_name,College,Book_Name,Price,Book_Photo.Photo,Book.Book_ID from Book,Student,Book_Photo where Book.Sell_ID=Student.S_ID and Book.Book_ID=Book_Photo.Book_ID and Student.S_ID=" + "'" + data[i][2] + "' and Book.Book_ID="+"'"+data[i][1]+"'"
        cursor.execute(sql)
        info = cursor.fetchone()
        result=[info]
        list=list+result
        i+=1
    final_data["data"]=list
    return jsonify(final_data)

@app.route('/del_shopcar/',methods=['post'])                                                 #删除购物车
def del_shopcar():
    original_data = request.get_json('data')
    SID = original_data["S_ID"]
    del_id = original_data["delete_id"]
    sql="DELETE FROM Shoopcar WHERE Book_ID =  "+"'"+del_id +"'"+"and Buy_ID = " +"'"+SID +"'"
    cursor.execute(sql)
    book_data.commit()
    return jsonify({"statue": 1})                                           #删除成功


@app.route('/add_shopcar/',methods=['post'])                                                 #添加购物车
def add_shopcar():
    original_data = request.get_json('data')
    SID = original_data["Sell_ID"]
    book = original_data["Book_ID"]
    BID = original_data["Buy_ID"]
    sql = "insert into Shoopcar values(" + "'" + BID + "','"+book+"','"+SID+"')"
    cursor.execute(sql)
    book_data.commit()
    return jsonify({"statue": 1})                                                              #添加成功

@app.route('/creat_order/',methods=['post'])                                                 #生成订单信息返回前端（未入库）
def creat_order():
    original_data = request.get_json('data')
    SID=original_data["S_ID"]
    Book_id = original_data["book_id"]
    i=0
    list=[]
    final_data = {"statue": 1}
    while i<len(Book_id):
        sql = "select Sell_ID from Shoopcar where Book_ID='" + Book_id[str(i)] + "' and Buy_ID='"+SID+"'"
        cursor.execute(sql)
        s_ID = cursor.fetchone()
        sql = "select Book_name,price,Book_Photo.Photo,Sex,Nick_name,Student.Photo,R_name,R_address,Phone from Student,Book,Book_Photo,Addresses where Student.S_ID=Book.Sell_ID and Book.Book_ID=Book_Photo.Book_ID and Student.S_ID='" + s_ID[0] + "' and Book.book_ID='" + Book_id[str(i)] + "'and A_num= 1"
        cursor.execute(sql)
        info=cursor.fetchone()
        result=[tuple(info)+tuple(Book_id[str(i)])]
        list=list+result
        i += 1
    final_data["data"]=list
    return jsonify(final_data)


@app.route('/creat_address/',methods=['post'])
def creat_address():                                                       #创建地址接口
    original_data = request.get_json('data')
    SID=original_data["S_ID"]
    name=original_data["n_name"]
    tel=original_data["n_tel"]
    ad=original_data["n_ad"]
    print("1")
    print(ad)
    print(type(tel))
    print(name)
    sql = "select count(*) from Addresses where S_ID="+"'"+SID+"'"
    print(sql)
    cursor.execute(sql)
    count = cursor.fetchone()
    num=count[0]+1
    sql = "insert into Addresses values('" + str(num) + "','" + str(num) + "','"+ name + "','" + SID + "','" + ad + "','"+ tel + "')"
    print(sql)
    cursor.execute(sql)
    book_data.commit()
    return jsonify({"statue": 1})                                       #创建成功



@app.route('/get_addresses/',methods=['post'])                                                     #获取用户地址数据
def get_addresses():
    original_data = request.get_json('data')
    S_ID = original_data["S_ID"]
    sql="select R_name,R_address,Phone from Addresses where S_ID="+"'"+S_ID+"'order by A_num"
    print(sql)
    cursor.execute(sql)
    final_data=cursor.fetchall()
    print(final_data)
    if final_data == None:
        return jsonify({"statue": 1})
    else:
        return jsonify({"statue":2,"data":final_data})


@app.route('/del_address/',methods=['post'])                                                 #删除地址
def del_address():
    original_data = request.get_json('data')
    SID = original_data["S_ID"]
    del_id = original_data["del_id"]
    sql = "select count(*) from Addresses where S_ID=" + "'" + SID + "'"
    print(sql)
    cursor.execute(sql)
    count = cursor.fetchone()
    print(count)
    sql="DELETE FROM Addresses WHERE A_num =  "+"'"+del_id +"'"+"and S_ID = " +"'"+SID +"'"
    print(sql)
    cursor.execute(sql)
    book_data.commit()
    sql = "update Addresses set A_num='"+del_id+"' where A_num='"+str(count[0])+"' and S_ID='" + SID + "'"
    print(sql)
    cursor.execute(sql)
    book_data.commit()

    return jsonify({"statue": 1})

@app.route('/change_address/',methods=['post'])                                                 #删除购物车
def change_address():
    original_data = request.get_json('data')
    SID = original_data["S_ID"]
    change_id = original_data["re_id"]
    sql="update Addresses set A_num='0' where A_num='1' and S_ID='"+SID+"'"
    print(sql)
    cursor.execute(sql)
    book_data.commit()
    sql="update Addresses set A_num='1' where A_num="+"'"+change_id+"'"+"and S_ID='"+SID+"'"
    print(sql)
    cursor.execute(sql)
    book_data.commit()
    sql = "update Addresses set A_num='"+change_id+"' where A_num='0' and S_ID='"+SID+"'"
    print(sql)
    cursor.execute(sql)
    book_data.commit()
    return jsonify({"statue": 1})

@app.route('/settlement/',methods=['post'])                                                           #结算（下单）接口
def settlement():
    original_data = request.get_json('data')
    SID = original_data["S_ID"]
    list = original_data["book_id"]
    message=original_data["message"]
    r_type=original_data["delev_way"]
    sum=original_data["sum"]
    i=0
    sql = "select count(*) from Order_Form"
    cursor.execute(sql)
    count = cursor.fetchone()[0]+1
    while i<len(list):
        print(i)
        try:
            sql= "select Sell_ID from Shoopcar where Book_ID='" + list[str(i)] + "'"
            print(sql)
            cursor.execute(sql)
            Sell_ID = cursor.fetchone()[0]
            print(Sell_ID)
            print(message)
            sql="select B_num from Addresses where A_num='1'"
            cursor.execute(sql)
            B_num=cursor.fetchone()
            sql = "insert into Order_Form values(" + "'" + str(count+i) + "',"+ "'" +list[str(i)] + "',"+ "'" + SID + "',"+  "'" + Sell_ID + "',"+  "'" + r_type[str(i)] + "',"+ "1," +  str(B_num[0])+",'" + message[str(i)] + "',"+str(sum)+")"
            print(sql)
            cursor.execute(sql)
            book_data.commit()
            sql="update Book set B_statue='已售' where Book_ID="+"'"+list[str(i)]+"'"
            cursor.execute(sql)
            book_data.commit()
            print(sql)
            sql = "delete  from Shoopcar where Book_ID=" + "'" + list[str(i)] + "'"
            cursor.execute(sql)
            book_data.commit()
            print(sql)
            i+=1
        except:
            print("有问题")
            return jsonify({"statue": 2})                                 #创建订单失败
    return jsonify({"statue": 1})                                         #创建订单成功



@app.route('/mordersearchall/',methods=['post'])
def mordersearchall():#全部订单(下的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    sSQL = "select Order_Form.*,Book_Photo.*,Student.S_name,Student.Photo,Book.Book_name from Student,Book_Photo,Order_Form,Book where Student.S_ID=Order_Form.Sell_ID and Order_Form.Book_Id=Book.Book_ID and Order_Form.Book_Id=Book_Photo.Book_ID and Order_Form.Buy_ID='"+S_ID+"'"
    cursor.execute(sSQL)
    result = cursor.fetchall()
    return jsonify({"data":result,"len":len(result)})

@app.route('/morderfinish/',methods=['Post'])
def morderfinish():#已完成订单(下的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    sSQL = "select Order_Form.*,Book_Photo.*,Student.S_name,Student.Photo,Book.Book_name from Student,Book_Photo,Order_Form,Book where Student.S_ID=Order_Form.Sell_ID and Order_Form.Book_Id=Book_Photo.Book_ID and Order_Form.B_statue=1 and Order_Form.Buy_ID='"+S_ID+"'"
    cursor.execute(sSQL)
    result = cursor.fetchall()
    print(result)
    return jsonify({"data":result,"len":len(result)})

@app.route('/morderdelete/',methods=['Post'])
def morderdelete():#删除订单(下的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    O_ID=data['O_ID']
    print(data)
    sSQL = "delete from Order_Form where Buy_ID='"+S_ID+"' and Order_ID='"+O_ID+"'"
    cursor.execute(sSQL)
    book_data.commit()
    return jsonify({"data":2001})  #删除订单成功

@app.route('/mordersearch1/',methods=['Post'])
def mordersearch1():#待发货订单(下的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    sSQL = "select Order_Form.*,Book_Photo.*,Student.S_name,Student.Photo,Book.Book_name from Student,Book_Photo,Order_Form,Book where Student.S_ID=Order_Form.Sell_ID and Order_Form.Book_Id=Book_Photo.Book_ID and Order_Form.B_statue=2 and Order_Form.Buy_ID='"+S_ID+"'"
    cursor.execute(sSQL)
    result = cursor.fetchall()
    return jsonify({"data":result,"len":len(result)})

@app.route('/mordersearch2/',methods=['Post'])
def mordersearch2():#待收货订单(下的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    sSQL = "select Order_Form.*,Book_Photo.*,Student.S_name,Student.Photo,Book.Book_name from Student,Book_Photo,Order_Form,Book where Student.S_ID=Order_Form.Sell_ID and Order_Form.Book_Id=Book_Photo.Book_ID and Order_Form.B_statue=3 and Order_Form.Buy_ID='"+S_ID+"'"

    cursor.execute(sSQL)
    result = cursor.fetchall()
    print(result)
    return jsonify({"data":result,"len":len(result)})


@app.route('/orderreceive/',methods=['Post'])
def orderreceive():#确认收货(下的)
    data = request.get_json('data')
    S_ID = data['S_ID']  #学号
    O_ID=data['O_ID']    #订单号
    sSQL = "update Order_Form set B_statue=1 where Buy_ID='"+S_ID+"' and Order_ID='"+O_ID+"'"
    cursor.execute(sSQL)
    book_data.commit()
    return jsonify({"data":2001})  #订单确认收货成功



@app.route('/gordersearchall/',methods=['Post'])
def gordersearchall():#全部订单(收到的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    sSQL = "select Order_Form.*,Book_Photo.*,Student.S_name,Student.Photo,Book.Book_name from Student,Book_Photo,Order_Form,Book where Student.S_ID=Order_Form.Buy_ID and Order_Form.Book_Id=Book_Photo.Book_ID and Order_Form.Sell_ID='"+S_ID+"'"
    cursor.execute(sSQL)
    result = cursor.fetchall()
    return jsonify({"data":result,"len":len(result)})

@app.route('/gordersearch1/',methods=['Post'])
def gordersearch1():#待寄件订单(收到的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    sSQL = "select Order_Form.*,Book_Photo.*,Student.S_name,Student.Photo,Book.Book_name from Student,Book_Photo,Order_Form,Book where Student.S_ID=Order_Form.Buy_ID and Order_Form.Book_Id=Book_Photo.Book_ID and Order_Form.B_statue=2 and Order_Form.Sell_ID='"+S_ID+"'"
    cursor.execute(sSQL)
    result = cursor.fetchall()
    print(result)
    return jsonify({"data":result,"len":len(result)})
@app.route('/gordersent/',methods=['Post'])
def gordersent():#寄件(收到的)
    data = request.get_json('data')
    S_ID = data['S_ID']  # 学号
    O_ID = data['O_ID']  # 订单号
    sSQL = "update Order_Form set B_statue=3 where Order_ID='"+O_ID+"'"  #将订单接受状态弄为3，待收货
    cursor.execute(sSQL)
    book_data.commit()
    return jsonify({"data":2001}) #寄件成功

@app.route('/gordersearch2/',methods=['Post'])
def gordersearch2():#待确认订单(收到的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    sSQL = "select Order_Form.*,Book_Photo.*,Student.S_name,Student.Photo,Book.Book_name from Student,Book_Photo,Order_Form,Book where Student.S_ID=Order_Form.Buy_ID and Order_Form.Book_Id=Book_Photo.Book_ID and Order_Form.B_statue=3 and Order_Form.Sell_ID='"+S_ID+"'"
    cursor.execute(sSQL)
    result = cursor.fetchall()
    return jsonify({"data":result,"len":len(result)})

@app.route('/gordersearch3/',methods=['Post'])
def gordersearch3():#已确认订单(收到的)
    data = request.get_json('data')
    S_ID = data['S_ID']
    sSQL = "select Order_Form.*,Book_Photo.*,Student.S_name,Student.Photo,Book.Book_name from Student,Book_Photo,Order_Form,Book where Student.S_ID=Order_Form.Buy_ID and Order_Form.Book_Id=Book_Photo.Book_ID and Order_Form.B_statue=1 and Order_Form.Sell_ID='"+S_ID+"'"
    cursor.execute(sSQL)
    result = cursor.fetchall()
    return jsonify({"data":result,"len":len(result)})

@app.route('/Book_details/',methods=['Post'])     #书的详情
def Book_details():
    data = request.get_json('data')
    book_ID = data["book_ID"]
    sql = "select Book_ID,Book_name,Author,Publish,Price,Condition,Describe from Book where Book_ID = "  + "'" + book_ID + "'"
    cursor.execute(sql)
    data = cursor.fetchone()
    sql = "select Photo from Book_Photo where Book_ID = " + "'" + book_ID + "'"
    cursor.execute(sql)
    Photo = cursor.fetchone()
    sql = "select Sell_ID from Book where Book_ID = " + "'" + book_ID + "'"
    cursor.execute(sql)
    sell_ID = cursor.fetchone()
    sql = "select Nick_name,Photo,Sex from Student where S_ID = " + "'" + sell_ID[0] + "'"
    cursor.execute(sql)
    sell_data = cursor.fetchone()
    data_list = []
    for i in data:
        data_list.append(i)
    data_list.append(Photo[0])
    data_list.append(sell_ID[0])
    for i in sell_data:
        data_list.append(i)
    print(data_list)
    return jsonify({"data": data_list})                                  #[书籍号，书籍名，作家，出版社，价格，新旧程度，详细描述，
                                                                            # 书籍图，卖家学号，卖家昵称，卖家头像,卖家性别]


if __name__ == '__main__':                                          #主函数
        book_data = get_connection()                                #连接数据库
        cursor = book_data.cursor()                                 #创建游标
        app.run(debug=True)                                         #运行URL
