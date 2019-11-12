# Theory of Mind Module
# ToM represents mental states
# described as triads of form Agent-Mental State-Object
import numpy as np
from output.logger import Logger
from model.model import Model

class ToM:

    # The set of mental states ToM represents.
    # Lets start with the BELIEF mental state.
    MENTAL_STATES = ["Believes"]

    def __init__(self):
        Model.__init__(self, Logger.MODEL_TOM)

    def set(self, affordances,intentions, id, edd, sam, mem):
        self.afford = affordances
        self.intentions = intentions
        self.id = id
        self.agents = id.agents
        self.edd = edd
        self.sam = sam
        self.memory  = mem
        self.tom_beliefs = []

    def process(self):
        # Create representations of the mental states 
        # of the form Agent-Mental State-Object

        # 'Believes' mental state
        # The mental state modeled here produces descriptions in the form
        # AGENT BELIEVES OBJECT AFFORDANCE or
        # AGENT BELIEVES OBJECT AFFORDANCE TARGET_OBJECT (due to an intention)
        for agent in range(self.edd.edd_eyes.shape[0]):
            tom_belief = []
            # For each agent line in edd_eyes
            # Retrieve the list of objects the agent sees.
            tom_belief.append(self.edd.edd_eyes[agent])
            tom_belief.append(self.MENTAL_STATES[0])
            for ent in range(self.edd.edd_agent_store.shape[1]):
                obj = self.edd.edd_agent_store[agent][ent]
                tom_belief.append(obj)
                for sublist in self.afford:
                    if sublist[0] == obj:
                        # Object has an affordance.
                        tom_belief.append(sublist[1])
                        break
                # Check if intentions from the environment 
                # are likely to change beliefs.
                tom_belief = self.check_intentions(tom_belief)
                self.tom_beliefs.append(tom_belief.copy())
                del tom_belief[2:] # Only keeps Agent and Belief 

            # Add the list of beliefs at the end to the Belief Memory.
            self.memory.add(self.tom_beliefs)
        
    def check_intentions(self, belief):
        # Next step is to analyse INTENTIONS and verify Beliefs that could be 
        # modified based on intentions detected in the environment.

        blf_agt = belief[0]
        blf_obj = belief[2]
        blf_afd = belief[3]

        for intention in self.intentions:
            agt = intention[0]
            intent = intention[1]
            obj = intention[2]
            tgt = intention[3]

            if (blf_obj == obj):
                # ie we only need to analyse an intention 
                # if the object is the same as the object in the current belief.
                belief = self.map_intention(intent, agt, obj, tgt, belief)

        if (len(belief) == 4):
            # Belief does not have a target object, set as None.
            belief.append('None')

        return belief

    def map_intention(self, intent, agt, obj, tgt, belief):
        mapper = {
            'None': self.skip,
            'ReachFor': self.reachFor,
            'Puts': self.put,
            'Gets': self.get,
            'Exits': self.skip,
            'Enters': self.skip,
            'Search': self.skip
        }
        # Get the function from mapper dictionary
        func = mapper.get(intent)
        # Execute the function
        return func(agt, obj, tgt, belief)

    def skip(self, agt, obj, tgt, belief):
        # Nothing to do
        return belief

    def reachFor(self, agt,obj, tgt, belief):
        # Reaching for an object results
        # on the object ending up on the agent hand.
        belief[3] = 'OnHand'
        belief.append('Of ' + agt)
        return belief
    
    def put(self, agt, obj, tgt, belief):
        belief[3] = 'HiddenIn'
        belief[4] = tgt
        return belief

    def get(self, agt, obj, tgt, belief):
        belief[3] = 'OnHand'
        belief.append('Of ' + agt)
        return belief

    def print(self, t):
        msg = "Evaluating Mind Step " + str(t)
        self.logger.write(msg)
        self.logger.write("ToM:")
        self.logger.write("Agents: " + str(self.agents()))
        self.logger.write("Intentions: " + str(self.intentions))
        self.logger.write("Beliefs: " + str(self.tom_beliefs))