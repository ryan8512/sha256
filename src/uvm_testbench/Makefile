# Makefile for SHA256 UVM Testbench
# Run from uvm_testbench directory

# Simulator selection
SIM ?= icarus

# RTL Configuration
TOPLEVEL_LANG = verilog
TOPLEVEL = sha256_core

# Verilog source files - relative to uvm_testbench directory
VERILOG_SOURCES += ../rtl/sha256_core.v
VERILOG_SOURCES += ../rtl/sha256_w_mem.v  
VERILOG_SOURCES += ../rtl/sha256_k_constants.v
VERILOG_SOURCES += ../rtl/sha256.v

# Python test module (without .py extension)
MODULE = testbench

# Compilation arguments
COMPILE_ARGS += -I../rtl

# Simulation arguments - VCD generation handled by cocotb
# Remove custom VCD args as they conflict with iverilog

# Python path - add current directory so imports work
export PYTHONPATH := $(PWD):$(PYTHONPATH)

# Cocotb logging
export COCOTB_LOG_LEVEL = INFO

# Include cocotb makefiles  
include $(shell cocotb-config --makefiles)/Makefile.sim

# Custom targets
.PHONY: clean run waves help

# Default target
run: 
	$(MAKE) sim

# Open waveforms (will be generated as dump.vcd by cocotb)
waves: 
	@if [ -f dump.vcd ]; then \
		gtkwave dump.vcd & \
	elif [ -f sha256_test.vcd ]; then \
		gtkwave sha256_test.vcd & \
	else \
		echo "No VCD file found. Run 'make WAVES=1' to generate waveforms."; \
	fi

# Enhanced clean
clean::
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf sim_build/
	rm -f *.vcd
	rm -f *.fst  
	rm -f *.ghw
	rm -f results.xml
	rm -f *.log

# Help target
help:
	@echo "SHA256 UVM Testbench Makefile"
	@echo "=============================="
	@echo "Targets:"
	@echo "  make         - Run simulation with icarus (default)"
	@echo "  make run     - Same as make"
	@echo "  make waves   - Open waveform viewer (gtkwave)"
	@echo "  make clean   - Clean build artifacts"
	@echo "  make help    - Show this help"
	@echo ""
	@echo "Simulator options:"
	@echo "  make SIM=icarus    - Use Icarus Verilog (default)"
	@echo "  make SIM=verilator - Use Verilator"
	@echo "  make SIM=questa    - Use Questa/ModelSim"
	@echo "  make SIM=vcs       - Use Synopsys VCS"
	@echo ""
	@echo "Debug options:"
	@echo "  make WAVES=1       - Generate waveforms"
	@echo "  make GUI=1         - Run with GUI (simulator dependent)"