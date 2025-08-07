from pyuvm import *

class SHA256Sequencer(uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)