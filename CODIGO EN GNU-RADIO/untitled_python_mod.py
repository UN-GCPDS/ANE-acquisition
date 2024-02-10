# this module will be imported in the into your flowgraph
import sys 
f1=94800000
f2=163000000
f=f1
step=100000

def sweeper(prob_lvl):
    global f
    if (prob_lvl ==0):
        f+=step
    if f>=f2:
        f=f1
    else:
        print(f)
        return f