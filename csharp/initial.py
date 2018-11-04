import random
files = ['Wiki-Vote', 'CA-CondMat', 'com-dblp.ungraph', 'soc-LiveJournal1']
file = 3
infile = open(files[file]+'.csv', 'r')
[v,e] = infile.readline().strip().split()
v = int(v)
e = int(e)
# e = int(infile.readline().strip())
ave = float(e)/float(v)
pre = {}
des = {}
for line in infile.readlines():
    [u, v, d] = [int(tmp) for tmp in line.strip().split()]
    if v not in pre:
        pre[v] = []
    if u not in des:
        des[u] = []
    pre[v].append(u)
    des[u].append(v)
infile.close()
print(1)
outfile = open(files[file]+'_ini.txt', 'w')
count = 0
source = []
target = []
for i in list(pre.keys()):
    if i not in des.keys(): continue
    if len(pre[i]) < 8*ave or len(des[i]) < 8*ave: continue
    for j in pre[i]:
        if len(des[j]) < ave:
           if j not in source and i not in target:
                source.append(j)
                target.append(i)
                count += 1
                outfile.write(str(j)+'\n')
                break
    if count == 1000:
        break
outfile.close()
