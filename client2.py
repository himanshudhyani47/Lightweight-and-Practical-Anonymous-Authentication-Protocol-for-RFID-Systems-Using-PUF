# client2.py
import time, socket, sys
import random
def puf(num):
    return int(num*7/13 + 11)

print("\nWelcome to Authentication phase of RFID\n")
print("Initialising....\n")
time.sleep(1)

s = socket.socket()
shost = socket.gethostname()
ip = socket.gethostbyname(shost)
print(shost, "(", ip, ")\n")
host = input(str("Enter server address: "))
name = "Tag"
port = 1234
print("\nTrying to connect to ", host, "(", port, ")\n")
time.sleep(1)
s.connect((host, port))
print("Connected...\n")

s.send(name.encode())
s_name = s.recv(1024)
s_name = s_name.decode()
print(s_name, "has joined the Socket\n")
######################################################################################################################################
f = open("tagBuffer.txt", "r")
tag = f.readline()
f.close()
nounce = str(random.randint(99,999999))
s.send(tag.encode())
s.send(nounce.encode())
######################################################################################################################################
#printing msg2 in rfid side
ci = s.recv(1024)
ci = ci.decode()
ri_xor = s.recv(1024)
ri_xor = ri_xor.decode()
ress = s.recv(1024)
ress = ress.decode()
print("Tag has received ci from server= ",ci)
print("Tag has received Ri* from server= ",ri_xor)
print("Tag has received Ress from server= ",ress)
######################################################################################################################################
ci = int(ci)
ri = puf(ci)
#check ress at client side
ressclient = hash(int(nounce) + 1 or ri or int(ri_xor))
if(ressclient == int(ress)):
    nsclient = ri ^ int(ri_xor)
    print("nsclient= ",nsclient)
    ci1 = hash(int(nounce) + 2 or nsclient or ri)
    ri1 = puf(ci1)
    ki = hash(ri or nsclient)
    ri_xor1 = ki ^ ri1
    rest = hash(int(nounce) + 2 or ki or ri_xor1)
    tid1 = hash(int(tag) or ri1)
    f = open("tagBuffer.txt", "a")
    f.write(str(tid1))
    f.close()
else:
    print("unauthorised reader")
#######################################################################################################################################
#send m3 to server
ri_xor1 = str(ri_xor1)
rest = str(rest)
s.send(ri_xor1.encode())
s.send(rest.encode())


