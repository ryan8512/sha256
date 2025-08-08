from pyuvm import *
from sha256_agent import SHA256Agent
from sha256_scoreboard import SHA256Scoreboard

class SHA256Env(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
    
    def build_phase(self):
        self.agent = SHA256Agent("agent", self)
        self.scoreboard = SHA256Scoreboard("scoreboard", self)
    
    def connect_phase(self):
        # Connect the analysis port to the scoreboard's analysis export
        self.agent.monitor.analysis_port.connect(self.scoreboard.analysis_export)