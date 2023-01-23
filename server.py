import socket, random,string
import threading
import sys
import pickle
from tcp_by_size import recv_by_size, send_with_size
from SQL_ORM import ItemORM, Item
from msg import Msg

#path = sys.argv[1]
path = 'data\\items.db'
db = ItemORM(path)
lock = threading.Lock()

UDP_PORT = 5501

def get_dir():
    lock.acquire()
    items = db.get_all_items()
    lock.release()
    return items


def get_shr(fields,ip):
    ok = 'OK'
    print(fields)
    for item in fields:
        i = Item(item[0], item[1], item[2],ip)
        lock.acquire()
        try:
            db.insert_item(i)
        except:
            ok = 'File already exists..'
        lock.release()
    return ok


def generate_token():
    N = 32
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))



def get_lnk(fields):
    lock.acquire()
    try:
        items = db.get_item_ip(fields[0], fields[1])
    except:
        return ''
    lock.release()
    return items


# LNK~NAME~SIZE.


def protocol_build_reply(message,ip):
    code, data = message.code, message.data

    if code == 'DIR':
        return get_dir()
    elif code == 'SHR':
        return get_shr(data,ip)
    elif code == 'LNK':
        return get_lnk(data)
    else:
        print("Unknown message, bye!")
        return 'EXT'


def handle_client(sock: socket.socket, id, addr):
    ip = addr[0]
    print(f'New client id: {id}, from ip: {ip}, port: {addr[1]}')
    while True:

        message = recv_by_size(sock)
        message = pickle.loads(message)

        reply = protocol_build_reply(message,ip)

        send_with_size(sock, pickle.dumps(reply))

        if message.code == "LNK": # send token
            tokens = []
            for ip_udp in reply:
                token = generate_token()
                tokens.append(token)
                udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                token_msg = ("TOKEN"+token).encode()
                udp.sendto(token_msg, (ip_udp[0], UDP_PORT))
                print('sent:   ' ,token_msg)

            send_with_size(sock,pickle.dumps(tokens))

        if message == 'EXT':
            break

    sock.close()


def main():
    threads = []
    srv_sock = socket.socket()

    srv_sock.bind(('0.0.0.0', 5500))

    srv_sock.listen(20)
    print('after listen ... start accepting')

    # next line release the port
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    i = 1
    while True:
        print('Main thread: before accepting ...')
        cli_sock, addr = srv_sock.accept()
        t = threading.Thread(target=handle_client,
                             args=(cli_sock, str(i), addr))
        t.start()
        i += 1
        threads.append(t)
        if i > 100000000:     # for tests change it to 4
            print('Main thread: going down for maintenance')
            break

    all_to_die = True
    print('Main thread: waiting to all clints to die')
    for t in threads:
        t.join()
    srv_sock.close()
    print('Bye ..')


if __name__ == "__main__":
    main()
