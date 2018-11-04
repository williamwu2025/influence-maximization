import networkx
import random
import time
import numpy
import queue
start=time.time();
fileflag=0;                                  #choose file
files=['Wiki-Vote.txt','CA-CondMat.txt',\
       'com-dblp.ungraph.txt','soc-LiveJournal1.txt'];
infile=open(files[fileflag]);
buffer=infile.readline();
flag=0;
number_of_target=50;                         #initial B
number_of_neighbor=100;
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

#propagation
totalcustomer=[];
for i in range(0,totalpropagation):
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
outfile=open('method2.txt','a');
outfile.write('average\t'+str(totalarray.mean())+'\tvariance\t'+str(totalarray.var())+\
              '\tmax\t'+str(totalarray.max())+'\tmin\t'+str(totalarray.min())+'\n');
outfile.close();