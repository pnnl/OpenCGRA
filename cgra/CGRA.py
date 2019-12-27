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
from ..lib.opt_type     import *
from ..mem.data.DataMem import DataMem

class CGRA( Component ):

  def construct( s, FunctionUnit, FuList, DataType, CtrlType,
                 width, height, num_ctrl ):
    print( "\nconstructing ", width, "x", height, " CGRA ...\n" )
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
    s.data_mem = DataMem( DataType, height, height )

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

      if i % width == 0:
        s.tile[i].to_mem_raddr   //= s.data_mem.recv_raddr[i//width]
        s.tile[i].from_mem_rdata //= s.data_mem.send_rdata[i//width]
        s.tile[i].to_mem_waddr   //= s.data_mem.recv_waddr[i//width]
        s.tile[i].to_mem_wdata   //= s.data_mem.recv_wdata[i//width]
      else:
        s.tile[i].to_mem_raddr.rdy //= 0
        s.tile[i].from_mem_rdata.en //= 0
        s.tile[i].from_mem_rdata.msg //= DataType(0, 0)
        s.tile[i].to_mem_waddr.rdy //= 0
        s.tile[i].to_mem_wdata.rdy //= 0

#    @s.update
#    def connect_data_mem():
#      # connect to the data memory
#      for i in range( s.num_tiles ):
##        for j in range( s.tile[i].element.fu_list_size ):
#        j = 0
#        print("1 opt_list: ", s.tile[i].element.fu[j].opt_list)
#        if i % width == 0:
#          if OPT_LD  in s.tile[i].element.fu[j].opt_list or\
#             OPT_STR in s.tile[i].element.fu[j].opt_list:
#            print("2 opt_list: ", s.tile[i].element.fu[j].opt_list)
#            for p in range( height ):
#              s.tile[i].element.fu[0].to_mem_raddr.rdy = s.data_mem.recv_raddr[i//width].rdy
#              s.data_mem.recv_raddr[i//width].msg = s.tile[i].element.fu[0].to_mem_raddr.msg
#              s.data_mem.recv_raddr[i//width].en = s.tile[i].element.fu[0].to_mem_raddr.en
#              s.tile[i].element.fu[0].from_mem_rdata.msg = s.data_mem.send_rdata[i//width].msg
#              s.tile[i].element.fu[0].from_mem_rdata.en = s.data_mem.send_rdata[i//width].en
#              s.data_mem.send_rdata[i//width].rdy = s.tile[i].element.fu[0].from_mem_rdata.rdy
#              s.tile[i].element.fu[0].to_mem_waddr.rdy = s.data_mem.recv_waddr[i//width].rdy
#              s.data_mem.recv_waddr[i//width].msg = s.data_mem.recv_waddr[i//width].msg
#              s.data_mem.recv_waddr[i//width].en = s.data_mem.recv_waddr[i//width].en
#              s.tile[i].element.fu[0].to_mem_wdata.rdy = s.data_mem.recv_wdata[i//width].rdy
#              s.data_mem.recv_wdata[i//width].msg = s.tile[i].element.fu[0].to_mem_wdata.msg
#              s.data_mem.recv_wdata[i//width].en = s.tile[i].element.fu[0].to_mem_wdata.en

  # Line trace
  def line_trace( s ):
    return "||".join([ x.element.line_trace() for x in s.tile ])

