from utils import *
import time
import numpy
import random
start=time.time();
fileflag=0;
gve=mygraph(fileflag);
s=numpy.loadtxt('target'+str(fileflag)+'.txt').astype(int);
num_of_x=100;
num_of_cd=10;
alpha=1;
num_of_propagate=100;
x=gve.g.nodes()[:num_of_x];
#with no cd
results=[];
for temp1 in range(0,num_of_propagate):
    realized=gve.realize();
    results.append(gve.propagate(realized,alpha));
results=numpy.array(results);
print(numpy.mean(results));
for temp1 in range(0,num_of_cd):
    [j1,j2]=random.sample(x,2);
    #[j1,j2]=[1,2];
    #print(gve.cu[j1]);
    #print(gve.cu[j2]);
    b=gve.cu[j1]+gve.cu[j2];
    low=max(0,b-1);
    high=min(1,b);
    if low>=high:continue;
    a1,a2,a3=gve.a1a2a3(j1,j2);
    roots=gve.solve(j1,j2,a1,a2,a3,b);
    points=gve.clip(roots,low,high);
    values=[];
    for temp2 in points:
        values.append(gve.value(j1,j2,a1,a2,a3,b,temp2));
    #probable points and corresponding values
    #print(points);
    #print(values);
    gve.cu[j1]=points[numpy.argmin(values)];
    gve.cu[j2]=b-gve.cu[j1];
    gve.update_prob_edge(j1);
    gve.update_prob_edge(j2);
#after cd
results=[];
for temp1 in range(0,num_of_propagate):
    realized=gve.realize();
    results.append(gve.propagate(realized,alpha));
results=numpy.array(results);
print(numpy.mean(results));
end=time.time();
print (end-start,'s');
test=gve.cu;