"""
==========================================================================
Tile_test.py
==========================================================================
Test cases for Tile.

Author : Cheng Tan
  Date : Dec 11, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..Tile                       import Tile
from ...fu.single.Alu             import Alu
from ...lib.opt_type              import *
from ...lib.messages              import *
from ...lib.routing_table         import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, DUT, FunctionUnit, DataType, ConfigType,
                 RoutingTableType, num_tile_inports, num_tile_outports,
                 src_data, src_opt, src_routing, sink_out ):

    s.num_tile_inports  = num_tile_inports
    s.num_tile_outports = num_tile_outports

    s.src_opt      = TestSrcRTL( ConfigType, src_opt )
    s.src_routing  = TestSrcRTL( RoutingTableType, src_routing )
    s.src_data     = [ TestSrcRTL( DataType, src_data[i]  )
                     for i in range( num_tile_inports  ) ]
    s.sink_out     = [ TestSinkCL( DataType, sink_out[i] )
                     for i in range( num_tile_outports ) ]

    s.dut = DUT( FunctionUnit, DataType, ConfigType, RoutingTableType )

    connect( s.src_opt.send,     s.dut.recv_opt     )
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

def test_cgra():
  num_tile_inports  = 4
  num_tile_outports = 4
  num_xbar_inports  = 6
  num_xbar_outports = 8
  DUT = Tile
  FunctionUnit = Alu
  DataType     = mk_data( 16, 1 )
  ConfigType   = mk_config( 16 )
  RoutingTable = mk_routing_table( num_xbar_inports, num_xbar_outports )
  src_opt      = [ ConfigType( OPT_ADD ),
                   ConfigType( OPT_SUB ),
                   ConfigType( OPT_NAH ) ]
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
  th = TestHarness( DUT, FunctionUnit, DataType, ConfigType,
                    RoutingTable, num_tile_inports, num_tile_outports,
                    src_data, src_opt, src_routing, sink_out )
  run_sim( th )

