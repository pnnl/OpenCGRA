"""
==========================================================================
CGRA_test.py
==========================================================================
Test cases for CGRA.

Author : Cheng Tan
  Date : Dec 11, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..CGRA                       import CGRA
from ...lib.opt_type              import *
from ...lib.messages              import *
from ...lib.routing_table         import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, DUT, DataType, RoutingTableType,
                 num_inports, num_outports,
                 src_data, src_routing, sink_out ):

    s.num_inports  = num_inports
    s.num_outports = num_outports

    s.src_routing  = TestSrcRTL( RoutingTableType, src_routing )
    s.src_data     = [ TestSrcRTL( DataType, src_data[i]  )
                     for i in range( num_inports  ) ]
    s.sink_out     = [ TestSinkCL( DataType, sink_out[i] )
                     for i in range( num_outports ) ]

    s.dut = DUT( DataType, RoutingTableType )

    for i in range( num_inports ):
      connect( s.src_data[i].send, s.dut.recv_data[i] )
      connect( s.dut.send_out[i],  s.sink_out[i].recv )
    connect( s.src_routing.send,     s.dut.recv_routing )

  def done( s ):
    done = True
    for i in range( s.num_inports  ):
      if not s.src_data[i].done():
        done = False
        break
    for i in range( s.num_outports ):
      if not s.sink_out[i].done():
        done = False
        break
    return done

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=100 ):
  test_harness.elaborate()
  test_harness.apply( SimulationPass )
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
  num_inports  = 5
  num_outports = 5
  DUT = CGRA
  DataType     = mk_data( 16, 1 )
  RoutingTable = mk_routing_table( num_inports, num_outports )
  src_routing  = [ RoutingTable( [0, 1, 2, 3, 4] ),
                   RoutingTable( [1, 0, 2, 3, 1] ),
                   RoutingTable( [4, 3, 2, 1, 0] ) ]
  src_data     = [ [DataType(1, 1), DataType( 1, 1)],
                   [DataType(2, 1), DataType( 2, 1)],
                   [DataType(3, 1), DataType( 3, 1)],
                   [DataType(4, 1), DataType( 4, 1)],
                   [DataType(5, 1), DataType( 5, 1)] ]
  sink_out     = [ [DataType(2, 1), DataType( 5, 1)],
                   [DataType(1, 1), DataType( 4, 1)],
                   [DataType(3, 1), DataType( 3, 1)],
                   [DataType(4, 1), DataType( 2, 1)],
                   [DataType(2, 1), DataType( 1, 1)] ]
  th = TestHarness( DUT, DataType, RoutingTable, num_outports, num_inports,
                    src_data, src_routing, sink_out )
  run_sim( th )

