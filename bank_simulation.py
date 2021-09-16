from random import *
import numpy
import math

plan = 3
error = False


class BankEmployee:  # class for employees
    def __init__(self, possible_list):
        self.is_busy = False
        self.possible_times = possible_list
        self.free_time = 0
        self.last = 0
        self.to_finish = None

    def important(self, plan_number, work):  # return the important attribute for any strategy
        if plan_number == 1:
            return self.last
        if plan_number == 2:
            average = 0
            for i in self.possible_times[work].keys():
                average += i * self.possible_times[work][i]
            return average
        if plan_number == 3:
            return min(self.possible_times[work].keys())

    def asset(self, time):  # calls when an employee starts to work
        self.is_busy = True
        self.to_finish = time

    def finish(self, time):  # calls when an employee finishes work
        self.is_busy = False
        self.last = time

    def free(self):
        return not self.is_busy


class Client:  # class for clients
    def __init__(self, work, primary_key):
        self.money = 500
        self.wait_time = 0
        self.exit_time = None
        self.is_waiting = True
        self.work = work
        self.to_finish = None
        self.pk = primary_key
        self.finished = False
        self.gave_money = 0

    def asset(self, time):  # calls when a client starts the work
        self.is_waiting = False
        self.to_finish = time

    def finish(self):  # calls when a client finishes the work
        self.finished = True


class AssetSystem:  # system that allocates employees to clients
    def asset(self, bank_employee, client_pk):  # allocates an employee to a client
        time = randomGenerator.work_time(bank_employee, clients[client_pk].work)
        clients[client_pk].asset(time)
        bank_employees[bank_employee].asset(time)
        money = 1000
        while money > 500:
            money = randomGenerator.normal()
        clients[client_pk].money -= money
        clients[client_pk].gave_money = money

    def choose_employee(self, free_bank_employees, client_pk):  # chooses an employee for client
        if len(free_bank_employees) == 1:
            self.asset(free_bank_employees[0], client_pk)
        else:
            work = clients[client_pk].work
            minimum = min(bank_employees[i].important(plan, work) for i in free_bank_employees)
            choosen_employees = []
            for i in free_bank_employees:
                if bank_employees[i].important(plan, work) == minimum:
                    choosen_employees.append(i)
            if len(choosen_employees) != 1:
                shuffle(choosen_employees)
            self.asset(choosen_employees[0], client_pk)


class ParameterLoader:  # class that reads input files
    def worker(self):  # reads works possibility time list for each work
        global error
        try:
            with open("bank_employee.txt", 'r') as f:
                file = f.read()
                a = file.split('\n')
                for i in range(len(a)):
                    b = a[i].split('  ')
                    list = []
                    for j in range(len(b)):
                        c = b[j].split(',')
                        dictionary = {}
                        for k in range(len(c)):
                            d = c[k].split(':')
                            dictionary[float(d[0])] = float(d[1])
                        list.append(dictionary)
                    bank_employees.append(BankEmployee(list))
            f.close()
        except:
            print("Input Error")
            error = True

    def client_time(self):  # reads possibility of the time clients come after each other
        global error
        try:
            with open("comming_time.txt", 'r') as f:
                file = f.read()
                a = file.split('\n')
                dictionary = {}
                for i in range(len(a)):
                    b = a[i].split(':')
                    dictionary[float(b[0])] = float(b[1])
            f.close()
            return dictionary
        except:
            print("Input Error")
            error = True

    def client_work(self):  # reads the clients possibility for each work
        global error
        try:
            with open("possible_work.txt", 'r') as f:
                file = f.read()
                a = file.split(',')
                list = []
                for i in a:
                    list.append(float(i))
            f.close()
            return list
        except:
            print("Input Error")
            error = True

    def normal(self):  # reads average and deviation of normal distribution
        global error
        try:
            with open("normal.txt", 'r') as f:
                file = f.read()
                splited = file.split('\n')
            f.close()
            return [float(splited[0]), float(splited[1])]
        except:
            print("Input Error")
            error = True


