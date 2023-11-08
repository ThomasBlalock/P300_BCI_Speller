
from pythonosc import dispatcher

from pythonosc import osc_server

import matplotlib.pyplot as plt

import numpy as np

 

# Data storage for Channel 8

channel_8_data = []

 

def eeg_handler(unused_addr, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, *args):

    global channel_8_data

    print(f"EEG data [Channel 8]: {ch8}")

    channel_8_data.append(ch8)


    # Keep only the last 250 points for plotting

    channel_8_data = channel_8_data[-250:]


    # Update the plot

    ax.clear()

    ax.plot(channel_8_data)

    ax.set_title("Real-time EEG Data from Channel 8")

    plt.draw()

    plt.pause(0.001)

 

if __name__ == "__main__":

    # Initialize the OSC dispatcher

    dispatcher = dispatcher.Dispatcher()

    dispatcher.map("/openbci", eeg_handler)

 

    # Initialize and start the OSC server

    server = osc_server.ThreadingOSCUDPServer(("localhost", 6677), dispatcher)

    print("Serving on {}".format(server.server_address))


    # Initialize Matplotlib for real-time plotting

    plt.ion()

    fig, ax = plt.subplots()

    plt.show(block=False)

 

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("Server closed.")
