from pyuvm import *
import cocotb
from cocotb.triggers import RisingEdge
from sha256_transaction import SHA256Transaction

class SHA256Monitor(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None #Will be set externally
        self.analysis_port = uvm_analysis_port("analysis_port", self)
    
    async def run_phase(self):
        self.raise_objection()
        while True:
            await RisingEdge(self.dut.clk)
            
            if self.dut.digest_value.value:
                txn = SHA256Transaction()
                txn.digest = int(self.dut.digest.value)
                txn.digest_valid = int(self.dut.digest_valid.value)
                txn.ready = int(self.dut.ready.value)
                
                self.logger.info(f"Observed digest: 0x{txn.digest:064x}")
                self.analysis_port.write(txn)
        self.drop_objection()