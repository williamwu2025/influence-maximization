import networkx
import random
import time
import numpy
import queue
import copy
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
number_of_optimize=1;
alpha=1;                                     #alpha
totalpropagation=10;                         #propagate
number_of_realization=10;
number_of_nschoose=25;
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

#initial25+choose25
neighbor=g.nodes()[:number_of_neighbor];
degrees=[];
for i in neighbor:degrees.append(g.degree(i));
degreesort=numpy.argsort(degrees);
initial25=[];
for i in degreesort[75:]:initial25.append(neighbor[i]);
ns=[];
for i in initial25:
    for j in g.neighbors(i):
        if j in neighbor and j not in ns and j not in initial25:ns.append(j);
choose25=random.sample(ns,25);
target=initial25+choose25;

#random resource allocation
u=[];
for i in neighbor:
    if i in initial25:u.append(0.9999);
    else:u.append(0.0001);
u=numpy.array(u);
select=numpy.loadtxt('cu'+str(fileflag)+'.txt').astype(int);

gn=g.nodes();
#calculate cu
cu=[];
for i in range(0,len(u)):
    if select[gn.index(neighbor[i])]==0:cu.append(u[i]*u[i]);
    elif select[gn.index(neighbor[i])]==1:cu.append(u[i]);
    elif select[gn.index(neighbor[i])]==2:cu.append(u[i]**0.5);
    
#load supergraph
supergraph=[];
infile=open('supergraph'+str(fileflag)+'.txt');
for temp in infile.readlines():
    supergraph.append(temp.split());
