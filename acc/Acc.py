"""
=========================================================================
Acc.py
=========================================================================

Author : Cheng Tan
  Date : Feb 3, 2020

"""

from pymtl3                   import *
from pymtl3.stdlib.ifcs       import SendIfcRTL, RecvIfcRTL

from ..fu.single.Alu    import Alu
from ..noc.Channel        import Channel

class Acc( Component ):

  def construct( s, FuDFG, DataType, CtrlType ): 

    # Interfaces

    s.recv_data    = [ RecvIfcRTL( DataType ) for _ in range ( 4 ) ]
    s.send_data    = [ SendIfcRTL( DataType ) for _ in range ( 1 ) ]

#    s.recv_opt     = [ RecvIfcRTL( CtrlType ) for _ in range ( 3 ) ]

    # Components

    s.elements = [ FuDFG.elements[i].fu_type( DataType, CtrlType, 2, 1, 10 ) 
                 for i in range(len( FuDFG.elements)) ]
    s.channels = [ Channel( DataType ) for _ in range( 2 ) ]

    # Connections
    in_index = 0
    channel_index = 0
    for e in FuDFG.elements:
      print( e.id )
      s.elements[e.id].recv_opt.msg = CtrlType( e.opt )
      s.elements[e.id].recv_opt.en = s.elements[e.id].recv_in[0].en
      if e.input == []:
        s.elements[e.id].recv_in[0] //= s.recv_data[in_index]
        in_index += 1
        s.elements[e.id].recv_in[1] //= s.recv_data[in_index]
        in_index += 1
      else:

        s.elements[e.input[0]].send_out[0] //= s.channels[channel_index].recv
        s.channels[channel_index].send     //= s.elements[e.id].recv_in[0]
        channel_index += 1
        s.elements[e.input[1]].send_out[0] //= s.channels[channel_index].recv
        s.channels[channel_index].send     //= s.elements[e.id].recv_in[1]
        channel_index += 1

      if e.output == []:
        s.elements[e.id].send_out[0] //= s.send_data[0]

  # Line trace
  def line_trace( s ):
    return "|".join(s.elements[x].line_trace() for x in range(len(s.elements)))

