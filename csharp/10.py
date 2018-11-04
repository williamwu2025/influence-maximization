from scipy.optimize import linprog
from time import time
import networkx as nx
import os
import psutil
from random import sample
filename = 'soc-LiveJournal1'
infile = open(filename+'.csv', 'r', encoding='utf-8')
[node, edge] = infile.readline().split()
succ = {}
pred = {}
x = []
y = []
for line in open(filename+'_ini100.txt', 'r', encoding='utf-8').readlines():
    x.append(int(line.strip()))
g = nx.DiGraph()
for line in infile.readlines():
    [source, target, degree] = [int(temp) for temp in line.strip().split()]
    g.add_edge(source, target)
    if source in x and target not in x:
        if target not in y:
            y.append(target)
        if source not in succ:
            succ[source] = []
        succ[source].append(target)
        if target not in pred:
            pred[target] = []
        pred[target].append(source)
infile.close()

# degree of nodes
w = {}
for node in x:
    w[node] = g.degree(node)
for node in y:
    w[node] = g.degree(node)

del g

c = []
aeq1 = []
aeq2 = []
for node in x:
    c.append(0)
    aeq1.append(1)
    aeq2.append(0)
for node in y:
    c.append(-w[node])
    aeq1.append(0)
    aeq2.append(1)

length = len(x)+len(y)
aub = []
bub = []
for target in range(len(y)):
    temp = [0] * length
    for source in range(len(x)):
        if x[source] in pred[y[target]]:
            temp[source] = -1
    temp[len(x)+target] = 1
    aub.append(temp)
    bub.append(0)

for b in [10]:
    start = time()
    b1 = 3
    b2 = 7
    beq = [b1, b2]
    ans = linprog(c, aub, bub, [aeq1, aeq2], beq, (0, 1))
    values = list(ans.x)[:100]
    allocation = {}
    for node in range(len(x)):
        allocation[x[node]] = values[node]
    decimal = []
    for node in allocation:
        if allocation[node] != 0 and allocation[node] != 1:
            decimal.append(node)

    # rounding
    while len(decimal) >= 2:
        [u1, u2] = sample(decimal, 2)
        total = allocation[u1] + allocation[u2]
        nr = list(set(succ[u1]).union(set(succ[u2])))
        if total <= 1:
            # situation1
            allocation[u1] = 0
            allocation[u2] = total
            sigma1 = 0
            for target in nr:
                temp = w[target]
                for source in pred[target]:
                    temp *= (1-allocation[source])
                sigma1 += temp
            # situation2
            allocation[u1] = total
            allocation[u2] = 0
            sigma2 = 0
            for target in nr:
                temp = w[target]
                for source in pred[target]:
                    temp *= (1-allocation[source])
                sigma2 += temp
            if sigma1 < sigma2:
                allocation[u1] = 0
                allocation[u2] = total
        else:
            # situation2
            allocation[u1] = total - 1
            allocation[u2] = 1
            sigma1 = 0
            for target in nr:
                temp = w[target]
                for source in pred[target]:
                    temp *= (1 - allocation[source])
                sigma1 += temp
            # situation2
            allocation[u1] = 1
            allocation[u2] = total - 1
            sigma2 = 0
            for target in nr:
                temp = w[target]
                for source in pred[target]:
                    temp *= (1 - allocation[source])
                sigma2 += temp
            if sigma1 < sigma2:
                allocation[u1] = total -1
                allocation[u2] = 1
        if allocation[u1] == 0 or allocation[u1] == 1:
            decimal.remove(u1)
        if allocation[u2] == 0 or allocation[u2] == 1:
            decimal.remove(u2)

    # greedy
    nr = {}
    offset = 11
    for source in allocation:
        if allocation[source] == 1:
            for target in succ[source]:
                nr[target] = w[target]
    # seed = sorted(nr.keys(), key=nr.__getitem__, reverse=True)[offset:b2+offset]
    seed = sorted(nr.keys(), key=nr.__getitem__, reverse=True)
    end = time()
    memory = int(float(psutil.Process(os.getpid()).memory_info().rss)/1024/1024/8)
    outfile = open(filename+str(b)+'.txt', 'w')
    for node in seed:
        outfile.write(str(node)+'\n')
    outfile.write('time='+str(round(end-start, 2))+'memory='+str(memory)+'\n')
    outfile.close()
