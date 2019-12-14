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
from ....lib.opt_type             import *
from ....lib.messages             import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType, ConfigType,
                 src_data, src_comp, sink_if, sink_else ):

    s.src_data       = TestSrcRTL( DataType, src_data  )
    s.src_comp       = TestSrcRTL( Bits1,    src_comp  )
    s.sink_if        = TestSinkCL( DataType, sink_if   )
    s.sink_else      = TestSinkCL( DataType, sink_else )

    s.dut = FunctionUnit( DataType, ConfigType )

    connect( s.src_data.send,      s.dut.recv_data       )
    connect( s.src_comp.send,      s.dut.recv_comp       )
    connect( s.dut.send_if,        s.sink_if.recv        )
    connect( s.dut.send_else,      s.sink_else.recv      )

  def done( s ):
    return s.src_data.done() and s.src_comp.done()  and\
           s.sink_if.done()  and s.sink_else.done() 

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=100 ):
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

def test_Branch():
  FU = Branch
  DataType   = mk_data( 16, 1 )
  ConfigType = mk_config( 16 )
  src_data   = [ DataType(1, 1), DataType(3, 1), DataType(9, 1) ]
  src_comp   = [ Bits1(0),       Bits1(1),       Bits1(0)       ]
  sink_if    = [ DataType(1, 0), DataType(3, 1), DataType(9, 0) ]
  sink_else  = [ DataType(1, 1), DataType(3, 0), DataType(9, 1) ]
  th = TestHarness( FU, DataType, ConfigType, src_data, src_comp,
                    sink_if, sink_else )

  run_sim( th )
