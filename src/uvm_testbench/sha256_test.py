from pyuvm import *
from sha256_env import SHA256Env
from sha256_transaction import SHA256Transaction
from cocotb.triggers import Timer
import random

class SHA256SimpleSequence(uvm_sequence):
    async def body(self):
        # Wait a bit before starting to let everything settle
        await Timer(100, "ns")
        
        for i in range(3):
            txn = SHA256Transaction()
            txn.init = 1 if i == 0 else 0
            txn.next = 0 if i == 0 else 1
            txn.mode = 0
            
            # Create safe 512-bit block values
            if i == 0:
                txn.block = 0  # First test with zero block
            elif i == 1:
                # Create a simple pattern
                txn.block = 0x123456789abcdef0fedcba9876543210
                # Extend to full 512 bits safely
                txn.block = txn.block << 256 | txn.block
            else:
                # Create another pattern
                txn.block = 0xaaaaaaaaaaaaaaaa5555555555555555
                txn.block = txn.block << 256 | txn.block
            
            self.logger.info(f"Sending transaction {i}: init={txn.init}, next={txn.next}, block=0x{txn.block:0128x}")
            
            await self.start_item(txn)
            await self.finish_item(txn)
            
            # Wait between transactions to allow processing
            await Timer(2000, "ns")  # 2us between transactions

class SHA256Test(uvm_test):
    def __init__(self, name, parent):
        super().__init__(name, parent)
    
    def build_phase(self):
        self.env = SHA256Env("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        
        # Wait for reset to complete and system to stabilize
        await Timer(200, "ns")
        
        self.logger.info("Starting SHA256 UVM Test")
        
        seq = SHA256SimpleSequence("simple_seq")
        await seq.start(self.env.agent.sequencer)
        
        # Wait a bit more to let final transactions complete
        await Timer(5000, "ns")
        
        self.logger.info("SHA256 UVM Test Complete")
        
        self.drop_objection()