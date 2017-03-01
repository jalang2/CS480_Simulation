from __future__ import division  # Simplify division
from turtle import Turtle, mainloop, setworldcoordinates    # Commands needed from Turtle
from random import expovariate as randexp, random           # Pseudo random number generation
import sys  # Use to write to out
import matplotlib.pyplot as plt
import numpy as np

def MovingAverage(x):

    return [np.mean(x[:k]) for k in range(1 , len(x) + 1)]

def PlotEverything(queueLengths, systemstates, timepoints):

    plt.figure(1)
    plt.subplot(221)
    plt.hist(queueLengths, normed=True, bins=min(20, max(queueLengths)))
    plt.title("Queue length")
    plt.subplot(222)
    plt.hist(systemstates, normed=True, bins=min(20, max(systemstates)))
    plt.title("System state")
    plt.subplot(223)
    plt.plot(timepoints, MovingAverage(queueLengths))
    plt.title("Average queue length")
    plt.subplot(224)
    plt.plot(timepoints, MovingAverage(systemstates))
    plt.title("Average system state")
    plt.show()


class Customer(Turtle):

    def __init__(self, arrivalRate, serviceRate, queue, server1, server2, speed):

        Turtle.__init__(self)  # Initialise all base Turtle attributes
        self.interarrivaltime = ( int(randexp(0.1))%10 + 1 )
        self.arrivalRate = arrivalRate
        self.serviceRate = serviceRate
        self.queue = queue
        self.served = False
        self.server1 = server1
        self.server2 = server2
        self.serviceTime = 0
        self.shape('circle')
        self.speed(speed)
        self.balked = False

    def move(self, x, y):
        self.setx(x)
        self.sety(y)


    def arrive(self, t):

        self.penup()
        self.arrivalTime = t
        #if len(self.queue) <= 13:
        self.move(self.queue.position[0] + 5, self.queue.position[1])
        self.color('blue')
        self.queue.join(self)
        #else:
        #  print "Line is to long!"

    def startService1(self, t):

        self.serviceTime = ( int(randexp(0.1))%10 + 2 )
        self.server1ServiceTime = self.serviceTime
        self.server2ServiceTime = 0
        if not self.served and not self.balked:
            self.move(self.server1.position[0], self.server1.position[1]-30)
            self.servicedate = t + self.serviceTime
            self.server1.start(self)
            self.color('red')
            self.endQueueDate = t

    def startService2(self, t):

        self.serviceTime = ( int(randexp(0.1))%10 + 5 )
        self.server2ServiceTime = self.serviceTime
        self.server1ServiceTime = 0
        if not self.served and not self.balked:
            self.move(self.server2.position[0], self.server2.position[1]+30)
            self.servicedate = t + self.serviceTime
            self.server2.start(self)
            self.color('red')
            self.endQueueDate = t

        
    def endService1(self):

        self.color('green')

        self.move(self.server1.position[0] + 50 + random(), self.server1.position[1] - 50 + random())
        self.server1.customers = self.server1.customers[1:]

        self.endServiceDate = self.endQueueDate + self.serviceTime
        self.waitingTime1 = self.endQueueDate - self.arrivalTime
        self.waitingTime2 = 0
        self.served = True

    def endService2(self):

        self.color('green')

        self.move(self.server2.position[0] + 50 + random(), self.server1.position[1] + 50 + random())
        self.server2.customers = self.server2.customers[1:]

        self.endServiceDate = self.endQueueDate + self.serviceTime
        self.waitingTime1 = 0
        self.waitingTime2 = self.endQueueDate - self.arrivalTime
        self.served = True

class Queue():

    def __init__(self, qposition):
        self.customers = []
        self.position = qposition
    def __iter__(self):
        return iter(self.customers)
    def __len__(self):
        return len(self.customers)
    def pop(self, index):

        for p in self.customers[:index] + self.customers[index + 1:]:  # Shift everyone up one queue spot
            x = p.position()[0]
            y = p.position()[1]
            p.move(x + 10, y)
        self.position[0] += 10  # Reset queue position for next arrivals
        return self.customers.pop(index)
    def join(self, customer):

        self.customers.append(customer)
        self.position[0] -= 10


class Server():

    def __init__(self, svrposition):
        self.customers = []
        self.position = svrposition

    def __iter__(self):
        return iter(self.customers)

    def __len__(self):
        return len(self.customers)

    def start(self,customer):

        self.customers.append(customer)
        self.customers = sorted(self.customers, key = lambda x : x.servicedate)
        self.nextServiceDate =  self.customers[0].servicedate

    def free(self):

        return len(self.customers) == 0


