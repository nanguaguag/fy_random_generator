import requests
import random
import string
import threading

# 26线程压力测试

count = {}


def multithread_scrapy(thread_id):
    count[thread_id] = 0

    for i in range(100):
        response = requests.get('http://127.0.0.1:5001/getNumber')
        print(response.text)
        count[thread_id] += 1
        print(thread_id, count[thread_id], sum(count.values()))


threadA = threading.Thread(target=multithread_scrapy, args='A')
threadB = threading.Thread(target=multithread_scrapy, args='B')
threadC = threading.Thread(target=multithread_scrapy, args='C')
threadD = threading.Thread(target=multithread_scrapy, args='D')
threadE = threading.Thread(target=multithread_scrapy, args='E')
threadF = threading.Thread(target=multithread_scrapy, args='F')
threadG = threading.Thread(target=multithread_scrapy, args='G')
threadH = threading.Thread(target=multithread_scrapy, args='H')
threadI = threading.Thread(target=multithread_scrapy, args='I')
threadJ = threading.Thread(target=multithread_scrapy, args='J')
threadK = threading.Thread(target=multithread_scrapy, args='K')
threadL = threading.Thread(target=multithread_scrapy, args='L')
threadM = threading.Thread(target=multithread_scrapy, args='M')
threadN = threading.Thread(target=multithread_scrapy, args='N')
threadO = threading.Thread(target=multithread_scrapy, args='O')
threadP = threading.Thread(target=multithread_scrapy, args='P')
threadQ = threading.Thread(target=multithread_scrapy, args='Q')
threadR = threading.Thread(target=multithread_scrapy, args='R')
threadS = threading.Thread(target=multithread_scrapy, args='S')
threadT = threading.Thread(target=multithread_scrapy, args='T')
threadU = threading.Thread(target=multithread_scrapy, args='U')
threadV = threading.Thread(target=multithread_scrapy, args='V')
threadW = threading.Thread(target=multithread_scrapy, args='W')
threadX = threading.Thread(target=multithread_scrapy, args='X')
threadY = threading.Thread(target=multithread_scrapy, args='Y')
threadZ = threading.Thread(target=multithread_scrapy, args='Z')

# 启动线程
threadA.start()
threadB.start()
threadC.start()
threadD.start()
threadE.start()
threadF.start()
threadG.start()
threadH.start()
threadI.start()
threadJ.start()
threadK.start()
threadL.start()
threadM.start()
threadN.start()
threadO.start()
threadP.start()
threadQ.start()
threadR.start()
threadS.start()
threadT.start()
threadU.start()
threadV.start()
threadW.start()
threadX.start()
threadY.start()
threadZ.start()
