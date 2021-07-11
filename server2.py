import time, socket, sys
import random
import uuid
import mysql.connector
import string
######################################################################################################################################
def findTID(ttid):
    print("Finding TID in Database")
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="rfid"
    )
    mycursor = mydb.cursor()
    sql = "Select * from server where pid ="+ttid
    mycursor.execute(sql)
    records = mycursor.fetchall()
    print("Printing first row of database which contains tid,ci,ri= ",records)
    servertid = records[0][0]
    
    if int(servertid) != int(ttid):
        print("Authentication failed")
    else:
        print("Server has found the Tag in its database")
        return records

######################################################################################################################################
def updateDB(tid1,ci1,ri1,tag):
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="rfid"
    )
    mycursor = mydb.cursor()
    #sql = "update server set pid= '"+tid1+"',cem= '"+ci1+"',rem= '"+ri1+"'where pid= '"+tag+"'"
    sql = """UPDATE server SET cem = %s,rem=%s,pid=%s WHERE pid = %s"""
    val = (ci1,ri1,tid1,tag)
    mycursor.execute(sql,val)
    mydb.commit()
    
######################################################################################################################################    
print("\nWelcome to Authentication phase of RFID\n")
print("Initialising....\n")
time.sleep(1)

s = socket.socket()
host = socket.gethostname()
ip = socket.gethostbyname(host)
port = 1234
s.bind((host, port))
print(host, "(", ip, ")\n")
name = "Server"
           
s.listen(1)
print("\nWaiting for incoming connections...\n")
conn, addr = s.accept()
print("Received connection from ", addr[0], "(", addr[1], ")\n")

s_name = conn.recv(1024)
s_name = s_name.decode()
print(s_name, "has connected to Socket\n")
conn.send(name.encode())
######################################################################################################################################
tag = conn.recv(1024)
tag = tag.decode()
nounce = conn.recv(1024)
nounce = int(nounce.decode())
print("Tag has sent TempID tid= ",tag)
print("Tag has sent count= ",nounce)
records = findTID(tag)
ns = random.randint(99,999999)
ri = int(records[0][2])
ci = records[0][1]
ri_xor = ri ^ ns
ress = hash(nounce + 1 or ri or ri_xor)

########################################################################################################################################
#sending m2 from server to tag
conn.send(ci.encode())
ri_xor = str(ri_xor)
conn.send(ri_xor.encode())
time.sleep(1)
ress = str(ress)
conn.send(ress.encode())
########################################################################################################################################
#recv msg m3
ri_xor1 = conn.recv(1024)
ri_xor1 = ri_xor1.decode()
rest = conn.recv(1024)
rest = rest.decode()
print("Server has received R*i+1= ",ri_xor1)
print("\nServer has received ResT= ",rest)
########################################################################################################################################
ki = hash(ri or ns)
#verify
ri_xor1 = int(ri_xor1)
rest1 = hash(nounce + 2 or ki or ri_xor1)
print("\nCalculated ResT= ",rest1)
if(int(rest) == rest1):
    print("ResT is verified")
    ri1 = ki ^ ri_xor1
    ci1 = hash(nounce + 2 or ns or ri)
    tid1 = hash(int(tag) or ri1)
    print("Updated tag Tid+1 = ",tid1)
    print("Updated challenge ci+1= ",ci1)
    print("Updated response ri+1= ",ri1)
    print("Storing updated tag, challenge, response in database...")
    print("Authentication successfull...")
else:
    print("Authentication failed")
updateDB(int(tid1),int(ci1),int(ri1),int(tag))
