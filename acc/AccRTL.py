"""
=========================================================================
AccRTL.py
=========================================================================

Author : Cheng Tan
  Date : Feb 3, 2020

"""

from pymtl3                 import *
from pymtl3.stdlib.ifcs     import SendIfcRTL, RecvIfcRTL

from ..fu.single.Alu        import Alu
from ..mem.const.ConstQueue import ConstQueue
from ..noc.Channel          import Channel
from ..noc.Multicaster      import Multicaster
from ..mem.data.PseudoDataMem import PseudoDataMem
from ..lib.opt_type         import *

class AccRTL( Component ):

  def construct( s, FuDFG, DataType, CtrlType ): 

    # Interfaces

#    s.recv_data    = [ RecvIfcRTL( DataType ) for _ in range( FuDFG.num_const  ) ]
    s.send_data    = SendIfcRTL( DataType )

    # Components

    preload_data = [ DataType( 1, 1 ), DataType( 1, 1 ), DataType( 1, 1 ),
                     DataType( 1, 1 ), DataType( 1, 1 ), DataType( 1, 1 ),
                     DataType( 1, 1 ), DataType( 1, 1 ), DataType( 1, 1 ),
                     DataType( 1, 1 ) ]
    s.data_mem = PseudoDataMem( DataType, 10, 2, 2, preload_data )
    s.const_bf = [ ConstQueue( DataType, [ FuDFG.const_list[i] ] )
                   for i in range( FuDFG.num_const  ) ]
    s.elements = [ FuDFG.nodes[i].fu_type( DataType, CtrlType, 2, 2, 10 ) 
                   for i in range( len( FuDFG.nodes ) ) ]
    s.mcasters = [ Multicaster( DataType, node.num_output[0] )
                   for node in FuDFG.nodes ]
    s.channels = [ Channel( DataType, FuDFG.layer_diff_list[i] ) for i in range( FuDFG.num_input ) ]
    s.exit = Bits1( 0 )
    s.exit_element = None

    # Connections
    in_index       = 0
    const_index    = 0
    channel_index  = 0
    mem_port_index = 0

    for node in FuDFG.nodes:
#      for i in range( node.num_output[0] ):
      s.elements[node.id].send_out[0] //= s.mcasters[node.id].recv

      if OPT_LD in s.elements[node.id].opt_list:
        s.data_mem.recv_raddr[mem_port_index] //= s.elements[node.id].to_mem_raddr
        s.data_mem.send_rdata[mem_port_index] //= s.elements[node.id].from_mem_rdata
        s.data_mem.recv_waddr[mem_port_index] //= s.elements[node.id].to_mem_waddr
        s.data_mem.recv_wdata[mem_port_index] //= s.elements[node.id].to_mem_wdata
        mem_port_index += 1

    for node in FuDFG.nodes:
      s.elements[node.id].recv_opt.msg = CtrlType( node.opt )

      for i in range( node.num_const ):
        s.elements[node.id].recv_in[i] //= s.const_bf[const_index].send_const
        const_index += 1

      for i in range( node.num_input ):
        s.channels[channel_index].recv //=\
            s.mcasters[node.input_node[i]].send[FuDFG.nodes[node.input_node[i]].current_output_index]
        FuDFG.nodes[node.input_node[i]].current_output_index += 1
        s.channels[channel_index].send //=\
            s.elements[node.id].recv_in[i+node.num_const]
#        print( "node: ", node.id, "; channel: ", channel_index )
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
    str_out = " | ".join(s.elements[x].line_trace() + s.mcasters[x].line_trace() for x in range(len(s.elements)))# + f'send.en: {s.send_data.en}'
    return str_out + "\n----------------------------------------------------------------"
#    return str_comp + " || " + " || ".join(s.channels[x].line_trace() for x in range(len(s.channels)))

