class Snake:
    def __init__(self, width=600, height=400):
        self.width = width
        self.height = height

    def xml(self):
        return """
<script type="application/processing">

var width = %s;
var height = %s;
var x = width/2;
var y = height/2;
var vx = 2;
var vy = 0;

void setup() {
  size(width,height);
  smooth();
  frameRate(10);
  loop();
}

void draw() {
  fill(255,0,0);
  ellipse(x,y,10,10);
  x = (x+vx+width) %% width;
  y = (y+vy+height) %% height;
}

void keyPressed() {
  if(key == CODED) {
    if(keyCode==UP) { vx = 0; vy-=1;}
    if(keyCode==DOWN) { vx = 0; vy+=1;}
    if(keyCode==LEFT) { vx-=1; vy = 0;}
    if(keyCode==RIGHT) { vx+=1; vy = 0;}
  }
}

void mousePressed() {
}

</script><canvas width="%spx" height="%spx"></canvas>
""" % (self.width,self.height,self.width, self.height)
