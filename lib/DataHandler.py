import pygame
import time
from brainflow.board_shim import BoardShim, BoardIds
from brainflow.board_shim import BrainFlowInputParams
import random
import pyautogui

class DataAcquisitionHandler:

    def __init__(self, port = 'COM4', flash_time = 0.75, wait_time = (1.5, 2.5)):
        self.flash_time = flash_time
        self.wait_time = wait_time
        self.__board = Board(port)
        self.__data = {}

    def __del__(self):
        del self.__board
        del GUI

    def get_data(self):
        return self.__data

    def run_data_trial_box(self, box_size = 'screen'):

        data = []
        GUI = Box_GUI()
        GUI.reset_screen(box_size)

        # Wait for any button press to start sequence
        while True:
            if GUI.button_press():
                break

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
            self.__board.start_stream()
            GUI.flash_box(box_size)
            time.sleep(self.flash_time)
            data.append(self.__board.get_data_stop_stream())
        
        del GUI

        # Save data to dict
        self.add_data({'box_data-' + str(box_size): data})

    def run_data_trial_QWERTY(self):
        pass

    def save(self, file_name):
        import pickle
        with open(file_name, 'wb') as f:
            pickle.dump(self.__data, f)

    def load(self, file_name):
        import pickle
        with open(file_name, 'rb') as f:
            data = pickle.load(f)
        self.add_data(data)
    
    def add_data(self, data):
        for key in data.keys():
            if key in self.__data.keys():
                self.__data[key].extend(data[key]) # append to existing key
            else:
                self.__data[key] = data[key] # create new key
    


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

    def start_stream(self):
        self.board.start_stream()

    def get_data_stop_stream(self):
        data = self.board.get_board_data()
        self.board.stop_stream()
        return data

    def get_data_keep_stream(self):
        return self.board.get_board_data()
    


class Box_GUI:

    # Constants
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0 , 0)
    GREEN = (0, 255, 0)

    def __init__(self):
        width, height = pyautogui.size()
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

    def flash_box(self, box_size):
        box_size = self.box_size_parser(box_size)
        center = ((self.window_size[0] - box_size[0])/2, (self.window_size[1] - box_size[1])/2)
        pygame.draw.rect(self.screen, self.RED, (center[0], center[1], box_size[0], box_size[1]), 0)
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

    def __init__(self):
        width, height = pyautogui.size()
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
    
    def reset_screen(self, button_size = None):
        col_margin = 5
        row_margin = 5
        if button_size == None:
            button_size = (self.window_size[0]/13, self.window_size[1]/5)
        
        # Draw buttons
        for y, row in enumerate(self.keyboard):
            for x, key in enumerate(row):
                if y>=1 and y<=3: # Letters
                    indent = 20
                elif key=="       ": # Space bar
                    button_size = (button_size[0]*5, button_size[1])
                    indent = int(self.window_size[0]/2 - button_size[0]/2)
                else:
                    indent = 0
                pygame.draw.rect(self.screen, self.WHITE, (indent+x*(button_size[0] + col_margin)+col_margin, 
                                                           y*(button_size[1] + row_margin)+row_margin, button_size[0], button_size[1]))
                text_surface = self.font.render(key, True, self.BLACK)
                self.screen.blit(text_surface, (indent+x*(button_size[0] + col_margin)+col_margin+button_size[0]/2 - text_surface.get_width()/2, 
                                                y*(button_size[1] + row_margin)+row_margin+button_size[1]/2 - text_surface.get_height()/2))
        
        pygame.display.flip()