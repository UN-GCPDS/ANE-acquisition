# this module will be imported in the into your flowgraph

f1 = 77000000
f2 = 108000000
f = f1

step = 100000

def sweeper(prob_lvl):
    global f1, f2, f, step
    if prob_lvl:
        f += step
    if f >= f2: 
        f=f1
    return f