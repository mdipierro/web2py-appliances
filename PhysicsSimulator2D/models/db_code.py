response.files.append(URL('static','js/processing.js'))

db.define_table('code',
                Field('title',requires=IS_NOT_IN_DB(db,'code.title')),
                Field('source','text'),
                auth.signature)
db.code.is_active.writable = db.code.is_active.readable = False

CODE = """
# Physics Simulation Code in CoffeeScript, by Massimo Di Pierro, BSD License

step_universe = (canvas) ->
  if timestep % 500 == 0 and timestep < 5000
    ball = new Ball()
    ball.color = [ random(255), random(255), random(255) ]
    ball.mass = 1.0 + random(3)
    ball.radius = 5 * ball.mass
    ball.x = width / 4
    ball.y = height * 3 / 4
    ball.vx = 2
    ball.vy = -1
    if balls.length == 2
      add_constraint ball, GUIDE(2, -1)
      add_force balls[0], SPRING(0.05, 50), balls[1]
  explode balls[2]  if timestep == 1400 and balls.length == 3
  eval(integrator)()
  canvas.background 255
  for ball in balls
    ball.draw canvas  if ball.active

class Ball
  constructor: ->
    @x = @y = 0.0
    @vx = @vy = 0.0
    @Fx = @Fy = 0.0
    @mass = 1.0
    @friction = 0.0
    @bounces = true
    @bounce_coefficient = 0.9
    @color = [ 0, 0, 0 ]
    @radius = 5
    @info = false
    @tail = 200
    @path = []
    @active = true
    @anchored = false
    @forces = []
    @constraints = []
    @moves = -> @active and not @anchored
    balls.push this
  
  compute_force: ->
    Fx = 0.0
    Fy = 0.0
    for force in @forces
      F = force()
      Fx += F[X]
      Fy += F[Y]
    @Fx = Fx - @friction * @vx
    @Fy = Fy - @friction * @vy - gravity * @mass
  
  step: ->
    @x = @x + dt * @vx
    @y = @y + dt * @vy
    @vx = @vx + dt * @Fx / @mass
    @vy = @vy + dt * @Fy / @mass
    @check_collisions()
    for constraint in @constraints
      constraint this
  
  check_collisions: -> handle_collisions(this) if @bounces
  
  draw: (canvas) ->
    canvas.fill @color[RED], @color[GREEN], @color[BLUE]
    canvas.noStroke()
    canvas.ellipse @x, height - @y, 2*@radius, 2*@radius
    display_info canvas, this  if @info
    display_tail canvas, this  if @tail

Euler = ->
  for ball in balls
    ball.compute_force()  if ball.moves()
  for ball in balls
    ball.step()  if ball.moves()

RungeKutta2 = ->
  for ball in balls
    ball.compute_force()  if ball.moves()
  for ball in balls
    if ball.moves()
      ball.ox = ball.x
      ball.oy = ball.y
      ball.ovx = ball.vx
      ball.ovy = ball.vy
      ball.oFx = ball.Fx
      ball.oFy = ball.Fy
      ball.step()
  for ball in balls
    ball.compute_force()  if ball.moves() and not ball.collided
  for ball in balls
    if ball.moves() and not ball.collided
      ball.vx = ball.ovx + dt / 2 * ball.oFx / ball.mass
      ball.vy = ball.ovy + dt / 2 * ball.oFy / ball.mass
      for constraint in ball.constraints
        constraint ball
      ball.x = ball.ox + dt * ball.vx
      ball.y = ball.oy + dt * ball.vy
      ball.vx = ball.ovx + dt / 2 * (ball.oFx + ball.Fx) / ball.mass
      ball.vy = ball.ovy + dt / 2 * (ball.oFy + ball.Fy) / ball.mass
      for constraint in ball.constraints
        constraint ball

AdamsMoultonBashforth = ->
  AB = (s, i) ->
    (55 * s[3][i] - 59 * s[2][i] + 37 * s[1][i] - 9 * s[0][i]) / 24
  AM = (s, i) ->
    (9 * s[3][i] + 19 * s[2][i] - 5 * s[1][i] + s[0][i]) / 24
  for ball in balls
    ball.compute_force()  if ball.moves()
  for ball in balls
    if ball.moves()
      ball.fh = []  unless ball.fh
      if ball.fh.length < 3
        ball.step()
        ball.check_collisions()
        ball.fh = [] if ball.collided 
        for constraint in ball.constraints
          constraint ball
      else
        ball.ox = ball.x
        ball.oy = ball.y
        ball.ovx = ball.vx
        ball.ovy = ball.vy
      ball.fh.push [ ball.vx, ball.vy, ball.Fx/ball.mass, ball.Fy/ball.mass ]
  for ball in balls
    if ball.moves() and ball.fh.length == 4
      ball.x = ball.ox + dt * AB(ball.fh, 0)
      ball.y = ball.oy + dt * AB(ball.fh, 1)
      ball.vx = ball.ovx + dt * AB(ball.fh, 2)
      ball.vy = ball.ovy + dt * AB(ball.fh, 3)
      for constraint in ball.constraints
        constraint ball
  for ball in balls
    if ball.moves() and ball.fh.length == 4
      ball.compute_force()
      ball.fh.splice 0, 1
      ball.fh.push [ ball.vx, ball.vy, ball.Fx/ball.mass, ball.Fy/ball.mass ]
  for ball in balls
    if ball.moves() and ball.fh.length == 4
      ball.x = ball.ox + dt * AM(ball.fh, 0)
      ball.y = ball.oy + dt * AM(ball.fh, 1)
      ball.vx = ball.ovx + dt * AM(ball.fh, 2)
      ball.vy = ball.ovy + dt * AM(ball.fh, 3)
      ball.fh.splice 0, 1
    ball.check_collisions()
    ball.fh = [] if ball.collided 
    for constraint in ball.constraints
      constraint ball

handle_collisions = (ball) ->
  ball.collided = false
  if ball.vx * dt < 0 and ball.x < ball.radius
    ball.vx = -ball.bounce_coefficient * ball.vx  
    ball.collided = true
  if ball.vy * dt < 0 and ball.y < ball.radius
    ball.vy = -ball.bounce_coefficient * ball.vy 
    ball.collided = true 
  if ball.vx * dt > 0 and ball.x > width - ball.radius
    ball.vx = -ball.bounce_coefficient * ball.vx  
    ball.collided = true
  if ball.vy * dt > 0 and ball.y > height - ball.radius
    ball.vy = -ball.bounce_coefficient * ball.vy  
    ball.collided = true

SPRING = (kappa, length) ->
  (d) ->
    kappa * (length - d)

R2INVERSE = (coeff) ->
  (d) ->
    coeff / (d * d)

add_force = (ball1, f, ball2) ->
  spring_ball1 = ->
    return [ 0, 0 ]  unless ball2.active
    x1 = ball1.x
    y1 = ball1.y
    x2 = ball2.x
    y2 = ball2.y
    d = sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    force = f(d)
    [ force * (x1 - x2) / d, force * (y1 - y2) / d ]  
  spring_ball2 = ->
    return [ 0, 0 ]  unless ball1.active
    x1 = ball1.x
    y1 = ball1.y
    x2 = ball2.x
    y2 = ball2.y
    d = sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    force = f(d)
    [ force * (x2 - x1) / d, force * (y2 - y1) / d ]  
  ball1.forces.push spring_ball1
  ball2.forces.push spring_ball2
  links.push [ ball1, ball2 ]

normalize = (vec) ->
  x = vec[X]
  y = vec[Y]
  norm = sqrt(x * x + y * y)
  [ x / norm, y / norm ]

scalar_product = (vec1, vec2) ->
  x1 = vec1[X]
  y1 = vec1[Y]
  x2 = vec2[X]
  y2 = vec2[Y]
  x1 * x2 + y1 * y2

project_out = (vec1, vec2) ->
  n = normalize(vec2)
  a = scalar_product(vec1, n)
  [ vec1[X] - a * n[X], vec1[Y] - a * n[Y] ]

PENDULUM = (x, y) ->
  (ball) ->
    v = project_out([ ball.vx, ball.vy ], [ x - ball.x, y - ball.y ])
    ball.vx = v[X]
    ball.vy = v[Y]

GUIDE = (x, y) ->
  (ball) ->
    v = project_out([ ball.vx, ball.vy ], [ y, -x ])
    ball.vx = v[X]
    ball.vy = v[Y]

add_constraint = (ball, f) ->
  ball.constraints.push f

explode = (ball) ->
  ball.active = false
  i = 0  
  while i < 20
    fragment = new Ball()
    fragment.color = [ 255, random(128), random(128) ]
    fragment.mass = 1.0 + random(1)
    fragment.radius = 5 * fragment.mass
    fragment.x = ball.x
    fragment.y = ball.y
    dv = random(5)
    theta = random(6.28)
    fragment.vx = ball.vx + dv * cos(theta)
    fragment.vy = ball.vy + dv * sin(theta)
    fragment.bounces = false
    fragment.tail = 50
    i++

display_info = (canvas, ball) ->
  canvas.text "vx=" + ball.vx.toFixed(2) + ",vy=" + ball.vy.toFixed(2), ball.x + ball.radius, height - ball.y - ball.radius
  canvas.stroke ball.color[RED], ball.color[GREEN], ball.color[BLUE], 80
  canvas.line ball.x, 0, ball.x, height
  canvas.text "x=" + ball.x.toFixed(2), ball.x + 5, height - 5
  canvas.line 0, height - ball.y, width, height - ball.y
  canvas.text "y=" + ball.y.toFixed(2), 5, height - ball.y - 5

display_tail = (canvas, ball) ->
  canvas.noStroke()
  length = Math.min(ball.tail, ball.path.length)
  i = 0
  while i < length
    op = 50 * (ball.tail - i) / ball.tail
    canvas.fill ball.color[RED], ball.color[GREEN], ball.color[BLUE], op
    point = ball.path[ball.path.length - i - 1]
    canvas.ellipse point[X], height - point[Y], 4, 4
    i++
  ball.path.push [ ball.x, ball.y ]

integrator = "AdamsMoultonBashforth"
X = 0
Y = 1
RED = 0
BLUE = 1
GREEN = 2
balls = []
timestep = 0
gravity = 0.5
dt = 0.2
height = 600
width = 800
pause = false
links = []
sin = Math.sin
cos = Math.cos
sqrt = Math.sqrt
random = (n) -> Math.random() * (n or 1)

window.onload = ->
  sketch = (canvas) ->
    fontA = canvas.loadFont("helvetica")
    canvas.textFont fontA, 18
    canvas.size width, height
    canvas.draw = ->
      unless pause
        step_universe canvas
        canvas.fill 0, 0, 0
        canvas.text "timestep=#{timestep} dt=#{dt} gravity=#{gravity}", 5, 20
        canvas.stroke 0
        for link in links
          canvas.line link[0].x,height-link[0].y,link[1].x,height-link[1].y
        timestep += (if (dt > 0) then 1 else -1)
  element = document.getElementById("canvasElement")
  canvas = new Processing(element,sketch)
"""

