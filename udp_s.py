import socket, threading,sys,hashlib
from time import time

UDP_PACKET_SIZE = 1000
UDP_PORT = 5501
TOKEN_VALID_TIME = 15 * 60 # in sec

path = 'c'

def md5(data):
    m = hashlib.md5()
    m.update(data)
    checksum = m.hexdigest()  # return 32 bytes string

    return checksum



def send_file(sock: socket.socket,address, filename):
    with open(path+'\\'+filename,'rb') as f:
        data = f.read()
    
    chunks = [ data[i:i+UDP_PACKET_SIZE] for i in range(0, len(data), UDP_PACKET_SIZE) ]

    for i,chuck in enumerate(chunks):
        message = str(len(chuck)).zfill(8)
        message += str(i).zfill(8)
        message += md5(chuck)
        message = message.encode()

        message+= chuck

        sock.sendto(message,address)


    print("server done sending")


def server_udp():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', UDP_PORT))

    tokens = {} # key is the token, value is dispatch time

    print("UDP server is up and running")

    while True:
        message, address = server_socket.recvfrom(1024)
            
        if message[:5].decode() == 'TOKEN':
            print('token= ',message[5:].decode())
            tokens[message[5:].decode()] = time()
        elif message[:3].decode() == 'FRQ':
            message = message.decode().split('~')
            token = message[2]
            #if time() - tokens[token] < TOKEN_VALID_TIME:
            name = message[1]
            send_file(server_socket,address ,name)
        



if __name__ == "__main__":
    server_udp()