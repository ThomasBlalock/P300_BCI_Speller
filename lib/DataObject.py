class DataObject:


    def __init__(self, data_dict, window_len = 250):

        self.keyboard_sessions = []

        if 'keyboard_data' in data_dict.keys():
            keyboard_session_list = data_dict['keyboard_data']

            for session_dict in keyboard_session_list:
                self.keyboard_sessions.append(SessionData(session_dict=session_dict, type='keyboard', window_len = window_len))

        self.box_sessions = []

        if 'box_data' in data_dict.keys():
            box_session_list = data_dict['box_data']

            for session_dict in box_session_list:
                self.box_sessions.append(SessionData(session_dict=session_dict, type='box', window_len = window_len))


    def get_data(self, decorator=None, type='box'):
        if decorator is None:
            keyboard_data = self.keyboard_sessions
            box_data = self.box_sessions
        else:
            keyboard_data, box_data = decorator.visit_data_object(object=self)
        return (keyboard_data, box_data)
    
    def accept(self, visitor):
        visitor.visit_data_object(object=self)




class SessionData:
    
    def __init__(self, session_dict, type, window_len = 250):
        metadata = session_dict['metadata']
        self.data = session_dict['data']
        self.start_time = metadata['start_time']
        self.length = metadata['length']
        self.flash_time_range = metadata['flash_time_range']
        self.sample_time = metadata['sample_time']
        self.description = metadata['description']
        self.type = type

        self.trials = []
        for trial in metadata['trials']:
            if self.type == 'keyboard':
                self.trials.append(KeyboardTrialData(trial_dict=trial, parent_session=self, window_len = window_len))
            elif self.type == 'box':
                self.trials.append(BoxTrialData(trial_dict=trial, parent_session=self, window_len = window_len))
            else:
                raise ValueError('Session type must be either keyboard or box')

    def get_data(self, decorator=None):
        if decorator is None:
            trials = self.trials
        else:
            trials = decorator.visit_session_data(session=self)
        return trials
    
    def accept(self, visitor):
        visitor.visit_session_data(session=self)



class TrialData:

    def __init__(self, trial_dict, parent_session, window_len = 250):
        timestamp = trial_dict['timestamp']
        data_len = len(parent_session.data[0])
        self.start_idx = (int) ( (timestamp[0] / parent_session.length) * data_len )
        self.end_idx = self.start_idx + window_len
        self.label = trial_dict['label']
        self.parent_session = parent_session

    def get_data(self, decorator=None):
        if decorator is None:
            data = self.parent_session.data[:, self.start_idx:self.end_idx]
        else:
            data = decorator.visit_trial_data(trial=self)
        return data
    
    def accept(self, visitor):
        visitor.visit_trial_data(trial=self)
    


class BoxTrialData(TrialData):

    def __init__(self, trial_dict, parent_session):
        super().__init__(trial_dict, parent_session)



class KeyboardTrialData(TrialData):

    def __init__(self, trial_dict, parent_session):
        super().__init__(trial_dict, parent_session)
        self.pattern = trial_dict['pattern']
        self.letter = trial_dict['letter']