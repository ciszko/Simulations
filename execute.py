from operator import attrgetter
import pandas as pd
import numpy as np
import pygame as pg
import sys


class Simulation(object):

    def __init__(self):
        # Config
        self.tps = 100.0

        # Initialization
        pg.init()
        self.screen = pg.display.set_mode((1280, 720))
        self.tps_clock = pg.time.Clock()
        self.tps_delta = 0.0
        self.p1 = ProcessBlock()

        while True:
            # Handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit(0)
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    sys.exit(0)

            # Ticking
            self.tps_delta += self.tps_clock.tick() / 1000
            while self.tps_delta > 1 / self.tps:
                self.tick()
                self.tps_delta -= 1 / self.tps

            # Drawing
            self.screen.fill((0, 0, 0))
            self.draw()
            pg.display.flip()

    def tick(self):
        # Check input
        keys = pg.key.get_pressed()

    def draw(self):
        self.p1.draw(self.screen)


class ProcessBlock(pg.sprite.Sprite):

    def __init__(self):
        self.surface = pg.Surface((50, 50), pg.SRCALPHA, 32)




class Process:

    def __init__(self, id, a_time, p_time):
        self.id = id
        self.a_time = a_time
        self.p_time = p_time
        self.l_time = p_time
        self.w_time = 0
        self.ta_time = 0
        self.is_available = False

    def __repr__(self):
        return repr((int(self.id),int(self.p_time),int(self.a_time),int(self.l_time)))


# Read data from an input file
def read_data(input_file):
    try:
        input_file = open(input_file, "r")
        input_file.seek(0)
        global total_p_time
        global process_q
        global input_list
        for line in input_file.readlines()[2:]:
            current_line = line.split(",")
            total_p_time += int(current_line[2])
            process_q += 1
            input_list.append(Process(int(current_line[0]), int(current_line[1]), int(current_line[2])))
        input_file.close()
    except FileNotFoundError:
        print("Nie znaleziono pliku: " + input_file)
        exit(1)
    except Exception as e:
        print(e)


# Save data to output file
def save_data(output_file, mode, algorithm):
    global total_p_time
    global processed_string
    global processed_order
    global process_list
    global process_list_int
    headers = ['PID', 'Czas wykonywania', 'Czas czekania', 'Czas przetwarzania']
    output_file = open(output_file, mode)
    if algorithm == 'fifo':
        output_file.write('################# FIFO #################')
    if algorithm == 'sjf':
        output_file.write('################# SJF #################')
    output_file.write("\nKolejność w jakiej wykonają się procesy:\n")
    output_file.write(processed_order + '\n')
    output_file.write(processed_string + '\n')
    process_list.sort(key=attrgetter('id'))
    df = pd.DataFrame(process_list_int, index=None)
    df.columns = headers
    output_file.write(df.__repr__())
    output_file.write('\n' + "Średni czas oczekiwania = " + str(process_list_int[:, 2].mean()))
    output_file.write('\n' + "Średni czas przetwarzania = " + str(np.around(process_list_int[:, 3].mean(), decimals=2)))
    output_file.write('\n')
    output_file.close()
    processed_string = ''
    processed_order = ''
    process_list_int = []


def process_data_fifo():
    global processed_string
    global processed_order
    global process_list
    global process_order_fifo
    process_list = input_list
    time = 0
    j = 0
    process_list.sort(key=attrgetter('a_time', 'id'))
    for i in range(process_q):
        processed_order += "[" + str(input_list[i].id) + "]"
    current_process = min(process_list, key=attrgetter('a_time', 'id'))
    current_process.w_time = 0
    current_process.ta_time = current_process.p_time
    processed_string += "[" + str(current_process.id) + "]"
    process_order_fifo.append(int(current_process.id))
    current_process.l_time -= 1
    for i in range(total_p_time-1):
        time += 1
        if current_process.l_time == 0:
            j += 1
            current_process = process_list[j]
            current_process.w_time = time - current_process.a_time
        processed_string += "[" + str(current_process.id) + "]"
        process_order_fifo.append(int(current_process.id))
        current_process.l_time -= 1
    for i in range(1, process_q):
        process_list[i].ta_time = process_list[i].w_time + process_list[i].p_time
    process_list_to_int()


