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

  def construct( s, DataType ):

    # Interface

    s.recv_in0 = RecvIfcRTL( DataType )
    s.recv_in1 = RecvIfcRTL( DataType )
    s.recv_opt = RecvIfcRTL( DataType )
    s.send_out = SendIfcRTL( DataType )

    @s.update
    def update_signal():
      s.recv_in0.rdy = s.send_out.rdy
      s.recv_in1.rdy = s.send_out.rdy
      s.recv_opt.rdy = s.send_out.rdy
      s.send_out.en  = s.recv_in0.en and s.recv_in1.en and s.recv_opt.en

  def line_trace( s ):
    return f'[{s.recv_in0.msg}] {OPT_SYMBOL_DICT[s.recv_opt.msg]} [{s.recv_in1.msg}] = [{s.send_out.msg}]'
