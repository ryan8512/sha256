from pyuvm import *
from sha256 import SHA256

class SHA256ScoreboardExport(uvm_analysis_export):
    '"""Monitor Export"""'
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.scoreboard = parent
    
    def write(self, txn):
        # Forward to scoreboard's write method
        self.scoreboard.write_transaction(txn)

class SHA256ScoreboardInputExport(uvm_analysis_export):
    '"""Driver Export"""'
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.scoreboard = parent
    
    def write(self, txn):
        # Forward to scoreboard's write method
        self.scoreboard.write_transaction_input(txn)

class SHA256Scoreboard(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
        # Create custom analysis export
        self.analysis_export = SHA256ScoreboardExport("analysis_export", self)
        self.input_export = SHA256ScoreboardInputExport("input_export", self)
        
        # Counter for received transactions
        self.transaction_count = 0

        # Store transactions as needed
        self.input_queue = []
        self.output_queue = []
    
    def write_transaction_input(self, txn):
        """This method will be called by the input export"""
        self.input_queue.append(txn)
        self.try_compare()
    
    def write_transaction(self, txn):
        """This method will be called by the analysis export"""
        self.transaction_count += 1
        self.output_queue.append(txn)
        self.try_compare()
    
    def try_compare(self):
        # Implement logic to match input/output transactions and check results
        if self.input_queue and self.output_queue:
            input_txn = self.input_queue.pop(0)
            output_txn = self.output_queue.pop(0)

            self.logger.info(f"=== Scoreboard Transaction #{self.transaction_count} ===")
            self.logger.info(f"Received digest: 0x{output_txn.digest:064x}")
            self.logger.info(f"Ready: {output_txn.ready}, Valid: {output_txn.digest_valid}")
            
            # Basic validation - digest should not be zero (unless it's the zero block result)
            if output_txn.digest == 0:
                self.logger.error("Received zero digest - this might indicate an error")
            else:
                self.logger.info("Non-zero digest received")
            
            # Check digest_valid should be 1
            if output_txn.digest_valid != 1:
                self.logger.error(f"Expected digest_valid=1, got {output_txn.digest_valid}")
            else:
                self.logger.info("digest_valid is correctly asserted")
            
            # For the zero block case, we can check against expected result
            if hasattr(output_txn, 'block') and output_txn.block == 0:
                expected = self.sha256_naked(str(hex(input_txn.block)))
                if expected and output_txn.digest == int(expected,16):
                    self.logger.info("Block Digest matched!")
                    self.logger.info(f"  Expected: 0x{expected}")
                    self.logger.info(f"  Actual:   0x{output_txn.digest:064x}")
                elif expected:
                    self.logger.error(f"Block Digest mismatch!")
                    self.logger.error(f"  Expected: 0x{expected}")
                    self.logger.error(f"  Actual:   0x{output_txn.digest:064x}")
            
            # Log statistics
            self.logger.info(f"Total transactions processed: {self.transaction_count}")
            self.logger.info("=" * 50)
    
    def sha256_naked(self, block:str) -> str:
        #Convert to list type (int)
        block = block[2:]  #Delete the 0x
        TC_block = [0] * 16
        for i in range(len(TC_block)):
            chunk = block[8*i: 8*i+8]
            TC_block[i] = int(chunk,16)
            
        my_sha256 = SHA256(verbose=0)
        my_sha256.init()
        my_sha256.next(TC_block)
        my_digest = my_sha256.get_digest()
        
        
        #Return back to byte
        reconstructed_bytes = b''.join(x.to_bytes(4, byteorder='big') for x in my_digest)
        return reconstructed_bytes.hex()