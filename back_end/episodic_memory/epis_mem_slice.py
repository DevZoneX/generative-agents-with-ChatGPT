import json

class EpisodicMemorySlice:
    
    nodeId = 1
    def __init__(self, time="", context=""):
        self.nodeId = EpisodicMemorySlice.nodeId
        EpisodicMemorySlice.nodeId += 1
        self.time = time
        self.context = context
        
    def get_info(self):
        return {
            'time': self.time,
            'context': self.context,
        }

    def write_in_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        existing_data[self.nodeId] = self.get_info()
        with open(file_path, 'w') as file:
            json.dump(existing_data, file)