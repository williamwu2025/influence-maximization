import networkx as nx
import random
import numpy as np
import time
try:import Queue as Q
except:import queue as Q
class data:
    graph=nx.DiGraph();
    x=[];
    files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1'];
    def __init__(self,file):
        infile=open(self.files[file]+'.txt');
        buffer=infile.readline();
        if buffer.find('Directed')==2:flag=1;
        elif buffer.find('Undirected')==2:flag=2;
        while buffer[0]=='#':buffer=infile.readline();
        order={};
        current=0;
        if flag==1:
            while buffer:
                [u,v]=buffer.split();
                if u not in order:
                    order[u]=current;
                    current+=1;
                if v not in order:
                    order[v]=current;
                    current+=1;
                self.graph.add_edge(order[u],order[v]);
                buffer=infile.readline();
        elif flag==2:
            while buffer:
                [u,v]=buffer.split();
                if u not in order:
                    order[u]=current;
                    current+=1;
                if v not in order:
                    order[v]=current;
                    current+=1;
                self.graph.add_edge(order[u],order[v]);
                self.graph.add_edge(order[v],order[u]);
                buffer=infile.readline();
        infile.close();
        self.x=[a for a in range(0,100)];
        print (self.graph.number_of_nodes(),'\tnodes');
        print (self.graph.number_of_edges(),'\tedges');

    def seed1(self,b1):return random.sample(self.x,b1);
        
    def neighbor(self,seed,x):
        result=[];
        for temp1 in seed:
            for temp2 in self.graph.neighbors(temp1):
                if temp2 not in result and temp2 not in seed and temp2 in x:
                    result.append(temp2);
        return result;

    def seed2(self,seed,b2):
        reach=self.neighbor(seed,self.x);
        if len(reach)<=b2:return reach;
        else:return random.sample(reach,b2);

    def generate(self,budget,alpha,num1,num2):
        b1=int(budget*0.2);
        b2=budget-b1;
        results=[];
        #generate seed
        for temp1 in range(0,num1):
            s1=self.seed1(b1);
            for temp2 in range(0,num2):
                s2=self.seed2(s1,b2);
                #propagate
                result=[self.propagate(s1,s2,alpha)];
                flag=0
                while True and flag<=50:
                    flag+=1;
                    temp=self.propagate(s1,s2,alpha);
                    previous=np.mean(result);
                    if abs(previous-temp)<=0.03*previous:break;
                    else:result.append(temp);
                results.append(previous);
        return np.mean(results);
        
    def propagate(self,seed1,seed2,alpha):
        q=Q.Queue();
        total=[];
        for temp in seed2:q.put(temp);
        while not q.empty():
            head=q.get();
            for temp in self.graph.neighbors(head):
                if temp not in total and random.random()<alpha/self.graph.in_degree(temp):
                    total.append(temp);
                    q.put(temp);
        return(len(seed1)+len(seed2)+len(total));

num_of_seed1=20;
num_of_seed2=20;
alphas=[0.6,0.8,1.0];
budgets=[10,20,30,40,50];
for file in range(0,4):
    dataset=data(file);
    for budget in budgets:
        for alpha in alphas:
            start=time.time();
            result=dataset.generate(budget,alpha,num_of_seed1,num_of_seed2);
            end=time.time();
            outfile=open('1.txt','a');
            outfile.write(dataset.files[file]+'\ta='+str(alpha)+'\tb='+str(budget)\
                +'\tr='+str(round(result,4))+'\tt='+str(round(end-start))+'s\n');
            outfile.close();