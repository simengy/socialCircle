import random

def addEdges(srcList, tgtList, filename='additional.txt', density=0.5):

    f = open(filename, 'a')

    for i in srcList:
        for j in tgtList:
                 
            if random.random()>1.0-density and i!=j:
                f.write('{} {} {} {} {}\n'.format(str(i), str(j), str(1), 'c', 'Black'))
    

if __name__ == '__main__':

    srcList = [58, 59, 39, 98, 46, 47, 82, 84, 92, 93 ]
    tgtList = [55, 96, 97, 1, 11, 80]
    
    addEdges(srcList, tgtList)
