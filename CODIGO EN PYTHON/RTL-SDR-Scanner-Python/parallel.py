from multiprocessing import Process
import time
import threading
def f(name):
    count=0
    for i in range(100):
        count+=1
    print(count)



def x(x):
    count=0
    for c in range(5):
        time.sleep(2)
        count+=1
    return count

def y(n):
    count=0
    for c in range(5):
        time.sleep(2)
        count-=1
        print(count)
    return count

if __name__ == '__main__':
    p1 = Process(target=x, args=('bob',))
    p2 = Process(target=y, args=('bob',))
    start=time.time()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"tiempo finalizado {time.time()-start}")