import networkx
import random
import time
import numpy
import queue
start=time.time();
fileflag=1;                                 #choose file
if fileflag==1:
    infile=open('Wiki-Vote.txt');
elif fileflag==2:
    infile=open('CA-CondMat.txt');
elif fileflag==3:
    infile=open('com-dblp.ungraph.txt');
elif fileflag==4:
    infile=open('soc-LiveJournal1.txt');
buffer=infile.readline();
flag=0;
number_of_customer=100;
number_of_target=50;                         #initial B
alpha=1;                                     #alpha
totalinitial=50;                            #choose seed
totalpropagation=50;                        #propagate
seed1=0;
seed2=0;
if (buffer.find('Directed')==2):
    flag=1;
elif (buffer.find('Undirected')==2):
    flag=2;
g=networkx.DiGraph();
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
infile.close();                             #read file
print (g.number_of_nodes(),'\tnodes');
print (g.number_of_edges(),'\tedges');
customer=g.nodes()[:number_of_customer];
seed1=random.randint(1,number_of_target-1);
seed2=number_of_target-seed1;
customer1=[];
#choose seed1
for i in range(0,seed1):
    temp=random.randint(0,number_of_customer-1);
    while customer[temp] in customer1:
        temp=random.randint(0,number_of_customer-1);
    customer1.append(customer[temp]);
neighbor=[];
#generate neighbors of seed1
for i in customer1:
    for j in g.neighbors(i):
        if (j not in neighbor) and (j not in customer1):
            neighbor.append(j);
totalcustomer=[];
end=time.time();
print (end-start,'s');

for n1 in range(0,totalinitial):
    #select seed2 randomly
    customer2=[];
    if seed2>=len(neighbor):
        for i in neighbor:
            customer2.append(i);
    else:
        for i in range(0,seed2):
            temp=random.randint(0,len(neighbor)-1);
            while neighbor[temp] in customer2:
                temp=random.randint(0,len(neighbor)-1);
            customer2.append(neighbor[temp]);
    for n2 in range(0,totalpropagation):
        total=customer1+customer2;
        #propagate through network
        currentcustomer=queue.Queue();
        for i in customer2:
            currentcustomer.put(i);
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
#show results
totalarray=numpy.array(totalcustomer);
print('average\t',totalarray.mean(),'\tvariance\t',totalarray.var());
print('max\t',totalarray.max(),'\tmin\t',totalarray.min());
end=time.time();
print ('totaltime\t',end-start,'s');