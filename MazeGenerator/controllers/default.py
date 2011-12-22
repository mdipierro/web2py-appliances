# -*- coding: utf-8 -*- 

class Maze:
    def __init__(self,side):
        """
        builds an empty square maze of side "side" and
        assumes start of maze is (0,0) and exit is (side-1,side-1)
        """
        self.side = side
    def map(self, x, y):
        """
        maps the (x,y) coordinate into a cell id with 0<=id<=side**2 
        """
        return x*self.side + y
    def parent(self,i):
        """
        implements the DisjointSets function parent
        it finds the presentative elment of set containing i
        """
        j = self.sets[i]
        while j>=0: i,j = j,self.sets[i]
        return i
    def join(self, i, j):
        """
        implements the DisjonintSets function join
        it joins the sets represented by elements i and j
        """        
        if i!=j: self.sets[i] = j
    def make(self):
        """
        builds a side*side maze by removing walls in random order
        until there is a path connecting every cell to every other cell
        it does not remove walls it introduces circular paths
       
        algorithm:
        - every cell is a DisjointSet
        - build a list of walls
        - delete a wall if it separates cells belonging to disjoint sets

        remaining walls are in self.links[x0,y0,x1,y1]=(x2,y2,x3,y3)
        deleted walls are in self.deleted[x0,y0,x1,y1]=(x2,y2,x3,y3)
        x0,y0,x1,y1 identifies the cells separated by the wall
        x2,y2,x3,y3 identifies the extremes of the wall for the purpose of drawing
        """
        import random
        self.sets = [-1]*(self.side**2)
        self.links = {}
        self.deleted  = {}
        self.solution = {}
        for x in range(self.side):
            for y in range(self.side):
                if y<self.side-1: self.links[x,y,x,y+1] = (x,y+1,x+1,y+1)
                if x<self.side-1: self.links[x,y,x+1,y] = (x+1,y,x+1,y+1)
        keys = self.links.keys()
        for i in range(0,len(keys)-1):
            j = random.randint(i+1,len(keys)-1)
            keys[i],keys[j] = keys[j],keys[i]
        for key in keys:
            x0,y0,x1,y1 = key
            pi = self.parent(self.map(x0,y0))
            pj = self.parent(self.map(x1,y1))
            if pi!=pj:
                self.deleted[key] = self.links[key]
                del self.links[key]
                self.join(pi,pj)
    def solve(self):
        """
        solves the maze as identified by self.seleted walls

        algorithm:
        - store cell (0,0) in a queue
        - loop until the queue is not empty
        - pop an element (x,y) from the queue and add to the queue
          neightbor elements not already in queue and not separeted by a wall
        - when a new cell (x0,y0) is added to the queue compute n, the length of the 
          shortest path connecting the cell to the start, and its previous neightbor 
          in the path (x,y) recursively    

        the solution is stored in self.solution[x0,y0]=(n,x,y) that for every cell (x0,y0)
        stores the length n of the path connecting to the start cell (0,0), and the 
        location previous element in the path (x,y).
        """
        self.solution = {(0,0):(1,0,0)}
        queue = [(0,0)]
        while queue:
            x,y = queue.pop()
            n,xo,yo = self.solution[x,y]
            for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                x0,y0 = x+dx,y+dy
                if 0<=x0<self.side and 0<=y0<self.side \
                        and not (x0,y0) in self.solution \
                        and ((x,y,x0,y0) in self.deleted or 
                             (x0,y0,x,y) in self.deleted):
                    self.solution[x0,y0] = (n+1,x,y)
                    queue.insert(0,(x0,y0))
    def xml(self):
        """
        given self.links and self.solution it builds a processing.js program to draw 
        and interact with the maze
        """
        response.files.append(URL(r=request,c='static',f='processing.min.js'))
        response.files.append(URL(r=request,c='static',f='processing.init.js'))
        side=self.side
        l=','.join('%i,%i,%i,%i' % k for k in self.links.values())
        d=','.join('%i,%i,%i,%i' % k for k in self.deleted.values())
        s=','.join('%i:%i' % (k[0]*self.side+k[1],v[1]*self.side+v[2]) for k,v in self.solution.items())
        xml = """
<script>
var width = %(width)s;
var side= %(side)s;
var stroke_weight = 2.0;
var solution = { %(solution)s };
</script>
<script type="application/processing">
var n = width/side;
int[] p = [ %(points)s ];
int[] q = [ %(deleted)s ];
void setup() { size(width, width); smooth(); frameRate(5); }
void draw() {  if(stroke_weight<0.1) { noLoop(); return; } drawnow(); }
void drawnow() {
  clear();
  // draw border of maze
  stroke(0);
  strokeWeight(2);
  line(0,n,0,width);
  line(n,0,width,0);
  line(width,0,width,width-n);
  line(0,width,width-n,width);
  // draw walls
  stroke(0);
  for(var i=0; i<p.length; i+=4) 
    line(n*p[i],n*p[i+1],n*p[i+2],n*p[i+3]); 
  // draw deleted walls until they fade out
  stroke(0);
  strokeWeight(stroke_weight);
  for(var i=0; i<q.length; i+=4) 
    line(n*q[i],n*q[i+1],n*q[i+2],n*q[i+3]); 
  // make the deleted walls fade			  
  stroke_weight=stroke_weight/2;
}
void mousePressed() {  
  // when the mouse is pressed or dragged draw shortest path to start of maze
  drawnow();	   
  strokeWeight(max((n-2)/2,2));
  x=int((mouseX-20)/n);
  y=int((mouseY-20)/n);
  stroke(255,255,0);
  k = x*side+y;    
  while(k && k<side*side) {
    k0 = solution[k];
    x0 = int(k0/side);
    y0 = k0 %% side;
    line(n*(x+0.5),n*(y+0.5),n*(x0+0.5),n*(y0+0.5));
    x=x0; y=y0; k=k0;
  }
}     
void mouseDragged() { mousePressed(); }
</script><canvas width="%(width)spx" height="%(width)spx"></canvas>
        """ % dict(points=l,deleted=d,solution=s,side=side, width=400)
        return xml


#@cache(request.env.path_info,time_expire=10,cache_model=cache.ram)
def index():
    """
    this is the only action (web2py specific code). makes the maze, solves it 
    and returns it serialized in processing.js
    """
    side=max(2,min(int(request.args(0) or 20),50))
    maze=Maze(side)
    maze.make()
    maze.solve()
    session.forget() # do not store sessions
    return dict(maze=XML(maze.xml()))

def embedded():
    side=30
    maze=Maze(side)
    maze.make()
    maze.solve()
    session.forget() # do not store sessions
    return dict(maze=XML(maze.xml()))
