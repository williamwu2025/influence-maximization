import networkx
import random
import time
import numpy
try:import Queue 
except:import queue as Queue
from sympy.solvers import solve
from sympy import Symbol,diff,ask,Q,evalf
start=time.time();
class mygraph:
    g=networkx.DiGraph();
    pu=[];
    cu=[];
    index={};
    supergraph=[];
    prob_edge=[];
    x=[];
    def __init__(self,file):
        infile=open(file+'.txt');
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
        self.x=self.g.nodes()[:100];
        for temp in range(0,self.g.number_of_nodes()):
            if temp in self.x:self.cu.append(50/len(self.x));
            else:self.cu.append(0);
        self.pu=numpy.loadtxt(file+'_pucu.txt').astype(int);
        #load supergraph
        infile=open(file+'_supergraph.txt');
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
            if abs(mean-temp)<0.03*mean:flag=1;
        return mean;    
    
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
            values.append(gve.value(j1,j2,a1,a2,a3,b,temp));
        self.cu[j1]=points[numpy.argmin(values)];
        self.cu[j2]=b-self.cu[j1];
        self.update_prob_edge(j1);
        self.update_prob_edge(j2);
        
        
files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1'];
num_of_cd=50;
alpha=[0.6,0.8,1.0];
num_of_propagate=50;
for file in files[:3]:
    gve=mygraph(file);
    for cd in range(0,num_of_cd):
        [j1,j2]=random.sample(gve.x,2);
        gve.cd(j1,j2);
    for tempalpha in alpha:
        results=[];
        for propagate in range(0,num_of_propagate):
            realized=gve.realize();
            results.append(gve.propagate(realized,tempalpha));
        results=numpy.array(results);
        outfile=open(file+'_method3.txt','a');
        outfile.write('alpha='+str(tempalpha)+\
                      ' mean='+str(round(numpy.mean(results),2))+'\n');
        outfile.close();
end=time.time();
print (end-start,'s');