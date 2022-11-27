

import pygame
import random

windowWidth = 700
windowHeight = 700

pygame.init()
window = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption("Collusion Simulation")
clock = pygame.time.Clock()

FPS = 60 # Hz
DELTA_T = 1 / FPS # s
SCALE = 0.01 # m/pixel


class Vector:
    def __init__(self, values):
        self.values = list(values)
        self.length = len(self.values)

    def __getitem__(self, index):
        return self.values[index]

    def __add__(self, other):
        result_values = [self.values[i]+other.values[i] for i in range(self.length)]
        return Vector(result_values)

    def __sub__(self, other):
        result_values = [self.values[i]-other.values[i] for i in range(self.length)]
        return Vector(result_values)

    def __mul__(self, other):
        # dot product
        if type(self) == Vector and type(other) == Vector:
            result = 0
            for i in range(self.length):
                result += self.values[i]*other.values[i]
            return result
        # scalar multiplication
        elif type(self) == Vector and type(other) == int or type(other) == float:
            result_values = [self.values[i]*other for i in range(self.length)]
            return Vector(result_values)

    def magnitude(self):
        total = 0
        for i in range(self.length):
            total += self.values[i]**2
        return total**0.5


class Box:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.thickness = 4

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x-self.thickness, self.y-self.thickness, self.width+2*self.thickness, self.height+2*self.thickness))
        pygame.draw.rect(window, (0, 0, 0), (self.x, self.y, self.width, self.height))


class Particle:
    def __init__(self, x, y, mass, x_velocity, y_velocity, color, radius):
        self.position = Vector([x,y]) # pixel, pixel
        self.mass = mass # kg
        self.velocity = Vector([x_velocity, y_velocity]) # m/s, m/s
        self.color = color # (R,G,B)
        self.radius = radius # pixel
        self.collided = False
        self.collusionCount = 5

    def move(self):
        self.position += self.velocity * (DELTA_T/SCALE)
        if self.collided:
            self.collusionCount -= 1
            if self.collusionCount == 0:
                self.collided = False
                self.collusionCount = 5
                

    def draw(self, window):
        position = (int(self.position[0]), int(self.position[1]))
        pygame.draw.circle(window, self.color, position, self.radius)

    def distance(self, other):
        vectoral_diff = self.position - other.position
        return vectoral_diff.magnitude()

    def handleBoxCollusion(self, box):
        # This function raises error !!!
        if self.collided:
            return
        
        # Continuous Collusion Detection
        if self.position[0] < box.x:
            self.position.values[0] = 2(box.x+self.radius) - self.position.values[0]
            self.velocity.values[0] = -self.velocity.values[0]
        elif self.position[0] > box.x+box.width:
            self.position.values[0] = 2(box.x+box.width-self.radius) - self.position.values[0]
            self.velocity.values[0] = -self.velocity.values[0]
        elif self.position[1] < box.y:
            self.position.values[1] = 2(box.y+self.radius) - self.position.values[1]
            self.velocity.values[1] = -self.velocity.values[1]
        elif self.position[1] > box.y+box.height:
            self.position.values[1] = 2(box.y+box.height-self.radius) - self.position.values[1]
            self.velocity.values[1] = -self.velocity.values[1]
        # Regular Collusion Detection
        else: 
            if self.position[0]-box.x <= self.radius or box.x+box.width-self.position[0] <= self.radius:
                self.velocity.values[0] = -self.velocity.values[0]
            if self.position[1]-box.y <= self.radius or box.y+box.height-self.position[1] <= self.radius:
                self.velocity.values[1] = -self.velocity.values[1]

    def handleParticleCollusion(self, other):
        normal_vector = Vector([self.position[0]-other.position[0],self.position[1]-other.position[1]])
        unit_normal = normal_vector * (1/normal_vector.magnitude())
        unit_tangent = Vector([-unit_normal[1], unit_normal[0]])
        self_normal_vel = unit_normal * self.velocity
        self_tangent_vel = unit_tangent * self.velocity
        other_normal_vel = unit_normal * other.velocity
        other_tangent_vel = unit_tangent * other.velocity
        new_self_normal_vel = (self_normal_vel*(self.mass-other.mass)+2*other.mass*other_normal_vel) / (self.mass+other.mass)
        new_other_normal_vel = (other_normal_vel*(other.mass-self.mass)+2*self.mass*self_normal_vel) / (self.mass+other.mass)
        self.velocity = unit_tangent*self_tangent_vel + unit_normal*new_self_normal_vel
        other.velocity = unit_tangent*other_tangent_vel + unit_normal*new_other_normal_vel
        

def check_particle_pairs(particles):
    for i in range(len(particles)):
        for j in range(i+1,len(particles)):
            if not particles[i].collided and not particles[j].collided and particles[i].distance(particles[j]) <= particles[i].radius+particles[j].radius:
                particles[i].handleParticleCollusion(particles[j])


def redraw_window(window, particles, box):
    window.fill((0, 0, 0))
    box.draw(window)
    for particle in particles:
        particle.draw(window)
    pygame.display.update()

box = Box(50, 50, 600, 600, (0, 0, 255))
particles = []
count = 20
while count != 0:
    radius = random.randint(8, 14)
    x = random.randint(55+radius, 595-radius)
    y = random.randint(55+radius, 595-radius)
    mass = random.randint(1, 10)
    x_velocity = random.randint(1, 2) * random.random()
    y_velocity = random.randint(1, 2) * random.random()
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    # dont initialize 2 or more particles at same position
    for i in range(len(particles)):
        if ((particles[i].position[0]-x)**2 + (particles[i].position[1]-y)**2)**0.5 <= particles[i].radius+radius+10:
            continue
    particles.append(Particle(x, y, mass, x_velocity, y_velocity, color, radius))
    count -= 1

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for particle in particles:
        particle.move()
        particle.handleBoxCollusion(box)

    check_particle_pairs(particles)
    redraw_window(window, particles, box)
    
pygame.quit()






















        
