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

from ..Alu                        import Alu
from ..Shifter                    import Shifter
from ..Mul                        import Mul
from ..Logic                      import Logic
from ....mem.const.ConstQueue     import ConstQueue
from ....lib.opt_type             import *
from ....lib.messages             import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType, ConfigType, num_inports,
                 num_outports, data_mem_size, src0_msgs, src1_msgs,
                 src_const, ctrl_msgs, sink_msgs ):

    s.src_in0  = TestSrcRTL( DataType,   src0_msgs )
    s.src_in1  = TestSrcRTL( DataType,   src1_msgs )
    s.src_opt  = TestSrcRTL( ConfigType, ctrl_msgs )
    s.sink_out = TestSinkCL( DataType,   sink_msgs )

    s.const_queue = ConstQueue( DataType, src_const )
    s.dut = FunctionUnit( DataType, ConfigType, num_inports, num_outports,
                          data_mem_size )

    connect( s.src_in0.send,    s.dut.recv_in[0] )
    connect( s.src_in1.send,    s.dut.recv_in[1] )
    connect( s.dut.recv_const,  s.const_queue.send_const )
    connect( s.src_opt.send,    s.dut.recv_opt   )
    connect( s.dut.send_out[0], s.sink_out.recv  )

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

def test_alu():
  FU = Alu
  DataType     = mk_data( 16, 1 )
  ConfigType   = mk_ctrl()
  data_mem_size = 8
  num_inports  = 2
  num_outports = 1
  src_in0      = [ DataType(1, 1), DataType(7, 1), DataType(4, 1) ]
  src_in1      = [ DataType(2, 1), DataType(3, 1), DataType(1, 1) ]
  src_const    = [ DataType(5, 1), DataType(0, 0), DataType(7, 1) ]
  sink_out     = [ DataType(6, 1), DataType(4, 1), DataType(11, 1) ]
  src_opt      = [ ConfigType( OPT_ADD_CONST ),
                   ConfigType( OPT_SUB ),
                   ConfigType( OPT_ADD_CONST ) ]
  th = TestHarness( FU, DataType, ConfigType, num_inports, num_outports,
                    data_mem_size, src_in0, src_in1, src_const, src_opt, sink_out )
  run_sim( th )

def test_logic():
  FU = Logic
  DataType = mk_data( 16, 1 )
  ConfigType = mk_ctrl()
  num_inports  = 2
  num_outports = 1
  data_mem_size = 8
  src_in0   = [ DataType(1, 1), DataType(2, 1), DataType(4, 1), DataType(1, 1)  ]
  src_in1   = [ DataType(2, 1), DataType(3, 1), DataType(3, 1), DataType(2, 1)  ]
  src_const = [ DataType(5, 1), DataType(0, 0), DataType(7, 1) ]
  sink_out  = [ DataType(3, 1), DataType(2, 1), DataType(0xfffb, 1), DataType(3, 1) ]
  src_opt   = [ ConfigType( OPT_OR  ), ConfigType( OPT_AND ),
                ConfigType( OPT_NOT ), ConfigType( OPT_XOR ) ]
  th = TestHarness( FU, DataType, ConfigType, num_inports, num_outports,
                    data_mem_size, src_in0, src_in1, src_const, src_opt, sink_out )
  run_sim( th )

def test_shifter():
  FU = Shifter
  DataType = mk_data( 16, 1 )
  ConfigType = mk_ctrl()
  num_inports  = 2
  num_outports = 1
  data_mem_size = 8
  src_in0   = [ DataType(1, 1), DataType(2, 1),  DataType(4, 1) ]
  src_in1   = [ DataType(2, 1), DataType(3, 1),  DataType(1, 1) ]
  src_const = [ DataType(2, 1), DataType(3, 1),  DataType(1, 1) ]
  sink_out  = [ DataType(4, 1), DataType(16, 1), DataType(2, 1) ]
  src_opt   = [ ConfigType( OPT_LLS ),
               ConfigType( OPT_LLS ),
               ConfigType( OPT_LRS ) ]
  th = TestHarness( FU, DataType, ConfigType, num_inports, num_outports,
                    data_mem_size, src_in0, src_in1, src_const, src_opt, sink_out )
  run_sim( th )

def test_mul():
  FU = Mul
  DataType = mk_data( 16, 1 )
  ConfigType = mk_ctrl()
  num_inports  = 2
  num_outports = 1
  data_mem_size = 8
  src_in0   = [ DataType(1, 1), DataType(2, 1), DataType(4, 1)  ]
  src_in1   = [ DataType(2, 1), DataType(3, 1), DataType(3, 1)  ]
  src_const = [ DataType(2, 1), DataType(3, 1), DataType(3, 1)  ]
  sink_out  = [ DataType(2, 1), DataType(6, 1), DataType(12, 1) ]
  src_opt   = [ ConfigType( OPT_MUL ),
                ConfigType( OPT_MUL ),
                ConfigType( OPT_MUL ) ]
  th = TestHarness( FU, DataType, ConfigType, num_inports, num_outports,
                    data_mem_size, src_in0, src_in1, src_const, src_opt, sink_out )
  run_sim( th )

