"""
==========================================================================
Comp_test.py
==========================================================================
Test cases for functional unit Phi.

Author : Cheng Tan
  Date : November 27, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..Comp                       import Comp
from ....lib.opt_type             import *
from ....lib.messages             import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType, ConfigType,
                 src_data, src_ref, src_opt, sink_msgs ):

    s.src_data = TestSrcRTL( DataType, src_data  )
    s.src_ref  = TestSrcRTL( DataType, src_ref   )
    s.src_opt  = TestSrcRTL( ConfigType, src_opt )
    s.sink_out = TestSinkCL( Bits1,    sink_msgs )

    s.dut = FunctionUnit( DataType, ConfigType )

    connect( s.src_data.send, s.dut.recv_data )
    connect( s.src_ref.send,  s.dut.recv_ref  )
    connect( s.src_opt.send,  s.dut.recv_opt  )
    connect( s.dut.send_pred, s.sink_out.recv )

  def done( s ):
    return s.src_data.done() and s.src_ref.done() and\
           s.src_opt.done()  and s.sink_out.done()

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

def test_Comp():
  FU = Comp
  DataType  = mk_data( 16, 1 )
  ConfigType  = mk_config( 16 )
  src_data  = [ DataType(9, 1),     DataType(3, 1),     DataType(3, 1)     ]
  src_ref   = [ DataType(9, 1),     DataType(5, 1),     DataType(2, 1)     ]
  src_opt   = [ ConfigType(OPT_EQ), ConfigType(OPT_LE), ConfigType(OPT_EQ) ]
  sink_out  = [ Bits1(1),           Bits1(1),           Bits1(0)           ]
  th = TestHarness( FU, DataType, ConfigType, src_data, src_ref, src_opt, sink_out )
  run_sim( th )
