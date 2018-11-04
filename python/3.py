import networkx as nx
import random
import time
import numpy as np
try:import Queue as qu
except:import queue as qu
from sympy import Symbol,diff,solve,ask,Q
class data:
    graph=nx.DiGraph();
    def __init__(self,file):
        self.name=file;
        infile=open(self.name+'.txt');
        buffer=infile.readline();
        if buffer.find('Directed')==2:flag=1;
        elif buffer.find('Undirected')==2:flag=2;
        while buffer[0]=='#':buffer=infile.readline();
        nodeorder={};
        currentorder=0;
        if flag==1:
            while buffer:
                [u,v]=buffer.split();
                if u not in nodeorder:
                    nodeorder[u]=currentorder;
                    currentorder+=1;
                if v not in nodeorder:
                    nodeorder[v]=currentorder;
                    currentorder+=1;
                self.graph.add_edge(nodeorder[u],nodeorder[v]);
                buffer=infile.readline();
        elif flag==2:
            while buffer:
                [u,v]=buffer.split();
                [u,v]=buffer.split();
                if u not in nodeorder:
                    nodeorder[u]=currentorder;
                    currentorder+=1;
                if v not in nodeorder:
                    nodeorder[v]=currentorder;
                    currentorder+=1;
                self.graph.add_edge(nodeorder[u],nodeorder[v]);
                self.graph.add_edge(nodeorder[v],nodeorder[u]);
                buffer=infile.readline();
        infile.close();
        self.x=[a for a in range(0,100)];
        print(self.graph.number_of_nodes(),'\tnodes');
        print(self.graph.number_of_edges(),'\tedges');
        self.p=np.loadtxt(self.name+'_pu.txt').astype(int);
        self.c=[];
        for temp in range(0,self.graph.number_of_nodes()):self.c.append(0.0);        

    def loadsupergraph(self,alpha):
        infile=open(self.name+'_'+str(alpha)+'.txt');
        self.supergraph=[];
        for temp1 in infile.readlines():
            edge=[];
            for temp2 in temp1.split():edge.append(int(temp2));
            self.supergraph.append(edge);
        infile.close();
        print(len(self.supergraph),'\tsuperedges');
        self.index={};
        self.seed=[];
        for temp1 in range(0,len(self.supergraph)):
            for temp2 in self.supergraph[temp1]:
                if temp2 not in self.index:self.index[temp2]=[temp1];
                else:self.index[temp2].append(temp1);

    def delete(self,node):
        edges=self.index[node];
        for temp1 in edges:
            for temp2 in self.supergraph[temp1]:self.index[temp2].remove(temp1);

    def initial(self,budget):
        for temp in self.x: self.c[temp] = 0.0
        seednum = int(budget * 1.6)
        degrees = []
        for temp in self.x: degrees.append(self.graph.degree(temp));
        for temp in range(0, seednum):
            target = np.argmax(degrees)
            self.c[target] = 0.625
            degrees[target] = -1
        outfile=open('3.txt','a')
        outfile.write(self.name+'\tbudget='+str(budget)+'\t')
        outfile.close()

    def cd(self,times):
        start=time.time()
        for temp in range(times):
            while True:
                j1=random.randint(0,99)
                j2=random.randint(0,99)
                b=self.c[j1]+self.c[j2]
                low=max(0.0,b-1.0)
                high=min(1.0,b)
                if low<high:break;
            a1,a2,a3=self.a1a2a3(j1,j2)
            root=self.equation(j1,j2,a1,a2,a3,b,low,high)
            root.append(low);root.append(high)
            best=self.value(a1,a2,a3,j1,j2,b,root)
            self.c[j1]=round(root[best],5)
            self.c[j2]=round(b-root[best],5)
        end=time.time()
        outfile=open('3.txt','a')
        outfile.write('time='+str(round(end-start))+'s\t')
        outfile.close()

    def value(self,a1,a2,a3,j1,j2,b,root):
        result=[];
        for temp in root:
            if self.p[j1]==0:left=temp**0.5;
            elif self.p[j1]==1:left=temp;
            elif self.p[j1]==2:left=temp**2;
            if self.p[j2]==0:right=(b-temp)**0.5;
            elif self.p[j2]==1:right=(b-temp);
            elif self.p[j2]==2:right=(b-temp)**2;
            result.append(a1*left+a2*right+a3*left*right);
        return np.argmin(result);

    def equation(self,j1,j2,a1,a2,a3,b,low,high):
        z=Symbol('z');
        if self.p[j1]==0:left=z**0.5;
        elif self.p[j1]==1:left=z;
        elif self.p[j1]==2:left=z**2;
        if self.p[j2]==0:right=(b-z)**0.5;
        elif self.p[j2]==1:right=(b-z);
        elif self.p[j2]==2:right=(b-z)**2;
        result=solve(diff(a1*left+a2*right+a3*left*right,z));
        root=[]
        for temp in result:
            if ask(Q.real(temp)):
                if temp>=low and temp<=high:root.append(float(temp));
        return root;

    def a1a2a3(self,j1,j2):
        index1=self.index[j1];index2=self.index[j2];
        index12=[];
        for temp in index1:
            if temp in index2:index12.append(temp);
        a1=0.0;a2=0.0;a3=0.0;
        if self.c[j1]==1.0 and self.c[j2]!=1.0:
            for temp in index2:
                if temp not in index12:a2=a2-self.sigma(temp);
            a2=a2/(1-self.pi(j2));
        elif self.c[j2]==1.0 and self.c[j1]!=1.0:
            for temp in index1:
                if temp not in index12:a1=a1-self.sigma(temp);
            a1=a1/(1-self.pi(j1));
        elif self.c[j1]!=1.0 and self.c[j2]!=1.0:
            for temp in index1:
                result=self.sigma(temp)/(1-self.pi(j1));
                if temp in index12:result/=(1-self.pi(j2));
                a1-=result;
            for temp in index2:
                result=self.sigma(temp)/(1-self.pi(j2));
                if temp in index12:result/=(1-self.pi(j1));
                a2-=result;
            for temp in index12:a3+=self.sigma(temp);
            a3=a3/(1-self.pi(j1))/(1-self.pi(j2));
        return (a1,a2,a3);

    def sigma(self,edge):
        p=1.0;
        for temp in self.supergraph[edge]:
            if temp in self.x:
                p *= (1 - self.pi(temp))
        return 1.0 - p

    def pi(self,node):
        if self.p[node]==0:return self.c[node]**0.5;
        if self.p[node]==1:return self.c[node];
        if self.p[node]==2:return self.c[node]**2;

    def propagate(self,alpha):
        total=[];
        for temp in self.x:
            if random.random()<self.pi(temp):total.append(temp);
        p=qu.Queue();
        for temp in total:p.put(temp);
        while not p.empty():
            head=p.get();
            for temp in self.graph.neighbors(head):
                if temp not in total and random.random()<\
                    alpha/self.graph.in_degree(temp):
                        total.append(temp);p.put(temp);
        return len(total);

    def generate(self,alpha,times):
        result=[]
        for temp in range(times):result.append(self.propagate(alpha))
        previous=np.mean(result)
        print(previous)
        outfile=open('3.txt','a')
        outfile.write('alpha='+str(alpha)+'\tresult='+\
                      str(round(np.mean(result),4))+'\n')
        outfile.close()

files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1']
propagate=1000
alphas=[0.6,0.8,1.0]
budgets=[10,20,30,40,50]
for file in files:
    dataset=data(file)
    for alpha in alphas:
        dataset.loadsupergraph(alpha)
        for budget in budgets:
            dataset.initial(budget)
            dataset.cd(50)
            dataset.generate(alpha,propagate)
        open('3.txt','a').write('\n')
