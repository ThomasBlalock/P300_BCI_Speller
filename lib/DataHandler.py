import pygame
import time
from brainflow.board_shim import BoardShim, BoardIds
from brainflow.board_shim import BrainFlowInputParams
import random
import pyautogui
import pickle
import torch
import numpy as np # impedence code vvv
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import butter, lfilter
from scipy.fft import fft, fftfreq

"""
Cyton Board Data Description:
   accel_channels : [9, 10, 11]
   analog_channels : [19, 20, 21]
   ecg_channels : [1, 2, 3, 4, 5, 6, 7, 8]
   eeg_channels : [1, 2, 3, 4, 5, 6, 7, 8]
   eeg_names : Fp1,Fp2,C3,C4,P7,P8,O1,O2
   emg_channels : [1, 2, 3, 4, 5, 6, 7, 8]
   eog_channels : [1, 2, 3, 4, 5, 6, 7, 8]
   marker_channel : 23
   name : Cyton
   num_rows : 24
   other_channels : [12, 13, 14, 15, 16, 17, 18]
   package_num_channel : 0
   sampling_rate : 250
   timestamp_channel : 22
"""

def bandstop_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.lfilter(b, a, data)
    return y

def calculate_impedance(eeg_data):
    # Apply a bandstop filter around 50Hz
    eeg_filtered = bandstop_filter(eeg_data, 49, 51, 250, order=3)

    N = 500
    T = 1.0 / 1000.0
    x = np.linspace(0.0, N*T, N, endpoint=False)
    yf = fft(eeg_filtered)
    xf = fftfreq(N, T)[:N//2]
    
    # This is an experimental method not a direct method to measure impedance
    # Here we assume that the maximum frequency component corresponds to the impedance
    peak_frequency = xf[np.argmax(np.abs(yf[0:N//2]))]

    # calculate impedance
    impedance = 1.0/peak_frequency
    
    return impedance

# impedence code ^^^

class Board:
    def __init__(self, port = 'COM4'):
        self.port = port
        # Prep board / data stream
        BoardShim.enable_dev_board_logger()
        params = BrainFlowInputParams()
        params.serial_port = self.port
        self.board = BoardShim(BoardIds.CYTON_BOARD, params)
        self.board.prepare_session()
        

    def __del__(self):
        self.board.release_session()    
        time.sleep(1.5) # It crashes if you  restart the board too quickly

    def start_stream(self):
        self.board.start_stream()

    def stop_stream(self):
        self.board.stop_stream()

    def get_data(self):
        return self.board.get_board_data()
    
    def get_impedance(self): # impedence code vvv
        # we start the stream
        self.start_stream()
        
        # get a chunk of data
        data = self.get_data()

        # we stop the stream
        self.stop_stream()

        # we get the eeg data
        eeg_data = data[0]  # assuming the eeg data is the first element in data
        # calculate the impedance and return it
        return calculate_impedance(eeg_data)
    


class Box_GUI:

    # Constants
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0 , 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)
    BLUE = (0, 0, 255)
    ORANGE = (255, 165, 0)
    PINK = (255, 192, 203)
    COLOR_LIST = [RED, GREEN, YELLOW, PURPLE, BLUE, ORANGE, PINK]

    def __init__(self, window_size = None):
        if window_size == None:
            width, height = pyautogui.size()
        else:
            width, height = window_size
        self.window_size = (width, height-(height/20))

        # Prep pygame window
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
        self.screen.fill(self.BLACK)

    def __del__(self):
        pygame.quit()
    
    def reset_screen(self, box_size):
        box_size = self.box_size_parser(box_size)
        center = ((self.window_size[0] - box_size[0])/2, (self.window_size[1] - box_size[1])/2)
        pygame.draw.rect(self.screen, self.GREEN, (center[0], center[1], box_size[0], box_size[1]), 0)
        pygame.display.update()
        pygame.display.flip()

    def flash_box(self, box_size, color='random'):
        if color == 'random':
            color = random.choice(self.COLOR_LIST)
        box_size = self.box_size_parser(box_size)
        center = ((self.window_size[0] - box_size[0])/2, (self.window_size[1] - box_size[1])/2)
        pygame.draw.rect(self.screen, color, (center[0], center[1], box_size[0], box_size[1]), 0)
        pygame.display.update()
        pygame.display.flip()

    def button_press(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return True
        return False
    
    def box_size_parser(self, box_size):
        if  type(box_size) == str:
            if box_size == 'screen' or box_size == 'full':
                return self.window_size
        elif type(box_size) == int:
            return (box_size, box_size)
        elif type(box_size) == tuple and len(box_size) == 2:
            return box_size
        else:
            raise ValueError('Invalid box size input: ' + type(box_size) + '. Must be string, int, or 2-valued tuple.')
        


class Keyboard_GUI:

    # Constants
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0 , 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)
    BLUE = (0, 0, 255)
    ORANGE = (255, 165, 0)
    PINK = (255, 192, 203)
    COLOR_LIST = [RED, YELLOW, PURPLE, BLUE, ORANGE, PINK]
    KEY_COLOR_LIST = [GREEN, YELLOW, PINK, WHITE]

    def __init__(self, window_size=None):
        if window_size == None:
            width, height = pyautogui.size()
        else:
            width, height = window_size
        self.window_size = (width, height-(height/20))
        self.window_size = (width, height-(height/20))
        self.keyboard = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace", "End"],
                    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P","(", ")"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"], 
                    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Enter"],
                    ["       "]]

        # Prep pygame window
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
        self.screen.fill(self.BLACK)
        self.font = pygame.font.SysFont("Arial", 20)

    def __del__(self):
        pygame.quit()
    
    def reset_screen(self, button_size = None, flash_keys = [], color='random', target_letter=None):
        if color == 'random':
            flash_color = random.choice(self.COLOR_LIST)
            flash_color_key = random.choice(self.KEY_COLOR_LIST)
        else:
            flash_color = color
        col_margin = 5
        row_margin = 5
        if button_size == None:
            button_size = (self.window_size[0]/13, self.window_size[1]/5)

        # Draw a big black box over everything
        pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.window_size[0], self.window_size[1]), 0)
        
        # Draw buttons
        for y, row in enumerate(self.keyboard):
            for x, key in enumerate(row):

                if key in flash_keys:
                    color = flash_color
                    key_color = flash_color_key
                else:
                    color = self.GREEN
                    key_color = self.BLACK

                if y>=1 and y<=3: # Letters
                    indent = 20
                elif key=="       ": # Space bar
                    button_size = (button_size[0]*5, button_size[1])
                    indent = int(self.window_size[0]/2 - button_size[0]/2)
                else:
                    indent = 0
                pygame.draw.rect(self.screen, color, (indent+x*(button_size[0] + col_margin)+col_margin, 
                                                           y*(button_size[1] + row_margin)+row_margin, button_size[0], button_size[1]))
                text_surface = self.font.render(key, True, key_color)
                self.screen.blit(text_surface, (indent+x*(button_size[0] + col_margin)+col_margin+button_size[0]/2 - text_surface.get_width()/2, 
                                                y*(button_size[1] + row_margin)+row_margin+button_size[1]/2 - text_surface.get_height()/2))
        
        # Draw target letter on bottom left corner
        if target_letter is not None:
            text_surface = self.font.render(target_letter, True, self.WHITE)
            self.screen.blit(text_surface, (5 + text_surface.get_width(), 
                                            self.window_size[1] - 5 - text_surface.get_height()))

        pygame.display.flip()

    def button_press(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return True
        return False
    
    def get_keyboard(self):
        return self.keyboard
    
    def flash_keys(self, keys, color='random', target_letter=None):
        if type(keys) == str:
            new_keys = [keys]
        elif type(keys) == list:
            new_keys = []
            if type(keys[0]) == list:
                for l in keys:
                    new_keys.extend(l)
            else:
                new_keys = keys
        else:
            raise ValueError('Invalid key input: ' + type(keys) + '. Must be string or list of strings.')
        
        self.reset_screen(flash_keys = new_keys, color=color, target_letter=target_letter)

    def get_search_pattern(self, prev_flash=None, response=True):
        if prev_flash is None:
            pattern = self.nested_to_1d_list(self.keyboard[:int(len(self.keyboard)/2)])
            full = self.nested_to_1d_list(self.keyboard)
        else:
            prev_flash = self.nested_to_1d_list(prev_flash)
            if response:
                pattern = prev_flash[:int(len(prev_flash)/4)]
                full = prev_flash[:int(len(prev_flash)/2)]
            else:
                pattern = prev_flash[int(len(prev_flash)/2):int(3*len(prev_flash)/4)]
                full = prev_flash[int(len(prev_flash)/2):]
        
        return pattern, full
    
    def nested_to_1d_list(self, l):
        new_l = []
        if type(l)!=list:
            new_l.append(l)
        else:
            for item in l:
                new_l.extend(self.nested_to_1d_list(item))
        return new_l
    
class DataAcquisitionHandler:

    def __init__(self, port = 'COM4', flash_time = (0.1, 0.3), wait_time = (1.5, 2.5), sample_time=1):
        self.flash_time = flash_time
        self.wait_time = wait_time
        self.sample_time = sample_time
        self.__board_port = port
        self.__data = {}

    def __del__(self):
        pass

    def meaure_impedance(self):
        board = Board(self.__board_port)
        impedance = board.impedance()
        del board
        return impedance

    def get_data(self):
        return self.__data

    def run_data_trial_box(self, box_size = 'screen', simulate=False, window_size = None, description=None):

        trials = []
        if window_size is not None:
            GUI = Box_GUI(window_size=window_size)
        else:
            GUI = Box_GUI()
        GUI.reset_screen(box_size)
        if not simulate:
            board = Board(self.__board_port)

        # Wait for any button press to start sequence
        while True:
            if GUI.button_press():
                break

        if  not simulate:
            start_time = time.time()
            board.start_stream()

        # Data collection loop
        while True:
            GUI.reset_screen(box_size)

            # make random wait time in wait_time range
            wait_time = random.uniform(self.wait_time[0], self.wait_time[1])
            i = 0
            end = False
            while i < wait_time:
                if GUI.button_press(): # Continuousely check for button press
                    end = True
                    break
                time.sleep(0.1)
                i += 0.1
            if end:
                break

            # Get data iteration (flash screen)
            if not simulate:
                trial_start_time = time.time()

            run_flash = random.choice([True, False])
            if run_flash:
                sample_time = 0
                while sample_time < self.sample_time:
                    GUI.flash_box(box_size) 
                    flash_time = random.uniform(self.flash_time[0], self.flash_time[1])
                    if sample_time + flash_time > self.sample_time:
                        flash_time = self.sample_time - sample_time
                    time.sleep(flash_time)
                    sample_time += flash_time
            else:
                time.sleep(self.sample_time)
            
            print("Label : "+str(run_flash))

            if not simulate:
                trial_end_time = time.time()

                trial_timestamps = (trial_start_time - start_time, trial_end_time - start_time)
                trial = {'timestamp': trial_timestamps, 'label': run_flash}

                trials.append(trial) # [{'timestamp': (start, end), 'flash_time': flash_time}, ...]
        
        if not simulate:
            data = board.get_data()
            board.stop_stream()
            del board

        del GUI

        if not simulate:
            end_time = time.time() - start_time
            metadata = {
                'start_time': start_time, # time in seconds
                'length': end_time, # time in seconds
                'trials': trials, # [(start, end), (start, end), ...]
                'flash_time_range': self.flash_time, # time in seconds
                'sample_time': self.sample_time, # time in seconds
                'box_size': box_size,
                'description': description # Text description passed in as an input
            }

            session_data = [{
                'metadata': metadata, # {'start_time': start_time, 'length': length 'flash_time': flash_time, 'timestamps': [(start, end), (start, end), ...]}}
                'data': data # [channel_1, channel_2, ..., channel_24]
            }]

            # Save data to dict
            self.add_data({'box_data': session_data})

    def run_data_trial_QWERTY(self, letter="Random", simulate=False, window_size=None, description=None):

        if letter=="Random":
            random_letter = True
        else:
            random_letter = False

        trials = []
        if window_size is not None:
            GUI = Keyboard_GUI(window_size=window_size)
        else:
            GUI = Keyboard_GUI(window_size = (1920, 1080))
        GUI.reset_screen()

        if not simulate:
            board = Board(self.__board_port)

        # Wait for any button press to start sequence
        while True:
            if GUI.button_press():
                break

        end = False

        if not simulate:
            start_time = time.time()
            board.start_stream()

        # Data collection loop
        while True:

            pattern = None
            label = True

            if end:
                    break

            if random_letter:
                choices = GUI.nested_to_1d_list(GUI.get_keyboard())
                random_idx = np.random.randint(0, len(choices))
                letter = choices[random_idx]
                
            GUI.reset_screen(target_letter=letter)

            while True:
                GUI.reset_screen(target_letter=letter)

                # make random wait time in wait_time range
                wait_time = random.uniform(self.wait_time[0], self.wait_time[1])
                i = 0
                end = False
                while i < wait_time:
                    if GUI.button_press(): # Continuousely check for button press
                        end = True
                        break
                    time.sleep(0.1)
                    i += 0.1
                if end:
                    break

                # Get flash pattern
                if pattern is None:
                    pattern, full = GUI.get_search_pattern()
                elif (len(pattern)==1 or len(pattern)==0) and label:
                    break
                elif len(full)==2:
                    break
                else:
                    pattern, full = GUI.get_search_pattern(prev_flash=full, response=label)

                if not simulate:
                    # Get data iteration (flash screen)
                    trial_start_time = time.time()

                sample_time = 0
                while sample_time < self.sample_time:
                    GUI.flash_keys(keys=pattern, target_letter=letter)
                    flash_time = random.uniform(self.flash_time[0], self.flash_time[1])
                    if sample_time + flash_time > self.sample_time:
                        flash_time = self.sample_time - sample_time
                    time.sleep(flash_time)
                    sample_time += flash_time

                if not simulate:
                    trial_end_time = time.time()
                    trial_timestamps = (trial_start_time - start_time, trial_end_time - start_time)
                    
                print("Pattern : "+str(pattern))
                
                label = self._get_label_keyboard(letter, pattern)
                
                print("Label : "+str(label))
                print("Letter : "+str(letter))

                if not simulate:
                    trial = {
                        'timestamp': trial_timestamps,
                        'pattern': pattern,
                        'letter': letter,
                        'label': label
                    }

                    trials.append(trial)
        
        if not simulate:
            data = board.get_data()
            board.stop_stream()
            del board

        del GUI

        if not simulate:
            end_time = time.time() - start_time
            metadata = {
                'start_time': start_time, # time in seconds
                'length': end_time, # time in seconds
                'trials': trials, # [(start, end), (start, end), ...]
                'flash_time_range': self.flash_time, # time in seconds
                'sample_time': self.sample_time, # time in seconds
                'description': description # Text description passed in as an input
            }

            session_data = [{
                'metadata': metadata, # {'start_time': start_time, 'length': length 'flash_time': flash_time, 'trials': [{'timestamp': (start, end), 'pattern': pattern, 'letter': letter, 'label' label}...}}
                'data': data # [channel_1, channel_2, ..., channel_24]
            }]

            self.add_data({'keyboard_data': session_data})

    def _get_label_keyboard(self, letter, pattern):
        if letter in pattern:
            return True
        else:
            return False

    def save(self, data=None, file_name="data.pkl"):
        if data is None:
            data = self.__data
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)

    def load(self, file_name="data.pkl"):
        with open(file_name, 'rb') as f:
            data = pickle.load(f)
        self.add_data(data)
    
    def add_data(self, data):
        for key in data.keys():
            if key in self.__data.keys():
                self.__data[key].extend(data[key]) # append to existing key
            else:
                self.__data[key] = data[key] # create new key

    def raw_data_stream(self, time_to_record = 100):
        board = Board(self.__board_port)
        board.start_stream()
        time.sleep(time_to_record)
        data = board.get_data()
        board.stop_stream()
        del board
        return data

    def parse_session_data(self, data): 
        """
        Parses the raw data stream into data windows for training/testing/deployment

        Params:
            data: dictionary containing metadata and raw data for a session.

        Returns:
            trial_data: list of tuples containing data windows for each trial and labels for each trial
            [ ( [channel1, ... channel24], label ), ...]
        """

        metadata = data['metadata']
        data = data['data']

        start_time = metadata['start_time']
        sample_time = metadata['sample_time']
        timestamps_labels = []
        for trial in metadata['trials']:
            timestamps_labels.append((trial['timestamp'], trial['label']))
        length = metadata['length']

        # Get interval
        interval_ratio = length/len(data[0])

        # Get data for each trial
        trial_data = []
        for timestamp_labels in timestamps_labels:
            timestamp = timestamp_labels[0]
            label = timestamp_labels[1]
            start = int((timestamp[0])/interval_ratio) 
            # Start - end is not fixed (runtime doesn't take same time each time). Use start - start+flash_time
            end = int((timestamp[0] + sample_time)/interval_ratio)
            trial_data.append((data[:, start:end], label))

        return trial_data