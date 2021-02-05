import socket
import select
import threading
import time
from collections import deque
import hashlib
import csv
import matplotlib
import matplotlib.pyplot as plt
import sys


def create_socket():
    try:
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating a socket on my machine
        return sock
    except socket.error as msg:
        print('Socket creation error: ',  str(msg))


def connect_socket(sock,hostone,port,t):
    try:
        sock.connect((hostone,port))
    except socket.error as msg:
        print('Socket connection error: ' + str(msg))
        time.sleep(t)
        print('Trying Again in ' + str(t) + ' sec')
        connect_socket(sock,hostone,port,2*t)



def send_msg(st,en):
    global filetodownload
    global host
    finalstring = 'GET /' + filetodownload + ' HTTP/1.1\r\nHost: '+ host + '\r\nConnection: keep-alive\r\nRange: bytes='+str(st)+'-'+str(en)+'\r\n\r\n'
    # print(finalstring)
    return finalstring.encode()
    # return b"".join([b'GET /big.txt HTTP/1.1\r\nHost: vayu.iitd.ac.in\r\nConnection: keep-alive\r\nRange: bytes=',str(st).encode(),b'-',str(en).encode(),b'\r\n\r\n'])


def download_chunk(tid,sock,chunk_queue,factor,startf,endf):
    global full_chunk, str
    global chunk_size
    global num_threads
    global datast
    global host
    global port
    global datath
    global lock
    global prsttime
    global datapt

    try:
        inittime=time.time()
        checkf=0
        mt=chunk_queue.copy()
        while checkf < factor:
            a=int(((checkf+1)*len(chunk_queue))/factor)
            b=int((checkf*len(chunk_queue))/factor)
            # print(a-b)
            # made sure not a large number of requests is sent by the client else, connection could be reset by the peer......
            for i in range(min(100,a-b)):
                st,en=chunk_queue.pop()
                # print((st,en))
                sock.sendall(send_msg(st,en))

            req=(a-b)*chunk_size
            # time.sleep(5)
            checkf+=1
            reply=b''
            head=[]
            # time.sleep(2)
            while select.select([sock], [], [], 3)[0]:
                    # while True:

                data=sock.recv(10240)

                    # print('-------------------------------------------------------------------------')
                if not data: break
                    # print(data)
                reply+=data
            # print(reply)
            exittime = time.time()
            # print(len(reply))
            # print(req)
            # if len(reply) < req:
            #     print('Waiting for 1 second')
            #     time.sleep(1)
            #     download_chunk(sock,mt,factor)
            head=reply.split(b'HTTP/1.1')
            currtime=time.time()
            counttocheck=0
            for i in range(len(datast)):
                if datast[i]!=b'':
                    counttocheck+=1
            datapt.append((currtime-prsttime,counttocheck))
            # print(head)
            headers=[]
            for i in range(len(head)):
                a=head[i]
                # print(a)
                if a != b'':
                    # print(a)
                    b=a.split(b'\r\n\r\n')
                    # print(b)
                    if len(b)>1:
                        headers.append(b[0])
                        headers.append(b[1])
                    else:
                        break
            # headers = reply.split(b'\r\n\r\n')
            datalist=[]
            headerslist=[]
            for i in range(len(headers)):
                if i%2==0:
                    headerslist.append(headers[i].split(b'\r\n'))
                else:
                    datalist.append(headers[i])
            rangelist=[]
            for i in range(len(headerslist)):
                content_size=0
                for j in range(len(headerslist[i])):
                    # j=len(headerslist[i])-ct-1
                    # content_size=0
                    fi=headerslist[i][j].split(b':')
                    # print(fi)
                    if fi[0]==b'Content-Length':
                        se=fi[1].split()[0]
                        # print(se)
                        content_size=int(se.decode('utf-8'))
                        # print(content_size)
                    if fi[0]==b'Content-Range':
                        se=fi[1].split()
                        # print(se)
                        th=se[1].split(b'/')
                        # fo=th.split(b'\\')
                        sting=th[0].decode('utf-8')
                        # print(str)
                        fi=sting.split("-")
                        # print(fi)
                        a=int(fi[0])
                        b=int(fi[1])
                        # print('--------------------------------------')
                        # print(b-a+1)
                        # print(content_size)
                        # checking whether the content size received is correct or not
                        # if b-a+1==chunk_size or b-a+1==full_chunk%chunk_size:
                        # print((a,b))
                        # print('Chunk Downloaded from ' + str(a) + '-' + str(b) + ' by thread id: ' + str(tid))
                        rangelist.append((a,b))
                        # else:
                        #     print('Hello')
                        #     assert(0)
                    if fi[0]==b'Connection':
                        se=fi[1].split()[0]
                        if se == b'close':
                            break


            # print(rangelist)
            # print('---------------------------------')
            # print(len(rangelist))
            # print(len(datalist))
            # print(len(datast))
            for i in range(len(rangelist)):
                st,en=rangelist[i]
                # diff=en-st+1
                # print(datast)
                # print(st,en)
                # print(en)

                index=int(st/chunk_size)
                # print(index)
                # lock.acquire()

                datast[index]=datalist[i]
                # lock.release()

            resend=deque()
            # lint=int((en-st)/chunk_size)+1
            # print('Wait for other Thread to complete their job for 2 secs')
            # time.sleep(2)
            l=int(startf/chunk_size)
            r=int(endf/chunk_size)+1
            # print((startf,endf))

            # print((l,r))
            for i in range(r-l):
                j=int(startf/chunk_size)+i
                # print(j)
                st=startf+i*chunk_size
                en=startf+(i+1)*chunk_size-1
                if len(datast[j])!=chunk_size and len(datast[j])!=full_chunk%chunk_size:
                    resend.append((st,en))

            # if len(datast[ts])!=full_chunk%chunk_size:
            #     st=ts*chunk_size
            #     en=full_chunk
            #     resend.append((st,en))
            # print(resend)
            print('Thread id: ' + str(tid) + ' in time ' + str(exittime-inittime) + ' and Packets downloaded: ' + str(len(mt)-len(resend)))
            datath.append((tid,len(mt)-len(resend),exittime-inittime))
            if len(resend)!=0:
                close_socket(sock)
                thread_op(tid,host,port,resend,startf,endf)


        # # print(headers)
        # data=''
        # for j in len(headers):
        #     data=



    except socket.error as msg:
        print('Socket download error: ' + str(msg) )
        # print(str(msg))
        # print("Error {0}".format(str(msg.args[0])).encode('utf-8', errors='ignore'))

        # download_chunk(sock,mt,2*factor)
        close_socket(sock)
        print('Waiting for 0.1 sec then restarting')
        time.sleep(0.1)
        thread_op(tid,host,port,mt,startf,endf)


