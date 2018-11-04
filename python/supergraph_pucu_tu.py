import networkx
import random
import time
import numpy
try:import Queue 
except:import queue as Queue
start=time.time();
class mygraph:
    g=networkx.DiGraph();
    x=[];
    supergraph=[];
    def __init__(self,filename):
        infile=open(filename+'.txt');
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
                self.g.add_edge(nodeorder[v],nodeorder[u]);
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
        print (self.g.number_of_nodes(),'\tnodes');
        print (self.g.number_of_edges(),'\tedges');
    
    def propagate_once(self,source,alpha):
        q=Queue.Queue();
        q.put(source);
        total=[];
        total.append(source);
        while not q.empty():
            head=q.get();
            for temp in self.g.neighbors(head):
                if temp not in total:
                    rand=random.random();
                    if rand<alpha/self.g.out_degree(head):
                        total.append(temp);
                        q.put(temp);
        return total;
    
    def propagate(self,alpha,num_of_superedge):
        supergraph=[];
        for temp in range(0,num_of_superedge):
            source=random.sample(self.x,1)[0];
            supergraph.append(self.propagate_once(source,alpha));
        return supergraph;
        
files=['Wiki-Vote','CA-CondMat','com-dblp.ungraph','soc-LiveJournal1'];
superedge=[250000,2000000,20000000,40000000];
for temp in range(3,4):
    gve=mygraph(files[temp]);
    pucu=[];
    tu=[];
    for temp1 in gve.g.nodes():
        rand=random.random();
        if rand<0.85:pucu.append(0);
        elif rand<0.95:pucu.append(1);
        else:pucu.append(2);
    for temp1 in gve.g.nodes():
        rand=random.random();
        tu.append(int(rand*100+1)/100.0);
    pucu=numpy.array(pucu);
    numpy.savetxt(files[temp]+'_pucu.txt',pucu,fmt='%1.0f');
    tu=numpy.array(tu);
    numpy.savetxt(files[temp]+'_tu.txt',tu,fmt='%1.2f');
    for edges in range(0,superedge[temp]):
        supergraph=gve.propagate(1,1);
        outfile=open(files[temp]+'_supergraph.txt','a');
        for temp1 in supergraph:
            for temp2 in temp1:outfile.write(str(temp2)+' ');
            outfile.write('\n');
        outfile.close();
end=time.time();
print (end-start,'s');