from pyuvm import *
from sha256_env import SHA256Env  # ADDED: Missing import
from sha256_transaction import SHA256Transaction
import random

class SHA256SimpleSequence(uvm_sequence):
    async def body(self):
        for i in range(3):
            txn = SHA256Transaction()
            txn.init = 1 if i == 0 else 0
            txn.next = 0 if i == 0 else 1
            txn.mode = 0
            txn.block = random.getrandbits(512)
            
            #self.logger.info(f"Sending transaction {i}: {txn}")
            await self.start_item(txn)
            await self.finish_item(txn)

class SHA256Test(uvm_test):
    def __init__(self, name, parent):
        super().__init__(name, parent)
    
    def build_phase(self):  # ADDED: Missing build_phase
        self.env = SHA256Env("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        
        seq = SHA256SimpleSequence("simple_seq")
        await seq.start(self.env.agent.sequencer)  # FIXED: was sequncer
        
        self.drop_objection()