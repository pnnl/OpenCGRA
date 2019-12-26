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
from ..lib.mem_param    import *

class CGRA( Component ):

  def construct( s, FunctionUnit, FuList, DataType, CtrlType,
                 width, height, num_ctrl ):

    # Constant
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    s.num_tiles = width * height
    s.num_mesh_ports = 4
    AddrType = mk_bits( clog2( CTRL_MEM_SIZE ) )

    # Interfaces

    s.recv_waddr = [ RecvIfcRTL( AddrType )  for _ in range( s.num_tiles ) ]
    s.recv_wopt  = [ RecvIfcRTL( CtrlType )  for _ in range( s.num_tiles ) ]

    # Components

    s.tile = [ Tile( FunctionUnit, FuList, DataType, CtrlType, num_ctrl ) 
               for _ in range( s.num_tiles ) ]
#    s.data_mem = 

    # Connections

    for i in range( s.num_tiles):
      s.recv_waddr[i] //= s.tile[i].recv_waddr
      s.recv_wopt[i]  //= s.tile[i].recv_wopt

      if i // width > 0:
        s.tile[i].send_data[SOUTH] //= s.tile[i-width].recv_data[NORTH]

      if i // width < height - 1:
        s.tile[i].send_data[NORTH] //= s.tile[i+width].recv_data[SOUTH]

      if i % width > 0:
        s.tile[i].send_data[WEST] //= s.tile[i-1].recv_data[EAST]

      if i % width < width - 1:
        s.tile[i].send_data[EAST] //= s.tile[i+1].recv_data[WEST]

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

