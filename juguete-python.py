import socket

a = ['GET/HOST', 'aaa', 'bbb', 'ccc']

print(a)

for i in range(0, len(a)):
    a[i].encode('utf-8')

print(a)

b = a[len(a) - 3]

print(b)