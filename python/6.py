from time import time
import networkx as nx
import random
import numpy as np
try:import Queue as q
except:import queue as q
from sympy import Symbol, diff, solve, ask, Q


class data:
    graph = nx.DiGraph()

    def __init__(self, file):
        self.name = file
        infile = open(self.name + '.txt')
        buffer = infile.readline()
        if buffer.find('Directed') == 2:
            flag = 1
        elif buffer.find('Undirected') == 2:
            flag = 2
        while buffer[0] == '#':
            buffer = infile.readline()
        order = {}
        current = 0
        if flag == 1:
            while buffer:
                [u, v] = buffer.split()
                if u not in order:
                    order[u] = current
                    current += 1
                if v not in order:
                    order[v] = current
                    current += 1
                self.graph.add_edge(order[u], order[v])
                buffer = infile.readline()
        elif flag == 2:
            while buffer:
                [u, v] = buffer.split()
                if u not in order:
                    order[u] = current
                    current += 1
                if v not in order:
                    order[v] = current
                    current += 1
                self.graph.add_edge(order[u], order[v])
                self.graph.add_edge(order[v], order[u])
                buffer = infile.readline()
        infile.close()
        self.x = [a for a in range(0, 100)]
        print(self.graph.number_of_nodes(), '\tnodes')
        print(self.graph.number_of_edges(), '\tedges')
        self.p = np.loadtxt(self.name + '_pu.txt').astype(int)
        self.t = np.loadtxt(self.name + '_tu.txt')
        self.d = np.linspace(0.1, 1, 10)
        self.c = [0] * self.graph.number_of_nodes()
        self.nx = []
        for i in self.x:
            for j in self.graph.neighbors(i):
                if j not in self.x and j not in self.nx:
                    self.nx.append(j)
        # self.b1 = len(self.x)
        # self.b2 = len(self.nx)

    def loadsupergraph(self, alpha):
        infile = open(self.name + '_' + str(alpha) + '.txt')
        self.supergraph = []
        for temp1 in infile.readlines():
            edge = []
            for temp2 in temp1.split(): edge.append(int(temp2))
            self.supergraph.append(edge)
        infile.close()
        print(len(self.supergraph), '\tsuperedges')
        self.index = {}
        for temp1 in range(0, len(self.supergraph)):
            for temp2 in self.supergraph[temp1]:
                if temp2 not in self.index:
                    self.index[temp2] = [temp1]
                else:
                    self.index[temp2].append(temp1)

    def newlyreached(self, u):
        old = self.ns(self.choose)
        new = self.ns([u])
        self.r = []
        for node in new:
            if node not in old:
                self.r.append(node)

    def ns(self, s):
        ans = []
        for i in s:
            for j in self.graph.neighbors(i):
                if j not in ans and j not in self.x:
                    ans.append(j)
        return ans

    def cu(self, node):
        if self.p[node] == 0:
            temp = self.t[node] ** 2
        elif self.p[node] == 1:
            temp = self.t[node]
        elif self.p[node] == 2:
            temp = self.t[node] ** 0.5
        for budget in self.d:
            if budget >= temp:
                return budget

    def nu(self, node):
        return len(self.index[node])

    def pi(self, node):
        if self.p[node] == 0:
            return self.c[node] ** 0.5
        elif self.p[node] == 1:
            return self.c[node]
        elif self.p[node] == 2:
            return self.c[node] ** 2

    def delete(self, node):
        edges = []
        for temp in self.index[node]:
            edges.append(temp)
        for temp1 in edges:
            for temp2 in self.supergraph[temp1]:
                self.index[temp2].remove(temp1)

    def sigma(self, edge):
        p = 1.0
        for temp in self.supergraph[edge]:
            if temp in self.r:
                p *= (1 - self.pi(temp))
        return 1.0 - p

    def initial(self, u):
        budget = self.cu(u) * self.b2 / self.b1
        if len(self.r) <= budget:
            for i in self.r:
                self.c[i] = 1.0
        elif len(self.r) <= float(budget * 1.5):
            for i in self.r:
                self.c[i] = round(budget / len(self.r), 4)
        seednum = int(budget * 1.5)
        degrees = []
        for node in self.r:
            degrees.append(self.graph.degree(node))
        for node in range(seednum):
            target = np.argmax(degrees)
            self.c[self.r[target]] = 0.667
            degrees[target] = -1

    def clean(self):
        for node in self.r:
            self.c[node]=0.0

    def cd(self, times):
        for temp in range(times):
            while True:
                [j1, j2] = random.sample(self.r, 2)
                b = self.c[j1] + self.c[j2]
                low = max(0.0, b - 1.0)
                high = min(1.0, b)
                if low < high:
                    break
            a1, a2, a3 = self.a1a2a3(j1, j2)
            root = self.equation(j1, j2, a1, a2, a3, b, low, high)
            root.append(low)
            root.append(high)
            best = self.value(a1, a2, a3, j1, j2, b, root)
            self.c[j1] = round(root[best], 5)
            self.c[j2] = round(b - root[best], 5)

    def value(self, a1, a2, a3, j1, j2, b, root):
        result = []
        for temp in root:
            if self.p[j1] == 0:
                left = temp ** 0.5
            elif self.p[j1] == 1:
                left = temp
            elif self.p[j1] == 2:
                left = temp ** 2
            if self.p[j2] == 0:
                right = (b - temp) ** 0.5
            elif self.p[j2] == 1:
                right = (b - temp)
            elif self.p[j2] == 2:
                right = (b - temp) ** 2
            result.append(a1 * left + a2 * right + a3 * left * right)
        return np.argmin(result)

    def equation(self, j1, j2, a1, a2, a3, b, low, high):
        z = Symbol('z')
        if self.p[j1] == 0:
            left = z ** 0.5
        elif self.p[j1] == 1:
            left = z
        elif self.p[j1] == 2:
            left = z ** 2
        if self.p[j2] == 0:
            right = (b - z) ** 0.5
        elif self.p[j2] == 1:
            right = (b - z)
        elif self.p[j2] == 2:
            right = (b - z) ** 2
        result = solve(diff(a1 * left + a2 * right + a3 * left * right, z))
        root = []
        for temp in result:
            if ask(Q.real(temp)):
                if low <= temp <= high:
                    root.append(float(temp))
        return root

    def a1a2a3(self, j1, j2):
        index1 = self.index[j1]
        index2 = self.index[j2]
        index12 = []
        for temp in index1:
            if temp in index2:
                index12.append(temp)
        a1 = 0.0
        a2 = 0.0
        a3 = 0.0
        if self.c[j1] == 1.0 and self.c[j2] != 1.0:
            for temp in index2:
                if temp not in index12:
                    a2 = a2 - self.sigma(temp)
            a2 = a2 / (1 - self.pi(j2))
        elif self.c[j2] == 1.0 and self.c[j1] != 1.0:
            for temp in index1:
                if temp not in index12:
                    a1 = a1 - self.sigma(temp)
            a1 = a1 / (1 - self.pi(j1))
        elif self.c[j1] != 1.0 and self.c[j2] != 1.0:
            for temp in index1:
                result = self.sigma(temp) / (1 - self.pi(j1))
                if temp in index12:
                    result /= (1 - self.pi(j2))
                a1 -= result
            for temp in index2:
                result = self.sigma(temp) / (1 - self.pi(j2))
                if temp in index12:
                    result /= (1 - self.pi(j1))
                a2 -= result
            for temp in index12:
                a3 += self.sigma(temp)
            a3 = a3 / (1 - self.pi(j1)) / (1 - self.pi(j2))
        return a1, a2, a3

    def maxq(self):
        total=0.0
        for i in self.supergraph:
            product=1.0
            for j in i:
                if j in self.r:
                    product *= (1 - self.pi(j))
            total += (1.0 - product)
        return total

    def adaptive(self, budget):
        self.choose = []
        self.seed = []
        self.b1 = budget * 0.2
        self.b2 = budget * 0.8
        self.b1use = 0.0
        self.b2use = 0.0
        start = time()
        while True:
            maxnode = self.maxnode()
            if self.b1 - self.b1use < self.cu(maxnode): break
            if self.b2 - self.b2use < self.cu(maxnode) * self.b2 / self.b1: break
            self.allocate(maxnode)
        end = time()
        result = []
        for times in range(10000):
            result.append(self.propagate(alpha))
        open('6.txt', 'a').write(self.name+'\tbudget='+str(budget)+\
        '\ttime='+str(round(end-start,4))+'s\talpha='+str(alpha)+\
        '\tresult='+str(round(np.mean(result), 4))+'\n')

    def propagate(self, alpha):
        q=Q.Queue()
        total=[]
        for temp in self.seed:
            total.append(temp)
            q.put(temp)
        while not q.empty():
            head=q.get()
            for temp in self.graph.neighbors(head):
                if temp not in total and random.random()<alpha/self.graph.in_degree(temp):
                    total.append(temp)
                    q.put(temp)
        return len(total)

    def allocate(self, node):
        self.c[node] = self.cu(node)
        self.b1use += self.c[node]
        self.b2used += self.c[node] * self.b2 / self.b1
        self.choose.append(node)
        self.newlyreached(node)
        self.initial(node)
        self.cd(50)
        for node in self.r:
            if self.t[node] <= self.pi(node):
                self.seed.append(node)
                self.delete(node)
        self.clean()

    def maxnode(self):
        maxratio = 0.0
        for node in self.x:
            if node in self.choose:
                continue
            self.newlyreached(node)
            self.initial(node)
            self.cd(50)
            ratio = self.maxq() / self.cu(node)
            self.clean()
            if ratio > maxratio:
                maxratio = ratio
                maxnode = node
        return maxnode

files = ['Wiki-Vote', 'CA-CondMat', 'com-dblp.ungraph', 'soc-LiveJournal1']
alphas = [0.6, 0.8, 1.0]
budgets = [10, 20, 30, 40, 50]
for file in files:
    dataset = data(file)
    for alpha in [0.6, 0.8, 1.0]:
        dataset.loadsupergraph(alpha)
        for budget in [10, 20, 30, 40, 50]:
            dataset.adaptive(budget)