import pygame
import time
from brainflow.board_shim import BoardShim, BoardIds
from brainflow.board_shim import BrainFlowInputParams
import random

class DataHandler:

    # Constants / Variables
    port = 'COM4'
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0 , 0)
    GREEN = (0, 255, 0)
    window_size = (1024, 1024)
    box_size = 512
    flash_time = 0.75
    wait_time = (1.5, 2.5)

    def __init__(self, port = 'COM4', window_size = (1024, 1024), box_size = 512, 
                 flash_time = 0.75, wait_time = (1.5, 2.5)):
        self.port = port
        self.window_size = window_size
        self.box_size = box_size
        self.flash_time = flash_time
        self.wait_time = wait_time

    def run_data_trial_box(self):
        # Run Trial

        # Prep board / data stream
        BoardShim.enable_dev_board_logger()
        params = BrainFlowInputParams()
        params.serial_port = self.port
        board = BoardShim(BoardIds.CYTON_BOARD, params)
        board.prepare_session()

        # Prep pygame window
        pygame.init()
        screen = pygame.display.set_mode(self.window_size)
        clock = pygame.time.Clock()
        data = []

        # Start window
        self._reset_screen(screen, self.box_size)
        pygame.display.flip()

        # Wait for any button press to start sequence
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    waiting = False

        # Data collection loop
        running = True
        while running:
            # make random wait time between 1.5 and 2.5 seconds
            wait_time = random.uniform(self.wait_time[0], self.wait_time[1])

            # Get data iteration (flash screen)
            board.start_stream ()
            self._flash_box(screen, self.box_size)
            time.sleep(self.flash_time)
            data_iter = board.get_board_data()  # get all data and remove it from internal buffer
            board.stop_stream()
            data.append(data_iter)

            # Unflash screen
            self._reset_screen(screen, self.box_size)
            time.sleep(wait_time)

            # Break if any button pressed
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    running = False

        board.release_session()
        pygame.quit()

        return data

    def run_data_trial_QWERTY(self):
        pass

    def _reset_screen(self, screen, box_size):
        screen.fill(self.BLACK)
        pygame.draw.rect(screen, self.GREEN, (self.window_size[0]/4, self.window_size[1]/4, box_size, box_size), 0)
        pygame.display.update()

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