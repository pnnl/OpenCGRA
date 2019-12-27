"""
==========================================================================
CGRA_test.py
==========================================================================
Test cases for CGRAs with different configurations.

Author : Cheng Tan
  Date : Dec 15, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ...lib.opt_type              import *
from ...lib.messages              import *
from ...lib.mem_param             import *

from ...fu.flexible.FlexibleFu    import FlexibleFu
from ...fu.single.Alu             import Alu
from ...fu.single.MemUnit         import MemUnit
from ..CGRA                       import CGRA

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, DUT, FunctionUnit, FuList, DataType, CtrlType, #RoutingTableType,
                 width, height, src_opt, ctrl_waddr):#, src_routing ):

    s.num_tiles = width * height
    AddrType = mk_bits( clog2( CTRL_MEM_SIZE ) )

    s.src_opt     = [ TestSrcRTL( CtrlType, src_opt[i] )
                      for i in range( s.num_tiles ) ]
    s.ctrl_waddr  = [ TestSrcRTL( AddrType, ctrl_waddr[i] )
                      for i in range( s.num_tiles ) ]
#    s.src_routing = [ TestSrcRTL( RoutingTableType, src_routing[i] )
#                      for i in range( s.num_tiles ) ]

    s.dut = DUT( FunctionUnit, FuList, DataType, CtrlType,# RoutingTableType,
                 width, height, len( src_opt ) )

    for i in range( s.num_tiles ):
      connect( s.src_opt[i].send,     s.dut.recv_wopt[i]  )
      connect( s.ctrl_waddr[i].send,  s.dut.recv_waddr[i] )
#      connect( s.src_routing[i].send, s.dut.recv_route[i] )

  def done( s ):
    done = True
    for i in range( s.num_tiles  ):
      if not s.src_opt[i].done():
        done = False
        break
#    for i in range( s.num_tiles ):
#      if not s.src_routing[i].done():
#        done = False
#        break
    return done

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

def test_cgra_universal():
  num_tile_inports  = 4
  num_tile_outports = 4
  num_xbar_inports  = 6
  num_xbar_outports = 8
  width  = 2
  height = 2
  RouteType = mk_bits( clog2( num_xbar_inports + 1 ) )
  AddrType = mk_bits( clog2( CTRL_MEM_SIZE ) )
  num_tiles    = width * height
  DUT          = CGRA
  FunctionUnit = FlexibleFu
  FuList      = [Alu, MemUnit]
  DataType     = mk_data( 16, 1 )
  CtrlType     = mk_ctrl( num_xbar_inports, num_xbar_outports )
#  RtTabType    = mk_routing_table( num_xbar_inports, num_xbar_outports )
  src_opt      = [ [ CtrlType( OPT_INC, [ 
                     RouteType(3), RouteType(2), RouteType(1), RouteType(0),
                     RouteType(4), RouteType(4), RouteType(4), RouteType(4)] ),
                     CtrlType( OPT_INC, [
                     RouteType(3),RouteType(2), RouteType(1), RouteType(0),
                     RouteType(4), RouteType(4), RouteType(4), RouteType(4)] ),
                     CtrlType( OPT_ADD, [
                     RouteType(3),RouteType(2), RouteType(1), RouteType(0),
                     RouteType(4), RouteType(4), RouteType(4), RouteType(4)] ) ] 
                     for _ in range( num_tiles ) ]
  ctrl_waddr   = [ [ AddrType( 0 ), AddrType( 1 ), AddrType( 2 ) ] 
                     for _ in range( num_tiles ) ]
#  src_route    = [ [ RtTabType([3, 2, 1, 0, 4, 4, 4, 4]),
#                     RtTabType([3, 2, 1, 0, 4, 4, 4, 4]),
#                     RtTabType([3, 2, 1, 0, 4, 4, 4, 4]) ]
#                     for _ in range( num_tiles ) ]
#  src_data     = [ [DataType(1, 1), DataType( 1, 1)],
#                   [DataType(2, 1), DataType( 2, 1)],
#                   [DataType(3, 1), DataType( 3, 1)],
#                   [DataType(4, 1), DataType( 4, 1)] ]
#  sink_out     = [ [DataType(4, 1), DataType( 3, 1), DataType( 3, 1)],
#                   [DataType(3, 1), DataType( 3, 1), DataType( 3, 1)],
#                   [DataType(2, 1), DataType( 3, 1)],
#                   [DataType(1, 1), DataType( 7, 1)] ]
  th = TestHarness( DUT, FunctionUnit, FuList, DataType, CtrlType,
                    width, height, src_opt, ctrl_waddr )
  run_sim( th )

