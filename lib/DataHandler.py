import pygame
import time
from brainflow.board_shim import BoardShim, BoardIds
from brainflow.board_shim import BrainFlowInputParams
import random

class DataHandler:

    def __init__(self, port = 'COM4', window_size = (1024, 1024), flash_time = 0.75, wait_time = (1.5, 2.5)):
        self.flash_time = flash_time
        self.wait_time = wait_time
        self.box_GUI = Box_GUI(window_size)
        self.board = Board(port)

    def __del__(self):
        del self.board
        del self.box_GUI

    def run_data_trial_box(self, box_size = 256):

        data = []

        self.box_GUI.reset_screen(box_size)

        # Wait for any button press to start sequence
        while True:
            if self.box_GUI.button_press():
                break

        # Data collection loop
        while True:
            # make random wait time in wait_time range
            wait_time = random.uniform(self.wait_time[0], self.wait_time[1])

            # Get data iteration (flash screen)
            self.board.start_stream()
            self.box_GUI.flash_box(box_size)
            time.sleep(self.flash_time)
            data.append(self.board.get_data_stop_stream())

            # Unflash screen
            self.box_GUI.reset_screen(box_size)
            time.sleep(wait_time)

            # Break if any button is pressed
            if self.box_GUI.button_press():
                break

        pygame.quit()

        return data

    def run_data_trial_QWERTY(self):
        pass

    def _flash_box(self, screen, box_size):
        screen.fill(self.BLACK)
        pygame.draw.rect(screen, self.RED, (self.window_size[0]/4, self.window_size[1]/4, box_size, box_size), 0)
        pygame.display.update()

    def print_to_file(self, data, file_name):
        # print data to file using pickle
        import pickle
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)

    def load_from_file(self, file_name):
        # Load pickle file 
        import pickle
        with open(file_name, 'rb') as f:
            data = pickle.load(f)
        return data
    

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

    def __init__(self, window_size = (1024, 1024)):
        self.window_size = window_size

        # Prep pygame window
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)

    def __del__(self):
        pygame.quit()
    
    def reset_screen(self, box_size):
        self.screen.fill(self.BLACK)
        pygame.draw.rect(self.screen, self.GREEN, (self.window_size[0]/4, self.window_size[1]/4, box_size, box_size), 0)
        pygame.display.update()
        pygame.display.flip()

    def flash_box(self, box_size):
        pygame.draw.rect(self.screen, self.RED, (self.window_size[0]/4, self.window_size[1]/4, box_size, box_size), 0)
        pygame.display.update()
        pygame.display.flip()

    def button_press(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return True
        return False