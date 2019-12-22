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

  def construct( s, DataType, CtrlType, MemSize = 8 ):

    # Components

    AddrType = mk_bits( clog2( MemSize ) )

    # Interface

    s.recv_in0  = RecvIfcRTL( DataType )
    s.recv_in1  = RecvIfcRTL( DataType )
    s.recv_in2  = RecvIfcRTL( DataType )
    s.recv_in3  = RecvIfcRTL( DataType )

    s.recv_opt  = RecvIfcRTL( CtrlType )
    s.send_out0 = SendIfcRTL( DataType )
    s.send_out1 = SendIfcRTL( DataType )

    # Interface to the data sram, need to interface them with 
    # the data memory module in top level
    s.to_mem_raddr   = SendIfcRTL( AddrType )
    s.from_mem_rdata = RecvIfcRTL( DataType )
    s.to_mem_waddr   = SendIfcRTL( AddrType )
    s.to_mem_wdata   = SendIfcRTL( DataType )

    @s.update
    def update_signal():
      s.recv_in2.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_in3.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_opt.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.send_out1.en = s.recv_in0.en   or s.recv_in1.en   or\
                       s.recv_in2.en   or s.recv_in3.en   or s.recv_opt.en

    @s.update
    def comb_logic():
      s.send_out0.msg = s.from_mem_rdata.msg
      s.send_out0.en = s.from_mem_rdata.en and s.recv_in0.en and s.recv_in1.en
      s.to_mem_waddr.en = b1( 0 )
      s.to_mem_wdata.en = b1( 0 )
      if s.recv_opt.msg.ctrl == OPT_LD:
        s.recv_in0.rdy  = s.to_mem_raddr.rdy
        s.recv_in1.rdy  = s.from_mem_rdata.rdy
        s.to_mem_raddr.msg = s.recv_in0.msg.payload
        s.to_mem_raddr.en = s.recv_in0.en
        s.from_mem_rdata.rdy = s.send_out0.rdy
        s.send_out0.msg = s.from_mem_rdata.msg

      elif s.recv_opt.msg.ctrl == OPT_STR:
        s.recv_in0.rdy = s.to_mem_waddr.rdy
        s.recv_in1.rdy = s.to_mem_wdata.rdy 
        s.to_mem_waddr.msg = s.recv_in0.msg.payload
        s.to_mem_waddr.en  = s.recv_in0.en
        s.to_mem_wdata.msg = s.recv_in1.msg
        s.to_mem_wdata.en  = s.recv_in1.en
        s.send_out0.en = b1( 0 )
        s.send_out0.msg = s.from_mem_rdata.msg

  def line_trace( s ):
    out_msg = s.send_out0.msg
    if s.send_out0.en == b1( 0 ):
      out_msg = 'xxxx.x'
    return f'[{s.recv_in0.msg}] {OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]} [{s.recv_in1.msg}] = [{out_msg}]'
