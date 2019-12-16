"""
=========================================================================
CGRA.py
=========================================================================

Author : Cheng Tan
  Date : Dec 15, 2019
"""

from pymtl3             import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ..noc.Crossbar     import Crossbar
from ..noc.Channel      import Channel
from ..tile.Tile        import Tile

class CGRA( Component ):

  def construct( s, FunctionUnit, DataType, CtrlType, RoutingTableType,
                 width, height ):

    # Constant
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    s.num_tiles = width * height
    s.num_mesh_ports = 4

    # Interfaces

    s.recv_opt = [ RecvIfcRTL( CtrlType )         
                   for _ in range( s.num_tiles ) ]
    s.recv_routing = [ RecvIfcRTL( RoutingTableType )
                       for _ in range( s.num_tiles ) ]

    # Components

    s.tile = [ Tile( FunctionUnit, DataType, CtrlType, RoutingTableType ) 
               for _ in range( s.num_tiles ) ]

    # Connections

    for i in range( s.num_tiles):
      s.recv_opt[i]     //= s.tile[i].recv_opt
      s.recv_routing[i] //= s.tile[i].recv_routing

      if i // width > 0:
        s.tile[i].send_data[SOUTH] //= s.tile[i-width].recv_data[NORTH]

      if i // width < height - 1:
        s.tile[i].send_data[NORTH] //= s.tile[i+width].recv_data[SOUTH]

      if i % width > 0:
        s.tile[i].send_data[WEST] //= s.tile[i-1].recv_data[EAST]

      if i % width < width - 1:
        s.tile[i].send_data[EAST] //= s.tile[i+1].recv_data[WEST]

      # Connect the unused ports
      # FIXME: for now we hackily ground the payload field so that pymtl
      # won't complain about net need driver.

      if i // width == 0:
        s.tile[i].send_data[SOUTH].rdy //= 0
        s.tile[i].recv_data[SOUTH].en  //= 0
        s.tile[i].recv_data[SOUTH].msg //= DataType( 0, 0 )

      if i // width == height - 1:
        s.tile[i].send_data[NORTH].rdy  //= 0
        s.tile[i].recv_data[NORTH].en   //= 0
        s.tile[i].recv_data[NORTH].msg  //= DataType( 0, 0 )

      if i % width == 0:
        s.tile[i].send_data[WEST].rdy  //= 0
        s.tile[i].recv_data[WEST].en   //= 0
        s.tile[i].recv_data[WEST].msg  //= DataType( 0, 0 )

      if i % width == width - 1:
        s.tile[i].send_data[EAST].rdy  //= 0
        s.tile[i].recv_data[EAST].en   //= 0
        s.tile[i].recv_data[EAST].msg  //= DataType( 0, 0 )

  # Line trace
  def line_trace( s ):
    return "||".join([ x.element.line_trace() for x in s.tile ])

