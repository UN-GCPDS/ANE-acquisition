## import dependencies
from time import sleep,time
import dask
from dask import delayed
## calculate square of a number

def calculate_square(x):
    count=0
    for x in x:
        sleep(0.1)
        count+= x**2
    return count

## calculate sum of two numbers
def get_sum(a,b):
    sleep(1)
    return a+b

#---------NORMAL COMPUTING-----------------#
start=time()
## calculate square of first number
x = calculate_square([x for x in range(100)])

## calculate square of second number
y = calculate_square([x for x in range(100)])

## calculate sum of two numbers
z = get_sum(x,y)
print(z,time()-start)

# #-----------USING DASH------------------#
start=time()
x = delayed(calculate_square)([x for x in range(1000)])
y = delayed(calculate_square)([x for x in range(1000)])
z = delayed(get_sum)(x, y)
print(z.compute(),time()-start)