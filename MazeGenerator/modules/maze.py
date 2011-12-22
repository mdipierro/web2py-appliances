class Maze:
    def __init__(self,side,start=None,stop=None):
        self.side=side
        self.start=start or 0
        self.stop=stop or side**2-1
    def map(self,x,y):
        return x*self.side+y
    def parent(self,i):
        j=self.sets[i]
        while j>=0:
            i,j=j,self.sets[i]
        return i
    def join(self,i,j):
        pi=self.parent(i)
        pj=self.parent(j)
        if pi!=pj:
            self.sets[pi]=pj
            self.n-=1
    def solve(self):
        import random
        self.sets=[-1]*(self.side**2)
        self.links={}
        self.n=self.side**2
        for x in range(self.side-1):
            for y in range(self.side-1):
                self.links[x,y,'u']=(x,y+1)
                self.links[x,y,'l']=(x+1,y)
        keys=self.links.keys()
        for i in range(0,len(keys)-1):
            j=random.randint(i+1,len(keys)-1)
            keys[i],keys[j]=keys[j],keys[i]
        for key in keys:
            x,y,k = key
            i=self.map(x,y)
            if k=='u': y=y+1
            elif k=='l': x=x+1
            j=self.map(x,y)
            pi=self.parent(i)
            pj=self.parent(j)
            if pi!=pj:           
                del self.links[key]
                self.join(pi,pj)
        return self.links

if __name__=='__main__':
    print Maze(5).solve()
