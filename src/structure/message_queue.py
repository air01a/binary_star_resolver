class Message_Queue:

    def __init__(self, type, data):
        self.type = type
        self.data = data

    def get_type(self):
        return self.type

    def get_data(self):
        return self.data