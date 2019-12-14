"""
==========================================================================
ThreeCombo_test.py
==========================================================================
Test cases for two parallelly combined functional unit followed by single
functional unit.

Author : Cheng Tan
  Date : November 29, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..ThreeMulAluShifter         import ThreeMulAluShifter
from ....lib.opt_type             import *
from ....lib.messages             import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType, ConfigType,
                 src0_msgs, src1_msgs, src2_msgs, src3_msgs,
                 config_msgs0, config_msgs1, config_msgs2,
                 sink_msgs ):

    s.src_in0   = TestSrcRTL( DataType,   src0_msgs    )
    s.src_in1   = TestSrcRTL( DataType,   src1_msgs    )
    s.src_in2   = TestSrcRTL( DataType,   src2_msgs    )
    s.src_in3   = TestSrcRTL( DataType,   src3_msgs    )
    s.src_opt0  = TestSrcRTL( ConfigType, config_msgs0 )
    s.src_opt1  = TestSrcRTL( ConfigType, config_msgs1 )
    s.src_opt2  = TestSrcRTL( ConfigType, config_msgs2 )
    s.sink_out  = TestSinkCL( DataType,   sink_msgs    )

    s.dut = FunctionUnit( DataType, ConfigType )

    connect( s.src_in0.send,  s.dut.recv_in0  )
    connect( s.src_in1.send,  s.dut.recv_in1  )
    connect( s.src_in2.send,  s.dut.recv_in2  )
    connect( s.src_in3.send,  s.dut.recv_in3  )
    connect( s.src_opt0.send, s.dut.recv_opt0 )
    connect( s.src_opt1.send, s.dut.recv_opt1 )
    connect( s.src_opt2.send, s.dut.recv_opt2 )
    connect( s.dut.send_out0, s.sink_out.recv )

  def done( s ):
    return s.src_in0.done()  and s.src_in1.done()  and\
           s.src_in2.done()  and s.src_in3.done()  and\
           s.src_opt0.done() and s.src_opt1.done() and\
           s.src_opt2.done() and s.sink_out.done()

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=1000 ):
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

def test_mul_alu_shifter():
  FU = ThreeMulAluShifter
  DataType = mk_data( 16, 1 )
  ConfigType = mk_config( 16 )
  src_in0  = [ DataType(1, 1), DataType(2, 1),  DataType(4, 1) ]
  src_in1  = [ DataType(2, 1), DataType(3, 1),  DataType(3, 1) ]
  src_in2  = [ DataType(1, 1), DataType(3, 1),  DataType(3, 1) ]
  src_in3  = [ DataType(1, 1), DataType(2, 1),  DataType(2, 1) ]
  sink_out = [ DataType(8, 1), DataType(12, 1), DataType(6, 1) ]
  src_opt0 = [ ConfigType(OPT_MUL), ConfigType(OPT_MUL), ConfigType(OPT_MUL) ]
  src_opt1 = [ ConfigType(OPT_ADD), ConfigType(OPT_SUB), ConfigType(OPT_SUB) ]
  src_opt2 = [ ConfigType(OPT_LLS), ConfigType(OPT_LLS), ConfigType(OPT_LRS) ]
  th = TestHarness( FU, DataType, ConfigType, src_in0, src_in1, src_in2, src_in3,
                    src_opt0, src_opt1, src_opt2, sink_out )
  run_sim( th )

