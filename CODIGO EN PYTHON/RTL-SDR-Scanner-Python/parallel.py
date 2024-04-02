#Christopher M. Church
#PhD Candidate, UC Berkeley, History
#Social Science D-Lab, UC Berkeley

import multiprocessing #import multiprocessing library
import time 
def worker(num):
    '''this is the process that will be created in the pool'''
    return num*2 #multiply the current number by two

if __name__ == '__main__': #this is needed to insert the process on Windows -- not needed in Linux
    start=time.time()
    nums = [x for x in range(1000)] #our list to iterate over and multiple each value by 2
    p = multiprocessing.Pool(4) #create a processor pool of 2
    values = p.map(func=worker,iterable=nums) #send the numbers into the process pool
    p.close() #close the process pool
    print(f"El tiempo el cual {time.time() }")
    print (values) #print out the new values