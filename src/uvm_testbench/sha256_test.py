
from pyuvm import *
from sha256_env import SHA256Env
from sha256_transaction import SHA256Transaction

class SHA256SimpleSequence(uvm_sequence):
    def __init__(self, name="SHA256SimpleSequence"):
        super().__init__(name)
    
    async def body(self):
        # Use print instead of logger for sequences to avoid initialization issues
        print("=== Starting SHA256 Sequence ===")
        
        # Test 1: Zero block
        print("--- Test 1: abc Block ---")
        txn = SHA256Transaction()
        txn.init = 1  # First transaction uses init
        txn.next = 0
        txn.mode = 1
        txn.block = 0x61626380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018  # 512-bit value
        
        
        print("Sending zero block transaction")
        await self.start_item(txn)
        await self.finish_item(txn)
        
        # Test 2: Simple pattern
        print("--- Test 2: abc Block 2 ---")
        txn = SHA256Transaction()
        txn.init = 1  # Subsequent transactions use next
        txn.next = 0
        txn.mode = 1
        txn.block = 0x61626380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018  # 512-bit value
        
        print(f"Sending pattern block (bits: {txn.block.bit_length()})")
        await self.start_item(txn)
        await self.finish_item(txn)
        
        # Test 3: Another pattern
        print("--- Test 3: Alternating Pattern ---")
        txn = SHA256Transaction()
        txn.init = 1
        txn.next = 0
        txn.mode = 1
        
        # Create alternating pattern
        pattern1 = 0xaaaaaaaaaaaaaaaa
        pattern2 = 0x5555555555555555
        txn.block = 0
        for j in range(4):  # 4 * 128 bits = 512 bits
            txn.block = (txn.block << 64) | pattern1
            txn.block = (txn.block << 64) | pattern2
        
        # Ensure it's not too large
        if txn.block.bit_length() > 512:
            txn.block = txn.block & ((1 << 512) - 1)
        
        print(f"Sending alternating pattern (bits: {txn.block.bit_length()})")
        await self.start_item(txn)
        await self.finish_item(txn)
    
        print("=== Sequence Complete ===")

class SHA256Test(uvm_test):
    def __init__(self, name, parent):
        super().__init__(name, parent)
    
    def build_phase(self):
        self.env = SHA256Env("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        
        self.logger.info("=== Starting SHA256 UVM Test ===")
        
        seq = SHA256SimpleSequence("simple_seq")
        await seq.start(self.env.agent.sequencer)
        
        self.logger.info("=== SHA256 UVM Test Complete ===")
        
        # Force termination of UVM components
        try:
            # Stop the monitor and driver explicitly
            self.env.agent.monitor.drop_objection()
            self.env.agent.driver.drop_objection()
        except:
            pass  # They might not have objections raised
        
        self.drop_objection()