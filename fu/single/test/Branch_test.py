"""
==========================================================================
Branch_test.py
==========================================================================
Test cases for functional unit branch.

Author : Cheng Tan
  Date : November 27, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..Branch                     import Branch 
from ....ifcs.opt_type            import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType, src_data, src_comp,
                 sink_out, sink_if_pred, sink_else_pred ):

    s.src_data       = TestSrcRTL( DataType, src_data       )
    s.src_comp       = TestSrcRTL( Bits1,    src_comp       )
    s.sink_if        = TestSinkCL( DataType, sink_out       )
    s.sink_else      = TestSinkCL( DataType, sink_out       )
    s.sink_if_pred   = TestSinkCL( Bits1,    sink_if_pred   )
    s.sink_else_pred = TestSinkCL( Bits1,    sink_else_pred )

    s.dut = FunctionUnit( DataType )

    connect( s.src_data.send,      s.dut.recv_data       )
    connect( s.src_comp.send,      s.dut.recv_comp       )
    connect( s.dut.send_if,        s.sink_if.recv        )
    connect( s.dut.send_else,      s.sink_else.recv      )
    connect( s.dut.send_if_pred,   s.sink_if_pred.recv   )
    connect( s.dut.send_else_pred, s.sink_else_pred.recv )

  def done( s ):
    return s.src_data.done()     and s.src_comp.done()       and\
           s.sink_if.done()      and s.sink_else.done()      and\
           s.sink_if_pred.done() and s.sink_else_pred.done()

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

def test_Branch():
  FU = Branch
  DataType       = Bits16
  src_data       = [ DataType(1), DataType(3), DataType(13) ]
  src_comp       = [ Bits1(0),    Bits1(1),    Bits1(0)     ]
  sink_out       = [ DataType(1), DataType(3), DataType(13) ]
  sink_if_pred   = [ Bits1(0),    Bits1(1),    Bits1(0)     ]
  sink_else_pred = [ Bits1(1),    Bits1(0),    Bits1(1)     ]
  th = TestHarness( FU, DataType, src_data, src_comp,
                    sink_out, sink_if_pred, sink_else_pred )
  run_sim( th )
