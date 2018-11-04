from random import random
files = ['Wiki-Vote', 'CA-CondMat', 'com-dblp.ungraph', 'soc-LiveJournal1']
file = 3
infile = open(files[file]+'.txt', 'r')
temp = infile.readline()
if 'Directed' in temp:
    flag = 0
if 'Undirected' in temp:
    flag = 1
while temp[0] == '#':
    temp = infile.readline()
v = 0
e = 0
order = {}
while temp:
    e += (flag+1)
    [source, target] = temp.strip().split()
    if source and target:
        if source not in order:
            order[source] = [v, flag]
            v += 1
        elif flag == 1:
            order[source][1] += 1
        if target not in order:
            order[target] = [v, 1]
            v += 1
        else:
            order[target][1] += 1
    temp = infile.readline()
infile.close()
# infile = open(files[file]+'.txt', 'r')
# outfile = open(files[file]+'.csv', 'w')
# outfile.write(str(v)+' '+str(e)+'\n')
# temp = infile.readline()
# while temp[0] == '#':
#     temp = infile.readline()
# while temp:
#     [source, target] = temp.strip().split()
#     if source and target:
#         outfile.write(str(order[source][0])+' '+str(order[target][0])+' '+str(order[target][1])+'\n')
#         if flag == 1:
#            outfile.write(str(order[target][0])+' '+str(order[source][0])+' '+str(order[source][1])+'\n')
#     temp = infile.readline()
# infile.close()
# outfile.close()
outfile = open(files[file]+'_cu.txt', 'w')
for i in range(v):
    temp = random()
    if temp < 0.15:
        outfile.write('0\n')
    elif temp < 0.35:
        outfile.write('1\n')
    else:
        outfile.write('2\n')
outfile.close()
# outfile = open(files[file]+'_tu.txt', 'w')
# for i in range(v):
#     outfile.write(str(round(random(), 2))+'\n')
# outfile.close()