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

  def construct( s, DataType, ConfigType ):

    # Interface

    s.recv_in0  = RecvIfcRTL( DataType   )
    s.recv_in1  = RecvIfcRTL( DataType   )
    s.recv_in2  = RecvIfcRTL( DataType   )
    s.recv_in3  = RecvIfcRTL( DataType   )
    s.recv_opt  = RecvIfcRTL( ConfigType )
    s.send_out0 = SendIfcRTL( DataType   )
    s.send_out1 = SendIfcRTL( DataType   )

    @s.update
    def update_signal():
      s.recv_in0.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_in1.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_in2.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_in3.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.recv_opt.rdy = s.send_out0.rdy or s.send_out1.rdy
      s.send_out0.en = s.recv_in0.en   or s.recv_in1.en   or\
                       s.recv_in2.en   or s.recv_in3.en   or s.recv_opt.en
      s.send_out1.en = s.recv_in0.en   or s.recv_in1.en   or\
                       s.recv_in2.en   or s.recv_in3.en   or s.recv_opt.en

  def line_trace( s ):
    return f'[{s.recv_in0.msg}] {OPT_SYMBOL_DICT[s.recv_opt.msg.config]} [{s.recv_in1.msg}] = [{s.send_out0.msg}]'
