"""
==========================================================================
Equal.py
==========================================================================
Functional unit for performing comparison.

Author : Cheng Tan
  Date : December 2, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ...ifcs.opt_type   import *

class Equal( Component ):

  def construct( s, DataType ):

    # Interface

    s.recv_data = RecvIfcRTL( DataType )
    s.recv_ref  = RecvIfcRTL( DataType )
    # send will be broadcasted to multiple dest
    s.send_out  = SendIfcRTL( DataType )
    s.send_pred = SendIfcRTL( Bits1    )

    @s.update
    def update_signal():
      s.recv_data.rdy = s.send_out.rdy
      s.recv_ref.rdy  = s.send_out.rdy
      s.send_out.en   = s.recv_in0.en   and s.recv_in1.en   and\
                        s.recv_pred0.en and s.recv_pred1.en
      s.send_pred.en  = s.recv_in0.en   and s.recv_in1.en   and\
                        s.recv_pred0.en and s.recv_pred1.en

    @s.update
    def comb_logic():
      s.send_out.msg  = s.recv_data.msg
      s.send_pred.msg = s.recv_comp.msg

