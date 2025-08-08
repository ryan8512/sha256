from pyuvm import *
from sha256_driver import SHA256Driver
from sha256_sequencer import SHA256Sequencer
from sha256_monitor import SHA256Monitor

class SHA256Agent(uvm_component):  # FIXED: was SHA256_agent
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
    def build_phase(self):
        self.sequencer = SHA256Sequencer("sequencer", self)
        self.driver = SHA256Driver("driver", self)
        self.monitor = SHA256Monitor("monitor", self)
    
    def connect_phase(self):
        self.driver.seq_item_port.connect(self.sequencer.seq_item_export)