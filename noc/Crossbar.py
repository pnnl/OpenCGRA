"""
=========================================================================
Crossbar.py
=========================================================================

Author : Cheng Tan
  Date : Dec 8, 2019
"""

from pymtl3             import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL

class Crossbar( Component ):

  def construct( s, DataType, ConfigType,
                 num_inports = 5, num_outports = 5 ):

    # Interface

#    s.recv_opt  = RecvIfcRTL( ConfigType )
    s.recv_data = [ RecvIfcRTL( DataType ) for _ in range ( num_inports  ) ]
    s.send_out  = [ SendIfcRTL( DataType ) for _ in range ( num_outports ) ]
#    s.pos  = InPort( PositionType )

    # Routing logic
    @s.update
    def update_signal():
      for i in range( num_inports ):
        s.recv_data[i].rdy = s.send_out[i].rdy
        s.send_out[i].en   = s.recv_data[i].en
        s.send_out[i].msg  = s.recv_data[i].msg

  # Line trace
  def line_trace( s ):
    out_str = "|".join([ str(x.msg) for x in s.send_out ])
    return f"{out_str}"