# Makes process_list easier to manipulate with numpy and pandas
def process_list_to_int():
    global process_list_int
    global process_list
    process_list.sort(key=attrgetter('id'))
    for p in process_list:
        process_list_int.append([int(p.id), int(p.p_time), int(p.w_time), int(p.ta_time)])
    process_list_int = np.array(process_list_int)


def process_data_sjf():
    global processed_string
    global processed_order
    global process_list
    global process_list_int
    global process_order_sjf
    process_list = input_list
    for p in process_list:
        p.l_time = p.p_time
        p.w_time = 0
        p.ta_time = 0
    current_process = min(process_list, key=attrgetter('a_time', 'id'))
    current_process.is_available = True
    process_list.sort(key=attrgetter('a_time', 'id'))
    for time in range(total_p_time):
        if current_process.l_time == 0:  # If left time is 0, then process is not available
            processed_order += '[' + str(current_process.id) + ']'
            current_process.is_available = False
            current_process = min((p for p in process_list if p.l_time > 0), key=lambda x: x.l_time)
        if time == total_p_time-1:        # last loop
            processed_order += '[' + str(current_process.id) + ']'
        for p in process_list:
            if time >= p.a_time:          # If arrive time is equal to time, process is available
                p.is_available = True
            if p.l_time == 0:             # Make sure that process is not available
                p.is_available = False    # vvv If any process has left time less than current
            if p.is_available is True and p.l_time < current_process.l_time:
                current_process = p
            if p is not current_process and p.l_time > 0 and p.a_time <= time:
                p.w_time += 1
        current_process.l_time -= 1
        processed_string += '[' + str(current_process.id) + ']'
        process_order_sjf.append(int(current_process.id))
    for i in range(process_q):
        process_list[i].ta_time = process_list[i].w_time + process_list[i].p_time
    process_list_to_int()

    
    def process_data_sjf2():
    global processed_string
    global processed_order
    global process_list
    global process_list_int
    global process_order_sjf
    process_list = input_list
    for p in process_list:
        p.l_time = p.p_time
        p.w_time = 0
        p.ta_time = 0
    current_process = min(process_list, key=attrgetter('a_time', 'l_time'))
    current_process.is_available = True
    # process_list.sort(key=attrgetter('a_time', 'id'))
    for time in range(total_p_time):
        if current_process.l_time == 0:
            current_process.is_available = False
            current_process = min((i for i in process_list if i.l_time > 0), key=lambda x: x.l_time)
        for p in process_list:
            if p is not current_process and p.a_time >= time:
                p.is_available = True
        for p in process_list:
            if p is not current_process and p.l_time > 0 and p.a_time <= time:
                p.w_time += 1
        current_process.l_time -= 1
            #print(' ' + str(current_process.priority) + ' ', end='')
        processed_string += '[' + str(current_process.id) + ']'
        process_order_sjf.append(int(current_process.id))
    for i in range(process_q):
        process_list[i].ta_time = process_list[i].w_time + process_list[i].p_time
    process_list_to_int()

if __name__ == "__main__":
    process_q = 0
    total_p_time = 0
    input_list = []
    process_list = []
    process_list_int = []
    process_order_fifo = []
    process_order_sjf = []
    processed_string = ""
    processed_order = ""
    read_data('input.txt')
    process_data_fifo()
    save_data('output.txt', "w", 'fifo')
    process_data_sjf()
    save_data('output.txt', 'a', 'sjf')
    print(process_order_fifo)
    print(process_order_sjf)
    Simulation()









