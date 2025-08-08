from pyuvm import *

class SHA256ScoreboardExport(uvm_analysis_export):
    """Custom analysis export that forwards to scoreboard"""
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.scoreboard = parent
    
    def write(self, txn):
        # Forward to scoreboard's write method
        self.scoreboard.write_transaction(txn)

class SHA256Scoreboard(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
        # Create custom analysis export
        self.analysis_export = SHA256ScoreboardExport("analysis_export", self)
        
        # Dictionary to map block -> expected digest
        self.expected_outputs = {}
    
    def write_transaction(self, txn):
        """This method will be called by the analysis export"""
        self.logger.info(f"Scoreboard received digest: 0x{txn.digest:064x}")
        
        # Find Expected digest based on something
        expected_digest = self.expected_outputs.get(txn.block, None)
        
        if expected_digest is None:
            self.logger.warning("No expected digest found for this block")
        else:
            if txn.digest != expected_digest:
                self.logger.error(f"Digest mismatch!\nExpected: 0x{expected_digest:064x}\nActual: 0x{txn.digest:064x}")
            else:
                self.logger.info("Digest matches expected")