import networkx
import random
import time
import numpy
import queue
from sympy.solvers import solve
from sympy import Symbol,diff
start=time.time();
fileflag=0;                                  #choose file
files=['Wiki-Vote.txt','CA-CondMat.txt',\
       'com-dblp.ungraph.txt','soc-LiveJournal1.txt'];
infile=open(files[fileflag]);
buffer=infile.readline();
flag=0;
number_of_target=50;                         #initial B
number_of_neighbor=100;
number_of_optimize=0;
alpha=1;                                     #alpha
totalpropagation=1000;                         #propagate
if (buffer.find('Directed')==2):
    flag=1;
elif (buffer.find('Undirected')==2):
    flag=2;
g=networkx.DiGraph();
#read file and generate graph
while buffer[0]=='#':
    buffer=infile.readline();
if flag==1:
    while buffer:
        [u,v]=buffer.split();
        g.add_edge(u,v);
        buffer=infile.readline();
elif flag==2:
    while buffer:
        [u,v]=buffer.split();
        g.add_edge(u,v);
        g.add_edge(v,u);
        buffer=infile.readline();
infile.close();
print (g.number_of_nodes(),'\tnodes');
print (g.number_of_edges(),'\tedges');


infile=open('target'+str(fileflag)+'.txt');
target=infile.readline().split();
infile.close();

#random resource allocation
neighbor=g.nodes()[:number_of_neighbor];
u=[];
for i in neighbor:
    if i in target:u.append(0.99);
    else:u.append(0.01);
u=numpy.array(u);
select=numpy.loadtxt('cu'+str(fileflag)+'.txt').astype(int);

cu=[];
for i in range(0,len(u)):
    if select[i]==0:cu.append(u[i]*u[i]);
    elif select[i]==1:cu.append(u[i]);
    elif select[i]==2:cu.append(u[i]**0.5);
#load supergraph
supergraph=[];
infile=open('supergraph'+str(fileflag)+'.txt');
for temp in infile.readlines():
    supergraph.append(temp.split());
infile.close();
index={};
for i in range(0,len(supergraph)):
    for j in supergraph[i]:
        if j in index:index[j].append(i);
        else:index[j]=[i];

#probability of edge
prob_edge=[];
for i in supergraph:
    temp=1.0;
    for j in i:
        if j in neighbor:temp*=(1-cu[neighbor.index(j)]);
    prob_edge.append(temp);
end=time.time();
print (end-start,'s');

