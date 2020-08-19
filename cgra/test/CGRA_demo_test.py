"""
==========================================================================
CGRA_demo_test.py
==========================================================================
Test cases for CGRAs with pseudo data/config memory.

Author : Cheng Tan
  Date : Dec 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ...lib.opt_type              import *
from ...lib.messages              import *
from ...lib.ctrl_helper           import *

from ...fu.flexible.FlexibleFu    import FlexibleFu
from ...fu.single.Alu             import Alu
from ...fu.single.Mul             import Mul
from ...fu.single.Logic           import Logic
from ...fu.single.Comp            import Comp
from ...fu.single.Branch          import Branch
from ...fu.single.Phi             import Phi
from ...fu.single.Shifter         import Shifter
from ...fu.single.MemUnit         import MemUnit
from ..PseudoCGRA                 import PseudoCGRA

import os

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, DUT, FunctionUnit, FuList, DataType, CtrlType,
                 width, height, ctrl_mem_size, data_mem_size,
                 src_opt, preload_data, preload_const ):

    s.num_tiles = width * height
    AddrType = mk_bits( clog2( ctrl_mem_size ) )

    s.dut = DUT( FunctionUnit, FuList, DataType, CtrlType, width, height,
                 ctrl_mem_size, data_mem_size, len( src_opt ), src_opt,
                 preload_data, preload_const )

#  def done( s ):
#    done = True
#    for i in range( s.num_tiles  ):
#      if not s.src_opt[i].done():
#        done = False
#        break
#    return done

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=7 ):
  test_harness.elaborate()
  test_harness.apply( SimulationPass() )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print()
  print( "{}:{}".format( ncycles, test_harness.line_trace() ))
  while ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{}:{}".format( ncycles, test_harness.line_trace() ))

  # Check timeout
#  assert ncycles < max_cycles

  print( '=' * 70 )
  print( test_harness.dut.data_mem.sram )

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

def test_CGRA_4x4_fir():
  target_json = "config_fir.json"
  script_dir  = os.path.dirname(__file__)
  file_path   = os.path.join( script_dir, target_json )

  II                = 4
  num_tile_inports  = 4
  num_tile_outports = 4
  num_xbar_inports  = 6
  num_xbar_outports = 8
  num_fu_in         = 4
  ctrl_mem_size     = 8
  width             = 4
  height            = 4
  num_tiles         = width * height
  RouteType         = mk_bits( clog2( num_xbar_inports + 1 ) )
  AddrType          = mk_bits( clog2( ctrl_mem_size ) )
  num_tiles         = width * height
  ctrl_mem_size     = II
  data_mem_size     = 10
  num_fu_in         = 4
  DUT               = PseudoCGRA
  FunctionUnit      = FlexibleFu
#  FuList            = [Alu, Mul, MemUnit, Shifter, Logic, Phi, Comp, Branch]
  FuList            = [MemUnit, Alu, Mul, Shifter, Logic, Phi, Comp, Branch]
  DataType          = mk_data( 16, 1 )
  CtrlType          = mk_ctrl( num_fu_in, num_xbar_inports, num_xbar_outports )
  cgra_ctrl         = CGRACtrl( file_path, CtrlType, RouteType, width, height,
                                num_fu_in, num_xbar_outports, II )
  src_opt           = cgra_ctrl.get_ctrl()
#  print( src_opt )
  preload_data  = [ DataType( 3, 1 ) ] * data_mem_size
  preload_const = [ [ DataType( 1, 1 ) ] * II ] * num_tiles


                    src_opt, preload_data, preload_const )
  run_sim( th )

#def test_CGRA():
#
#  # Attribute of CGRA
#  width     = 4
#  height    = 4
#  DUT       = CGRA
#  FuList    = [ ALU ]
#  DataType  = mk_data( 16 )
#  CtrlType  = mk_ctrl()
#  cgra_ctrl = CGRACtrl( "control_signal.json", CtrlType )
#
#  # FL golden reference
#  fu_dfg    = DFG( "dfg.json" )
#  data_mem  = acc_fl( fu_dfg, DataType, CtrlType )
#
#  th = TestHarness( DUT, FuList, cgra_ctrl, DataType, CtrlType,
#                    width, height, data_mem ) 
#  run_sim( th )

