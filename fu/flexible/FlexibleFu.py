"""
==========================================================================
FlexibleFu.py
==========================================================================
A flexible functional unit whose functionality can be parameterized.

Author : Cheng Tan
  Date : Dec [2]4, [2][0][1]9

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs  import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type     import *

from ..single.Alu        import Alu
from ..single.Shifter    import Shifter
from ..single.Mul        import Mul
from ..single.Logic      import Logic

class FlexibleFu( Component ):

  def construct( s, FuList, DataType, CtrlType, num_inports, num_outports,
                 data_mem_size ):

    # Constant

    s.fu_list_size = len( FuList )
    AddrType = mk_bits( clog2( data_mem_size ) )

    # Interface

    s.recv_in    = [ RecvIfcRTL( DataType ) for _ in range( num_inports  ) ]
    s.recv_const = RecvIfcRTL( DataType )
    s.recv_opt   = RecvIfcRTL( CtrlType )
    s.send_out   = [ SendIfcRTL( DataType ) for _ in range( num_outports ) ]

    s.to_mem_raddr   = SendIfcRTL( AddrType )
    s.from_mem_rdata = RecvIfcRTL( DataType )
    s.to_mem_waddr   = SendIfcRTL( AddrType )
    s.to_mem_wdata   = SendIfcRTL( DataType )

    # Components

    s.fu = [ FuList[i]( DataType, CtrlType, num_inports, num_outports,
             data_mem_size ) for i in range( s.fu_list_size ) ]

    # Connection

    for i in range( s.fu_list_size ):
#      s.fu[i].recv_const //= s.recv_const
#      s.fu[i].recv_const.msg = s.recv_const.msg
#      s.fu[i].recv_const.en  = s.recv_const.en
      if OPT_LD in s.fu[i].opt_list:
        s.to_mem_raddr   //= s.fu[i].to_mem_raddr
        s.from_mem_rdata //= s.fu[i].from_mem_rdata
        s.to_mem_waddr   //= s.fu[i].to_mem_waddr
        s.to_mem_wdata   //= s.fu[i].to_mem_wdata

    @s.update
    def comb_logic():

      for j in range( num_outports ):
        s.send_out[j].en  = b1( 0 )

      for i in range( s.fu_list_size ):

        # const connection
        s.fu[i].recv_const.msg = s.recv_const.msg
        s.fu[i].recv_const.en  = s.recv_const.en
        s.recv_const.rdy = s.recv_const.rdy or s.fu[i].recv_const.rdy

        # opt connection
        s.fu[i].recv_opt.msg = s.recv_opt.msg
        s.fu[i].recv_opt.en  = s.recv_opt.en
        s.recv_opt.rdy       = s.fu[i].recv_opt.rdy or s.recv_opt.rdy

        # recv_in connection
        for j in range( num_inports ):
          s.fu[i].recv_in[j].msg = s.recv_in[j].msg
          s.fu[i].recv_in[j].en  = s.recv_in[j].en
          s.recv_in[j].rdy       = s.fu[i].recv_in[j].rdy or s.recv_in[j].rdy
         
        # send_out connection
        for j in range( num_outports ):
          if s.fu[i].send_out[j].en:
            s.send_out[j].msg = s.fu[i].send_out[j].msg
            s.send_out[j].en  = s.fu[i].send_out[j].en
          s.fu[i].send_out[j].rdy = s.send_out[j].rdy

  def line_trace( s ):
    opt_str = " #"
    if s.recv_opt.en:
      opt_str = OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]
    return f'[{s.recv_in[0].msg}] {opt_str} [{s.recv_in[1].msg} ({s.recv_const.msg}) ] = [{s.send_out[0].msg}]'

