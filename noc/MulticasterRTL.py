"""
=========================================================================
MulticasterRTL.py
=========================================================================

Author : Cheng Tan
  Date : Feb 16, 2019
"""

from pymtl3             import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL

from ..lib.opt_type     import *

class MulticasterRTL( Component ):

  def construct( s, DataType, num_outports = 2 ):

    # Constand
    if num_outports == 0:
      num_outports = 1

    # Interface

    s.recv = RecvIfcRTL( DataType )
    s.send = [ SendIfcRTL( DataType ) for _ in range ( num_outports ) ]

    @s.update
    def update_signal():
      s.recv.rdy = s.send[0].rdy
      for i in range( num_outports ):
        s.recv.rdy = s.recv.rdy and s.send[i].rdy
        s.send[i].en       = s.recv.en
        s.send[i].msg      = s.recv.msg

  # Line trace
  def line_trace( s ):
    recv_str = s.recv.msg
    out_str  = "|".join([ str(x.msg) for x in s.send ])
    return f"{recv_str} -> {out_str}({s.recv.rdy},{s.send[0].en})"

