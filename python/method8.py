import networkx
import random
import time
import numpy
import queue
import copy
start=time.time();
files=['Wiki-Vote.txt','CA-CondMat.txt','com-dblp.ungraph.txt','soc-LiveJournal1.txt'];

class mygraph:
    g=networkx.DiGraph();pu=[];cu=[];index={};supergraph=[];prob_edge=[];
    def __init__(self,fileflag):
        infile=open(files[fileflag]);
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
            for temp2 in temp1.split():tempedge.append(int(temp2));
            self.supergraph.append(tempedge);
        infile.close();
        for i in range(0,len(self.supergraph)):
            for j in self.supergraph[i]:
                if j in self.index:self.index[j].append(i);
                else:self.index[j]=[i];
        for i in self.supergraph:
            temp=1.0;
            for j in i:temp*=(1-self.pucu(j));
            self.prob_edge.append(temp);
        print (self.g.number_of_nodes(),'\tnodes');
        print (self.g.number_of_edges(),'\tedges');
        print (len(self.supergraph),'\tsuperedges');

    def pucu(self,j):
        if self.pu[j]==0:return self.cu[j]**2;
        elif self.pu[j]==1:return self.cu[j];
        elif self.pu[j]==2:return self.cu[j]**0.5;

    def pid(self,j,cu):
        if self.pu[j]==0:return cu**2;
        elif self.pu[j]==1:return cu;
        elif self.pu[j]==2:return cu**0.5;

    def update_prob_edge(self,j):
        for edge in self.index[j]:
            temp1=1.0;
            for temp2 in self.supergraph[edge]:temp1*=(1-self.pucu(temp2));
            self.prob_edge[edge]=temp1;

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

    def ns(self,s):
        neighbor=[];
        for temp1 in s:
            for temp2 in self.g.neighbors(temp1):
                if temp2 not in neighbor and temp2 not in s:neighbor.append(temp2);
        return neighbor;

    def delsuperedge(self,nodenumber):
        for edge in self.index[nodenumber]:
            for node in self.supergraph[edge]:
                if node!=nodenumber:self.index[node].remove(edge);
        self.index.pop(nodenumber);
        return;

    def newlyreached(self,s,realized,u):
        temp1=self.ns(realized);
        temp2=self.ns([u]);
        result=[];
        for temp in s:
            if temp not in temp1 and temp in temp2:result.append(temp);
        return result;

    def sigmahh(self,nodes):
        sigma=len(nodes);
        for temp in nodes:sigma-=self.prob_edge[temp];
        return sigma;

    def sigmarr(self,s1):
        total=0;
        for temp1 in self.supergraph:
            temp=1.0;
            for temp2 in temp1:
                if temp2 in s1:temp*=1-self.pid(temp2,s1[temp2]);
            total+=(1-temp);
        return total;
    
    def kick(self,u,d,z):
        for temp in d:
            if [z[0],temp] in u:u.remove([z[0],temp]);
        return;

    def pick(self,u,d,ai,kcu):
        while len(u) and sum(ai.values())<=kcu-min(d):
            maxresult=0;
            for z in u:
                ai[z[0]]=z[1];
                result=self.sigmarr(ai);
                ai.pop(z[0]);
                if result/z[1]>maxresult:
                    maxresult=result/z[1];maxz=z;
            if maxz[1]+sum(ai.values())<=kcu:ai[maxz[0]]=maxz[1];
            self.kick(u,d,maxz);
        return ai;

    def triple(self,r,d,s1,kcu):
        z=[];
        for temp1 in r:
            for temp2 in d:z.append([temp1,temp2]);
        #all ai
        for a1 in range(0,len(z)-2):
            for a2 in range(a1+1,len(z)-1):
                for a3 in range(a2+1,len(z)):
                    #a valid triple
                    if z[a1][0]==z[a2][0] or z[a1][0]==z[a3][0]\
                        or z[a2][0]==z[a3][0]:continue;
                    if z[a1][1]+z[a2][1]+z[a3][1]>kcu:continue;
                    u=copy.deepcopy(z);self.kick(u,d,z[a1]);
                    self.kick(u,d,z[a2]);self.kick(u,d,z[a3]);
                    ai={z[a1][0]:z[a1][1],z[a2][0]:z[a2][1],\
                            z[a3][0]:z[a3][1]};
                    ai=self.pick(u,d,ai,kcu);
                    if self.sigmarr(ai)>self.sigmarr(s1):s1=copy.deepcopy(ai);
        return s1;

    def tuple(self,r,d,s2,kcu):
        z=[];
        for temp1 in r:
            for temp2 in d:z.append([temp1,temp2]);
        #all ai
        for a1 in range(0,len(z)):
            if z[a1][1]>kcu:continue;
            ai={z[a1][0]:z[a1][1]};
            if self.sigmarr(ai)>self.sigmarr(s2):s2=copy.deepcopy(ai);
        for a1 in range(0,len(z)-1):
            for a2 in range(a1+1,len(z)):
                #a valid tuple
                if z[a1][0]==z[a2][0] or z[a1][1]+z[a2][1]>kcu:continue;
                ai={z[a1][0]:z[a1][1],z[a2][0]:z[a2][1]};
                if self.sigmarr(ai)>self.sigmarr(s2):s2=copy.deepcopy(ai);
        return s2;

