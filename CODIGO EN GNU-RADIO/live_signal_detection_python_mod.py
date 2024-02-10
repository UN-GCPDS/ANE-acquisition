# this module will be imported in the into your flowgraph
import sys 
f1=88000000
f2=108000000
f=f1
step=1000000

def sweeper(prob_lvl):
    global f
    if prob_lvl:
        f+=step
    if f>=f2:
       f=f1
    else:
        return f