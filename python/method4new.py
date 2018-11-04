import networkx
import random
import time
import numpy
import queue
import copy
from sympy.solvers import solve
from sympy import Symbol,diff,ask,Q,evalf
start=time.time();
files=['Wiki-Vote.txt','CA-CondMat.txt','com-dblp.ungraph.txt','soc-LiveJournal1.txt'];
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
        #s=numpy.loadtxt('target'+str(fileflag)+'.txt').astype(int);
        self.cu=[-1.0]*100;
        while self.cu[99]<0 or self.cu[99]>1:
            sum=0;
            for i in range(0,99):
                self.cu[i]=random.random()/2;
                sum+=self.cu[i];
                self.cu[99]=25-sum;
        for temp in range(100,self.g.number_of_nodes()):
            self.cu.append(0.0);
        #for temp in self.g.nodes():
            #if temp not in s:self.cu.append(0.0);
            #else:self.cu.append(1.0);
        #    if temp<100:self.cu.append(0.5);
        #    else:self.cu.append(0.0);
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
        print (len(self.prob_edge),'\tsuperedges');
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
        
    def ns(self,s):
        neighbor=[];
        for temp1 in s:
            for temp2 in self.g.neighbors(temp1):
                if temp2 not in neighbor and temp2 not in s:neighbor.append(temp2);
        return neighbor;
        
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

    def phase1realize(self,s):
        result=[];
        for temp in s:
            if random.random()<self.pucu(temp):result.append(temp);
        return result;
    
    def sigmahh(self):
        sum=len(self.prob_edge);
        for temp in self.prob_edge:sum-=temp;
        return sum;
        
fileflag=0;
gve=mygraph(fileflag);
#s=numpy.loadtxt('target'+str(fileflag)+'.txt').astype(int);
num_of_x=100;
alpha=1;
num_of_phase1=2;
num_of_phase2=2;
num_of_realize=2;
num_of_propagate=5;
num_of_initial=25;
x=gve.g.nodes()[:num_of_x];
#choose 25 initial
degrees=[];
for temp in x:degrees.append(gve.g.degree(temp));
degreesort=numpy.argsort(degrees);
initial=[];
for temp in degreesort[75:]:initial.append(x[temp]);
for temp in x:
    if temp in initial:gve.cu[temp]=0.9999;
    else:gve.cu[temp]=0.0001;
for temp in x:gve.update_prob_edge(temp);
#with no cd
#results=[];
#for temp1 in range(0,num_of_propagate):
#    realized=gve.realize();
#    results.append(gve.propagate(realized,alpha));
#results=numpy.array(results);
#print(numpy.mean(results));
for phase1 in range(num_of_phase1):
    [i,j]=random.sample(initial,2);
    b=gve.cu[i]+gve.cu[j];
    low=max(0,b-1);
    high=min(1,b);
    if low>=high:continue;
    maxqns=[];
    maxqnsi=[];
    maxqnsj=[];
    maxqnsij=[];
    for realize in range(0,num_of_realize):
        s=[];
        for temp in initial:
            if temp!=i and temp!=j:s.append(temp);
        s=gve.phase1realize(s);
        ns=[];
        for temp in gve.ns(s):
            if temp not in x:ns.append(temp);
        nschoose=random.sample(ns,25);
        for temp in nschoose:gve.cu[temp]=1.0;
        for temp in nschoose:gve.update_prob_edge(temp);
        
        for phase2 in range(0,num_of_phase2):
            [j1,j2]=random.sample(ns,2);
            gve.cd(j1,j2);
        #maxqnsmean
        maxqns.append(gve.sigmahh());
        maxqnscu=copy.deepcopy(gve.cu);
            
        s.append(i);
        ns=[];
        for temp in gve.ns(s):
            if temp not in x:ns.append(temp);
        for phase2 in range(0,num_of_phase2):
            [j1,j2]=random.sample(ns,2);
            gve.cd(j1,j2);
        #maxqnsimean
        maxqnsi.append(gve.sigmahh());
            
        s.append(j);
        ns=[];
        for temp in gve.ns(s):
            if temp not in x:ns.append(temp);
        for phase2 in range(0,num_of_phase2):    
            [j1,j2]=random.sample(ns,2);
            gve.cd(j1,j2);
        #maxqnsijmean
        maxqnsij.append(gve.sigmahh());
        
        #restore
        gve.cu=copy.deepcopy(maxqnscu);
        for temp in gve.g.nodes():gve.update_prob_edge(temp);

        s=[];
        for temp in initial:
            if temp!=i:s.append(temp);
        ns=[];
        for temp in gve.ns(s):
            if temp not in x:ns.append(temp);
        for phase2 in range(0,num_of_phase2):    
            [j1,j2]=random.sample(ns,2);
            gve.cd(j1,j2);
        #maxqnsjmean
        maxqnsj.append(gve.sigmahh());
        
        #restore
        for temp in gve.ns(initial):gve.cu[temp]=0;
        for temp in initial:gve.update_prob_edge(temp);
    
    maxqnsmean=numpy.mean(numpy.array(maxqns));
    maxqnsimean=numpy.mean(numpy.array(maxqnsi));
    maxqnsjmean=numpy.mean(numpy.array(maxqnsj));
    maxqnsijmean=numpy.mean(numpy.array(maxqnsij));    
    a1=maxqnsimean-maxqnsmean;
    a2=maxqnsjmean-maxqnsmean;
    a3=maxqnsijmean+maxqnsmean-maxqnsimean-maxqnsjmean;
    roots=gve.solve(i,j,a1,a2,a3,b);
    points=gve.clip(roots,low,high);
    values=[];
    for temp in points:
        values.append(gve.value(i,j,a1,a2,a3,b,temp));
    gve.cu[i]=points[numpy.argmin(values)];
    gve.cu[j]=b-gve.cu[i];
    gve.update_prob_edge(i);
    gve.update_prob_edge(j);
    
#after cd
#results=[];
#for temp1 in range(0,num_of_propagate):
#    realized=gve.realize();
#    results.append(gve.propagate(realized,alpha));
#results=numpy.array(results);
#print(numpy.mean(results));
end=time.time();
print (end-start,'s');
test=gve.cu;