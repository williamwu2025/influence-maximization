import networkx
import random
import time
import numpy
try:import Queue 
except:import queue as Queue
start=time.time();
class mygraph:
    g=networkx.DiGraph();
    x=[];
    def __init__(self,filename):
        infile=open(filename+'.txt');
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
                self.g.add_edge(nodeorder[u],nodeorder[v]);
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
                self.g.add_edge(nodeorder[u],nodeorder[v]);
                self.g.add_edge(nodeorder[v],nodeorder[u]);
                buffer=infile.readline();
        infile.close();
        self.x=self.g.nodes()[:100];
        print (self.g.number_of_nodes(),'\tnodes');
        print (self.g.number_of_edges(),'\tedges');
    
    def chooseb1(self,totalb):
        b1=int(totalb/10);
        seed1=random.sample(self.x,b1);
        return seed1;
    
    def chooseb2(self,seed1):
        b2=9*len(seed1);
        b1neighbor=self.neighborinx(seed1);
        if len(b1neighbor)>=b2:seed2=random.sample(b1neighbor,b2);
        else:seed2=b1neighbor;
        return seed2;
    
    def neighborinx(self,s):
        result=[]
        for temp1 in s:
            for temp2 in self.g.neighbors(temp1):
                if temp2 not in s and temp2 not in result and temp2 in self.x:
                    result.append(temp2);
        return result;
    
    def propagate_once(self,seed1,seed2,alpha):
        q=Queue.Queue();
        total=[];
        for temp in seed1:total.append(temp);
        for temp in seed2:
            q.put(temp);
            total.append(temp);
        while not q.empty():
            head=q.get();
            for temp in self.g.neighbors(head):
                if temp not in total:
                    rand=random.random();
                    if rand<alpha/self.g.in_degree(temp):
                        total.append(temp);
                        q.put(temp);
        return len(total);
    
    def propagate(self,seed1,seed2,alpha):
        results=[];
        for times in range(0,10):
            results.append(self.propagate_once(seed1,seed2,alpha));
        flag=0;
        while(flag==0):
            temp=self.propagate_once(seed1,seed2,alpha);
            results.append(temp);
            mean=sum(results)/len(results);
            if abs(mean-temp)<0.05*mean:flag=1;
        return mean;
        

files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1'];
num_of_seed1=50;
num_of_seed2=50;
alpha=[0.6,0.8,1.0];
b=[10,20,30,40,50];
for file in files:
    gve=mygraph(file);
    for tempb in b:
        for tempalpha in alpha:
            result=[];
            for temp1 in range(0,num_of_seed1):
                seed1=gve.chooseb1(tempb);
                for temp2 in range(0,num_of_seed2):
                    seed2=gve.chooseb2(seed1);
                    result.append(gve.propagate(seed1,seed2,tempalpha));
            outfile=open(file+'_method1.txt','a');
            result=numpy.array(result);
            outfile.write('b='+str(round(tempb,2))+' alpha='+\
                          str(round(tempalpha,2))+' mean='+\
                          str(round(result.mean(),2))+' max='+\
                          str(round(result.max(),2))+' min='+\
                          str(round(result.min(),2))\
                          +'\n');
            outfile.close();
end=time.time();
print (end-start,'s');