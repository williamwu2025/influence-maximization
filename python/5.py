import networkx as nx
import random
import time
import numpy as np
try:import Queue as q
except:import queue as q
class data:
    graph=nx.DiGraph();
    def __init__(self,file):
        self.name=file;
        infile=open(self.name+'.txt');
        buffer=infile.readline();
        if (buffer.find('Directed')==2):flag=1;
        elif (buffer.find('Undirected')==2):flag=2;
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
        self.t=np.loadtxt(self.name+'_tu.txt');
        self.d=np.linspace(0.1,1,10);

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
        for temp1 in range(0,len(self.supergraph)):
            for temp2 in self.supergraph[temp1]:
                if temp2 not in self.index:self.index[temp2]=[temp1];
                else:self.index[temp2].append(temp1);
        self.seed=[];
        self.c=[];
        for temp in range(0,self.graph.number_of_nodes()):self.c.append(0.0);

    def cu(self,node):
        if self.p[node]==0:temp=self.t[node]**2;
        elif self.p[node]==1:temp=self.t[node];
        elif self.p[node]==2:temp=self.t[node]**0.5;
        for budget in self.d:
            if budget>=temp:return budget;

    def nu(self,node):return len(self.index[node]);

    def pi(self,node):
        if self.p[node]==0:return self.c[node]**0.5;
        if self.p[node]==1:return self.c[node];
        if self.p[node]==2:return self.c[node]**2;

    def allocate(self,budget):
        total=0;
        start=time.time();
        while total<10:
            maximum=0;
            for temp in self.x:
                n=self.nu(temp);
                c=self.cu(temp);
                if float(n)/c>maximum:
                    flag=temp;
                    maximum=float(n)/c;
            if total+self.cu(flag)>10:break;
            self.c[flag]=self.cu(flag);
            total+=self.c[flag];
            self.seed.append(flag);
            self.delete(flag);
        end=time.time();
        outfile=open('5.txt','a');
        outfile.write(self.name+'\tbudget='+str(budget)+'\ttime='+\
                      str(round(end-start))+'s\t');
        outfile.close();

    def delete(self,node):
        edges=self.index[node];
        for temp1 in edges:
            for temp2 in self.supergraph[temp1]:self.index[temp2].remove(temp1);

    def propagate(self,alpha):
        p=q.Queue();
        total=[];
        for temp in self.seed:
            p.put(temp);
            total.append(temp);
        while not p.empty():
            head=p.get();
            for temp in self.graph.neighbors(head):
                if temp not in total and random.random()<\
                    alpha/self.graph.in_degree(temp):
                        p.put(temp);
                        total.append(temp);
        return len(total);

    def generate(self,alpha):
        result=[self.propagate(alpha)];
        flag=0;
        while flag<10000:
            temp=self.propagate(alpha);
            previous=np.mean(result);
            if abs(previous-temp)<=0.01*previous:break;
            else:result.append(temp);
        outfile=open('5.txt','a');
        outfile.write('alpha='+str(alpha)+'\tresult='+\
                      str(round(previous,4))+'\n');
        outfile.close();

alphas=[0.6,0.8,1.0];
budgets=[10,20,30,40,50];
files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1'];
for file in files:
    dataset=data(file);
    for alpha in alphas:
        dataset.loadsupergraph(alpha);
        for budget in budgets:
            dataset.allocate(budget);
            dataset.generate(alpha);
        outfile=open('5.txt','a');
        outfile.write('\n');
        outfile.close();