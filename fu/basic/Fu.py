"""
==========================================================================
Alu.py
==========================================================================
Simple generic functional unit for CGRA tile.

Author : Cheng Tan
  Date : November 27, 2019
"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *

class Fu( Component ):

  def construct( s, DataType, CtrlType, num_inports, num_outports,
                 data_mem_size=4 ):

    AddrType = mk_bits( clog2( data_mem_size ) )
    s.const_zero = DataType(0, 0)
    FuInType = mk_bits( clog2( num_inports + 1 ) )

    # Interface

    s.recv_in    = [ RecvIfcRTL( DataType ) for _ in range( num_inports ) ]
    s.recv_const = RecvIfcRTL( DataType )
    s.recv_opt   = RecvIfcRTL( CtrlType )
    s.send_out   = [ SendIfcRTL( DataType ) for _ in range( num_outports ) ]

    # Redundant interfaces for MemUnit
    s.to_mem_raddr   = SendIfcRTL( AddrType )
    s.from_mem_rdata = RecvIfcRTL( DataType )
    s.to_mem_waddr   = SendIfcRTL( AddrType )
    s.to_mem_wdata   = SendIfcRTL( DataType )

#    # For pick input register, basic FU normally has 2 inputs,
#    # if more inputs are required, they should be added inside
#    # specific inherit module.
#    in0 = FuInType( 0 )
#    in1 = FuInType( 0 )

    @s.update
    def update_signal():
#      if s.recv_opt.en:
#        in0 = s.recv_opt.msg.fu_in[0] - FuInType( 1 )
#        in1 = s.recv_opt.msg.fu_in[1] - FuInType( 1 )
#        s.recv_in[in0].rdy = b1( 1 )
#        s.recv_in[in1].rdy = b1( 1 )

#      for i in range( num_inports ):
#        s.recv_in[i].rdy = b1( 1 ) if s.recv_opt.msg.fu_in[i] > FuInType( 0 ) else b1( 0 )
#        for j in range( num_outports ):
#          s.recv_in[i].rdy = s.send_out[j].rdy or s.recv_in[i].rdy

      for j in range( num_outports ):
        s.recv_const.rdy = s.send_out[j].rdy or s.recv_const.rdy
        s.recv_opt.rdy = s.send_out[j].rdy or s.recv_opt.rdy

    @s.update
    def update_mem():
      s.to_mem_waddr.en    = b1( 0 )
      s.to_mem_wdata.en    = b1( 0 )
      s.to_mem_wdata.msg   = s.const_zero
      s.to_mem_waddr.msg   = AddrType( 0 )
      s.to_mem_raddr.msg   = AddrType( 0 )
      s.to_mem_raddr.en    = b1( 0 )
      s.from_mem_rdata.rdy = b1( 0 )

  def line_trace( s ):
    opt_str = " #"
#    if s.send_out[0].en:
#      opt_str = OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]
#    return f'[{s.recv_in[0].msg}] {opt_str} [{s.recv_in[1].msg} ({s.recv_const.msg}) ] = [{s.send_out[0].msg}]'
    if s.recv_opt.en:
      opt_str = OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]
    out_str = ",".join([str(x.msg) for x in s.send_out])
    recv_str = ",".join([str(x.msg) for x in s.recv_in])
    return f'[recv: {recv_str}] {opt_str} (const: {s.recv_const.msg}) ] = [out: {out_str}] (s.recv_opt.rdy: {s.recv_opt.rdy}, {OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]}, send[0].en: {s.send_out[0].en}) '
