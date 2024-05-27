import pymysql

def GetConn():
    try:
        conn = pymysql.connect(host='localhost',user='root',password='123456',database='bilibili')
    except Exception as e:
        print("连接失败！\n",e)
        print()
    else:
        print("连接成功！\n")
        return conn

def CloseConn(cur,conn):
    try:
        if cur:
            cur.close()
        if conn:
            conn.close()
    except Exception as e:
        print("操作异常！！！\n")
