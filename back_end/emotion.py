from episodic_memory.API_gabriel import get_completion

class Emotion:
    def __init__(self, joy, sadness, fear, love, hate, pride, shame, thresholds, function, stable):
        self.emotions = {
            "Joy": joy,
            "Sadness": sadness,
            "Fear": fear,
            "Love": love,
            "Hate": hate,
            "Pride": pride,
            "Shame": shame
        }
        self.history = {
            "Joy": [joy],
            "Sadness": [sadness],
            "Fear": [fear],
            "Love": [love],
            "Hate": [hate],
            "Pride": [pride],
            "Shame": [shame]
        }
        self.activation_thresholds = thresholds
        self.weakening_function = function
        self.stable_state = stable

    def get_emotion(self):
        description = []
        for trait, value in self.emotions.items():
            description.append(f"{trait}: {value}")
        return "\n".join(description)

    def modify_thresholds(self, thresholds):
        self.activation_thresholds = thresholds

    def modify_function(self, function):
        self.weakening_function = function

    def modify_stable(self, stable):
        self.stable_state = stable

    def modify_emotion(self, emotion, value):
        if emotion in self.emotions:
            if 0 <= value <= 1:
                self.emotions[emotion] = value
                self.history[emotion].append(value)
            else:
                print("Value must be between 0 and 1.")
        else:
            print("The specified trait does not exist.")

    def reset_emotions(self):
        for emotion in list(self.history.keys()):
            setattr(self, emotion, 0)
            self.history[emotion].append(0)

    def get_emotion_history(self, emotion):
        return self.history[emotion]

    def get_emotions_history(self):
        description = []
        for emotion_name, values in self.history.items():
            description.append([emotion_name, values])
        return description

    def print_emotions(self):
        desc = ", ".join(["{} at {}".format(emotion_name, values) for emotion_name, values in self.emotions.items()])
        return ("Here is its current emotional state: (0 means the emotion is not felt, 1 means it is felt to the maximum) - " + desc + ".")

    def update_emotion_resp(self, response):
        if response == 'False':
            return False
        else:
            lines = response.split('\n')
            if len(lines) > 1:
                new_values = [float(x) for x in lines[1].strip('[]').split(',')]
                for emotion, new_val in zip(self.emotions.keys(), new_values):
                    if 0 <= new_val <= 1:
                        self.emotions[emotion] = new_val
                        self.history[emotion].append(new_val)
                    else:
                        print(f"Value for {emotion} must be between 0 and 1.")    
                return True
            
    def update_emotion(self,agent,event):
        prompt_emotion = f"I am trying to model the emotions of a NPC named {agent.name} from a video game. Here's the event that just happened in the life of this NPC: {event}"+agent.emotion.print_emotions()+agent.personality.print_personality()+"Should we change the emotional state? If no, simply respond with False. If yes, modify the emotion values I provided above and give them to me in the following format, separated by &&:\n&&\nTrue\nt\n&&\n, where t is a Python array of size 7, and each element corresponds, in order, to the following characteristics: Joy, Sadness, Fear, Love, Hate, Pride, Shame, with values ranging from 0 to 1."
        message_emotion = [ {'role':'system',
        'content': prompt_emotion},
        ]
        response_emotion = get_completion(message_emotion, model="gpt-3.5-turbo", max_tokens=500, temperature=0)
        self.update_emotion_resp(response_emotion)
        return response_emotion
        
        

''' 
# Example of use
npc = Emotion(0,0,0,0,0,0,0,0,0,0)
npc.modify_emotion("Joy", 0.5)

print(npc.get_emotion_history("Joy"))   # Displays [0.5]
print(npc.get_emotion_history("Fear"))  # Displays [0.3]

npc.reset_emotions()
print(npc.get_emotion_history("Joy"))   # Displays [0.5, 0]

# Examples of use:
response1 = 'True\n[0.2, 0.9, 0.5, 0.1, 0, 0.3, 0]'
response2 = 'False'

print(update(response1))  # Displays: [0.2, 0.9, 0.5, 0.1, 0, 0.3, 0]
print(update(response2))  # Displays: False

'''