#main
fileflag=0;gve=mygraph(fileflag);
#threshold
#tu=numpy.random.rand(gve.g.number_of_nodes());
#numpy.savetxt('tu.txt',tu,fmt='%1.2f');
tu=numpy.loadtxt('tu.txt');
#possible discrete values
d=numpy.linspace(0.1,1,10);
alpha=1;num_of_x=100;x=numpy.arange(0,100,1);
nx=gve.ns(x);totalbudget=50;
#b1=totalbudget*len(x)/(len(x)+len(nx));
#b2=totalbudget-b1;
b1=8.0;b2=42.0;b1realized=[];b2realized=[];
num_of_propagate=10;b1used=0;b2used=0;
while b1used<=b1 and b2used<=b2:
    maxresult=0;
    for temp1 in x:
        if temp1 in b1realized:continue;
        r=gve.newlyreached(nx,b1realized,temp1);
        if len(r)<=2:continue;
        s1={};s2={};
        mincu=gve.nuandcu(temp1,tu,d)[1];
        kcu=b2*mincu/b1;
        s1=gve.triple(r,d,s1,kcu);
        s2=gve.tuple(r,d,s2,kcu);
        sigmas1=gve.sigmarr(s1);sigmas2=gve.sigmarr(s2);
        #compare s1 and s2
        if sigmas1>=sigmas2:
            if sigmas1/mincu>maxresult:
                maxs=copy.deepcopy(s1);
                maxu=temp1;maxcu=mincu;
                maxresult=sigmas1/mincu;
        elif sigmas2/mincu>maxresult:
            maxs=copy.deepcopy(s2);
            maxu=temp1;maxcu=mincu;
            maxresult=sigmas2/mincu;
    if b1used+maxcu>b1:break;
    b1realized.append(maxu);b1used+=maxcu;
    gve.cu[maxu]=maxcu;gve.delsuperedge(maxu);
    b2new=sum(list(maxs.values()));
    if b2used+b2new>b2:break;
    b2used+=b2new;
    for temp in maxs.keys():
        gve.cu[temp]=maxs[temp];gve.delsuperedge(temp);
        if random.random()<=gve.pid(temp,maxs[temp]):b2realized.append(temp);
    for temp in gve.g.nodes():gve.update_prob_edge(temp);

seed=b2realized;
results=[];
for temp in range(0,num_of_propagate):results.append(gve.propagate(seed,alpha));
results=numpy.array(results);
print(numpy.mean(results));
end=time.time();
print(end-start,'\ts');