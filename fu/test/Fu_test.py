"""
==========================================================================
Alu_test.py
==========================================================================
Test cases for functional unit.

Author : Cheng Tan
  Date : November 27, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..Alu                        import Alu
from ..Shifter                    import Shifter
from ..Mul                        import Mul
from ..Logic                      import Logic
from ..MemUnit                    import MemUnit
from ...ifcs.opt_type             import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType,
                 src0_msgs, src1_msgs,
                 config_msgs, sink_msgs ):

    s.src_in0  = TestSrcRTL( DataType, src0_msgs   )
    s.src_in1  = TestSrcRTL( DataType, src1_msgs   )
    s.src_opt  = TestSrcRTL( DataType, config_msgs )
    s.sink_out = TestSinkCL( DataType, sink_msgs   )

    s.dut = FunctionUnit( DataType )

    connect( s.src_in0.send, s.dut.recv_in0  )
    connect( s.src_in1.send, s.dut.recv_in1  )
    connect( s.src_opt.send, s.dut.recv_opt  )
    connect( s.dut.send_out, s.sink_out.recv )

  def done( s ):
    return s.src_in0.done() and s.src_in1.done() and\
           s.src_opt.done() and s.sink_out.done()

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=1000 ):
  test_harness.elaborate()
  test_harness.apply( SimulationPass )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print()
  print( "{}:{}".format( ncycles, test_harness.line_trace() ))
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{}:{}".format( ncycles, test_harness.line_trace() ))

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

def test_alu():
  FU = Alu
  DataType = Bits16
  src_in0  = [ DataType(1), DataType(2), DataType(9) ]
  src_in1  = [ DataType(2), DataType(3), DataType(1) ]
  sink_out = [ DataType(3), DataType(5), DataType(8) ]
  src_opt  = [ DataType(OPT_ADD), DataType(OPT_ADD), DataType(OPT_SUB) ]
  th = TestHarness( FU, DataType, src_in0, src_in1, src_opt, sink_out )
  run_sim( th )

def test_shifter():
  FU = Shifter
  DataType = Bits16
  src_in0  = [ DataType(1), DataType(2),  DataType(4) ]
  src_in1  = [ DataType(2), DataType(3),  DataType(1) ]
  sink_out = [ DataType(4), DataType(16), DataType(2) ]
  src_opt  = [ DataType(OPT_LLS), DataType(OPT_LLS),  DataType(OPT_LRS) ]
  th = TestHarness( FU, DataType, src_in0, src_in1, src_opt, sink_out )
  run_sim( th )

def test_mul():
  FU = Mul
  DataType = Bits16
  src_in0  = [ DataType(1), DataType(2), DataType(4)  ]
  src_in1  = [ DataType(2), DataType(3), DataType(3)  ]
  sink_out = [ DataType(2), DataType(6), DataType(12) ]
  src_opt  = [ DataType(OPT_MUL), DataType(OPT_MUL), DataType(OPT_MUL) ]
  th = TestHarness( FU, DataType, src_in0, src_in1, src_opt, sink_out )
  run_sim( th )

def test_logic():
  FU = Logic
  DataType = Bits16
  src_in0  = [ DataType(1), DataType(2), DataType(4), DataType(1)  ]
  src_in1  = [ DataType(2), DataType(3), DataType(3), DataType(2)  ]
  sink_out = [ DataType(3), DataType(2), DataType(0xfffb), DataType(3) ]
  src_opt  = [ DataType(OPT_OR), DataType(OPT_AND), 
               DataType(OPT_NOT), DataType(OPT_XOR) ]
  th = TestHarness( FU, DataType, src_in0, src_in1, src_opt, sink_out )
  run_sim( th )

def test_MemUnit():
  FU = MemUnit
  DataType = Bits16
  src_in0  = [ DataType(1), DataType(3), DataType(3) ]
  src_in1  = [ DataType(0), DataType(5), DataType(2) ]
  sink_out = [ DataType(2), DataType(2), DataType(5) ]
  src_opt  = [ DataType(OPT_LD), DataType(OPT_STR), DataType(OPT_LD) ]
  th = TestHarness( FU, DataType, src_in0, src_in1, src_opt, sink_out )
  run_sim( th )
