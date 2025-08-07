from pyuvm import uvm_object
import cocotb

class SHA256Transaction(uvm_object):
    def __init__(self, name="SHA256Transaction"):
        super().__init__(name)
        
        # Inputs except the clock and reset
        self.init = 0
        self.next = 0
        self.mode = 0
        self.block = 0 
        
        
        # Optionally, output
        self.ready = 0
        self.digest = 0
        self.digest_valid = 0
        
    
    def __str__(self):
        return (f"[SHA256Transaction init={self.init} next={self.next} "
                f"mode={self.mode} block=0x{self.block:0128x}]")