"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"

NCARS = 10

class Monitor():
    def __init__(self):
        self.number_north = Value('i', 0)
        self.number_south = Value('i', 0)
        self.number_north_waiting = Value('i',0)
        self.number_south_waiting = Value('i', 0)
        self.turn = Value('i',0)
        #turn 0 for NORTH
        #turn 1 for SOUTH
        self.mutex = Lock()
        self.no_north = Condition(self.mutex)
        self.no_south = Condition(self.mutex)
        self.nobody = Condition(self.mutex)

    def are_no_north(self):
        return self.number_north.value == 0 and (self.turn.value == 0 or self.number_north_waiting.value == 0)

    def are_no_south(self):
        return self.number_south.value == 0 and (self.turn.value == 1 or self.number_south_waiting.value == 0)

    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == SOUTH:
            self.number_north_waiting.value += 1
            self.no_south.wait_for(self.are_no_south)
            self.number_north_waiting.value -= 1
            self.number_north.value += 1
        else:
            self.number_south_waiting.value += 1
            self.no_north.wait_for(self.are_no_north)
            self.number_south_waiting.value -= 1
            self.number_south.value += 1
        self.mutex.release()

    def stop_north(self):
        self.mutex.acquire()
        self.number_north.value -= 1
        self.turn.value = 1
        if self.number_north.value == 0:
            self.nobody.notify()
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        if direction == SOUTH:
                    self.number_north.value -= 1
                    self.turn.value = 1
                    if self.number_north.value == 0:
                        self.nobody.notify()
        else:
                    self.number_south.value -= 1
                    self.turn.value = 0
                    if self.number_south.value == 0:
                        self.nobody.notify()
        self.mutex.release()

def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")



def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':
    main()
