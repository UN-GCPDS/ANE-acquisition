# from multiprocessing import Process
# import time
# import threading
# import ray 

# @ray.remote
# def x(x):
#     count=0
#     for c in range(5):
#         count+=1
#     return count
# @ray.remote  
# def y(n):
#     count=0
#     for c in range(5):
#         count-=1
#         print(count)
#     return count

# if __name__ == "__main__":
#     start=time.time()
#     ret_id1 = x.remote("X")
#     ret_id2 = y.remote("X")
#     ret1, ret2 = ray.get([ret_id1, ret_id2])
#     print(ret1,ret2)
#     print(f"tiempo finalizado {time.time()-start}")
# # if __name__ == '__main__':
# #     p1 = Process(target=x, args=('bob',))
# #     p2 = Process(target=y, args=('bob',))
# #     start=time.time()
# #     p1.start()
# #     p2.start()
# #     p1.join()
# #     p2.join()
# #     print(f"tiempo finalizado {time.time()-start}")
import multiprocessing
import time
import datetime

def yourfunction(x):
    return x*3
# if __name__ == '__main__':
#     start=time.time()
#     data=[]
#     list=[x for x in range(20000)]
#     for x in list:
#         data.append(yourfunction(x))
#     for row in data:
#         print(row)
#     print(f"El tiempo que se demora el codigo es {time.time()-start}")
if __name__ == '__main__':
    start=time.time()
    with multiprocessing.Pool(processes=4) as pool:
        data = pool.map(yourfunction, [[x for x in range(10000)],[y for y in range(10000,20000)]])
    for row in data:
        print(row)
    print(f"El tiempo que se demora el codigo es {time.time()-start}")