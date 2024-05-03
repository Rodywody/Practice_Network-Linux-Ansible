import getpass
import telnetlib

HOST = "192.168.1.62" #ip 주소 입력
user = input("Enter your remote account: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Username: ")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")

tn.write(b"en\n")
tn.write(b"conf t\n")
tn.write(b"int l0\n")
tn.write(b"ip add 1.1.1.1 255.255.255.0\n")
tn.write(b"no sh\n")
tn.write(b"end\n")
tn.write(b"sh ip int br\n")
tn.write(b"exit\n")
tn.write(b"wr\n")

print(tn.read_all().decode('ascii'))
