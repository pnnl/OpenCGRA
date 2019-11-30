"""
==========================================================================
Mem_test.py
==========================================================================
Test cases for functional unit.

Author : Cheng Tan
  Date : November 29, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..Mem         import Mem
from ...ifcs.opt_type import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType,
                 src0_msgs, src1_msgs,
                 config_msgs, sink_msgs ):

    s.src_addr = TestSrcRTL( DataType, src0_msgs   )
    s.src_data = TestSrcRTL( DataType, src1_msgs   )
    s.src_opt  = TestSrcRTL( DataType, config_msgs )
    s.sink_out = TestSinkCL( DataType, sink_msgs   )

    s.dut = FunctionUnit( DataType )

    connect( s.src_addr.send, s.dut.recv_addr )
    connect( s.src_data.send, s.dut.recv_data )
    connect( s.src_opt.send,  s.dut.recv_opt  )
    connect( s.dut.send_out,  s.sink_out.recv )

  def done( s ):
    return s.src_addr.done() and s.src_data.done() and\
           s.src_opt.done()  and s.sink_out.done()

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=1000 ):
  test_harness.elaborate()
  test_harness.apply( SimulationPass )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print()
  print( "{}:{}".format( ncycles, test_harness.line_trace() ) )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{}:{}".format( ncycles, test_harness.line_trace() ) )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

def test_Mem():
  FU = Mem
  DataType = Bits16
  src_in0  = [ DataType(1), DataType(3), DataType(3) ]
  src_in1  = [ DataType(0), DataType(5), DataType(2) ]
  sink_out = [ DataType(2), DataType(2), DataType(5) ]
  src_opt  = [ DataType(OPT_LD), DataType(OPT_STR), DataType(OPT_LD) ]
  th = TestHarness( FU, DataType, src_in0, src_in1, src_opt, sink_out )
  run_sim( th )

