#=========================================================================
# ChannelRTL_test.py
#=========================================================================
# Simple test for Channel
#
# Author : Cheng Tan
#   Date : Dec 11, 2019

import pytest
from pymtl3                        import *
from pymtl3.stdlib.test.test_srcs  import TestSrcRTL
from pymtl3.stdlib.test.test_sinks import TestSinkRTL, TestSinkCL
from pymtl3.stdlib.test            import TestVectorSimulator
from ..ChannelRTL                  import ChannelRTL
from ...lib.messages               import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src  = TestSrcRTL ( MsgType, src_msgs  )
    s.sink = TestSinkRTL( MsgType, sink_msgs )
    s.dut  = ChannelRTL( MsgType )

    # Connections
    s.src.send //= s.dut.recv
    s.dut.send //= s.sink.recv

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.dut.line_trace() + \
                               " | -> " + s.sink.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Create a simulator
  test_harness.elaborate()
  test_harness.apply( SimulationPass() )
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

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

DataType  = mk_data( 16, 1 )
test_msgs = [ DataType(7,1,1), DataType(4,1), DataType(1,1), DataType(2,1), DataType(3,1) ]
sink_msgs = [ DataType(7,1,0), DataType(4,1), DataType(1,1), DataType(2,1), DataType(3,1) ]

def test_simple():
  th = TestHarness( DataType, test_msgs, sink_msgs)
  run_sim( th )
