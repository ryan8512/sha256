from pyuvm import *
import cocotb 
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.handle import SimHandleBase

class SHA256Driver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None  # Will be set externally
    
    async def run_phase(self):
        self.raise_objection()
        while True:
            txn = await self.seq_item_port.get_next_item()
            
            self.logger.info(f"Driving transaction: {txn}")
            await self.drive_tran
            
            self.seq_item_port.item_done()
        self.drop_objection()
        
    async def drive_transaction(self, txn):
        await RisingEdge(self.dut.clk)
        
        #Apply Inputs
        self.dut.init.value = txn.input
        self.dut.next.value = txn.next
        self.dut.mode.value = txn.mode
        self.dut.block.value = txn.block
        
        await RisingEdge(self.dut.clk)
        
        # Deassert init/next
        self.dut.init.value = 0
        self.dut.next.value = 0
        
        # Optional: Wait until DUT is ready
        while self.dut.ready.value == 0:
            await RisingEdge(self.dut.clk)