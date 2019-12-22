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

from ..MemUnit                    import MemUnit
from ....mem.data.DataMem         import DataMem
from ....lib.opt_type             import *
from ....lib.messages             import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType, ConfigType,
                 src0_msgs, src1_msgs, ctrl_msgs, sink_msgs ):

    s.src_in0  = TestSrcRTL( DataType,   src0_msgs   )
    s.src_in1  = TestSrcRTL( DataType,   src1_msgs   )
    s.src_opt  = TestSrcRTL( ConfigType, ctrl_msgs )
    s.sink_out = TestSinkCL( DataType,   sink_msgs   )

    s.dut = FunctionUnit( DataType, ConfigType )
    s.data_mem = DataMem( DataType )

    connect( s.dut.to_mem_raddr,   s.data_mem.recv_raddr[0] )
    connect( s.dut.from_mem_rdata, s.data_mem.send_rdata[0] )
    connect( s.dut.to_mem_waddr,   s.data_mem.recv_waddr[0] )
    connect( s.dut.to_mem_wdata,   s.data_mem.recv_wdata[0] )

    connect( s.src_in0.send,  s.dut.recv_in0  )
    connect( s.src_in1.send,  s.dut.recv_in1  )
    connect( s.src_opt.send,  s.dut.recv_opt  )
    connect( s.dut.send_out0, s.sink_out.recv )

  def done( s ):
    return s.src_in0.done() and s.src_in1.done() and\
           s.src_opt.done() and s.sink_out.done()

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

def test_Mem():
  FU = MemUnit
  DataType = mk_data( 16, 1 )
  ConfigType = mk_ctrl()
  src_in0  = [ DataType(1, 1), DataType(3, 1), DataType(3, 1), DataType(3, 1) ]
  src_in1  = [ DataType(9, 1), DataType(6, 1), DataType(2, 1), DataType(7, 1) ]
  sink_out = [ DataType(0, 0), DataType(6, 1), DataType(6, 1) ]
  src_opt  = [ ConfigType( OPT_LD  ),
               ConfigType( OPT_STR ),
               ConfigType( OPT_LD  ),
               ConfigType( OPT_LD  ) ]
  th = TestHarness( FU, DataType, ConfigType, src_in0, src_in1, src_opt, sink_out )
  run_sim( th )