x=Symbol("x");
#optimize coordinate descent
for i in range(0,number_of_optimize):
    j1=random.randint(0,number_of_neighbor-1);
    while neighbor[j1] not in index:
        j1=random.randint(0,number_of_neighbor-1);
    j2=random.randint(0,number_of_neighbor-1);
    while neighbor[j2] not in index or j1==j2:
        j2=random.randint(0,number_of_neighbor-1);
    b=u[j1]+u[j2];
    low=max(0,b-1);
    high=min(1,b);
    if low==high:continue;
    index1=index[neighbor[j1]];
    index2=index[neighbor[j2]];
    index12=[i for i in index1 if i in index2];
    a1=0;
    a2=0;
    a3=0;
    if cu[j1]==1:
        a1=0;
        a3=0;
        for j in index2:a2-=prob_edge[j]/(1-cu[j2]);
    elif cu[j2]==1:
        a2=0;
        a3=0;
        for j in index1:a1-=prob_edge[j]/(1-cu[j1]);
    elif cu[j1]!=1 and cu[j2]!=1:
        for j in index1:
            temp=prob_edge[j]/(1-cu[j1]);
            if j in index12:temp/=(1-cu[j2]);
            a1-=temp;
        for j in index2:
            temp=prob_edge[j]/(1-cu[j2]);
            if j in index12:temp/=(1-cu[j1]);
            a2-=temp;
        for j in index12:
            temp=prob_edge[j]/(1-cu[j1])/(1-cu[j2]);
            a3+=temp;
    if select[j1]==0:
        if select[j2]==0:
            result=solve(diff(a1*x*x+a2*(b-x)*(b-x)+a3*x*x*(b-x)*(b-x),x),x);
        elif select[j2]==1:
            result=solve(diff(a1*x*x+a2*(b-x)+a3*x*x*(b-x),x),x);
        elif select[j2]==2:
            result=solve(diff(a1*x*x+a2*((b-x)**0.5)+a3*x*x*((b-x)**0.5),x),x);
    elif select[j1]==1:
        if select[j2]==0:
            result=solve(diff(a1*x+a2*(b-x)*(b-x)+a3*x*(b-x)*(b-x),x),x);
        elif select[j2]==1:
            result=solve(diff(a1*x+a2*(b-x)+a3*x*(b-x),x),x);
        elif select[j2]==2:
            result=solve(diff(a1*x+a2*((b-x)**0.5)+a3*x*((b-x)**0.5),x),x);
    elif select[j1]==2:
        if select[j2]==0:
            result=solve(diff(a1*(x**0.5)+a2*(b-x)*(b-x)+a3*(x**0.5)*(b-x)*(b-x),x),x);
        elif select[j2]==1:
            result=solve(diff(a1*(x**0.5)+a2*(b-x)+a3*(x**0.5)*(b-x),x),x);
        elif select[j2]==2:
            result=solve(diff(a1*(x**0.5)+a2*((b-x)**0.5)+a3*(x**0.5)*((b-x)**0.5),x),x);
    points=[low,high];
    print(a1,a2,a3);
    for point in result:
        temp=abs(point);
        if temp>=low and temp<=high:points.append(temp);
    values=[];
    if select[j1]==0:
        if select[j2]==0:
            for point in points:
                values.append(a1*point*point+a2*(b-point)*(b-point)+\
                              a3*point*point*(b-point)*(b-point));  
        elif select[j2]==1:
            for point in points:
                values.append(a1*point*point+a2*(b-point)+\
                              a3*point*point*(b-point));
        elif select[j2]==2:
            for point in points:
                values.append(a1*point*point+a2*((b-point)**0.5)+\
                              a3*point*point*((b-point)**0.5));
    elif select[j1]==1:
        if select[j2]==0:
            for point in points:
                values.append(a1*point+a2*(b-point)*(b-point)+\
                              a3*point*(b-point)*(b-point));
        elif select[j2]==1:
            for point in points:
                values.append(a1*point+a2*(b-point)+\
                              a3*point*(b-point));
        elif select[j2]==2:
            for point in points:
                values.append(a1*point+a2*((b-point)**0.5)+\
                              a3*point*((b-point)**0.5));
    elif select[j1]==2:
        if select[j2]==0:
            for point in points:
                values.append(a1*(point**0.5)+a2*(b-point)*(b-point)+\
                              a3*(point**0.5)*(b-point)*(b-point));
        elif select[j2]==1:
            for point in points:
                values.append(a1*(point**0.5)+a2*(b-point)+\
                              a3*(point**0.5)*(b-point));
        elif select[j2]==2:
            for point in points:
                values.append(a1*(point**0.5)+a2*((b-point)**0.5)+\
                              a3*(point**0.5)*((b-point)**0.5));
    u[j1]=points[numpy.argmin(values)];
    u[j2]=b-u[j1];
    if select[j1]==0:cu[j1]=u[j1]*u[j1];
    elif select[j1]==1:cu[j1]=u[j1];
    elif select[j1]==2:cu[j1]=u[j1]**0.5;
    if select[j2]==0:cu[j2]=u[j2]*u[j2];
    elif select[j2]==1:cu[j2]=u[j2];
    elif select[j2]==2:cu[j2]=u[j2]**0.5;
    for edge in index1:
        temp=1.0;
        for j in supergraph[edge]:
            if j in neighbor:temp*=(1-cu[neighbor.index(j)]);
        prob_edge[edge]=temp;
    for edge in index2:
        temp=1.0;
        for j in supergraph[edge]:
            if j in neighbor:temp*=(1-cu[neighbor.index(j)]);
        prob_edge[edge]=temp;
end=time.time();
print (end-start,'s');
    
cu=[];
for i in range(0,len(u)):
    if select[i]==0:cu.append(u[i]*u[i]);
    elif select[i]==1:cu.append(u[i]);
    else:cu.append(u[i]**0.5);    

#propagation
totalcustomer=[];
for i in range(0,totalpropagation):
    target=[];
    for j in range(0,number_of_neighbor):
        if random.random()<cu[j]:target.append(neighbor[j]);
    total=[];
    currentcustomer=queue.Queue();
    for j in target:
        currentcustomer.put(j);
        total.append(j);
    #from now on only currentcustomer takes effect
    while (not currentcustomer.empty()):
        head=currentcustomer.get();
        for j in g.neighbors(head):
            if j not in total:
                temp=random.random();
                if temp<alpha/g.in_degree(j):
                    total.append(j);
                    currentcustomer.put(j);
    totalcustomer.append(len(total));
totalarray=numpy.array(totalcustomer);
outfile=open('method3.txt','a');
outfile.write('average\t'+str(totalarray.mean())+'\tvariance\t'+str(totalarray.var())+\
              '\tmax\t'+str(totalarray.max())+'\tmin\t'+str(totalarray.min())+'\n');
outfile.close();
end=time.time();
print (end-start,'s');