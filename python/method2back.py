import networkx
import random
import time
import numpy
import copy
try:import Queue 
except:import queue as Queue
start=time.time();
class mygraph:
    g=networkx.DiGraph();
    x=[];
    supergraph=[];
    index={};
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
        infile=open(filename+'_supergraph.txt');
        for temp1 in infile.readlines():
            temp=[];
            for temp2 in temp1.split():temp.append(int(temp2));
            self.supergraph.append(temp);
        infile.close();
        
        for temp1 in range(0,len(self.supergraph)):
            for temp2 in self.supergraph[temp1]:
                if temp2 not in self.index:self.index[temp2]=[temp1];
                else:self.index[temp2].append(temp1);
            
        self.x=self.g.nodes()[:100];
        print (self.g.number_of_nodes(),'\tnodes');
        print (self.g.number_of_edges(),'\tedges');
        print (len(self.supergraph),'\tsuperedges');
    
    def choose(self,b):
        tempindex=copy.deepcopy(self.index);
        seed=[];
        for temp1 in range(0,b):
            max=0;
            for temp2 in self.x:
                if len(tempindex[temp2])>max:
                    target=temp2;
                    max=len(tempindex[temp2]);
            seed.append(target);
            for temp2 in tempindex[target]:
                for temp3 in self.supergraph[temp2]:
                    if temp3!=target:tempindex[temp3].remove(temp2);
            tempindex[target]=[];
        return seed;
    
    def propagate_once(self,target,alpha):
        q=Queue.Queue();
        total=[];
        for temp in target:
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
    
    def propagate(self,target,alpha):
        results=[];
        for temp in range(0,10):
            results.append(self.propagate_once(target,alpha));
        flag=0;
        while(flag==0):
            temp=self.propagate_once(target,alpha);
            results.append(temp);
            mean=sum(results)/len(results);
            if abs(mean-temp)<0.01*mean:flag=1;
        return mean;
        

files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1'];
alpha=[0.6,0.8,1.0];
b=[10,20,30,40,50];
for temp in files:
    gve=mygraph(temp);
    for tempb in b:
        target=gve.choose(tempb);
        for tempalpha in alpha:
            result=round(gve.propagate(target,tempalpha),2);
            outfile=open(temp+'_method2.txt','a');
            outfile.write('b='+str(tempb)+' alpha='+str(tempalpha)+\
                          ' mean='+str(result)+'\n');
            outfile.close();
end=time.time();
print (end-start,'s');