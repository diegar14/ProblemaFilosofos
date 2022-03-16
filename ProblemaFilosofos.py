from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Array, Manager

import time
import random

NPHIL = 5

K = 100

class Table:
    def __init__(self, manager):
        self.size = NPHIL
        self.chopsticks = manager.list([True]*NPHIL)
        self.mutex = Lock()
        self.cond = Condition(self.mutex)
        
    def wants_eat(self,num):
        self.mutex.acquire()
        self.cond.wait_for(lambda: self.chopsticks[num] and self.chopsticks[(num+1)%NPHIL])
        print (f"Philosopher {num} eating")
        self.chopsticks[num] = False
        self.chopsticks[(num+1)%NPHIL] = False
        self.mutex.release()
    
    def wants_think(self,num):
        self.chopsticks[num] = True
        self.chopsticks[(num+1)%NPHIL] = True

    
class AnticheatTable:
    def __init__(self, manager):
        self.size = NPHIL
        self.chopsticks = manager.list([True]*NPHIL)
        self.anticheat = manager.list([])
        self.mutex = Lock()
        self.cond = Condition(self.mutex)
        self.cond2 = Condition(self.mutex)
        
    def wants_eat(self,num):
        if num not in self.anticheat:
            self.anticheat.append(num)
        
        self.mutex.acquire()
        self.cond.wait_for(lambda: self.anticheat[0] == num)
        self.cond2.wait_for(lambda: self.chopsticks[num] and self.chopsticks[(num+1)%NPHIL])
        print (f"Philosopher {num} eating")
        print(self.anticheat)
        self.chopsticks[num] = False
        self.chopsticks[(num+1) % NPHIL] = False
        self.anticheat.pop(0)
        print(self.anticheat)        
        self.mutex.release()
    
    def wants_think(self,num):
        self.chopsticks[num] = True
        self.chopsticks[(num+1)%NPHIL] = True
            

def delay(n=5):
    time.sleep(random.random()/n)

def philosopher_task(num:int, table: AnticheatTable):
    cnt = 0
    while cnt < K:
        print (f"Philosopher {num} thinking")
        table.wants_eat(num)
        print (f"Philosopher {num} wants to eat")
        delay()
        
        table.wants_think(num)
        delay()
        print (f"Philosopher {num} stops eating")
        cnt += 1

def main():
    manager = Manager()
    table = AnticheatTable(manager)
    philosophers = [Process(target=philosopher_task, args=(i,table)) for i in range(NPHIL)]
    for i in philosophers:
        i.start()
    for i in philosophers:
        i.join()

if __name__ == '__main__':
    main()