def close_socket(sock):
    try:
        sock.close()
    except socket.error as msg:
        print('Socket closing error: ' + str(msg))


def thread_op(tid,host,port,queue,st,en):

    sock=create_socket()
    connect_socket(sock,host,port,1)
    download_chunk(tid,sock,queue,1,st,en)


def main():
    global num_threads
    global full_chunk
    global chunk_size
    global datast
    global host
    global port
    global ts
    global lock
    global filetodownload
    global datath
    global prsttime
    global datapt
    sys.setrecursionlimit(1500)

    with open("t.csv") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        # next(reader, None)  # skip the headers
        data_read = [row for row in reader]

    dataarr=[]
    for i in range(len(data_read)):
        datapt=[]
        prsttime=time.time()
        lock=threading.Lock()
        # full_chunk=6488666
        chunk_size=10000
        num_threads=int(data_read[i][1])
        hostsite=data_read[i][0].split('/')
        # print(st)

        host = hostsite[-2]
        filetodownload=hostsite[-1]
        port=80
        print(host)
        print(filetodownload)
        clientSocket = create_socket()
        connect_socket(clientSocket, host, port, 1)
        string = 'GET /' + filetodownload + ' HTTP/1.1\r\nHOST:' + str(host) + '\r\nConnection: keep-alive\r\nRange: bytes=' + str(0 * 100) + '-' + str(0 * 100 + 99) + '\r\n\r\n'
        # print(string)
        clientSocket.send(string.encode())
        data = clientSocket.recv(4096)

        splt = data.split(b'\r\n\r\n')
        header = splt[0]
        # print(header)
        temp = header.split(b"Content-Range: bytes")
        # print(temp)
        temp = temp[1].split(b"\r\n")[0]
        # print(temp)
        temp = temp.split(b"/")[1]
        # print(temp)
        # print(temp)
        close_socket(clientSocket)
        full_chunk = int(temp.decode())
        chunkpthread= int(full_chunk/(chunk_size*num_threads))
        datath = []
        # print(datath)

        ts=int(full_chunk/chunk_size)
        datast=[b'']*(ts+1)
        # numthreads=1
        thread_arr = []
        queue_arr= []
        count=0
        st=0
        en=chunk_size-1
        current_sz=0

        for i in range(num_threads):
            queue=deque()
            for j in range(chunkpthread):
                queue.append((st,en))
                st+=chunk_size
                en+=chunk_size
                current_sz+=chunk_size
            queue_arr.append(queue)

        while current_sz<full_chunk:
            queue_arr[len(queue_arr)-1].append((st,en))
            st+=chunk_size
            en+=chunk_size
            current_sz+=chunk_size


        # port = 80

        print(full_chunk)
        for i in range(num_threads):
            st1,en1=queue_arr[i].pop()
            st2,en2=queue_arr[i].popleft()
            queue_arr[i].append((st1,en1))
            queue_arr[i].appendleft((st2,en2))
            # print((st2,en1))
            # print
            t=threading.Thread(target=thread_op,args=(i,host,port,queue_arr[i],st2,en1))
            thread_arr.append(t)


        print('Starting Threads')
        a=time.time()
        for i in range(num_threads):
            thread_arr[i].start()

        for i in range(num_threads):
            thread_arr[i].join()
        b=time.time()
        # print(datapt)



        check=b''
        i=0
        for j in datast:
            i+=1
            # print(j)
            if j==b'':
                print(i)
            check=b"".join([check,j])
        filename='new.txt'
        f = open(filename, 'wb')
        f.write(check)
        f.close()



        # plotting graphs
        # bytesdownloaded=[]
        # timespent=[]
        # for j in datapt:
        #     timetaken,bytesdownloadedin=j
        #     bytesdownloaded.append(bytesdownloadedin*chunk_size)
        #     timespent.append(timetaken)
        # plt.plot(timespent,bytesdownloaded)
        # plt.xlabel('Time')
        # plt.ylabel('Bytes Downloaded')
        # plt.legend(['10 Threads, 10 KB Chunks, ' + str(host)])
        # plt.title('Bytes Downloaded vs Time')
        # # plt.axis([0,timespent.max*+2,-10,])
        # plt.savefig('fig'+str(i)+'.png')
        # plt.show()

        dataarr.append((num_threads,b-a))
        print(dataarr)
        print('Checking MD5SUM')
        # checking md5sum
        original_md5 = '70a4b9f4707d258f559f91615297a3ec'
        with open(filename) as file_to_check:
            data = file_to_check.read()
            data = data.encode('utf-8')
            md5_returned = hashlib.md5(data).hexdigest()
        if original_md5 == md5_returned:
            print("MD5 verified.")
        else:
            print("MD5 verification failed!.")

        print('Total Time Taken: ' + str(b-a))
        print(datath)

    # print(dataarr)





if __name__ == '__main__':
    main()