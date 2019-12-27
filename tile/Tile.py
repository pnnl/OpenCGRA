"""
=========================================================================
Tile.py
=========================================================================

Author : Cheng Tan
  Date : Dec 11, 2019
"""

from pymtl3                   import *
from pymtl3.stdlib.ifcs       import SendIfcRTL, RecvIfcRTL
from ..noc.Crossbar           import Crossbar
from ..noc.Channel            import Channel
from ..mem.ctrl.CtrlMem       import CtrlMem
from ..fu.flexible.FlexibleFu import FlexibleFu

class Tile( Component ):

  def construct( s, Fu, FuList, DataType, CtrlType, 
                 ctrl_mem_size, data_mem_size, num_ctrl ):

    # Constant

    num_xbar_inports  = 6
    num_xbar_outports = 8
    num_fu_inports    = 4
    num_fu_outports   = 2
    num_mesh_ports    = 4

    CtrlAddrType = mk_bits( clog2( ctrl_mem_size ) )
    DataAddrType = mk_bits( clog2( data_mem_size ) )

    # Interfaces

    s.recv_data    = [ RecvIfcRTL( DataType ) for _ in range ( num_mesh_ports ) ]
    s.send_data    = [ SendIfcRTL( DataType ) for _ in range ( num_mesh_ports ) ]

    # Ctrl
    s.recv_waddr = RecvIfcRTL( CtrlAddrType )
    s.recv_wopt  = RecvIfcRTL( CtrlType )
    # Data
    s.to_mem_raddr   = SendIfcRTL( DataAddrType )
    s.from_mem_rdata = RecvIfcRTL( DataType )
    s.to_mem_waddr   = SendIfcRTL( DataAddrType )
    s.to_mem_wdata   = SendIfcRTL( DataType )

    # Components

    s.element  = FlexibleFu( FuList, DataType, CtrlType, num_fu_inports,
                             num_fu_outports, data_mem_size )
    s.crossbar = Crossbar( DataType, CtrlType, num_xbar_inports,
                           num_xbar_outports )
    s.ctrl_mem = CtrlMem( CtrlType, ctrl_mem_size, num_ctrl )
    s.channel  = [ Channel ( DataType ) for _ in range( num_xbar_outports ) ]

    # Connections

    # Ctrl
    s.ctrl_mem.recv_waddr //= s.recv_waddr
    s.ctrl_mem.recv_ctrl  //= s.recv_wopt 
    # Data
    s.to_mem_raddr   //= s.element.to_mem_raddr
    s.from_mem_rdata //= s.element.from_mem_rdata
    s.to_mem_waddr   //= s.element.to_mem_waddr
    s.to_mem_wdata   //= s.element.to_mem_wdata

    for i in range( num_mesh_ports ):
      s.recv_data[i] //= s.crossbar.recv_data[i]

    for i in range( num_xbar_outports ):
      s.crossbar.send_data[i] //= s.channel[i].recv

    for i in range( num_mesh_ports ):
      s.channel[i].send //= s.send_data[i]

    for i in range( num_fu_inports ):
      s.channel[num_mesh_ports+i].send //= s.element.recv_in[i]

    for i in range( num_fu_outports ):
      s.element.send_out[i] //= s.crossbar.recv_data[num_mesh_ports+i]

    @s.update
    def update_opt():
      s.element.recv_opt.msg  = s.ctrl_mem.send_ctrl.msg
      s.crossbar.recv_opt.msg = s.ctrl_mem.send_ctrl.msg
      s.element.recv_opt.en  = s.ctrl_mem.send_ctrl.en
      s.crossbar.recv_opt.en = s.ctrl_mem.send_ctrl.en
      s.ctrl_mem.send_ctrl.rdy = s.element.recv_opt.rdy and s.crossbar.recv_opt.rdy

  # Line trace
  def line_trace( s ):

    recv_str    = "|".join([ str(x.msg) for x in s.recv_data ])
    channel_recv_str = "|".join([ str(x.recv.msg) for x in s.channel ])
    channel_send_str = "|".join([ str(x.send.msg) for x in s.channel ])
#    out_str = "|".join([ str(x.msg) for x in s.send_out ])
    out_str  = "|".join([ x.line_trace() for x in s.send_data ])
    return f"{recv_str} => [{s.crossbar.recv_opt.msg}] ({s.element.line_trace()}) => {channel_recv_str} => {channel_send_str} => {out_str}"

