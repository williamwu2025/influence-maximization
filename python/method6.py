import networkx
import random
import time
import numpy
import queue
import copy
from sympy.solvers import solve
from sympy import Symbol,diff,ask,Q,evalf
start=time.time();
start=time.time();
files=['Wiki-Vote.txt','CA-CondMat.txt','com-dblp.ungraph.txt','soc-LiveJournal1.txt'];
fileflag=0;
class mygraph:
    g=networkx.DiGraph();
    pu=[];
    cu=[];
    index={};
    supergraph=[];
    prob_edge=[];
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
        
    def a1a2a3(self,j1,j2):
        index1=self.index[j1];
        index2=self.index[j2];
        index12=[temp for temp in index1 if temp in index2];
        a1=0;
        a2=0;
        a3=0;
        if self.pucu(j1)==1:
            a1=0;
            a3=0;
            for j in index2:a2-=self.prob_edge[j]/(1-self.pucu(j2));
        elif self.pucu(j2)==1:
            a2=0;
            a3=0;
            for j in index1:a1-=self.prob_edge[j]/(1-self.pucu(j1));
        elif self.pucu(j1)!=1 and self.pucu(j2)!=1:
            for j in index1:
                temp=self.prob_edge[j]/(1-self.pucu(j1));
                if j in index12:temp/=(1-self.pucu(j2));
                a1-=temp;
            for j in index2:
                temp=self.prob_edge[j]/(1-self.pucu(j2));
                if j in index12:temp/=(1-self.pucu(j1));
                a2-=temp;
            for j in index12:
                temp=self.prob_edge[j]/(1-self.pucu(j1))/(1-self.pucu(j2));
                a3+=temp;
        return(a1,a2,a3);

    #equation solver
    def solve(self,j1,j2,a1,a2,a3,b):
        x=Symbol("x");
        if self.pu[j1]==0 and self.pu[j2]==0:
            return(solve(diff(a1*x*x+a2*(b-x)*(b-x)+a3*x*x*(b-x)*(b-x),x),x));
        if self.pu[j1]==0 and self.pu[j2]==1:
            return(solve(diff(a1*x*x+a2*(b-x)+a3*x*x*(b-x),x),x));
        if self.pu[j1]==0 and self.pu[j2]==2:
            return(solve(diff(a1*x*x+a2*((b-x)**0.5)+a3*x*x*((b-x)**0.5),x),x));
        if self.pu[j1]==1 and self.pu[j2]==0:
            return(solve(diff(a1*x+a2*(b-x)*(b-x)+a3*x*(b-x)*(b-x),x),x));
        if self.pu[j1]==1 and self.pu[j2]==1:
            return(solve(diff(a1*x+a2*(b-x)+a3*x*(b-x),x),x));
        if self.pu[j1]==1 and self.pu[j2]==2:
            return(solve(diff(a1*x+a2*((b-x)**0.5)+a3*x*((b-x)**0.5),x),x));
        if self.pu[j1]==2 and self.pu[j2]==0:
            return(solve(diff(a1*(x**0.5)+a2*(b-x)*(b-x)+a3*(x**0.5)*(b-x)*(b-x),x),x));
        if self.pu[j1]==2 and self.pu[j2]==1:
            return(solve(diff(a1*(x**0.5)+a2*(b-x)+a3*(x**0.5)*(b-x),x),x));
        if self.pu[j1]==2 and self.pu[j2]==2:
            return(solve(diff(a1*(x**0.5)+a2*((b-x)**0.5)+a3*(x**0.5)*((b-x)**0.5),x),x));
    
    def clip(self,roots,low,high):
        temp=[low,high];
        for i in roots:
            if ask(Q.real(i)):
                if i.evalf()>low and i.evalf()<high:
                    temp.append(float(i.evalf()));
        return temp;
    
    def value(self,j1,j2,a1,a2,a3,b,i):
        if self.pu[j1]==0 and self.pu[j2]==0:
            return(a1*i*i+a2*(b-i)*(b-i)+a3*i*i*(b-i)*(b-i));
        if self.pu[j1]==0 and self.pu[j2]==1:
            return(a1*i*i+a2*(b-i)+a3*i*i*(b-i));
        if self.pu[j1]==0 and self.pu[j2]==2:
            return(a1*i*i+a2*((b-i)**0.5)+a3*i*i*((b-i)**0.5));
        if self.pu[j1]==1 and self.pu[j2]==0:
            return(a1*i+a2*(b-i)*(b-i)+a3*i*(b-i)*(b-i));
        if self.pu[j1]==1 and self.pu[j2]==1:
            return(a1*i+a2*(b-i)+a3*i*(b-i));
        if self.pu[j1]==1 and self.pu[j2]==2:
            return(a1*i+a2*((b-i)**0.5)+a3*i*((b-i)**0.5));
        if self.pu[j1]==2 and self.pu[j2]==0:
            return(a1*(i**0.5)+a2*(b-i)*(b-i)+a3*(i**0.5)*(b-i)*(b-i));
        if self.pu[j1]==2 and self.pu[j2]==1:
            return(a1*(i**0.5)+a2*(b-i)+a3*(i**0.5)*(b-i));
        if self.pu[j1]==2 and self.pu[j2]==2:
            return(a1*(i**0.5)+a2*((b-i)**0.5)+a3*(i**0.5)*((b-i)**0.5));
        
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
        self.index[nodenumber]=[];
        return;

    def cd(self,j1,j2):
        b=self.cu[j1]+self.cu[j2];
        low=max(0,b-1);
        high=min(1,b);
        if low>=high:return;
        a1,a2,a3=self.a1a2a3(j1,j2);
        roots=self.solve(j1,j2,a1,a2,a3,b);
        points=self.clip(roots,low,high);
        values=[];
        for temp in points:
            values.append(self.value(j1,j2,a1,a2,a3,b,temp));
        self.cu[j1]=points[numpy.argmin(values)];
        self.cu[j2]=b-self.cu[j1];
        self.update_prob_edge(j1);
        self.update_prob_edge(j2);
        return;
        
    def newlyreached(self,ns,realized,u):
        temp1=self.ns(realized);
        temp2=self.ns([u]);
        result=[];
        for temp in ns:
            if temp not in temp1 and temp in temp2:result.append(temp);
        return result;
    
    def sigmahh(self,nodes):
        sum=len(nodes);
        for temp in nodes:sum-=self.prob_edge[temp];
        return sum;
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
#b1=totalbudget*len(x)/(len(x)+len(nx));
#b2=totalbudget-b1;
b1=8.0;
b2=42.0;
b1realized=[];
b2realized=[];
num_of_propagate=10;
num_of_cd=1;
b1used=0;
b2used=0;
while (b1used<=b1)and(b2used<=b2):
    maximum=0;
    for temp1 in x:
        if temp1 in b1realized:continue; 
        newlyreached=gve.newlyreached(nx,b1realized,temp1);
        if len(newlyreached)<2:continue;
        mincu=gve.nuandcu(temp1,tu,d)[1];
        budget=b2*mincu/b1;
        #cd in newlyreached
        for temp2 in newlyreached:gve.cu[temp2]=budget/len(newlyreached);
        for temp2 in newlyreached:gve.update_prob_edge(temp2);
        for temp2 in range(0,num_of_cd):
            [i,j]=random.sample(newlyreached,2);
            gve.cd(i,j);
        sigmahh=gve.sigmahh(b1realized+newlyreached);
        if (sigmahh/mincu)>maximum:
            maximum=sigmahh/mincu;
            maxnode=temp1;
            maxnodecu=copy.deepcopy(gve.cu);
        for temp2 in newlyreached:gve.cu[temp2]=0;
        for temp2 in newlyreached:gve.update_prob_edge(temp2);
                
    gve.cu=copy.deepcopy(maxnodecu);
    newlyreached=gve.newlyreached(nx,b1realized,maxnode);
    for temp2 in newlyreached:gve.update_prob_edge(temp2);

    gve.cu[maxnode]=gve.nuandcu(maxnode,tu,d)[1];
    gve.update_prob_edge(maxnode);
    if b1used+gve.cu[maxnode]<=b1:
        b1realized.append(maxnode);
        b1used+=gve.cu[maxnode];
        #gve.delsuperedge(maxnode);
    else:break;
    if b2used+gve.cu[maxnode]*b2/b1<=b2:
        b2used+=gve.cu[maxnode]*b2/b1;
    else:break;
    realized=gve.realize();
    for temp in realized:
        if temp not in b2realized and temp not in b1realized:
            b2realized.append(temp);
    for temp in newlyreached:
        gve.delsuperedge(temp);

results=[];
for temp in range(0,num_of_propagate):
    results.append(gve.propagate(b2realized,alpha));
results=numpy.array(results);
print(numpy.mean(results));
end=time.time();
print(end-start,'\ts');