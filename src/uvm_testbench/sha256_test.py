
from cocotb.triggers import Timer
from pyuvm import *
from sha256_env import SHA256Env
from sha256_transaction import SHA256Transaction

class SHA256SimpleSequence(uvm_sequence):
    def __init__(self, name="SHA256SimpleSequence"):
        super().__init__(name)
    
    async def body(self):
        # Wait a bit before starting to let everything settle
        await Timer(500, "ns")
        
        # Use print instead of logger for sequences to avoid initialization issues
        print("=== Starting SHA256 Sequence ===")
        
        # Test 1: Zero block
        print("--- Test 1: Zero Block ---")
        txn = SHA256Transaction()
        txn.init = 1  # First transaction uses init
        txn.next = 0
        txn.mode = 1
        txn.block = 0x61626380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018  # 512-bit value
        
        
        print("Sending zero block transaction")
        await self.start_item(txn)
        await self.finish_item(txn)
        
        # Wait longer between transactions
        await Timer(5000, "ns")  # 5us between transactions
        
        # Test 2: Simple pattern
        print("--- Test 2: Pattern Block ---")
        txn = SHA256Transaction()
        txn.init = 1  # Subsequent transactions use next
        txn.next = 0
        txn.mode = 1
        txn.block = 0x61626380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018  # 512-bit value
        
        # Create a safe 512-bit pattern
        # pattern = 0x123456789abcdef0
        # txn.block = 0
        # for j in range(8):  # 8 * 64 bits = 512 bits
        #     txn.block = (txn.block << 64) | pattern
        
        # # Ensure it's not too large
        # if txn.block.bit_length() > 512:
        #     txn.block = txn.block & ((1 << 512) - 1)
        
        print(f"Sending pattern block (bits: {txn.block.bit_length()})")
        await self.start_item(txn)
        await self.finish_item(txn)
        
        await Timer(5000, "ns")  # 5us wait
        
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
        
        await Timer(3000, "ns")  # Final wait
        print("=== Sequence Complete ===")

class SHA256Test(uvm_test):
    def __init__(self, name, parent):
        super().__init__(name, parent)
    
    def build_phase(self):
        self.env = SHA256Env("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        
        # Wait for reset to complete and system to stabilize
        await Timer(1000, "ns")  # 1us wait for reset
        
        self.logger.info("=== Starting SHA256 UVM Test ===")
        
        seq = SHA256SimpleSequence("simple_seq")
        await seq.start(self.env.agent.sequencer)
        
        # Wait for all operations to complete
        await Timer(5000, "ns")  # Reduced wait time
        
        self.logger.info("=== SHA256 UVM Test Complete ===")
        
        # Force termination of UVM components
        try:
            # Stop the monitor and driver explicitly
            self.env.agent.monitor.drop_objection()
            self.env.agent.driver.drop_objection()
        except:
            pass  # They might not have objections raised
        
        self.drop_objection()