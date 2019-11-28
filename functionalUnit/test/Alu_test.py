"""
==========================================================================
Alu_test.py
==========================================================================
Test cases for simple generic ALU.

Author : Cheng Tan
  Date : November 27, 2019

"""

from pymtl3 import *
#from pymtl3.stdlib.test import TestSinkCL
#from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..Alu import Alu

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

#  def construct( s, DataType, src_msgs, sink_msgs, configs ):
  def construct( s, DataType, src_msg=None, sink_msg=None ):

    s.dut = Alu( DataType )
    s.dut.in0 = DataType( 20 )
    s.dut.in1 = DataType( 12 )

  def done( s ):
    return s.dut.in0 + s.dut.in1 == s.dut.out

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( th, max_cycles=1000 ):
  print()
  th.elaborate()
  th.apply( SimulationPass )
  th.sim_reset()
  ncycles = 0
  th.line_trace()
  th.tick()
  ncycles += 1
  print( th.line_trace() )
  assert th.done()

def test_alu():
  DataType = Bits16
  th = TestHarness( DataType )
  run_sim( th )

  

