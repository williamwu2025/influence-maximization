import networkx as nx
import random
import time
import numpy as np
try:import Queue as Q
except:import queue as Q
class data:
    graph=nx.DiGraph();
    files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1'];
    def __init__(self,file):
        infile=open(self.files[file]+'.txt');
        buffer=infile.readline();
        if buffer.find('Directed')==2:flag=1;
        elif buffer.find('Undirected')==2:flag=2;
        while buffer[0]=='#':buffer=infile.readline();
        order={};
        current=0;
        if flag==1:
            while buffer:
                [u,v]=buffer.split();
                if u not in order:
                    order[u]=current;
                    current+=1;
                if v not in order:
                    order[v]=current;
                    current+=1;
                self.graph.add_edge(order[v],order[u]);
                buffer=infile.readline();
        elif flag==2:
            while buffer:
                [u,v]=buffer.split();
                if u not in order:
                    order[u]=current;
                    current+=1;
                if v not in order:
                    order[v]=current;
                    current+=1;
                self.graph.add_edge(order[u],order[v]);
                self.graph.add_edge(order[v],order[u]);
                buffer=infile.readline();
        infile.close();
        print (self.graph.number_of_nodes(),'\tnodes');
        print (self.graph.number_of_edges(),'\tedges');
    def propagate(self,alpha,file):
        edges=[250000,2000000,20000000,40000000];
        outfile=open(self.files[file]+'_'+str(alpha)+'.txt','w');
        start=time.time();
        for temp in range(0,edges[file]):
            source=random.randint(0,99);
            q=Q.Queue();
            q.put(source);
            total=[source];
            while not q.empty():
                head=q.get();
                for temp in self.graph.neighbors(head):
                    if temp not in total and random.random()<alpha/self.graph.out_degree(head):
                        total.append(temp);
                        q.put(temp);
            for node in total:outfile.write(str(node)+' ');
            outfile.write('\n');
        end=time.time();
        outfile.close();
        outfile=open(self.files[file]+'_gbt.txt','a');
        outfile.write(str(alpha)+' '+str(end-start)+'s\n');
        outfile.close();
        return;
    def putu(self,file):
        p=[];
        t=[];
        for temp in range(0,self.graph.number_of_nodes()):
            rand=random.random();
            p.append(int(rand>0.85)+int(rand>0.95));
            t.append(random.randint(0,100)/100);
        np.savetxt(self.files[file]+'_pu.txt',np.array(p),fmt='%1.0f');
        np.savetxt(self.files[file]+'_tu.txt',np.array(t),fmt='%1.2f');
        return;

alphas=[0.6,0.8,1.0];
for file in range(0,4):
    dataset=data(file);
    dataset.putu(file);
    for alpha in alphas:
        dataset.propagate(alpha,file);