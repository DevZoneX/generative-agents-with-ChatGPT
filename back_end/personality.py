'''
➢ Extraversion vs Introversion: Externalization of feelings and reactions
➢ Neuroticism vs Emotional Stability: Sensation of negative emotions
➢ Agreeableness vs Disagreeableness: Seeking social harmony
➢ Openness vs Closedness: Intellectual curiosity, openness
➢ Conscientiousness vs Unconscientiousness: Organization and persistence
'''

from episodic_memory.API_gabriel import get_completion

class Personality:
    def __init__(self, neuroticism=0, extraversion=0, openness=0, agreeableness=0, conscientiousness=0):
        self.traits = {
            "Neuroticism": neuroticism,
            "Extraversion": extraversion,
            "Openness": openness,
            "Agreeableness": agreeableness,
            "Conscientiousness": conscientiousness
        }
        self.history = {"Neuroticism": [neuroticism],
                        "Extraversion": [extraversion],
                        "Openness": [openness],
                        "Agreeableness": [agreeableness],
                        "Conscientiousness": [conscientiousness]}

    def modify_personality(self, trait, value):
        if trait in self.traits:
            if 0 <= value <= 1:
                self.traits[trait] = value
                self.history[trait].append(value)
            else:
                print("Value must be between 0 and 1.")
        else:
            print("The specified trait does not exist.")

    def reset_personality(self):
        for trait in list(self.history.keys()):
            setattr(self, trait, 0)
            self.history[trait].append(0)

    def get_personality_history_trait(self, trait):
        return self.history[trait]

    def get_personality_history(self):
        description = []
        for trait, history in self.history.items():
            description.append(f"{trait}: {history}")
        return "\n".join(description)

    def print_personality(self):
        desc = ", ".join([f"{trait} at {values}" for trait, values in self.traits.items()])
        return ("Here is the current personality: (0 means the personality trait is not present, 1 means it is strongly present) - " + desc + ".")

    def update_personality_resp(self, response):
        if response == 'False':
            return False
        else:
            lines = response.split('\n')
            if len(lines) > 1:
                new_values = [float(x) for x in lines[1].strip('[]').split(',')]
                for trait, new_val in zip(self.traits.keys(), new_values):
                    if 0 <= new_val <= 1:
                        self.traits[trait] = new_val
                        self.history[trait].append(new_val)
                    else:
                        print(f"Value for {trait} must be between 0 and 1.")
                return True
    
    def update_personality(self, agent, event):
        prompt_personality = f"I am trying to model the personality of a NPC named {agent.name} from a video game. Here's the event that just happened in the life of this NPC: {event}"+agent.emotion.print_emotions()+agent.personality.print_personality()+"Should we change the personality? If no, simply respond with False. If yes, modify the emotion values I provided above and give them to me in the following format, separated by &&:\n&&\nTrue\nt\n&&\n, where t is a Python array of size 5, and each element corresponds, in order, to the following characteristics: Neuroticism, Extraversion, Openness, Agreeableness, Conscientiousness with values ranging from 0 to 1."
        
        message_personality = [{'role': 'system', 'content': prompt_personality}]
        
        response_personality = get_completion(message_personality, model="gpt-3.5-turbo", max_tokens=500, temperature=0)
        self.update_personality_resp(response_personality)
        
        return response_personality

"""
# Example of use
p = Personality(0.5, 0.7, 0.3, 0.8, 0.6)
print(p.print_personality())
"""

