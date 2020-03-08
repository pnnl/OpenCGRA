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
                 data_mem_size ):

    # Interface

    s.recv_in    = [ RecvIfcRTL( DataType ) for _ in range( num_inports ) ]
    s.recv_const = RecvIfcRTL( DataType )
    s.recv_opt   = RecvIfcRTL( CtrlType )
    s.send_out   = [ SendIfcRTL( DataType ) for _ in range( num_inports ) ]

    @s.update
    def update_signal():
      for i in range( num_inports ):
        for j in range( num_outports ):
          s.recv_in[i].rdy = s.send_out[j].rdy or s.recv_in[i].rdy

      for j in range( num_outports ):
        s.recv_const.rdy = s.send_out[j].rdy or s.recv_const.rdy
        s.recv_opt.rdy = s.send_out[j].rdy or s.recv_opt.rdy

  def line_trace( s ):
    opt_str = " #"
    if s.send_out[0].en:
      opt_str = OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]
    return f'[{s.recv_in[0].msg}] {opt_str} [{s.recv_in[1].msg} ({s.recv_const.msg}) ] = [{s.send_out[0].msg}]'