db.code.source.default = CODE

OTHER_CODE_CS = """

# code for the buttons (optional, resets some parameters)
window.reset_balls = ->
  balls = []
  links = []
  timestep = 0
window.set_speed = (new_dt) ->
  dt = new_dt
window.play_pause = (status) ->
  pause = status
window.info_on = (status) ->
  for ball in balls
    ball.info = status
window.tail_on = (status) ->
  for ball in balls
    ball.tail = status and 200    
    ball.path = []  if not status
window.set_gravity = (new_gravity) ->
  gravity = new_gravity
window.reverse_time = (status) ->
  dt = -dt
  for ball of balls
    ball.bounce_coefficient = 1.0 / ball.bounce_coefficient
"""

OTHER_CODE_JS ="""
reset_balls = function() {
  balls = [];
  links = [];
  return timestep = 0;
};
set_speed = function(new_dt) {
  return dt = new_dt;
};
play_pause = function(status) {
  return pause = status;
};
info_on = function(status) {
  for (i in balls) balls[i].info = status;
};
tail_on = function(status) {
  for (i in balls) { balls[i].tail = status && 200; if(!status) balls[i].path = []; };
};
set_gravity = function(new_gravity) {
  return gravity = new_gravity;
};
reverse_time = function(status) {
  dt = -dt;
  for (i in balls) balls[i].bounce_coefficient = 1.0 / balls[i].bounce_coefficient;
};
"""
