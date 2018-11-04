import networkx as nx
import numpy as np
import random
import time
try:import Queue as qu
except:import queue as qu
from sympy import Symbol,diff,solve,ask,Q


class data:
    graph=nx.DiGraph()

    def __init__(self,file):
        self.name=file
        infile=open(self.name+'.txt')
        buffer=infile.readline()
        if (buffer.find('Directed')==2):flag=1
        elif (buffer.find('Undirected')==2):flag=2
        while buffer[0]=='#':buffer=infile.readline()
        nodeorder={}
        currentorder=0
        if flag==1:
            while buffer:
                [u,v]=buffer.split()
                if u not in nodeorder:
                    nodeorder[u]=currentorder
                    currentorder+=1
                if v not in nodeorder:
                    nodeorder[v]=currentorder
                    currentorder+=1
                self.graph.add_edge(nodeorder[u],nodeorder[v])
                buffer=infile.readline()
        elif flag==2:
            while buffer:
                [u,v]=buffer.split()
                [u,v]=buffer.split()
                if u not in nodeorder:
                    nodeorder[u]=currentorder
                    currentorder+=1
                if v not in nodeorder:
                    nodeorder[v]=currentorder
                    currentorder+=1
                self.graph.add_edge(nodeorder[u],nodeorder[v])
                self.graph.add_edge(nodeorder[v],nodeorder[u])
                buffer=infile.readline()
        infile.close()
        self.x=[a for a in range(0,100)]
        print(self.graph.number_of_nodes(),'\tnodes')
        print(self.graph.number_of_edges(),'\tedges')
        self.p=np.loadtxt(self.name+'_pu.txt').astype(int)
        self.c=[]
        self.t=np.loadtxt(self.name+'_tu.txt')
        self.d = np.linspace(0.1, 1, 10)
        for temp in range(0,self.graph.number_of_nodes()):self.c.append(0.0)

    def cu(self,node):
        if self.p[node]==0:temp=self.t[node]**2
        elif self.p[node]==1:temp=self.t[node]
        elif self.p[node]==2:temp=self.t[node]**0.5
        for budget in self.d:
            if budget>=temp:return budget

    def loadsupergraph(self,alpha):
        infile=open(self.name+'_'+str(alpha)+'.txt')
        self.supergraph=[]
        for temp1 in infile.readlines():
            edge=[]
            for temp2 in temp1.split():edge.append(int(temp2))
            self.supergraph.append(edge)
        infile.close()
        print(len(self.supergraph),'\tsuperedges')
        self.index={}
        for temp1 in range(0,len(self.supergraph)):
            for temp2 in self.supergraph[temp1]:
                if temp2 not in self.index:self.index[temp2]=[temp1]
                else:self.index[temp2].append(temp1)

    def pre_initial(self,budget):
        budget=int(budget*0.2)
        self.seed=[]
        for temp in self.graph.nodes():self.c[temp]=0.0
        seednum=int(budget*1.5)
        degrees=[]
        for temp in self.x:degrees.append(self.graph.degree(temp))
        for temp in range(0,seednum):
            target=np.argmax(degrees)
            self.c[target]=0.667
            self.seed.append(target)
            degrees[target]=-1

    def initial(self,budget):
        budget=int(budget*0.8)
        for temp in self.ns:self.c[temp]=0.0
        seednum=int(budget*1.5)
        degrees=[]
        for temp in self.ns:degrees.append(self.graph.degree(temp))
        for temp in range(0,seednum):
            target=np.argmax(degrees)
            self.c[self.ns[target]]=0.667
            degrees[target]=-1

    def cd(self,times):
        for temp in range(times):
            while True:
                [j1,j2]=random.sample(self.ns,2)
                b=self.c[j1]+self.c[j2]
                low=max(0.0,b-1.0)
                high=min(1.0,b)
                if j1 not in self.index or j2 not in self.index:continue
                if low<high:break
            a1,a2,a3=self.a1a2a3(j1,j2)
            root=self.equation(j1,j2,a1,a2,a3,b,low,high)
            root.append(low);root.append(high)
            best=self.value(a1,a2,a3,j1,j2,b,root)
            self.c[j1]=round(root[best],5)
            self.c[j2]=round(b-root[best],5)

    def value(self,a1,a2,a3,j1,j2,b,root):
        result=[]
        for temp in root:
            if self.p[j1]==0:left=temp**0.5
            elif self.p[j1]==1:left=temp
            elif self.p[j1]==2:left=temp**2
            if self.p[j2]==0:right=(b-temp)**0.5
            elif self.p[j2]==1:right=(b-temp)
            elif self.p[j2]==2:right=(b-temp)**2
            result.append(a1*left+a2*right+a3*left*right)
        return np.argmin(result)

    def equation(self,j1,j2,a1,a2,a3,b,low,high):
        z=Symbol('z')
        if self.p[j1]==0:left=z**0.5
        elif self.p[j1]==1:left=z
        elif self.p[j1]==2:left=z**2
        if self.p[j2]==0:right=(b-z)**0.5
        elif self.p[j2]==1:right=(b-z)
        elif self.p[j2]==2:right=(b-z)**2
        result=solve(diff(a1*left+a2*right+a3*left*right,z))
        root=[]
        for temp in result:
            if ask(Q.real(temp)):
                if temp>=low and temp<=high:root.append(float(temp))
        return root

    def a1a2a3(self,j1,j2):
        index1=self.index[j1];index2=self.index[j2]
        index12=[]
        for temp in index1:
            if temp in index2:index12.append(temp)
        a1=0.0;a2=0.0;a3=0.0
        if self.c[j1]==1.0 and self.c[j2]!=1.0:
            for temp in index2:
                if temp not in index12:a2=a2-self.sigma(temp)
            a2=a2/(1-self.pi(j2))
        elif self.c[j2]==1.0 and self.c[j1]!=1.0:
            for temp in index1:
                if temp not in index12:a1=a1-self.sigma(temp)
            a1=a1/(1-self.pi(j1))
        elif self.c[j1]!=1.0 and self.c[j2]!=1.0:
            for temp in index1:
                result=self.sigma(temp)/(1-self.pi(j1))
                if temp in index12:result/=(1-self.pi(j2))
                a1-=result
            for temp in index2:
                result=self.sigma(temp)/(1-self.pi(j2))
                if temp in index12:result/=(1-self.pi(j1))
                a2-=result
            for temp in index12:a3+=self.sigma(temp)
            a3=a3/(1-self.pi(j1))/(1-self.pi(j2))
        return (a1,a2,a3)

    def sigma(self,edge):
        p=1.0
        for temp in self.supergraph[edge]:
            if temp in self.ns:
                p *= (1 - self.pi(temp))
        return 1.0 - p

    def pi(self,node):
        if self.p[node]==0:return self.c[node]**0.5
        if self.p[node]==1:return self.c[node]
        if self.p[node]==2:return self.c[node]**2

    def propagate(self,alpha):
        total=[]
        for temp in self.ns:
            if random.random()<self.pi(temp):total.append(temp)
        p=qu.Queue()
        for temp in total:p.put(temp)
        while not p.empty():
            head=p.get()
            for temp in self.graph.neighbors(head):
                if temp not in total and random.random()<\
                    alpha/self.graph.in_degree(temp):
                        total.append(temp);p.put(temp)
        return len(total)

    def generate(self,alpha):
        result=self.maxq()*self.graph.number_of_nodes()/len(self.supergraph)
        return round(result,4)

    def save(self):
        stash={}
        for node in self.ns: stash[node] = self.c[node]
        return stash

    def resume(self, stash):
        for node in stash: self.c[node] = stash[node]

    def pre_cd(self,budget):
        self.pre_initial(budget)
        start=time.time()
        for temp in range(50):
            while True:
                [i,j]=random.sample(self.seed,2)
                b=self.c[i]+self.c[j]
                low=max(0.0,b-1.0)
                high=min(1.0,b)
                if low<high:break
            s=[]
            for node in self.seed:
                if node!=i and node!=j and self.t[node]<self.pi(node):
                    s.append(node)
            self.reach(s);self.initial(budget);self.cd(20)
            qs=self.maxq();tempqs=self.save()
            s.append(i);self.reach(s);self.cd(10)
            qsi=self.maxq();tempqsi=self.save()
            self.clean();s.remove(i);s.append(j)
            self.reach(s);self.resume(tempqs);self.cd(10)
            qsj=self.maxq();tempqsj=self.save()
            self.clean();s.append(i);self.reach(s);
            if qsi>=qsj:self.resume(tempqsi)
            else:self.resume(tempqsj)
            self.cd(10);qsij=self.maxq();self.clean()
            a1=qsi-qs;a2=qsj-qs;a3=qsij+qs-qsi-qsj
            root=self.equation(i,j,a1,a2,a3,b,low,high)
            root.append(low);root.append(high)
            best=self.value(a1,a2,a3,i,j,b,root)
            self.c[i]=round(root[best],5)
            self.c[j]=round(b-root[best],5)
        end=time.time()
        outfile=open('4.txt','a')
        outfile.write(self.name+'\tbudget='+str(budget)+'\ttime='\
                      +str(round(end-start))+'s\t')
        outfile.close()

    def pre_generate(self,alpha,budget):
        s=[]
        for node in self.seed:
            if self.t[node]<self.pi(node):s.append(node)
        self.reach(s)
        self.initial(budget)
        self.cd(50)
        result=self.generate(alpha)
        outfile=open('4.txt','a')
        outfile.write('alpha='+str(alpha)+'\tresult='+\
                      str(round(np.mean(result),4))+'\n')
        outfile.close()

    def maxq(self):
        total=0.0
        for i in self.supergraph:
            product=1.0
            for j in i:
                if j in self.ns:product*=(1-self.pi(j))
            total+=(1.0-product)
        return total
    
    def clean(self):
        for i in self.ns:self.c[i]=0.0

    def reach(self,s):
        self.ns=[]
        for i in s:
            for j in self.graph.neighbors(i):
                if j not in self.x and j not in self.ns:self.ns.append(j)

for file in ['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1']:
    dataset=data(file)
    for alpha in [0.6, 0.8, 1.0]:
        dataset.loadsupergraph(alpha)
        for budget in [10, 20, 30, 40, 50]:
            dataset.pre_cd(budget)
            dataset.pre_generate(alpha,budget)
        open('4.txt', 'a').write('\n')