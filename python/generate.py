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
if (buffer.find('Directed')==2):
    flag=1;
elif (buffer.find('Undirected')==2):
    flag=2;
g=networkx.DiGraph();
#read file and generate graph
nodeorder={};
currentorder=0;
while buffer[0]=='#':
    buffer=infile.readline();
if flag==1:
    while buffer:
        [u,v]=buffer.split();
        if u not in nodeorder:
            nodeorder[u]=currentorder;
            currentorder+=1;
        if v not in nodeorder:
            nodeorder[v]=currentorder;
            currentorder+=1;
        g.add_edge(nodeorder[v],nodeorder[u]);
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
        g.add_edge(nodeorder[u],nodeorder[v]);
        g.add_edge(nodeorder[v],nodeorder[u]);
        buffer=infile.readline();
infile.close();
print (g.number_of_nodes(),'\tnodes');
print (g.number_of_edges(),'\tedges');

number_of_superedge=250000;                       #generate super edges
supergraph=[];
index={};
indexcount={};
#generate supergraph
for i in range(0,number_of_superedge):
    graph=[];
    #randomly choose source node
    source=g.nodes()[random.randint(0,g.number_of_nodes()-1)];
    graph.append(source);
    currentcustomer=queue.Queue();
    currentcustomer.put(source);
    if source in index:
        index[source].append(i);
        indexcount[source]+=1;
    else:
        index[source]=[i];
        indexcount[source]=1;
    #propagate through network
    while (not currentcustomer.empty()):
        head=currentcustomer.get();
        for j in g.neighbors(head):
            if j not in graph and random.random()<alpha/g.out_degree(head):
                graph.append(j);
                currentcustomer.put(j);
                if j in index:
                    index[j].append(i);
                    indexcount[j]+=1;
                else:
                    index[j]=[i];
                    indexcount[j]=1;
    supergraph.append(graph);
end=time.time();
print (end-start,'s');


neighbor=g.nodes()[:number_of_neighbor];
target=[];
for i in neighbor:
    if i in indexcount.keys():
        maxnode=i;
        break;
for i in range(0,number_of_target):
    for j in neighbor:
        if j not in target and j in indexcount.keys():
            if indexcount[j]>indexcount[maxnode]:
                maxnode=j;
    #select maxnode
    target.append(maxnode);
    for j in index[maxnode]:
        for k in supergraph[j]:
            if k != maxnode:
                index[k].remove(j);
                indexcount[k]-=1;
    indexcount[maxnode]=0;
    index[maxnode]=[];             

outfile=open('target'+str(fileflag)+'.txt','w');
for i in target:outfile.write(str(i)+' ');
outfile.write('\n');
outfile.close();

outfile=open('supergraph'+str(fileflag)+'.txt','w');
for i in supergraph:
    for j in i:
        outfile.write(str(j)+' ');
    outfile.write('\n');
outfile.close();

outfile=open('cu'+str(fileflag)+'.txt','w');
for i in range(0,g.number_of_nodes()):
    temp=random.random();
    if temp<0.85:outfile.write('0\n');
    elif temp<0.95:outfile.write('1\n');
    else:outfile.write('2\n');
outfile.close();
end=time.time();
print (end-start,'s');