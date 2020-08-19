"""
==========================================================================
Sel.py
==========================================================================
Functional unit Select for CGRA tile.

Author : Cheng Tan
  Date : May 23, 2020

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type    import *

class Sel( Component ):

  def construct( s, DataType, CtrlType, num_inports, num_outports,
                 data_mem_size=4 ):

    AddrType = mk_bits( clog2( data_mem_size ) )
    s.const_zero = DataType(0, 0)
    s.true = DataType(1, 1)
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

#    @s.update
#    def update_signal():

    @s.update
    def update_mem():
      s.to_mem_waddr.en    = b1( 0 )
      s.to_mem_wdata.en    = b1( 0 )
      s.to_mem_wdata.msg   = s.const_zero
      s.to_mem_waddr.msg   = AddrType( 0 )
      s.to_mem_raddr.msg   = AddrType( 0 )
      s.to_mem_raddr.en    = b1( 0 )
      s.from_mem_rdata.rdy = b1( 0 )

    @s.update
    def comb_logic():

      # For pick input register, Selector needs at least 3 inputs
      in0 = FuInType( 0 )
      in1 = FuInType( 0 )
      in2 = FuInType( 0 )
      for i in range( num_inports ):
        s.recv_in[i].rdy = b1( 0 )
      if s.recv_opt.en and s.recv_opt.msg.fu_in[0] != FuInType( 0 ) and\
                           s.recv_opt.msg.fu_in[1] != FuInType( 0 ) and\
                           s.recv_opt.msg.fu_in[2] != FuInType( 0 ):
        in0 = s.recv_opt.msg.fu_in[0] - FuInType( 1 )
        in1 = s.recv_opt.msg.fu_in[1] - FuInType( 1 )
        in2 = s.recv_opt.msg.fu_in[2] - FuInType( 1 )
        s.recv_in[in0].rdy = b1( 1 )
        s.recv_in[in1].rdy = b1( 1 )
        s.recv_in[in2].rdy = b1( 1 )

#      for i in range( num_inports ):
#        s.recv_in[i].rdy = b1( 1 ) if s.recv_opt.msg.fu_in[i] > FuInType( 0 ) else b1( 0 )
#        for j in range( num_outports ):
#          s.recv_in[i].rdy = s.send_out[j].rdy or s.recv_in[i].rdy

      for j in range( num_outports ):
        s.recv_const.rdy = s.send_out[j].rdy or s.recv_const.rdy
        s.recv_opt.rdy = s.send_out[j].rdy or s.recv_opt.rdy


      for j in range( num_outports ):
        s.send_out[j].en = s.recv_opt.en# and s.send_out[j].rdy and s.recv_in[0].en
      if s.recv_opt.msg.ctrl == OPT_SEL:
        if s.recv_in[in0].msg.payload == s.true.payload:
          s.send_out[0].msg = s.recv_in[in1].msg
        else:
          s.send_out[0].msg = s.recv_in[in2].msg
      else:
        for j in range( num_outports ):
          s.send_out[j].en = b1( 0 )

  def line_trace( s ):
#    symbol = "#"
#    symbol = "T"
#    if s.recv_in[0].msg.predicate == Bits1(1):
#      symbol = "T" if s.recv_in[0].msg.payload == s.true.payload else "F"
#    return f'[{s.recv_in[1].msg}] {symbol} [{s.recv_in[2].msg}] = [{s.send_out[0].msg}]'
    opt_str = " #"
    if s.recv_opt.en:
      opt_str = OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]
    out_str = ",".join([str(x.msg) for x in s.send_out])
    recv_str = ",".join([str(x.msg) for x in s.recv_in])
    return f'[recv: {recv_str}] {opt_str} (const: {s.recv_const.msg}) ] = [out: {out_str}] (s.recv_opt.rdy: {s.recv_opt.rdy}, {OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]}, send[0].en: {s.send_out[0].en}) '
