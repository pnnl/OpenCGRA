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

#    s.src_data  = [ TestSrcRTL( DataType, src_data[i]  )
#                  for i in range( FuDFG.num_const   ) ]
    s.sink_out  = TestSinkCL( DataType, sink_out )

    s.dut = DUT( FuDFG, DataType, CtrlType )

#    for i in range( FuDFG.num_const  ):
#      connect( s.src_data[i].send, s.dut.recv_data[i] )
    connect( s.dut.send_data, s.sink_out.recv )

  def done( s ):
    return s.sink_out.done()

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=10 ):
  test_harness.elaborate()
  test_harness.apply( SimulationPass() )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
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
  target_json = "dfg_fir.json"
  script_dir  = os.path.dirname(__file__)
  file_path   = os.path.join( script_dir, target_json )
  DataType = mk_data( 16, 1 )
  CtrlType = mk_ctrl()
  const_data = [ DataType( 1, 1  ),
                 DataType( 0, 1  ),
                 DataType( 1, 1  ),
                 DataType( 0, 1  ),
                 DataType( 1, 1  ),
                 DataType( 2, 1 ) ]
  data_spm = [ 3 for _ in range(100) ]
  fu_dfg = DFG( file_path, const_data, data_spm )

  print( "----------------- FL test ------------------" )
  # FL golden reference
  acc_fl( fu_dfg, DataType, CtrlType, const_data )#, data_spm )
  print()
#
#  print( "----------------- RTL test ------------------" )
#  DUT      = AccRTL
#  sink_out = [ DataType( 1, 1 ) ]
#  th = TestHarness( DUT, fu_dfg, DataType, CtrlType, const_data, sink_out )
#  run_sim( th )


