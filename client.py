import socket
import threading
import pickle
import sys
import os
import hashlib
from tcp_by_size import recv_by_size, send_with_size
from msg import Msg
from time import time
from udp_s import server_udp,UDP_PACKET_SIZE,UDP_PORT,TOKEN_VALID_TIME,md5

EXIT = False
path = ''
threads = []

UDP_MESSAGE_SIZE = 1048



def send_pickle(sock, data):
    send_with_size(sock, pickle.dumps(data))


def recv_pickle(sock):
    return pickle.loads(recv_by_size(sock))


def get_size(filename):
    return os.path.getsize(path+'\\'+filename)


def get_md5(filename):
    with open(path+"\\"+filename, 'rb') as f:
        data = f.read()

    m = hashlib.md5()
    m.update(data)
    checksum = m.hexdigest()  # return 32 bytes string

    return checksum



def do_action(sock: socket.socket, message: str):
    if message == 'EXT':
        send_pickle(sock, Msg(message))
    elif message == 'DIR':
        send_pickle(sock, Msg(message))
        data = recv_pickle(sock)

        print(f"\n\n\tFile name\t\tSize")
        for i, item in enumerate(data):
            print(f"{i+1}\t{item[0]}\t\t\t{item[1]}")
        print('\n\n')
    elif message == 'SHR':
        data = []
        files = os.listdir(path)
        for file in files:
            data.append((file, get_size(file), get_md5(file)))

        send_pickle(sock, Msg(message, data))
        data = recv_pickle(sock)
        print(data)

    elif message == 'LNK':
        name = input("Enter the item name: ").strip()
        size = int(input("Enter the item size: ").strip())

        send_pickle(sock, Msg(message, (name, size)))
        ip = recv_pickle(sock)
        if ip == '':
            print("file does not exist anymore :( ")

        tokens = pickle.loads(recv_by_size(sock))

        create_clients_udp(ip, tokens, name, size)


def client_tcp(server_ip):
    global EXIT
    sock = socket.socket()
    sock.connect((server_ip, 5500))

    while not EXIT:
        print("\n\n1 - Get files list")
        print("2 - Report the server about the files in the shared folder")
        print("3 - Get a file from other client")
        print("e - To EXIT")
        command = input("Type your command: ")
        if command == 'e':
            EXIT = True
            message = 'EXT'
        elif command == '1':
            message = 'DIR'
        elif command == '2':
            message = 'SHR'
        elif command == '3':
            message = 'LNK'
        else:
            print('Unknown input.... try again')
            continue

        do_action(sock, message)
        print('again')

    sock.close()




def client_udp(ip, token, name, size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"FRQ~{name}~{token}".encode())
    sock.sendto(f"FRQ~{name}~{token}".encode(), (ip[0], UDP_PORT))
    print('sent 3')

    full_data_dict = {}
    if size % UDP_PACKET_SIZE == 0:
        packets_amount = int(size/UDP_PACKET_SIZE)
    else:
        packets_amount = int(size/UDP_PACKET_SIZE) + 1


    while len(list(full_data_dict.keys())) < packets_amount:
        data, addr = sock.recvfrom(UDP_MESSAGE_SIZE)
        p_size = int(data[:8].decode())
        p_id = int(data[8:16].decode())
        checksum = data[16:48].decode()
        data = data[48:]

        
        if len(data) == p_size:
            if md5(data) == checksum:
                full_data_dict[str(p_id)] = data


    full_data = b''
    for i in range(packets_amount):
        full_data += full_data_dict[str(i)]

    with open(name, 'wb') as f:
        f.write(full_data)


def create_clients_udp(ip: list, tokens: list, name, size):
    global threads

    for i in range(len(ip)):
        udp_t = threading.Thread(
            target=client_udp, args=(ip[i], tokens[i], name, size))
        udp_t.start()
        threads.append(udp_t)

    print('done')



        


def main(server_ip):
    global threads
    udp_server_thread = threading.Thread(target=server_udp)
    udp_server_thread.start()
    threads.append(udp_server_thread)

    client_tcp(server_ip)
    for t in threads:
        t.join()


if __name__ == '__main__':
    server_ip = '127.0.0.1'
    if len(sys.argv) == 3:
        server_ip = sys.argv[1]
        path = sys.argv[2]
    else:
        #server_ip = input("enter the server IP: ")
        path = input("enter the shared folder: ")
    main(server_ip)
    #client_udp('127.0.0.1','aaa','liam.txt',16)
