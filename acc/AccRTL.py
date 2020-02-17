"""
=========================================================================
Acc.py
=========================================================================

Author : Cheng Tan
  Date : Feb 3, 2020

"""

from pymtl3                 import *
from pymtl3.stdlib.ifcs     import SendIfcRTL, RecvIfcRTL

from ..fu.single.Alu        import Alu
from ..mem.const.ConstQueue import ConstQueue
from ..noc.Channel          import Channel
from ..lib.opt_type         import *

class AccRTL( Component ):

  def construct( s, FuDFG, DataType, CtrlType ): 

    # Interfaces

#    s.recv_data    = [ RecvIfcRTL( DataType ) for _ in range( FuDFG.num_const  ) ]
    s.send_data    = SendIfcRTL( DataType )

    # Components

    s.const_bf = [ ConstQueue( DataType, [ FuDFG.const_list[i] ] )
                   for i in range( FuDFG.num_const  ) ]
    s.elements = [ FuDFG.nodes[i].fu_type( DataType, CtrlType, 2, 2, 10 ) 
                   for i in range( len( FuDFG.nodes ) ) ]
    s.channels = [ Channel( DataType ) for _ in range( FuDFG.num_input ) ]
    s.exit = Bits1( 0 )
    s.exit_element = None

    # Connections
    in_index      = 0
    const_index   = 0
    channel_index = 0
    for node in FuDFG.nodes:
      s.elements[node.id].recv_opt.msg = CtrlType( node.opt )
      for i in range( node.num_input + node.num_const ):
        if node.num_const - i > 0:
          s.elements[node.id].recv_in[i] //= s.const_bf[const_index].send_const
          const_index += 1
        else:
          s.channels[channel_index].recv //=\
              s.elements[node.input_node[i-node.num_const]].send_out[0]
          s.channels[channel_index].send //=\
              s.elements[node.id].recv_in[i]
          print( "node: ", node.id, "; channel: ", channel_index )
          channel_index += 1

      if node.live_out > 0:
        s.exit_element = s.elements[node.id]
        s.elements[node.id].send_out[1] //= s.send_data

    @s.update
    def check_exit():
      if( s.exit == Bits1( 0 ) ):
        s.exit = s.send_data.en

    @s.update_ff
    def enable_opt():
      for node in FuDFG.nodes:
        if( s.exit == Bits1( 1 ) ):
          s.elements[node.id].recv_opt.en <<= Bits1( 0 )
        else:
          s.elements[node.id].recv_opt.en <<= Bits1( 1 )

  # Line trace
  def line_trace( s ):
    return " | ".join(s.elements[x].line_trace() for x in range(len(s.elements)))# + f'send.en: {s.send_data.en}'
#    return str_comp + " || " + " || ".join(s.channels[x].line_trace() for x in range(len(s.channels)))

