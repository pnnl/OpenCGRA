"""
==========================================================================
MemUnit.py
==========================================================================
Scratchpad memory access unit for (the left most) CGRA tiles.

Author : Cheng Tan
  Date : November 29, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs  import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type     import *
from ..basic.Fu          import Fu

class MemUnit( Component ):

  def construct( s, DataType, CtrlType, num_inports, num_outports,
                 data_mem_size ):

    # Constant

    AddrType = mk_bits( clog2( data_mem_size ) )
    # Components

    s.opt_list = [OPT_LD, OPT_STR]

    # Interface

    s.recv_in  = [ RecvIfcRTL( DataType ) for _ in range( num_inports  ) ]
    s.recv_const = RecvIfcRTL( DataType )
    s.recv_opt = RecvIfcRTL( CtrlType )
    s.send_out = [ SendIfcRTL( DataType ) for _ in range( num_outports ) ]

    # Interface to the data sram, need to interface them with 
    # the data memory module in top level
    s.to_mem_raddr   = SendIfcRTL( AddrType )
    s.from_mem_rdata = RecvIfcRTL( DataType )
    s.to_mem_waddr   = SendIfcRTL( AddrType )
    s.to_mem_wdata   = SendIfcRTL( DataType )

    @s.update
    def comb_logic():

      for i in range( 2, num_inports ):
        for j in range( num_outports ):
          s.recv_in[i].rdy = s.send_out[j].rdy or s.recv_in[i].rdy

      for j in range( num_outports ):
        s.recv_const.rdy = s.send_out[j].rdy or s.recv_const.rdy

      for j in range( num_outports ):
        s.recv_opt.rdy = s.send_out[j].rdy or s.recv_opt.rdy

      for j in range( num_outports ):
        for i in range( num_inports ):
          s.send_out[j].en = s.recv_in[i].en or s.send_out[j].en
        s.send_out[j].en = s.send_out[j].en and s.recv_opt.en

      if s.recv_opt.msg.ctrl not in s.opt_list:
        for j in range( 1, num_outports ):
          s.send_out[j].en = b1( 0 )

      s.send_out[0].msg = s.from_mem_rdata.msg
#      s.send_out[0].en = s.from_mem_rdata.en and s.recv_in[0].en and s.recv_in[1].en
      s.to_mem_waddr.en = b1( 0 )
      s.to_mem_wdata.en = b1( 0 )
      if s.recv_opt.msg.ctrl == OPT_LD:
        s.send_out[0].en     = s.from_mem_rdata.en and s.recv_in[0].en
        s.recv_in[0].rdy     = s.to_mem_raddr.rdy
        s.recv_in[1].rdy     = s.from_mem_rdata.rdy
        s.to_mem_raddr.msg   = s.recv_in[0].msg.payload
        s.to_mem_raddr.en    = s.recv_in[0].en
        s.from_mem_rdata.rdy = s.send_out[0].rdy
        s.send_out[0].msg    = s.from_mem_rdata.msg

      elif s.recv_opt.msg.ctrl == OPT_STR:
        s.send_out[0].en   = s.from_mem_rdata.en and s.recv_in[0].en and s.recv_in[1].en
        s.recv_in[0].rdy   = s.to_mem_waddr.rdy
        s.recv_in[1].rdy   = s.to_mem_wdata.rdy 
        s.to_mem_waddr.msg = s.recv_in[0].msg.payload
        s.to_mem_waddr.en  = s.recv_in[0].en
        s.to_mem_wdata.msg = s.recv_in[1].msg
        s.to_mem_wdata.en  = s.recv_in[1].en
        s.send_out[0].en   = b1( 0 )
        s.send_out[0].msg  = s.from_mem_rdata.msg

  def line_trace( s ):
    out_msg = s.send_out[0].msg
    if s.send_out[0].en == b1( 0 ):
      out_msg = 'xxxx.x'
    return f'[{s.recv_in[0].msg}] {OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]} [{s.recv_in[1].msg}] = [{out_msg}]'

