# Makefile for SHA256 UVM Testbench

# Simulator
SIM ?= icarus

# Top-level module (should be sha256_core based on your interface)
TOPLEVEL = sha256_core

# Verilog sources - adjust paths as needed
VERILOG_SOURCES = ../rtl/sha256_core.v
VERILOG_SOURCES += ../rtl/sha256_k_constants.v  
VERILOG_SOURCES += ../rtl/sha256_w_mem.v

# Python test modules
MODULE = simple_testbench

# Additional Icarus Verilog arguments
COMPILE_ARGS += -I../rtl

# Export PYTHONPATH to include current directory
export PYTHONPATH := $(PWD):$(PYTHONPATH)

# Default target
all: sim

# Run simple signal test first
simple:
	@echo "Running simple RTL test..."
	$(MAKE) sim MODULE=simple_testbench

# Run the corrected simple test
corrected:
	@echo "Running corrected simple test..."
	$(MAKE) sim MODULE=sha256_simple_test

# Run UVM test
uvm:
	@echo "Running UVM test..."
	$(MAKE) sim MODULE=testbench

# Quick signal check
quick:
	@echo "Running quick signal test..."
	$(MAKE) sim MODULE=sha256_simple_test TESTCASE=quick_signal_test

# Clean generated files
cleans:
	rm -rf __pycache__/
	rm -rf sim_build/
	rm -f results.xml
	rm -f *.vcd
	rm -f *.fst

# Include the common cocotb makefile
include $(shell cocotb-config --makefiles)/Makefile.sim

# Help target
help:
	@echo "Available targets:"
	@echo "  simple    - Run basic RTL interface test"
	@echo "  corrected - Run corrected signal test"  
	@echo "  quick     - Run quick signal accessibility test"
	@echo "  uvm       - Run full UVM testbench"
	@echo "  cleans     - Clean generated files"
	@echo "  help      - Show this help"
	@echo ""
	@echo "Variables:"
	@echo "  SIM       - Simulator (default: icarus)"
	@echo "  TOPLEVEL  - Top module (default: sha256_core)"