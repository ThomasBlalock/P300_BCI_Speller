class DataVisitor(object):

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


class MakeWindowsDataVisitor(DataVisitor):
    """
    Returns a list of tuples ( data_window, label )
    """


    @staticmethod
    def visit_data_object(object, type):
        """
        Returns a list of tuples ( data_windows, label )
        """
        sessions = object.keyboard_sessions if type == 'keyboard' else object.box_sessions

        data = []
        for session in sessions:
            data.extend(MakeWindowsDataVisitor.visit_session_data(session=session))
        return data
    

    @staticmethod
    def visit_session_data(session):
        """
        Returns a list of tuples ( data_windows, label )
        """
        data = []
        for trial in session.trials:
            data.append(MakeWindowsDataVisitor.visit_trial_data(trial=trial))
        return data
    

    @staticmethod
    def visit_trial_data(trial):
        """
        Returns a tuple ( data_windows, label )
        """
        start = trial.timestamp[0]
        end = start + trial.parent_session.sample_time

        # Make it an index for the data rather than a time
        data_len = len(trial.parent_session.data[0])
        start = (int) ( (start / trial.parent_session.length) * data_len )
        end = (int) ( (end / trial.parent_session.length) * data_len )

        return ( trial.parent_session.data[:, start:end], trial.label )