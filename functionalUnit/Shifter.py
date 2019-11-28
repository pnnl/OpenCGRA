"""
==========================================================================
Alu.py
==========================================================================
Simple generic Shifter for CGRA tile.

Author : Cheng Tan
  Date : November 28, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from .opt_type import *

class Shifter( Component ):

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
      if s.recv_opt.msg == OPT_LLS:
        s.send_out.msg = s.recv_in0.msg << s.recv_in1.msg
      elif s.recv_opt.msg == OPT_LRS:
        s.send_out.msg = s.recv_in0.msg >> s.recv_in1.msg

    @s.update
    def update_signal():
      s.recv_in0.rdy = s.send_out.rdy
      s.recv_in1.rdy = s.send_out.rdy
      s.recv_opt.rdy = s.send_out.rdy
      s.send_out.en  = s.recv_in0.en and s.recv_in1.en and s.recv_opt.en

  def line_trace( s ):
    opt = '?'
    if s.recv_opt.msg == OPT_LLS:
      opt = '<<'
    elif s.recv_opt.msg == OPT_LRS:
      opt = '>>'
    return f'{s.recv_in0.msg} {opt} {s.recv_in1.msg} = {s.send_out.msg}'
