"""
==========================================================================
Acc_test.py
==========================================================================
Test cases for HLS in terms of accelerator design.

Author : Cheng Tan
  Date : Feb 3, 2020

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ...lib.messages              import *
from ..AccFL                      import acc_fl
from ..AccRTL                     import AccRTL
from ...lib.dfg_helper            import *

import os

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, DUT, FuDFG, DataType, CtrlType, src_data, sink_out ):
    s.num_liveout = FuDFG.num_liveout

    s.src_data  = [ TestSrcRTL( DataType, src_data[i]  )
                  for i in range( FuDFG.num_const  ) ]
    s.sink_out  = [ TestSinkCL( DataType, sink_out[i] )
                  for i in range( FuDFG.num_liveout ) ]

    s.dut = DUT( FuDFG, DataType, CtrlType )

    for i in range( FuDFG.num_const  ):
      connect( s.src_data[i].send, s.dut.recv_data[i] )
    for i in range( FuDFG.num_liveout ):
      connect( s.dut.send_data[i], s.sink_out[i].recv )

  def done( s ):
    done_flag = True
    for i in range( s.num_liveout ):
      if not s.sink_out[i].done():
        done_flag = False
    return done_flag

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=10 ):
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

def test_acc():
  target_json = "dfg_simple.json"
  script_dir  = os.path.dirname(__file__)
  file_path   = os.path.join( script_dir, target_json )
  fu_dfg      = DFG( file_path )

  DUT      = AccRTL
  DataType = mk_data( 16, 1 )
  CtrlType = mk_ctrl()
  src_data = [ [DataType(6-2*i, 1)] for i in range( fu_dfg.num_const ) ]

  sink_out = [ [DataType(20, 1)] ]
  th = TestHarness( DUT, fu_dfg, DataType, CtrlType, src_data, sink_out )
  run_sim( th )

  # FL golden reference
  acc_fl( fu_dfg, DataType, CtrlType, src_data )

