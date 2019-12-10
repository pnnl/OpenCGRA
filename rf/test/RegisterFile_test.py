"""
==========================================================================
RegisterFile_test.py
==========================================================================
Test cases for register file.

Author: Cheng Tan
  Date: Dec 10, 2019

"""

import pytest
from pymtl3                        import *
from pymtl3.stdlib.test            import TestVectorSimulator

from pymtl3.stdlib.rtl             import RegisterFile

#-------------------------------------------------------------------------
# TestVectorSimulator test
#-------------------------------------------------------------------------

def run_tv_test( dut, test_vectors ):

  # Define input/output functions

  def tv_in( dut, tv ):
    dut.raddr[0] = tv[0]
    dut.waddr[0] = tv[2]
    dut.wdata[0] = tv[3]
    dut.wen[0]   = tv[4]

  def tv_out( dut, tv ):
    assert dut.rdata == tv[1]

  # Run the test

  sim = TestVectorSimulator( dut, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_pipe_Bits():

  run_tv_test( RegisterFile( Bits32, 1 ), [
    #  raddr   rdata    waddr     wdata   wen
    [  b1(0),  b32(0),  b1(0), b1(0),  b1(0) ],
    [  b1(0),  b32(0),  b1(0), b1(0),  b1(1) ],
    [  b1(0),  b32(0),  b1(0), b1(0),  b1(1) ],
    [  b1(0),  b32(0),  b1(0), b1(1),  b1(1) ],
    [  b1(0),  b32(0),  b1(0), b1(1),  b1(1) ],
    [  b1(0),  b32(0),  b1(0), b1(0),  b1(0) ],
    [  b1(0),  b32(0),  b1(0), b1(1),  b1(1) ],
    [  b1(0),  b32(0),  b1(0), b1(1),  b1(1) ],
    [  b1(0),  b32(0),  b1(0), b1(1),  b1(1) ],
    [  b1(0),  b32(0),  b1(0), b1(1),  b1(1) ],
] )

##-------------------------------------------------------------------------
## TestHarness
##-------------------------------------------------------------------------
#
#class TestHarness( Component ):
#
#  def construct( s, MsgType, src_msgs, sink_msgs ):
#
#    s.src  = TestSrcRTL   ( MsgType, src_msgs )
#    s.dut  = InputUnitRTL ( MsgType )
#    s.sink = TestSinkRTL  ( MsgType, sink_msgs )
#
#    # Connections
#    s.src.send     //= s.dut.recv
#    s.dut.give.msg //= s.sink.recv.msg
#
#    @s.update
#    def up_give_en():
#      if s.dut.give.rdy and s.sink.recv.rdy:
#        s.dut.give.en  = b1(1)
#        s.sink.recv.en = b1(1)
#      else:
#        s.dut.give.en  = b1(0)
#        s.sink.recv.en = b1(0)
#
#  def done( s ):
#    return s.src.done() and s.sink.done()
#
#  def line_trace( s ):
#    return "{} >>> {} >>> {}".format(
#      s.src.line_trace(),
#      s.dut.line_trace(),
#      s.sink.line_trace(),
#    )
#
##-------------------------------------------------------------------------
## run_sim
##-------------------------------------------------------------------------
#
#def run_sim( th, max_cycles=1000 ):
#
#  # Create a simulator
#  th.apply( DynamicSim )
#  th.sim_reset()
#
#  # Run simulation
#
#  ncycles = 0
#  print()
#  print( "{:3}:{}".format( ncycles, th.line_trace() ))
#  while not th.done() and ncycles < max_cycles:
#    th.tick()
#    ncycles += 1
#    print( "{:3}:{}".format( ncycles, th.line_trace() ))
#
#  # Check timeout
#  assert ncycles < max_cycles
#
##-------------------------------------------------------------------------
## Test cases
##-------------------------------------------------------------------------
#
#def test_simple():
#  test_msgs = [ b16( 4 ), b16( 1 ), b16( 2 ), b16( 3 ) ]
#  arrival_time = [ 2, 3, 4, 5 ]
#  th = TestHarness( Bits16, test_msgs, test_msgs )
#  run_sim( th )
#
