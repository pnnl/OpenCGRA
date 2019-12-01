"""
==========================================================================
Phi.py
==========================================================================
Functional unit Phi for CGRA tile.

Author : Cheng Tan
  Date : November 30, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...ifcs.opt_type   import *

class Phi( Component ):

  def construct( s, DataType ):

    # Interface

    s.recv_in0   = RecvIfcRTL( DataType )
    s.recv_in1   = RecvIfcRTL( DataType )
    s.recv_pred0 = RecvIfcRTL( Bits1    )
    s.recv_pred1 = RecvIfcRTL( Bits1    )
    s.recv_opt   = RecvIfcRTL( DataType )
    s.send_out   = SendIfcRTL( DataType )

    @s.update
    def update_signal():
      s.recv_in0.rdy   = s.send_out.rdy
      s.recv_in1.rdy   = s.send_out.rdy
      s.recv_pred0.rdy = s.send_out.rdy
      s.recv_pred1.rdy = s.send_out.rdy
      s.recv_opt.rdy   = s.send_out.rdy
      s.send_out.en    = s.recv_in0.en   and s.recv_in1.en   and\
                         s.recv_pred0.en and s.recv_pred1.en and\
                         s.recv_opt.en

    @s.update
    def comb_logic():
      assert( not (s.recv_pred0.msg==Bits1(1) and s.recv_pred1.msg==Bits1(1)) )
      if s.recv_pred0.msg == Bits1( 1 ):
        s.send_out.msg = s.recv_in0.msg
      elif s.recv_pred0.msg == Bits1( 1 ):
        s.send_out.msg = s.recv_in1.msg

  def line_trace( s ):
    return f'[{s.recv_in0.msg}({s.recv_pred0.msg})] ? [{s.recv_in1.msg}({s.recv_pred1.msg})] = [{s.send_out.msg}]'
