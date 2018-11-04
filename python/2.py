import networkx as nx
import numpy as np
import random
from time import time
try:import Queue as Q
except:import queue as Q
class data:
    graph=nx.DiGraph();
    x=[];
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
        start=time();
        for temp1 in range(0,len(self.supergraph)):
            for temp2 in self.supergraph[temp1]:
                if temp2 not in self.index:self.index[temp2]=[temp1];
                else:self.index[temp2].append(temp1);
        end=time();
        outfile=open('2.txt','a');
        outfile.write(self.name+'\talpha='+str(alpha)+\
                      '\tindex='+str(round(end-start))+'s\n');
        outfile.close();

    def generate(self,budget,alpha):
        start=time();
        self.choose(budget);
        end=time();
        result=[self.propagate(self.seed,alpha)];
        flag=0;
        while flag<=100:
            flag+=1;
            temp=self.propagate(self.seed,alpha);
            previous=np.mean(result);
            if abs(previous-temp)<=0.03*previous:break;
            else:result.append(temp);
        outfile=open('2.txt','a');
        outfile.write(self.name+'\talpha='+str(alpha)+'\tbudget='+str(budget)\
            +'\ttime='+str(round(end-start))+'s\tresult='+str(round(previous,4))+'\n');
        outfile.close();

    def propagate(self,seed,alpha):
        q=Q.Queue();
        total=[];
        for temp in seed:
            total.append(temp);
            q.put(temp);
        while not q.empty():
            head=q.get();
            for temp in self.graph.neighbors(head):
                if temp not in total and random.random()<alpha/self.graph.in_degree(temp):
                    total.append(temp);
                    q.put(temp);
        return(len(total));

    def choose(self,budget):
        for temp1 in range(0,10):
            max=0;
            for temp2 in self.x:
                if len(self.index[temp2])>max:
                    target=temp2;
                    max=len(self.index[target]);
            self.seed.append(target);
            self.delete(target);

    def delete(self,node):
        edges=self.index[node];
        for temp1 in edges:
            for temp2 in self.supergraph[temp1]:self.index[temp2].remove(temp1);

files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1'];
alphas=[0.6,0.8,1.0];
budgets=[10,20,30,40,50];
for file in files:
    dataset=data(file);
    for alpha in alphas:
        dataset.loadsupergraph(alpha);
        for budget in budgets:
            dataset.generate(budget,alpha);
        outfile=open('2.txt','a');
        outfile.write('\n');
        outfile.close();
        