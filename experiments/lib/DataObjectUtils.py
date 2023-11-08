import scipy.signal as signal

class DataDecorator(object):

    @staticmethod
    def visit_data_object(object):
        raise NotImplementedError
    
    @staticmethod
    def visit_session_data(session):
        raise NotImplementedError
    
    @staticmethod
    def visit_trial_data(trial, raw_data):
        raise NotImplementedError


##########################################################################################


class MakeWindowsDataDecorator(DataDecorator):
    """
    Returns a list of tuples ( data_window, label )
    """

    def __init__(self):
        pass


    def visit_data_object(self, object, type):
        """
        Returns a list of tuples ( data_windows, label )
        """
        sessions = object.keyboard_sessions if type == 'keyboard' else object.box_sessions

        data = []
        for session in sessions:
            data.extend(self.visit_session_data(session=session))
        return data
    

    def visit_session_data(self, session):
        """
        Returns a list of tuples ( data_windows, label )
        """
        data = []
        for trial in session.trials:
            data.append(self.visit_trial_data(trial=trial))
        return data
    

    def visit_trial_data(self, trial):
        """
        Returns a tuple ( data_windows, label )
        """
        start = trial.timestamp[0]
        end = start + trial.parent_session.sample_time

        # Make it an index for the data rather than a time
        data_len = len(trial.parent_session.data[0])
        start = (int) ( (start / trial.parent_session.length) * data_len )
        end = (int) ( (end / trial.parent_session.length) * data_len )

        window = self.transform_window(trial.parent_session.data[:, start:end])
        label = self.transform_label(trial.label)

        return ( window, label )
    
    def transform_window(window):
        return window
    
    def transform_label(label):
        return label
    

class MakeTensorWindowsDataDecorator(MakeWindowsDataDecorator):
    """
    Returns a list of tuples ( data_window, label ) for each window in the format of a pytorch tensor
    """

    @staticmethod
    def transform_label(label):
        if not label:
            label = 0
        elif label:
            label = 1
        else:
            raise ValueError('MakeTensorWindowsDataVisitor object/ transform_label method: Label must be a boolean')
        
        return torch.tensor(label)
    
    @staticmethod
    def transform_window(window):
        return torch.from_numpy(window).float()
    


############################################################################################################

class DataVisitor(object):

    def visit_data_object(self, object):
        raise NotImplementedError
    
    def visit_session_data(self, session):
        raise NotImplementedError

    def visit_trial_data(self, trial):
        raise NotImplementedError
    

#################################################################


class FilterVisitor(DataVisitor):
    """
    Modifies the data inside the DataObject to be bandpass filtered
    """

    SAMPLE_RATE = 250
    ORDER = 3

    def __init__():
        raise NotImplementedError

    def visit_data_object(self, object):
        for session in object.keyboard_sessions:
            self.visit_session_data(session=session)

        for session in object.box_sessions:
            self.visit_session_data(session=session)
    
    def visit_session_data(self, session):
        data = []
        for i, channel in enumerate(session.data):
            # Only the channels with EM data will be filtered
            if i>1 and i<9:
                data.append(self.filter(channel))
            else:
                data.append(channel)

        session.data = np.array(data)

    def visit_trial_data(self, trial):
        pass

    def filter(self, data):
        raise NotImplementedError
    

class BandpassFilterVisitor(FilterVisitor):

    def __init__(self, low, high):
        self.low = low
        self.high = high

    def filter(self, data):
        """Bandpass filter using scipy.signal.butter"""
        b, a = signal.butter(3, [self.low, self.high], btype='bandpass', fs=self.SAMPLE_RATE)
        return signal.lfilter(b, a, data)
    

class BandstopFilterVisitor(FilterVisitor):
    
    def __init__(self, low, high):
        self.low = low
        self.high = high
    
    def filter(self, data):
        """Bandstop filter using scipy.signal.butter"""
        b, a = signal.butter(3, [self.low, self.high], btype='bandstop', fs=self.SAMPLE_RATE)
        return signal.lfilter(b, a, data)