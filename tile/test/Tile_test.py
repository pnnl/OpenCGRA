"""
==========================================================================
Tile_test.py
==========================================================================
Test cases for Tile.

Author : Cheng Tan
  Date : Dec 11, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test              import TestSinkCL
from pymtl3.stdlib.test.test_srcs    import TestSrcRTL

from ..Tile                          import Tile
from ...lib.opt_type                 import *
from ...lib.messages                 import *
from ...lib.routing_table            import *

from ...fu.single.Alu                import Alu
from ...fu.triple.ThreeMulAluShifter import ThreeMulAluShifter
from ...fu.universal.UniversalFu     import UniversalFu

from ...mem.ctrl.CtrlMem             import CtrlMem

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, DUT, FunctionUnit, DataType, CtrlType, AddrType,
                 RoutingTableType, num_tile_inports, num_tile_outports,
                 ctrl_mem_size, src_data, src_opt,
                 opt_waddr, src_routing, sink_out ):

    s.num_tile_inports  = num_tile_inports
    s.num_tile_outports = num_tile_outports

    AddrType       = mk_bits( clog2( ctrl_mem_size ) )

    s.src_opt      = TestSrcRTL( CtrlType, src_opt )
    s.opt_waddr    = TestSrcRTL( AddrType, opt_waddr )
    s.src_routing  = TestSrcRTL( RoutingTableType, src_routing )
    s.src_data     = [ TestSrcRTL( DataType, src_data[i]  )
                     for i in range( num_tile_inports  ) ]
    s.sink_out     = [ TestSinkCL( DataType, sink_out[i] )
                     for i in range( num_tile_outports ) ]

    s.dut = DUT( FunctionUnit, DataType, CtrlType, RoutingTableType,
                 ctrl_mem_size, len(src_opt) )

    connect( s.src_opt.send,     s.dut.recv_wopt    )
    connect( s.opt_waddr.send,   s.dut.recv_waddr   )
    connect( s.src_routing.send, s.dut.recv_routing )

    for i in range( num_tile_inports ):
      connect( s.src_data[i].send, s.dut.recv_data[i] )
    for i in range( num_tile_outports ):
      connect( s.dut.send_data[i],  s.sink_out[i].recv )

  def done( s ):
    done = True
#    for i in range( s.num_inports  ):
#      if not s.src_data[i].done():
#        done = False
#        break
    for i in range( s.num_tile_outports ):
      if not s.sink_out[i].done():
        done = False
        break
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

def test_tile_alu():
  num_tile_inports  = 4
  num_tile_outports = 4
  num_xbar_inports  = 6
  num_xbar_outports = 8
  ctrl_mem_size     = 8

  AddrType     = mk_bits( clog2( ctrl_mem_size ) )
  DUT          = Tile
  FunctionUnit = Alu
  DataType     = mk_data( 16, 1 )
  CtrlType     = mk_ctrl()
  RoutingTable = mk_routing_table( num_xbar_inports, num_xbar_outports )
  src_opt      = [ CtrlType( OPT_ADD ),
                   CtrlType( OPT_SUB ) ]
  opt_waddr    = [ AddrType( 0 ), AddrType( 1 ) ]
  src_routing  = [ RoutingTable( [3, 2, 1, 0, 3, 2, 1, 0] ),
                   RoutingTable( [2, 2, 2, 4, 3, 0, 0, 0] ),
                   RoutingTable( [4, 4, 1, 1, 0, 0, 0, 0] ) ]
  src_data     = [ [DataType(1, 1), DataType( 1, 1)],
                   [DataType(2, 1), DataType( 2, 1)],
                   [DataType(3, 1), DataType( 3, 1)],
                   [DataType(4, 1), DataType( 4, 1)] ]
  sink_out     = [ [DataType(4, 1), DataType( 3, 1), DataType( 3, 1)],
                   [DataType(3, 1), DataType( 3, 1), DataType( 3, 1)],
                   [DataType(2, 1), DataType( 3, 1)],
                   [DataType(1, 1), DataType( 7, 1)] ]
  th = TestHarness( DUT, FunctionUnit, DataType, CtrlType, AddrType,
                    RoutingTable, num_tile_inports, num_tile_outports,
                    ctrl_mem_size, src_data, src_opt,
                    opt_waddr, src_routing, sink_out )
  run_sim( th )

def test_tile_triple():
  num_tile_inports  = 4
  num_tile_outports = 4
  num_xbar_inports  = 6
  num_xbar_outports = 8
  ctrl_mem_size     = 8

  AddrType     = mk_bits( clog2( ctrl_mem_size ) )
  DUT = Tile
  FunctionUnit = ThreeMulAluShifter
  DataType     = mk_data( 16, 1 )
  CtrlType     = mk_ctrl()
  RoutingTable = mk_routing_table( num_xbar_inports, num_xbar_outports )
  src_opt      = [ CtrlType( OPT_MUL_SUB_LLS ) ]
  opt_waddr    = [ AddrType( 0 ) ]
  src_routing  = [ RoutingTable( [3, 2, 1, 0, 0, 1, 3, 1] ),
                   RoutingTable( [4, 0, 1, 2, 0, 0, 0, 0] ) ]
  src_data     = [ [DataType(1, 1), DataType( 1, 1)],
                   [DataType(2, 1), DataType( 2, 1)],
                   [DataType(3, 1), DataType( 3, 1)],
                   [DataType(4, 1), DataType( 4, 1)] ]
  sink_out     = [ [DataType(4, 1), DataType( 8, 1)],
                   [DataType(3, 1), DataType( 1, 1)],
                   [DataType(2, 1), DataType( 2, 1)],
                   [DataType(1, 1), DataType( 3, 1)] ]
  th = TestHarness( DUT, FunctionUnit, DataType, CtrlType, AddrType,
                    RoutingTable, num_tile_inports, num_tile_outports,
                    ctrl_mem_size, src_data, src_opt, opt_waddr, src_routing,
                    sink_out )
  run_sim( th )

def test_tile_universal():
  num_tile_inports  = 4
  num_tile_outports = 4
  num_xbar_inports  = 6
  num_xbar_outports = 8
  ctrl_mem_size     = 8

  AddrType     = mk_bits( clog2( ctrl_mem_size ) )
  DUT = Tile
  FunctionUnit = UniversalFu
  DataType     = mk_data( 16, 1 )
  CtrlType     = mk_ctrl()
  RoutingTable = mk_routing_table( num_xbar_inports, num_xbar_outports )
  src_opt      = [ CtrlType( OPT_ADD ),
                   CtrlType( OPT_SUB ) ]
  opt_waddr    = [ AddrType( 0 ), AddrType( 1 ) ]
  src_routing  = [ RoutingTable( [3, 2, 1, 0, 3, 2, 1, 0] ),
                   RoutingTable( [2, 2, 2, 4, 3, 0, 0, 0] ),
                   RoutingTable( [4, 4, 1, 1, 0, 0, 0, 0] ) ]
  src_data     = [ [DataType(1, 1), DataType( 1, 1)],
                   [DataType(2, 1), DataType( 2, 1)],
                   [DataType(3, 1), DataType( 3, 1)],
                   [DataType(4, 1), DataType( 4, 1)] ]
  sink_out     = [ [DataType(4, 1), DataType( 3, 1), DataType( 3, 1)],
                   [DataType(3, 1), DataType( 3, 1), DataType( 3, 1)],
                   [DataType(2, 1), DataType( 3, 1)],
                   [DataType(1, 1), DataType( 7, 1)] ]
  th = TestHarness( DUT, FunctionUnit, DataType, CtrlType, AddrType,
                    RoutingTable, num_tile_inports, num_tile_outports,
                    ctrl_mem_size, src_data, src_opt, opt_waddr, src_routing,
                    sink_out )
  run_sim( th )


