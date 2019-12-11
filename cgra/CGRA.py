"""
=========================================================================
CGRA.py
=========================================================================

Author : Cheng Tan
  Date : Dec 11, 2019
"""

from pymtl3             import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ..noc.Crossbar     import Crossbar
from ..noc.Channel      import Channel

class CGRA( Component ):

  def construct( s, DataType, RoutingTableType ):

    # Interfaces

    num_inports  = 5
    num_outports = 5
    s.recv_routing = RecvIfcRTL( RoutingTableType )
    s.recv_data = [ RecvIfcRTL( DataType ) for _ in range ( num_inports  ) ]
    s.send_out  = [ SendIfcRTL( DataType ) for _ in range ( num_outports ) ]

    # Components
    s.crossbar = Crossbar( DataType, RoutingTableType, num_inports, num_outports )
    s.channel  = [ Channel ( DataType ) for _ in range( num_inports ) ]

    # Connections
    for i in range( num_inports ):
      s.recv_data[i] //= s.channel[i].recv
      s.channel[i].send //= s.crossbar.recv_data[i]
      s.crossbar.send_out[i] //= s.send_out[i]
    s.recv_routing //= s.crossbar.recv_routing

  # Line trace
  def line_trace( s ):
    channel_str = "|".join([ x.recv.line_trace() for x in s.channel ])
#    out_str = "|".join([ str(x.msg) for x in s.send_out ])
    out_str  = "|".join([ x.line_trace() for x in s.send_out  ])
    return f"{channel_str} [{s.crossbar.recv_routing.msg}] {out_str}"

