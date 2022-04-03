"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process, Manager
from multiprocessing import Value
from ctypes import c_char_p

SOUTH = "sur"
NORTH = "norte"
NCARS = 50



class Monitor():
    def __init__(self , manager, manager1, manager2, direccion, NCARS):
        self.mutex = Lock()
        self.cochesnorte = manager
        self.cochessur = manager1
        self.tunel = manager2
        self.direction = direccion
        self.numero = Value('i', 0)
        self.polician = Condition(self.mutex)
        self.policias = Condition(self.mutex)



    
    def wants_enter(self, cid, direction):
        self.mutex.acquire()
        print(f"El coche {cid} que va en direccion {direction} quiere entrar al tunel")
        if (len(self.cochesnorte) >= 4 or len(self.cochessur) >=4):     #Si hay mas de cuatro coches esperando en cualquier direccion, cambia el sentido de la marcha para    
                print(f'El coche {cid} espera porque ya hay muchos coches esperando')
                if direction == NORTH:                                  #que no haya una espera infinita por parte de los coches de una de las direcciones
                    self.cochesnorte.append(f'Coche {cid}')
                    self.polician.wait() 
                    self.cochesnorte.pop()
                    direction == self.direction.value
                else:
                    self.cochessur.append(f'Coche {cid}')
                    self.policias.wait()
                    self.cochessur.pop()
                    direction = self.direction.value
                    
        if self.numero.value == 0:    #Si no hay coches en el tunel, entra el siguiente coches independientemente de la direccion
            self.direction.value = direction
        

        if (self.direction.value != direction):
            print(f'El coche {cid} espera')
            if direction == NORTH:
                self.cochesnorte.append(f'Coche {cid}')
                self.polician.wait() 
                self.cochesnorte.pop()
            else:
                self.cochessur.append(f'Coche {cid}')
                self.policias.wait()
                self.cochessur.pop()
        print(f'El coche {cid} que va en direccion {direction} entra en el tunel')
        self.tunel.append(f'Coche {cid}')
        print("Tunel = ", self.tunel)
        self.numero.value += 1
        print("El numero de coches que hay dentro del tunel es", self.numero.value)
        self.mutex.release()

    def leaves_tunnel(self, cid, direction):
        self.mutex.acquire()
        print(f'El coche {cid} que va en direccion {direction} sale del tunel')
        self.tunel.remove(f'Coche {cid}')
        print("Tunel = ", self.tunel)
        self.numero.value -= 1
        print("El numero de coches que hay dentro del tunel es", self.numero.value)
        print("Lista de coches esperando hacia el norte: ", self.cochesnorte)
        print("Lista de coches esperando hacia el sur: ", self.cochessur)
        if self.numero.value == 0:
            if self.direction.value == NORTH:
                if len(self.cochessur) != 0:
                    self.direction.value = SOUTH
                    self.policias.notify_all()
                else:
                    self.polician.notify_all()
            else:
                if len(self.cochesnorte) != 0:
                    self.direction.value = NORTH
                    self.polician.notify_all()
                else:
                    self.policias.notify()
        self.mutex.release()






def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    
    delay(6)
    monitor.wants_enter(cid,direction)
    delay(3)
    monitor.leaves_tunnel(cid, direction)
   
   

def main():

    manager = Manager()
    cochesnorte = manager.list()
    manager1 = Manager()
    cochessur = manager1.list()
    manager2 = Manager()
    tunel = manager2.list()
    
    
    cid = Value('i', 0)
    
    cochess = []
    for i in range(NCARS):
        if random.randint(0,1)==1:
            direction = NORTH
        else:
            direction = SOUTH
        if i == 0:
            direccion = manager.Value(c_char_p, direction)
            monitor = Monitor(cochesnorte, cochessur, tunel, direccion, NCARS)
        cochess.append(Process(target=car, args=(i, direction, monitor)))
    
    for i in range(NCARS):
        cochess[i].start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s
        
    for i in range(NCARS):
        cochess[i].join()
   



if __name__ == "__main__":
    main()
