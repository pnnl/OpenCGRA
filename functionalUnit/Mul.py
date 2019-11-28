"""
==========================================================================
Mul.py
==========================================================================
Simple generic Muliplier for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from .opt_type import *

class Mul( Component ):

  def construct( s, DataType ):

    # Constant
    OptType = Bits5

    # Interface

    s.recv_in0 = RecvIfcRTL( DataType )
    s.recv_in1 = RecvIfcRTL( DataType )
    s.recv_opt = RecvIfcRTL( DataType )
    s.send_out = SendIfcRTL( DataType )

    @s.update
    def comb_logic():
      if s.recv_opt.msg == OPT_MUL:
        s.send_out.msg = s.recv_in0.msg * s.recv_in1.msg

    @s.update
    def update_signal():
      s.recv_in0.rdy = s.send_out.rdy
      s.recv_in1.rdy = s.send_out.rdy
      s.recv_opt.rdy = s.send_out.rdy
      s.send_out.en  = s.recv_in0.en and s.recv_in1.en and s.recv_opt.en

  def line_trace( s ):
    opt = '?'
    if s.recv_opt.msg == OPT_MUL:
      opt = 'x'
    return f'{s.recv_in0.msg} {opt} {s.recv_in1.msg} = {s.send_out.msg}'
