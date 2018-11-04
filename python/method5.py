import networkx
import random
import time
import numpy
import queue
start=time.time();
files=['Wiki-Vote.txt','CA-CondMat.txt','com-dblp.ungraph.txt','soc-LiveJournal1.txt'];
fileflag=0;
class mygraph:
    g=networkx.DiGraph();
    pu=[];
    cu=[];
    index={};
    supergraph=[];
    def __init__(self,fileflag):
        infile=open(files[fileflag]);
        buffer=infile.readline();
        if (buffer.find('Directed')==2):flag=1;
        elif (buffer.find('Undirected')==2):flag=2;
        while buffer[0]=='#':
            buffer=infile.readline();
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
        #load pu and cu
        for temp in self.g.nodes():self.cu.append(0.0);
        self.cu=numpy.array(self.cu);
        self.pu=numpy.loadtxt('cu'+str(fileflag)+'.txt').astype(int);
        #load supergraph
        infile=open('supergraph'+str(fileflag)+'.txt');
        for temp1 in infile.readlines():
            tempedge=[];
            for temp2 in temp1.split():
                tempedge.append(int(temp2));
            self.supergraph.append(tempedge);
        infile.close();
        for i in range(0,len(self.supergraph)):
            for j in self.supergraph[i]:
                if j in self.index:self.index[j].append(i);
                else:self.index[j]=[i];
        print (self.g.number_of_nodes(),'\tnodes');
        print (self.g.number_of_edges(),'\tedges');
        print (len(self.supergraph),'\tsuperedges');
        
    def pucu(self,j):
        if self.pu[j]==0:return self.cu[j]**2;
        elif self.pu[j]==1:return self.cu[j];
        elif self.pu[j]==2:return self.cu[j]**0.5;
        
    def realize(self):
        result=[];
        for temp in range(0,len(self.pu)):
            if random.random()<self.pucu(temp):result.append(temp);
        return(result);
        
    def propagate(self,realized,alpha):
        customers=queue.Queue();
        total=[];
        for temp in realized:
            total.append(temp);
            customers.put(temp);
        while (not customers.empty()):
            head=customers.get();
            for temp in self.g.neighbors(head):
                if temp not in total:
                    if (random.random())<alpha/self.g.in_degree(temp):
                        total.append(temp);
                        customers.put(temp);
        return(len(total));
    
    def nuandcu(self,nodenumber,tu,d):
        nu=len(self.index[nodenumber]);
        if self.pu[nodenumber]==0:cu=tu[nodenumber]**0.5;
        elif self.pu[nodenumber]==1:cu=tu[nodenumber];
        elif self.pu[nodenumber]==2:cu=tu[nodenumber]*tu[nodenumber];
        for temp in d:
            if temp>=cu:
                cu=temp;
                break;
        return nu,cu;
    '''
    def allocatecu(self,nodenumber,tu,d):
        if self.pu[nodenumber]==0:cu=tu**0.5;
        elif self.pu[nodenumber]==1:cu=tu;
        elif self.pu[nodenumber]==2:cu=tu*tu;
        for temp in d:
            if temp>=cu:
                cu=temp;
                break;
        return (cu);
    '''
    def ns(self,s):
        neighbor=[];
        for temp1 in s:
            for temp2 in self.g.neighbors(temp1):
                if temp2 not in neighbor and temp2 not in s:neighbor.append(temp2);
        return neighbor;
    
    def delsuperedge(self,nodenumber):
        self.index[nodenumber]=[];

#main
gve=mygraph(fileflag);
#threshold
#tu=numpy.random.rand(gve.g.number_of_nodes());
#numpy.savetxt('tu.txt',tu,fmt='%1.2f');
tu=numpy.loadtxt('tu.txt');
#possible discrete values
d=numpy.linspace(0.1,1,10);
alpha=1;
num_of_x=100;
x=gve.g.nodes()[:num_of_x];
nx=gve.ns(x);
totalbudget=50;
budgetused=0;
realized=[];
num_of_propagate=100;
while (budgetused<=totalbudget):
    maximum=0;
    for temp1 in x:
        (tempnu,tempcu)=gve.nuandcu(temp1,tu,d);
        if tempnu/tempcu>maximum:
            maximum=tempnu/tempcu;
            choosenode=temp1;
    if gve.nuandcu(choosenode,tu,d)[1]+budgetused<=totalbudget:
        realized.append(choosenode);
        budgetused+=gve.nuandcu(choosenode,tu,d)[1];
        gve.delsuperedge(choosenode);
    else:break;
results=[];
for temp in range(0,num_of_propagate):results.append(gve.propagate(realized,alpha));
results=numpy.array(results);
print(numpy.mean(results));
end=time.time();
print(end-start,'\ts');