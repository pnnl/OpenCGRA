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

  def construct( s, DataType, RoutingTableType,
                 num_inports = 5, num_outports = 5 ):

    # Interface

    s.recv_routing = RecvIfcRTL( RoutingTableType )
    s.recv_data = [ RecvIfcRTL( DataType ) for _ in range ( num_inports  ) ]
    s.send_out  = [ SendIfcRTL( DataType ) for _ in range ( num_outports ) ]
#    s.pos  = InPort( PositionType )

    # Routing logic
    @s.update
    def update_signal():
      out_rdy = b1(0)
      for i in range( num_outports ):
        in_dir  = s.recv_routing.msg.outport[i]
        out_rdy = out_rdy | s.send_out[i].rdy
        s.recv_data[in_dir].rdy = s.send_out[i].rdy
        s.send_out[i].en        = s.recv_data[in_dir].en
        s.send_out[i].msg       = s.recv_data[in_dir].msg
      s.recv_routing.rdy = out_rdy

  # Line trace
  def line_trace( s ):
    recv_str = "|".join([ str(x.msg) for x in s.recv_data ])
    out_str  = "|".join([ str(x.msg) for x in s.send_out  ])
    return f"{recv_str} [{s.recv_routing.msg}] {out_str}"

