import socket
import select
import hashlib
import time

def create_socket():
    try:
        global sock
        global hostone
        global hosttwo
        global port
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating a socket on my machine
        hostone='103.27.9.4'#Vayu's IP address
        # hosttwo=''
        port=80 #port to reserve on my machine
    except socket.error as msg:
        print('Socket creation error: ', + str(msg))


def connect_socket():
    try:
        global sock
        global hostone
        global hosttwo
        global port
        sock.connect((hostone,port))
    except socket.error as msg:
        print('Socket connection error: ' + str(msg))


def download_file():
    try:
        global sock
        global hostone
        global port
        print('Attempting Download!!')
        global filename
        global DownloadDir
        # global f
        sock.sendall(b'GET /big.txt HTTP/1.1\r\nHOST: vayu.iitd.ac.in\r\n\r\n')
        reply = b''
        while select.select([sock], [], [], 3)[0]:
            data = sock.recv(1)
            if not data: break
            reply += data
            # print(data)
        # print('File Downloaded')
        headers = reply.split(b'\r\n\r\n')[0]
        # print(headers)
        finalout = reply[len(headers) + 4:]
        f = open(filename, 'wb')
        f.write(finalout)
        f.close()
        print('Checking MD5SUM')
        # checking md5sum
        original_md5='70a4b9f4707d258f559f91615297a3ec'
        with open(filename) as file_to_check:
            data = file_to_check.read()
            data=data.encode('utf-8')
            md5_returned = hashlib.md5(data).hexdigest()
        if original_md5 == md5_returned:
            print ("MD5 verified.")
        else:
            print ("MD5 verification failed!.")



    except socket.error as msg:
        print('download error: ' + str(msg))



def close_socket():
    global sock
    try:
        sock.close()
    except socket.error as msg:
        print('Socket closing error: ' + str(msg))



def main():
    global DownloadDir
    global filename
    DownloadDir=''
    filename='big.txt'

    a = time.time()
    create_socket()
    connect_socket()
    download_file()
    close_socket()
    b=time.time()
    print(b-a)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