infile.close();
index={};
indexcount={};
for i in range(0,len(supergraph)):
    for j in supergraph[i]:
        if j in index:
            index[j].append(i);
            indexcount[j]+=1;
        else:
            index[j]=[i];
            indexcount[j]=1;

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
for z1 in range(0,number_of_optimize):
    [i,j]=random.sample(initial25,2);
    for z2 in range(0,number_of_realization):
        realized=[];
        for z3 in range(0,number_of_neighbor):
            if neighbor[z3] in initial25 and random.random()<cu[z3]:
                realized.append(neighbor[z3]);
        if i in realized:realized.remove(i);
        if j in realized:realized.remove(j);
        ns=[];
        for z3 in realized:
            for z4 in g.neighbors(z3):
                if z4 not in neighbor and z4 not in ns:ns.append(z4);
        nschoose=[];
        tempindex=copy.deepcopy(index);
        tempindexcount=copy.deepcopy(indexcount);
        for z3 in ns:
            if z3 in tempindexcount.keys():
                maxnode=z3;
                break;
        for z3 in range(0,number_of_nschoose):
            for z4 in ns:
                if z4 not in nschoose and z4 in indexcount.keys():
                    if indexcount[z4]>indexcount[maxnode]:maxnode=z4;
            #select maxnode
            nschoose.append(maxnode);
            for z4 in index[maxnode]:
                for z5 in supergraph[z4]:
                    if z5 != maxnode:
                        index[z5].remove(z4);
                        indexcount[z5]-=1;
            indexcount[maxnode]=0;
            index[maxnode]=[];
        chooseu=[];
        for z3 in ns:
            if z3 in nschoose:chooseu.append(0.9999);
            else:chooseu.append(0.0001);
        choosecu=[];
        for z3 in range(0,len(chooseu)):
            if select[gn.index(ns[z3])]==0:choosecu.append(chooseu[z3]*chooseu[z3]);
            elif select[gn.index(ns[z3])]==1:choosecu.append(chooseu[z3]);
            elif select[gn.index(ns[z3])]==2:choosecu.append(chooseu[z3]**0.5);    
        
        #optimize coordinate descent
        for z3 in range(0,number_of_optimize):
            j1=random.randint(0,len(ns)-1);
            while ns[j1] not in index:
                j1=random.randint(0,len(ns)-1);
            j2=random.randint(0,len(ns)-1);
            while ns[j2] not in index or j1==j2:
                j2=random.randint(0,len(ns)-1);
            b=chooseu[j1]+chooseu[j2];
            low=max(0,b-1);
            high=min(1,b);
            if low==high:continue;
            index1=index[ns[j1]];
            index2=index[ns[j2]];
            index12=[ii for ii in index1 if ii in index2];
            a1=0;
            a2=0;
            a3=0;
            if choosecu[j1]==1:
                a1=0;
                a3=0;
                for z4 in index2:a2-=prob_edge[z4]/(1-choosecu[j2]);
            elif choosecu[j2]==1:
                a2=0;
                a3=0;
                for z4 in index1:a1-=prob_edge[z4]/(1-choosecu[j1]);
            elif chooseu[j1]!=1 and choosecu[j2]!=1:
                for z4 in index1:
                    temp=prob_edge[z4]/(1-choosecu[j1]);
                    if z4 in index12:temp/=(1-choosecu[j2]);
                    a1-=temp;
                for z4 in index2:
                    temp=prob_edge[z4]/(1-choosecu[j2]);
                    if z4 in index12:temp/=(1-choosecu[j1]);
                    a2-=temp;
                for z4 in index12:
                    temp=prob_edge[z4]/(1-choosecu[j1])/(1-choosecu[j2]);
                    a3+=temp;
            if select[gn.index(ns[j1])]==0:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*x*x+a2*(b-x)*(b-x)+a3*x*x*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*x*x+a2*(b-x)+a3*x*x*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*x*x+a2*((b-x)**0.5)+a3*x*x*((b-x)**0.5),x),x);
            elif select[gn.index(ns[j1])]==1:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*x+a2*(b-x)*(b-x)+a3*x*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*x+a2*(b-x)+a3*x*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*x+a2*((b-x)**0.5)+a3*x*((b-x)**0.5),x),x);
            elif select[gn.index(ns[j1])]==2:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*(x**0.5)+a2*(b-x)*(b-x)+a3*(x**0.5)*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*(x**0.5)+a2*(b-x)+a3*(x**0.5)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*(x**0.5)+a2*((b-x)**0.5)+a3*(x**0.5)*((b-x)**0.5),x),x);
            points=[low,high];
            for point in result:
                temp=abs(point);
                if temp>=low and temp<=high:points.append(temp);
            values=[];
            if select[gn.index(ns[j1])]==0:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*point*point+a2*(b-point)*(b-point)+\
                              a3*point*point*(b-point)*(b-point));  
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*point*point+a2*(b-point)+\
                              a3*point*point*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*point*point+a2*((b-point)**0.5)+\
                              a3*point*point*((b-point)**0.5));
            elif select[gn.index(ns[j1])]==1:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*point+a2*(b-point)*(b-point)+\
                              a3*point*(b-point)*(b-point));
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*point+a2*(b-point)+\
                              a3*point*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*point+a2*((b-point)**0.5)+\
                              a3*point*((b-point)**0.5));
            elif select[gn.index(ns[j1])]==2:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*(b-point)*(b-point)+\
                              a3*(point**0.5)*(b-point)*(b-point));
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*(b-point)+\
                              a3*(point**0.5)*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*((b-point)**0.5)+\
                              a3*(point**0.5)*((b-point)**0.5));
            chooseu[j1]=points[numpy.argmin(values)];
            chooseu[j2]=b-chooseu[j1];
            if select[gn.index(ns[j1])]==0:choosecu[j1]=chooseu[j1]*chooseu[j1];
            elif select[gn.index(ns[j1])]==1:choosecu[j1]=chooseu[j1];
            elif select[gn.index(ns[j1])]==2:choosecu[j1]=chooseu[j1]**0.5;
            if select[gn.index(ns[j2])]==0:choosecu[j2]=chooseu[j2]*chooseu[j2];
            elif select[gn.index(ns[j2])]==1:choosecu[j2]=chooseu[j2];
            elif select[gn.index(ns[j2])]==2:choosecu[j2]=chooseu[j2]**0.5;
            for edge in index1:
                temp=1.0;
                for z4 in supergraph[edge]:
                    if z4 in ns:temp*=(1-choosecu[j1]);
                prob_edge[edge]=temp;
            for edge in index2:
                temp=1.0;
                for z4 in supergraph[edge]:
                    if z4 in ns:temp*=(1-choosecu[j2]);
                prob_edge[edge]=temp;
        totalcustomer=[];
        for z3 in range(0,totalpropagation):
            nsrealized=[];
            for z3 in range(0,len(ns)):
                if random.random()<choosecu[z3]:nsrealized.append(ns[z3]);
            total=[];
            currentcustomer=queue.Queue();
            for z4 in nsrealized:
                currentcustomer.put(z4);
                total.append(z4);
            #from now on only currentcustomer takes effect
            while (not currentcustomer.empty()):
                head=currentcustomer.get();
                for z5 in g.neighbors(head):
                    if z5 not in total and z5 not in neighbor:
                        temp=random.random();
                        if temp<alpha/g.in_degree(z5):
                            total.append(z5);
                            currentcustomer.put(z5);
            totalcustomer.append(len(total));
        totalarray=numpy.array(totalcustomer);
        maxqnsmean=totalarray.mean();
        maxqns=copy.deepcopy(ns);
        maxqnsu=copy.deepcopy(chooseu);
        maxqnscu=copy.deepcopy(choosecu);
        
        #maxqnsi
        for z3 in g.neighbors(i):
            if z3 not in neighbor and z3 not in ns:
                ns.append(z3);
                chooseu.append(0.0001);
                if select[gn.index(z3)]==0:choosecu.append(0.0001*0.0001);
                elif select[gn.index(z3)]==1:choosecu.append(0.0001);
                elif select[gn.index(z3)]==2:choosecu.append(0.0001**0.5); 
        for z3 in range(0,number_of_optimize):
            j1=random.randint(0,len(ns)-1);
            while ns[j1] not in index:
                j1=random.randint(0,len(ns)-1);
            j2=random.randint(0,len(ns)-1);
            while ns[j2] not in index or j1==j2:
                j2=random.randint(0,len(ns)-1);
            b=chooseu[j1]+chooseu[j2];
            low=max(0,b-1);
            high=min(1,b);
            if low==high:continue;
            index1=index[ns[j1]];
            index2=index[ns[j2]];
            index12=[ii for ii in index1 if ii in index2];
            a1=0;
            a2=0;
            a3=0;
            if choosecu[j1]==1:
                a1=0;
                a3=0;
                for z4 in index2:a2-=prob_edge[z4]/(1-choosecu[j2]);
            elif choosecu[j2]==1:
                a2=0;
                a3=0;
                for z4 in index1:a1-=prob_edge[z4]/(1-choosecu[j1]);
            elif chooseu[j1]!=1 and choosecu[j2]!=1:
                for z4 in index1:
                    temp=prob_edge[z4]/(1-choosecu[j1]);
                    if z4 in index12:temp/=(1-choosecu[j2]);
                    a1-=temp;
                for z4 in index2:
                    temp=prob_edge[z4]/(1-choosecu[j2]);
                    if z4 in index12:temp/=(1-choosecu[j1]);
                    a2-=temp;
                for z4 in index12:
                    temp=prob_edge[z4]/(1-choosecu[j1])/(1-choosecu[j2]);
                    a3+=temp;
            if select[gn.index(ns[j1])]==0:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*x*x+a2*(b-x)*(b-x)+a3*x*x*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*x*x+a2*(b-x)+a3*x*x*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*x*x+a2*((b-x)**0.5)+a3*x*x*((b-x)**0.5),x),x);
            elif select[gn.index(ns[j1])]==1:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*x+a2*(b-x)*(b-x)+a3*x*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*x+a2*(b-x)+a3*x*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*x+a2*((b-x)**0.5)+a3*x*((b-x)**0.5),x),x);
            elif select[gn.index(ns[j1])]==2:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*(x**0.5)+a2*(b-x)*(b-x)+a3*(x**0.5)*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*(x**0.5)+a2*(b-x)+a3*(x**0.5)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*(x**0.5)+a2*((b-x)**0.5)+a3*(x**0.5)*((b-x)**0.5),x),x);
            points=[low,high];
            for point in result:
                temp=abs(point);
                if temp>=low and temp<=high:points.append(temp);
            values=[];
            if select[gn.index(ns[j1])]==0:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*point*point+a2*(b-point)*(b-point)+\
                              a3*point*point*(b-point)*(b-point));  
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*point*point+a2*(b-point)+\
                              a3*point*point*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*point*point+a2*((b-point)**0.5)+\
                              a3*point*point*((b-point)**0.5));
            elif select[gn.index(ns[j1])]==1:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*point+a2*(b-point)*(b-point)+\
                              a3*point*(b-point)*(b-point));
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*point+a2*(b-point)+\
                              a3*point*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*point+a2*((b-point)**0.5)+\
                              a3*point*((b-point)**0.5));
            elif select[gn.index(ns[j1])]==2:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*(b-point)*(b-point)+\
                              a3*(point**0.5)*(b-point)*(b-point));
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*(b-point)+\
                              a3*(point**0.5)*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*((b-point)**0.5)+\
                              a3*(point**0.5)*((b-point)**0.5));
            chooseu[j1]=points[numpy.argmin(values)];
            chooseu[j2]=b-chooseu[j1];
            if select[gn.index(ns[j1])]==0:choosecu[j1]=chooseu[j1]*chooseu[j1];
            elif select[gn.index(ns[j1])]==1:choosecu[j1]=chooseu[j1];
            elif select[gn.index(ns[j1])]==2:choosecu[j1]=chooseu[j1]**0.5;
            if select[gn.index(ns[j2])]==0:choosecu[j2]=chooseu[j2]*chooseu[j2];
            elif select[gn.index(ns[j2])]==1:choosecu[j2]=chooseu[j2];
            elif select[gn.index(ns[j2])]==2:choosecu[j2]=chooseu[j2]**0.5;
            for edge in index1:
                temp=1.0;
                for z4 in supergraph[edge]:
                    if z4 in ns:temp*=(1-choosecu[j1]);
                prob_edge[edge]=temp;
            for edge in index2:
                temp=1.0;
                for z4 in supergraph[edge]:
                    if z4 in ns:temp*=(1-choosecu[j2]);
                prob_edge[edge]=temp;
        totalcustomer=[];
        for z3 in range(0,totalpropagation):
            nsrealized=[];
            for z3 in range(0,len(ns)):
                if random.random()<choosecu[z3]:nsrealized.append(ns[z3]);
            total=[];
            currentcustomer=queue.Queue();
            for z4 in nsrealized:
                currentcustomer.put(z4);
                total.append(z4);
            #from now on only currentcustomer takes effect
            while (not currentcustomer.empty()):
                head=currentcustomer.get();
                for z5 in g.neighbors(head):
                    if z5 not in total and z5 not in neighbor:
                        temp=random.random();
                        if temp<alpha/g.in_degree(z5):
                            total.append(z5);
                            currentcustomer.put(z5);
            totalcustomer.append(len(total));
        totalarray=numpy.array(totalcustomer);
        maxqnsimean=totalarray.mean();
        
        #maxqnsij
        for z3 in g.neighbors(j):
            if z3 not in neighbor and z3 not in ns:
                ns.append(z3);
                chooseu.append(0.0001);
                if select[gn.index(z3)]==0:choosecu.append(0.0001*0.0001);
                elif select[gn.index(z3)]==1:choosecu.append(0.0001);
                elif select[gn.index(z3)]==2:choosecu.append(0.0001**0.5); 
        for z3 in range(0,number_of_optimize):
            j1=random.randint(0,len(ns)-1);
            while ns[j1] not in index:
                j1=random.randint(0,len(ns)-1);
            j2=random.randint(0,len(ns)-1);
            while ns[j2] not in index or j1==j2:
                j2=random.randint(0,len(ns)-1);
            b=chooseu[j1]+chooseu[j2];
            low=max(0,b-1);
            high=min(1,b);
            if low==high:continue;
            index1=index[ns[j1]];
            index2=index[ns[j2]];
            index12=[ii for ii in index1 if ii in index2];
            a1=0;
            a2=0;
            a3=0;
            if choosecu[j1]==1:
                a1=0;
                a3=0;
                for z4 in index2:a2-=prob_edge[z4]/(1-choosecu[j2]);
            elif choosecu[j2]==1:
                a2=0;
                a3=0;
                for z4 in index1:a1-=prob_edge[z4]/(1-choosecu[j1]);
            elif chooseu[j1]!=1 and choosecu[j2]!=1:
                for z4 in index1:
                    temp=prob_edge[z4]/(1-choosecu[j1]);
                    if z4 in index12:temp/=(1-choosecu[j2]);
                    a1-=temp;
                for z4 in index2:
                    temp=prob_edge[z4]/(1-choosecu[j2]);
                    if z4 in index12:temp/=(1-choosecu[j1]);
                    a2-=temp;
                for z4 in index12:
                    temp=prob_edge[z4]/(1-choosecu[j1])/(1-choosecu[j2]);
                    a3+=temp;
            if select[gn.index(ns[j1])]==0:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*x*x+a2*(b-x)*(b-x)+a3*x*x*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*x*x+a2*(b-x)+a3*x*x*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*x*x+a2*((b-x)**0.5)+a3*x*x*((b-x)**0.5),x),x);
            elif select[gn.index(ns[j1])]==1:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*x+a2*(b-x)*(b-x)+a3*x*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*x+a2*(b-x)+a3*x*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*x+a2*((b-x)**0.5)+a3*x*((b-x)**0.5),x),x);
            elif select[gn.index(ns[j1])]==2:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*(x**0.5)+a2*(b-x)*(b-x)+a3*(x**0.5)*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*(x**0.5)+a2*(b-x)+a3*(x**0.5)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*(x**0.5)+a2*((b-x)**0.5)+a3*(x**0.5)*((b-x)**0.5),x),x);
            points=[low,high];
            for point in result:
                temp=abs(point);
                if temp>=low and temp<=high:points.append(temp);
            values=[];
            if select[gn.index(ns[j1])]==0:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*point*point+a2*(b-point)*(b-point)+\
                              a3*point*point*(b-point)*(b-point));  
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*point*point+a2*(b-point)+\
                              a3*point*point*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*point*point+a2*((b-point)**0.5)+\
                              a3*point*point*((b-point)**0.5));
            elif select[gn.index(ns[j1])]==1:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*point+a2*(b-point)*(b-point)+\
                              a3*point*(b-point)*(b-point));
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*point+a2*(b-point)+\
                              a3*point*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*point+a2*((b-point)**0.5)+\
                              a3*point*((b-point)**0.5));
            elif select[gn.index(ns[j1])]==2:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*(b-point)*(b-point)+\
                              a3*(point**0.5)*(b-point)*(b-point));
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*(b-point)+\
                              a3*(point**0.5)*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*((b-point)**0.5)+\
                              a3*(point**0.5)*((b-point)**0.5));
            chooseu[j1]=points[numpy.argmin(values)];
            chooseu[j2]=b-chooseu[j1];
            if select[gn.index(ns[j1])]==0:choosecu[j1]=chooseu[j1]*chooseu[j1];
            elif select[gn.index(ns[j1])]==1:choosecu[j1]=chooseu[j1];
            elif select[gn.index(ns[j1])]==2:choosecu[j1]=chooseu[j1]**0.5;
            if select[gn.index(ns[j2])]==0:choosecu[j2]=chooseu[j2]*chooseu[j2];
            elif select[gn.index(ns[j2])]==1:choosecu[j2]=chooseu[j2];
            elif select[gn.index(ns[j2])]==2:choosecu[j2]=chooseu[j2]**0.5;
            for edge in index1:
                temp=1.0;
                for z4 in supergraph[edge]:
                    if z4 in ns:temp*=(1-choosecu[j1]);
                prob_edge[edge]=temp;
            for edge in index2:
                temp=1.0;
                for z4 in supergraph[edge]:
                    if z4 in ns:temp*=(1-choosecu[j2]);
                prob_edge[edge]=temp;
        totalcustomer=[];
        for z3 in range(0,totalpropagation):
            nsrealized=[];
            for z3 in range(0,len(ns)):
                if random.random()<choosecu[z3]:nsrealized.append(ns[z3]);
            total=[];
            currentcustomer=queue.Queue();
            for z4 in nsrealized:
                currentcustomer.put(z4);
                total.append(z4);
            #from now on only currentcustomer takes effect
            while (not currentcustomer.empty()):
                head=currentcustomer.get();
                for z5 in g.neighbors(head):
                    if z5 not in total and z5 not in neighbor:
                        temp=random.random();
                        if temp<alpha/g.in_degree(z5):
                            total.append(z5);
                            currentcustomer.put(z5);
            totalcustomer.append(len(total));
        totalarray=numpy.array(totalcustomer);
        maxqnsijmean=totalarray.mean();
        
        #masqnsj
        ns=copy.deepcopy(maxqns);
        chooseu=copy.deepcopy(maxqnsu);
        choosecu=copy.deepcopy(maxqnscu);
        for z3 in g.neighbors(j):
            if z3 not in neighbor and z3 not in ns:
                ns.append(z3);
                chooseu.append(0.0001);
                if select[gn.index(z3)]==0:choosecu.append(0.0001*0.0001);
                elif select[gn.index(z3)]==1:choosecu.append(0.0001);
                elif select[gn.index(z3)]==2:choosecu.append(0.0001**0.5); 
        for z3 in range(0,number_of_optimize):
            j1=random.randint(0,len(ns)-1);
            while ns[j1] not in index:
                j1=random.randint(0,len(ns)-1);
            j2=random.randint(0,len(ns)-1);
            while ns[j2] not in index or j1==j2:
                j2=random.randint(0,len(ns)-1);
            b=chooseu[j1]+chooseu[j2];
            low=max(0,b-1);
            high=min(1,b);
            if low==high:continue;
            index1=index[ns[j1]];
            index2=index[ns[j2]];
            index12=[ii for ii in index1 if ii in index2];
            a1=0;
            a2=0;
            a3=0;
            if choosecu[j1]==1:
                a1=0;
                a3=0;
                for z4 in index2:a2-=prob_edge[z4]/(1-choosecu[j2]);
            elif choosecu[j2]==1:
                a2=0;
                a3=0;
                for z4 in index1:a1-=prob_edge[z4]/(1-choosecu[j1]);
            elif chooseu[j1]!=1 and choosecu[j2]!=1:
                for z4 in index1:
                    temp=prob_edge[z4]/(1-choosecu[j1]);
                    if z4 in index12:temp/=(1-choosecu[j2]);
                    a1-=temp;
                for z4 in index2:
                    temp=prob_edge[z4]/(1-choosecu[j2]);
                    if z4 in index12:temp/=(1-choosecu[j1]);
                    a2-=temp;
                for z4 in index12:
                    temp=prob_edge[z4]/(1-choosecu[j1])/(1-choosecu[j2]);
                    a3+=temp;
            if select[gn.index(ns[j1])]==0:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*x*x+a2*(b-x)*(b-x)+a3*x*x*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*x*x+a2*(b-x)+a3*x*x*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*x*x+a2*((b-x)**0.5)+a3*x*x*((b-x)**0.5),x),x);
            elif select[gn.index(ns[j1])]==1:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*x+a2*(b-x)*(b-x)+a3*x*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*x+a2*(b-x)+a3*x*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*x+a2*((b-x)**0.5)+a3*x*((b-x)**0.5),x),x);
            elif select[gn.index(ns[j1])]==2:
                if select[gn.index(ns[j2])]==0:
                    result=solve(diff(a1*(x**0.5)+a2*(b-x)*(b-x)+a3*(x**0.5)*(b-x)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==1:
                    result=solve(diff(a1*(x**0.5)+a2*(b-x)+a3*(x**0.5)*(b-x),x),x);
                elif select[gn.index(ns[j2])]==2:
                    result=solve(diff(a1*(x**0.5)+a2*((b-x)**0.5)+a3*(x**0.5)*((b-x)**0.5),x),x);
            points=[low,high];
            for point in result:
                temp=abs(point);
                if temp>=low and temp<=high:points.append(temp);
            values=[];
            if select[gn.index(ns[j1])]==0:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*point*point+a2*(b-point)*(b-point)+\
                              a3*point*point*(b-point)*(b-point));  
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*point*point+a2*(b-point)+\
                              a3*point*point*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*point*point+a2*((b-point)**0.5)+\
                              a3*point*point*((b-point)**0.5));
            elif select[gn.index(ns[j1])]==1:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*point+a2*(b-point)*(b-point)+\
                              a3*point*(b-point)*(b-point));
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*point+a2*(b-point)+\
                              a3*point*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*point+a2*((b-point)**0.5)+\
                              a3*point*((b-point)**0.5));
            elif select[gn.index(ns[j1])]==2:
                if select[gn.index(ns[j2])]==0:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*(b-point)*(b-point)+\
                              a3*(point**0.5)*(b-point)*(b-point));
                elif select[gn.index(ns[j2])]==1:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*(b-point)+\
                              a3*(point**0.5)*(b-point));
                elif select[gn.index(ns[j2])]==2:
                    for point in points:
                        values.append(a1*(point**0.5)+a2*((b-point)**0.5)+\
                              a3*(point**0.5)*((b-point)**0.5));
            chooseu[j1]=points[numpy.argmin(values)];
            chooseu[j2]=b-chooseu[j1];
            if select[gn.index(ns[j1])]==0:choosecu[j1]=chooseu[j1]*chooseu[j1];
            elif select[gn.index(ns[j1])]==1:choosecu[j1]=chooseu[j1];
            elif select[gn.index(ns[j1])]==2:choosecu[j1]=chooseu[j1]**0.5;
            if select[gn.index(ns[j2])]==0:choosecu[j2]=chooseu[j2]*chooseu[j2];
            elif select[gn.index(ns[j2])]==1:choosecu[j2]=chooseu[j2];
            elif select[gn.index(ns[j2])]==2:choosecu[j2]=chooseu[j2]**0.5;
            for edge in index1:
                temp=1.0;
                for z4 in supergraph[edge]:
                    if z4 in ns:temp*=(1-choosecu[j1]);
                prob_edge[edge]=temp;
            for edge in index2:
                temp=1.0;
                for z4 in supergraph[edge]:
                    if z4 in ns:temp*=(1-choosecu[j2]);
                prob_edge[edge]=temp;
        totalcustomer=[];
        for z3 in range(0,totalpropagation):
            nsrealized=[];
            for z3 in range(0,len(ns)):
                if random.random()<choosecu[z3]:nsrealized.append(ns[z3]);
            total=[];
            currentcustomer=queue.Queue();
            for z4 in nsrealized:
                currentcustomer.put(z4);
                total.append(z4);
            #from now on only currentcustomer takes effect
            while (not currentcustomer.empty()):
                head=currentcustomer.get();
                for z5 in g.neighbors(head):
                    if z5 not in total and z5 not in neighbor:
                        temp=random.random();
                        if temp<alpha/g.in_degree(z5):
                            total.append(z5);
                            currentcustomer.put(z5);
            totalcustomer.append(len(total));
        totalarray=numpy.array(totalcustomer);
        maxqnsjmean=totalarray.mean();
        
        #optimize ij
        b=u[neighbor.index(i)]+u[neighbor.index(j)];
        low=max(0,b-1);
        high=min(1,b);
        if low==high:continue;
        a1=maxqnsimean-maxqnsmean;
        a2=maxqnsjmean-maxqnsmean;
        a3=maxqnsijmean+maxqnsmean-maxqnsimean-maxqnsjmean;
        if select[gn.index(i)]==0:
            if select[gn.index(j)]==0:
                result=solve(diff(a1*x*x+a2*(b-x)*(b-x)+a3*x*x*(b-x)*(b-x),x),x);
            elif select[gn.index(j)]==1:
                result=solve(diff(a1*x*x+a2*(b-x)+a3*x*x*(b-x),x),x);
            elif select[gn.index(j)]==2:
                result=solve(diff(a1*x*x+a2*((b-x)**0.5)+a3*x*x*((b-x)**0.5),x),x);
        elif select[gn.index(i)]==1:
            if select[gn.index(j)]==0:
                result=solve(diff(a1*x+a2*(b-x)*(b-x)+a3*x*(b-x)*(b-x),x),x);
            elif select[gn.index(j)]==1:
                result=solve(diff(a1*x+a2*(b-x)+a3*x*(b-x),x),x);
            elif select[gn.index(j)]==2:
                result=solve(diff(a1*x+a2*((b-x)**0.5)+a3*x*((b-x)**0.5),x),x);
        elif select[gn.index(i)]==2:
            if select[gn.index(j)]==0:
                result=solve(diff(a1*(x**0.5)+a2*(b-x)*(b-x)+a3*(x**0.5)*(b-x)*(b-x),x),x);
            elif select[gn.index(j)]==1:
                result=solve(diff(a1*(x**0.5)+a2*(b-x)+a3*(x**0.5)*(b-x),x),x);
            elif select[gn.index(j)]==2:
                result=solve(diff(a1*(x**0.5)+a2*((b-x)**0.5)+a3*(x**0.5)*((b-x)**0.5),x),x);
        points=[low,high];
        for point in result:
            temp=abs(point);
            if temp>=low and temp<=high:points.append(temp);
        values=[];
        if select[gn.index(i)]==0:
            if select[gn.index(j)]==0:
                for point in points:
                    values.append(a1*point*point+a2*(b-point)*(b-point)+\
                              a3*point*point*(b-point)*(b-point));  
            elif select[gn.index(j)]==1:
                for point in points:
                    values.append(a1*point*point+a2*(b-point)+\
                              a3*point*point*(b-point));
            elif select[gn.index(j)]==2:
                for point in points:
                    values.append(a1*point*point+a2*((b-point)**0.5)+\
                              a3*point*point*((b-point)**0.5));
        elif select[gn.index(i)]==1:
            if select[gn.index(j)]==0:
                for point in points:
                    values.append(a1*point+a2*(b-point)*(b-point)+\
                              a3*point*(b-point)*(b-point));
            elif select[gn.index(j)]==1:
                for point in points:
                    values.append(a1*point+a2*(b-point)+\
                              a3*point*(b-point));
            elif select[gn.index(j)]==2:
                for point in points:
                    values.append(a1*point+a2*((b-point)**0.5)+\
                              a3*point*((b-point)**0.5));
        elif select[gn.index(i)]==2:
            if select[gn.index(j)]==0:
                for point in points:
                    values.append(a1*(point**0.5)+a2*(b-point)*(b-point)+\
                              a3*(point**0.5)*(b-point)*(b-point));
            elif select[gn.index(j)]==1:
                for point in points:
                    values.append(a1*(point**0.5)+a2*(b-point)+\
                              a3*(point**0.5)*(b-point));
            elif select[gn.index(j)]==2:
                for point in points:
                    values.append(a1*(point**0.5)+a2*((b-point)**0.5)+\
                              a3*(point**0.5)*((b-point)**0.5));
        u[neighbor.index(i)]=points[numpy.argmin(values)];
        u[neighbor.index(j)]=b-u[neighbor.index(i)];
        if select[gn.index(i)]==0:cu[neighbor.index(i)]=u[neighbor.index(i)]*u[neighbor.index(i)];
        elif select[gn.index(i)]==1:cu[neighbor.index(i)]=u[neighbor.index(i)];
        elif select[gn.index(i)]==2:cu[neighbor.index(i)]=u[neighbor.index(i)]**0.5;
        if select[gn.index(j)]==0:cu[neighbor.index(j)]=u[neighbor.index(j)]*u[neighbor.index(j)];
        elif select[gn.index(j)]==1:cu[neighbor.index(j)]=u[neighbor.index(j)];
        elif select[gn.index(j)]==2:cu[neighbor.index(j)]=u[neighbor.index(j)]**0.5;
        for edge in index1:
            temp=1.0;
            for z4 in supergraph[edge]:
                if z4 in ns:temp*=(1-choosecu[j1]);
            prob_edge[edge]=temp;
        for edge in index2:
            temp=1.0;
            for z4 in supergraph[edge]:
                if z4 in ns:temp*=(1-choosecu[j2]);
            prob_edge[edge]=temp;
end=time.time();
print (end-start,'s');