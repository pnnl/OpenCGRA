"""
==========================================================================
CGRA_test.py
==========================================================================
Test cases for CGRAs with different configurations.

Author : Cheng Tan
  Date : Dec 15, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test              import TestSinkCL
from pymtl3.stdlib.test.test_srcs    import TestSrcRTL

from ...lib.opt_type                 import *
from ...lib.messages                 import *
from ...lib.routing_table            import *

from ...fu.universal.UniversalFu     import UniversalFu
from ..CGRA                          import CGRA

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, DUT, FunctionUnit, DataType, CtrlType,
                 RoutingTableType, width, height,
                 src_opt, src_routing ):

    s.num_tiles = width * height

    s.src_opt     = [ TestSrcRTL( CtrlType, src_opt[i] )
                      for i in range( s.num_tiles ) ]
    s.src_routing = [ TestSrcRTL( RoutingTableType, src_routing[i] )
                      for i in range( s.num_tiles ) ]
#    s.src_data    = [ TestSrcRTL( DataType, src_data[i]  )
#                    for i in range( num_tile_inports  ) ]
#    s.sink_out    = [ TestSinkCL( DataType, sink_out[i] )
#                    for i in range( num_tile_outports ) ]

    s.dut = DUT( FunctionUnit, DataType, CtrlType, RoutingTableType,
                 width, height )

    for i in range( s.num_tiles ):
      connect( s.src_opt[i].send,     s.dut.recv_opt[i]     )
      connect( s.src_routing[i].send, s.dut.recv_routing[i] )

  def done( s ):
    done = True
    for i in range( s.num_tiles  ):
      if not s.src_opt[i].done():
        done = False
        break
    for i in range( s.num_tiles ):
      if not s.src_routing[i].done():
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

def test_cgra_universal():
  num_tile_inports  = 4
  num_tile_outports = 4
  num_xbar_inports  = 6
  num_xbar_outports = 8
  width  = 2
  height = 2
  num_tiles    = width * height
  DUT          = CGRA
  FunctionUnit = UniversalFu
  DataType     = mk_data( 16, 1 )
  CtrlType     = mk_ctrl()
  RoutingTable = mk_routing_table( num_xbar_inports, num_xbar_outports )
  src_opt      = [ [ CtrlType( OPT_INC ), CtrlType( OPT_INC ), CtrlType( OPT_ADD ) ] 
                     for _ in range( num_tiles ) ]
  src_routing  = [ [ RoutingTable([3, 2, 1, 0, 4, 4, 4, 4]),
                     RoutingTable([3, 2, 1, 0, 4, 4, 4, 4]),
                     RoutingTable([3, 2, 1, 0, 4, 4, 4, 4]) ]
                     for _ in range( num_tiles ) ]
#  src_data     = [ [DataType(1, 1), DataType( 1, 1)],
#                   [DataType(2, 1), DataType( 2, 1)],
#                   [DataType(3, 1), DataType( 3, 1)],
#                   [DataType(4, 1), DataType( 4, 1)] ]
#  sink_out     = [ [DataType(4, 1), DataType( 3, 1), DataType( 3, 1)],
#                   [DataType(3, 1), DataType( 3, 1), DataType( 3, 1)],
#                   [DataType(2, 1), DataType( 3, 1)],
#                   [DataType(1, 1), DataType( 7, 1)] ]
  th = TestHarness( DUT, FunctionUnit, DataType, CtrlType, RoutingTable,
                    width, height, src_opt, src_routing )
  run_sim( th )