class Sim():

    def __init__(self, T, arrivalRate, serviceRate, speed=6 ):
        ##################
        bLx = -10 # This sets the size of the canvas (I think that messing with this could increase speed of turtles)
        bLy = -110
        tRx = 230
        tRy = 5
        setworldcoordinates(bLx,bLy,tRx,tRy)
        qposition = [(tRx+bLx)/2, (tRy+bLy)/2]  # The position of the queue
        ##################

        self.T = T
        self.completed = []
        self.balked = []
        self.arrivalRate = arrivalRate
        self.serviceRate = serviceRate
        self.customers = []
        self.queue = Queue(qposition)
        self.queueLengthDict = {}
        self.server1 = Server([qposition[0] + 50, qposition[1]])
        self.server2 = Server([qposition[0] + 50, qposition[1]])
        self.speed = max(0,min(10,speed))
        self.systemstatedict = {}

    def newCustomer(self):

      
        if len(self.customers) == 0:
           self.customers.append(Customer(self.arrivalRate, self.serviceRate, self.queue, self.server1, self.server2, self.speed))
           

    def printProgress(self, t, length):
        sys.stdout.write("\r%.2f%% of simulation completed (t=%s of %s)\t The length of the queue is: %d" % (100 * t/self.T, t, self.T, length))
        sys.stdout.flush()

    def run(self):

        t = 0
        self.newCustomer()                            # Create a new customer
        nextCustomer = self.customers.pop()           # Set this customer to be the next customer
        nextCustomer.arrive(t)                        # Make the next customer arrive for service (potentially at the queue)
        nextCustomer.startService1(t)                 # This customer starts service immediately
        #nextCustomer.startService2(t)                 # This customer starts service immediately
        self.newCustomer()                            

        while t < self.T:
            t += 1
            self.printProgress(t, len(self.queue) )                     # Output progress to screen

            # Check if service finishes
            if not self.server1.free() and t > ( self.server1.nextServiceDate): # or self.server2.nextServiceDate 
                self.completed.append(self.server1.customers[0])            # Add completed customer to completed list
                self.server1.customers[0].endService1()                      # End service of a customer in service
                if len(self.queue)>0:                                      # Check if there is a queue
                    nextService = self.queue.pop(0)                        # This returns customer to go to service and updates queue.
                    nextService.startService1(t)
                    self.newCustomer()                                     # Create a new customer that is now waiting to arrive

            if not self.server2.free() and t > ( self.server2.nextServiceDate ):
                self.completed.append(self.server2.customers[0])           # Add completed customer to completed list
                self.server2.customers[0].endService2()                    # End service of a customer in service
                if len(self.queue)>0:                                      # Check if there is a queue
                    nextService = self.queue.pop(0)                        # This returns customer to go to service and updates queue.
                    nextService.startService2(t)
                    self.newCustomer()                                     # Create a new customer that is now waiting to arrive


            # Check if customer that is waiting arrives
            if t > self.customers[-1].interarrivaltime + nextCustomer.arrivalTime:
                nextCustomer = self.customers.pop()
                nextCustomer.arrive(t)                           # Make the next customer arrive for service (potentially at the queue)

                if nextCustomer.balked and len(self.queue) < 10:
                    self.balked.append(nextCustomer)

                if self.server1.free():
                    if len(self.queue) == 0:                               # Check if there is elements in the queue      
                        nextCustomer.startService1(t)
                    else: 
                        nextService = self.queue.pop(0)                    # This returns customer to go to service and updates queue.
                        nextService.startService1(t)

                elif self.server2.free():
                    if len(self.queue) == 0:                               # Check if there is elements in the queue  
                        nextCustomer.startService2(t)
                    else:  
                        nextService = self.queue.pop(0)                    # This returns customer to go to service and updates queue.
                        nextService.startService2(t)
            
            self.newCustomer()
            self.collectData(t)

    def collectData(self,t):

        self.queueLengthDict[t] = len(self.queue)

        if self.server1.free() or self.server2.free():
           self.systemstatedict[t] = 0

        else:
           self.systemstatedict[t] = self.queueLengthDict[t] + 1

    def plot(self, savefig, warmup=0):
        #string = "arrivalRate=%s-serviceRate=%s-T=%s.pdf" % (self.arrivalRate, self.serviceRate, self.T ) # An identifier
       
        queueLengths = []
        systemstates = []
        timepoints = []
        for t in self.queueLengthDict:
           if t >= warmup:
              queueLengths.append(self.queueLengthDict[t])
              systemstates.append(self.systemstatedict[t])
              timepoints.append(t)
        PlotEverything(queueLengths, systemstates, timepoints)

    def printsummary(self, warmup=0):

        totaltime = 0

        self.queueLengths = []
        self.systemstates = []

        for t in self.queueLengthDict:
            if t >= warmup:
               self.queueLengths.append(self.queueLengthDict[t])
               self.systemstates.append(self.systemstatedict[t])

        self.meanqueuelength = np.mean(self.queueLengths)
        self.meansystemstate = np.mean(self.systemstates)

        self.totalserver1servicetime = []
        self.totalserver2servicetime = []

        self.waitingTimeServer1 = []
        self.waitingTimeServer2 = []
        self.servicetimes = []

        for p in self.completed:
            if p.arrivalTime >= warmup:
               if p.waitingTime1 != 0:
                  self.waitingTimeServer1.append(p.waitingTime1)
               if p.waitingTime2 != 0:
                  self.waitingTimeServer2.append(p.waitingTime2)
               self.servicetimes.append(p.serviceTime)
               if p.server1ServiceTime != 0:
                  self.totalserver1servicetime.append(p.server1ServiceTime)
               if p.server2ServiceTime != 0:
                  self.totalserver2servicetime.append(p.server2ServiceTime)

        totaltime = len(self.queueLengthDict)
        self.totalserver1busytime = sum(self.totalserver1servicetime)
        self.totalserver2busytime = sum(self.totalserver2servicetime)

        self.meanserver1servicetime = np.mean(self.totalserver1servicetime)
        self.meanserver2servicetime = np.mean(self.totalserver2servicetime)

        self.totalwaitingtimesserver1 = totaltime - self.totalserver1busytime
        self.totalwaitingtimesserver2 = totaltime - self.totalserver2busytime

        self.meanwaitingtimesserver1 = self.totalwaitingtimesserver1 / len(self.waitingTimeServer1)
        self.meanwaitingtimesserver2 = self.totalwaitingtimesserver2 / len(self.waitingTimeServer2)

        self.percentbusyserver1 = self.totalserver1busytime/totaltime
        self.percentbusyserver2 = self.totalserver2busytime/totaltime

        self.totalservicetimes = sum(self.totalserver1servicetime + self.totalserver2servicetime)

        self.totalwaitingtime = sum(self.waitingTimeServer2) + sum(self.waitingTimeServer1)
        self.meanwaitingtime = ( np.mean(self.waitingTimeServer2) + np.mean(self.waitingTimeServer1) ) / 2
        self.meanservertime =  np.mean(self.totalwaitingtime) #+ self.meanwaitingtime ) / 2


        print ("\n%sSummary statistics%s" % (10*"-",10*"-"))

        print ("\n=========================---System Info---==============================")
        print ("Average customer wait time: %.03f" % self.meanwaitingtime)
        print ("Total customer wait time: %.03f" % self.totalwaitingtime)
        print ("Total busy time: %.03f" % self.totalservicetimes )
        print ("Average busy time: %.03f" % self.meanservertime)
        print ("Average queue length: %.03f" % self.meanqueuelength)

        print ("\n=========================---Server 1 Info---==============================")
        print ("Average server 1 busy time: %.03f" % self.meanserver1servicetime)
        print ("Total server 1 busy time: %.03f" % self.totalserver1busytime)
        print ("Server 1 was busy %.1f of the time" % (100*self.percentbusyserver1))
        print ("Average server 1 waiting time: %.03f" % self.meanwaitingtimesserver1)
        print ("Total server 1 waiting time: %.03f" % self.totalwaitingtimesserver1 )
        print ("Number of customers server 1 served : %d" % len(self.totalserver1servicetime) )

        print ("\n=========================---Server 2 Info---==============================")
        print ("Average server2 busy time: %.03f" % self.meanserver2servicetime)
        print ("Total server2 busy time: %.03f" % self.totalserver2busytime)
        print ("Server 2 was busy %.1f%% of the time" % (100*self.percentbusyserver2) )
        print ("Average server2 wait time: %.03f" % self.meanwaitingtimesserver2)
        print ("Total server2 wait time: %.03f" % self.totalwaitingtimesserver2 )
        print ("Number of customers sever 2 served : %d" % len(self.totalserver2servicetime) )

        print ("\n=========================---System---==============================")
        print ("Total system time: %.03f" % totaltime)
        print ("Average system state: %.03f" % self.meansystemstate)
        print (39 * "==" + "\n")
        


if __name__ == '__main__':

    arrivalRate = 2.4
    serviceRate = 1.2
    T = 600
    warmup = 2
    savefig = False
    sim = Sim(T, arrivalRate, serviceRate, speed=10 )
    sim.run()
    sim.printsummary(warmup=warmup)
    sim.plot(savefig)
