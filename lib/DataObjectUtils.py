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