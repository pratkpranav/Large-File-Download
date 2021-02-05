import socket
import select
import threading
import binascii
# from http.server import BaseHTTPRequestHandler
# from io import BytesIO
#
# class HTTPRequest(BaseHTTPRequestHandler):
#     def __init__(self, request_text):
#         self.rfile = BytesIO(request_text)
#         self.raw_requestline = self.rfile.readline()
#         self.error_code = self.error_message = None
#         self.parse_request()
#
#
#     def send_error(self, code, message):
#         self.error_code = code
#         self.error_message = message

def create_socket():
    try:
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating a socket on my machine
        return sock
    except socket.error as msg:
        print('Socket creation error: ',  str(msg))


def connect_socket(sock,hostone,port):
    try:
        sock.connect((hostone,port))
    except socket.error as msg:
        print('Socket connection error: ' + str(msg))


def download_chunk(sock,st,en):
    global replystr
    global finaltarget
    global datast
    try:
        sock.sendall(b"".join([b'GET /big.txt HTTP/1.1\r\nHost: vayu.iitd.ac.in\r\nConnection: keep-alive\r\nRange: bytes=',str(st).encode(),b'-',str(en).encode(),b'\r\n\r\n']))
        reply=b''
        while select.select([sock], [], [], 3)[0]:
            data = sock.recv(1024)
            if not data: break
            reply += data
        # print(reply)
        # T=BaseHTTPRequestHandler(reply)
        # print(T.error_code)
        print(reply.split(b'\r\n\r\n'))
        headers = reply.split(b'\r\n\r\n')[0]
        # print(headers)
        curr=int(st/(en-st))
        datast[curr]=reply[len(headers) + 4:]
        replystr = b"".join([replystr, reply[len(headers) + 4:]])
        print('File Chunk Downloaded from ' + str(st) + ' to ' + str(en))
    except socket.error as msg:
        print('Socket download error: ' + str(msg))


def close_socket(sock):
    try:
        sock.close()
    except socket.error as msg:
        print('Socket closing error: ' + str(msg))


def thread_op(final_target,port,host,chunk_size):
    global current_start
    global lock
    global reply
    sock=create_socket()
    connect_socket(sock,host,port)
    while current_start < final_target:
        lock.acquire()
        st=current_start
        en=current_start+chunk_size
        current_start=current_start+chunk_size
        lock.release()
        download_chunk(sock,st,en-1)








def main():
    global current_start
    global lock
    global replystr
    global final_target
    global datast
    # print(b"".join([b'GET /big.txt HTTP/1.1\r\nHost: vayu.iitd.ac.in\r\nConnection: keep-alive\r\nRange: bytes=',str(10).encode(),b'-',str(20).encode(),b'\r\n\r\n']))
    lock=threading.Lock()
    current_start=0
    thread_arr=[]
    num_threads=1
    replystr=b''
    port=80
    final_target=20000
    host = '103.27.9.4'  # Vayu's IP address
    chunk_size=100
    ts=int(final_target/chunk_size)
    datast=[b'']*(ts+1)

    for i in range(num_threads):
        t=threading.Thread(target=thread_op,args=(final_target,port,host,chunk_size))
        thread_arr.append(t)

    print('Starting Threads')
    for i in range(num_threads):
        thread_arr[i].start()

    for i in range(num_threads):
        thread_arr[i].join()

    check=b''
    for j in datast:
        check=b"".join([check,j])
    filename='new.txt'
    f = open(filename, 'wb')
    f.write(check)
    f.close()

    print('Done!')





if __name__ == '__main__':
    main()