class RandomGenerator:  # class for generating random
    def work_time(self, bank_employee, work):  # generates random work time for each work and employee
        random_number = random()
        for i in bank_employees[bank_employee].possible_times[work].keys():
            if random_number < bank_employees[bank_employee].possible_times[work][i]:
                return i
            random_number -= bank_employees[bank_employee].possible_times[work][i]

    def next_customer(self):  # generate time for arriving next client
        dictionary = parameterLoader.client_time()
        random_number = random()
        for i in dictionary.keys():
            if random_number < dictionary[i]:
                return i
            random_number -= dictionary[i]

    def client_work(self):  # generates client work
        list = parameterLoader.client_work()
        random_number = random()
        for i in range(len(list)):
            if random_number < list[i]:
                return i
            random_number -= list[i]

    def normal(self):  # generates random number in normal distribution by python built-in method
        list = parameterLoader.normal()
        random_list = numpy.random.normal(list[0], list[1], 1)
        return random_list[0]

    def old_normal(self): # generates random number in normal distribution by taking integrate
        list = parameterLoader.normal()
        random_number = random()
        a = abs(random_number - 0.5)
        number = 100
        last_number = 200
        while abs(self.antegral(number) - a) > 0.0001:
            if self.antegral(number) > a:
                last_number = number
                number /= 2
            else:
                new_number = (number + last_number) / 2
                last_number = number
                number = new_number
        if random_number < 0.5:
            number = -number
        return number * list[1] + list[0]

    def f(self, number):  # returns value of standard normal distribution function
        return 1 / (math.sqrt(2 * math.pi)) * math.e ** (-(number ** 2) / 2)

    def antegral(self, number):  # takes integrate
        count = 0
        height = self.f(0)
        for i in range(100000000):
            x = uniform(0, number)
            y = uniform(0, height)
            if y < self.f(x):
                count += 1
        return (count / 100000000) * number * height


class Queue:  # class for queue
    def __init__(self):
        self.list = []

    def enqueue(self, obj):  # queues a client
        self.list.append(obj)

    def dequeue(self):  # takes a client out of queue
        client = self.list[0]
        del self.list[:1]
        return client


def free_employees():  # returns free employees
    free_bank_employees = []
    for i in range(len(bank_employees)):
        if not bank_employees[i].is_busy:
            free_bank_employees.append(i)
    return free_bank_employees


def client_coming():  # calls when there is time for arriving a client
    work = randomGenerator.client_work()
    client = Client(work, len(clients))
    clients.append(client)
    free_bank_employees = free_employees()
    if len(free_bank_employees) == 0:
        q.enqueue(client)
    else:
        asset.choose_employee(free_bank_employees, client.pk)


def check_free():  # checks if there is a free employee and a waiting client at a time
    for bank_employee in bank_employees:
        if bank_employee.free() and len(q.list) > 0:
            return True
    return False


def ready():  # takes client out of queue and allocates it to an employee
    client = q.dequeue()
    asset.choose_employee(free_employees(), client.pk)


def go(total_time, delta_time):  # time goes on ...
    now = 0
    next = 0
    while now <= total_time:
        if abs(now - next) < 0.000001:
            client_coming()
            next = now + randomGenerator.next_customer()
        while check_free():
            ready()
        for bank_employee in bank_employees:
            if bank_employee.is_busy:
                bank_employee.to_finish -= delta_time
                if bank_employee.to_finish <= 0:
                    bank_employee.finish(now)
            else:
                bank_employee.free_time += delta_time
        for client in clients:
            if not client.finished:
                if client.is_waiting:
                    client.wait_time += delta_time
                else:
                    client.to_finish -= delta_time
                    if client.to_finish <= 0:
                        client.finish()
        now += delta_time


clients = []
bank_employees = []
parameterLoader = ParameterLoader()
parameterLoader.worker()
randomGenerator = RandomGenerator()
q = Queue()
asset = AssetSystem()
if not error:
    total_time = input("time: ")
    go(int(total_time), 0.1)
    waited = 0
    money_giving = 0
    for client in clients:
        if client.wait_time > 0:
            waited += 1
        if client.gave_money > 0:
            money_giving += 1

    print("average employee free time:", sum(bank_employee.free_time for bank_employee in bank_employees) / len(bank_employees))
    print("average customer waiting time:", sum(customer.wait_time for customer in clients) / len(clients))
    print("possibility of a customer being queued:", waited / len(clients))
    print("possibility of a customer give money to bank:", money_giving / len(clients))
