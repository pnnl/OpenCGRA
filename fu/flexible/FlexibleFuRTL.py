"""
==========================================================================
FlexibleFuRTL.py
==========================================================================
A flexible functional unit whose functionality can be parameterized.

Author : Cheng Tan
  Date : Dec 24, 2019

"""

from pymtl3                  import *
from pymtl3.stdlib.ifcs      import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type         import *
from ...fu.single.MemUnitRTL import MemUnitRTL
from ...fu.single.AdderRTL   import AdderRTL

class FlexibleFuRTL( Component ):

  def construct( s, DataType, CtrlType, num_inports, num_outports,
                 data_mem_size, FuList ):

    # Constant
    s.fu_list_size = len( FuList )
    AddrType = mk_bits( clog2( data_mem_size ) )

    # Interface
    s.recv_in    = [ RecvIfcRTL( DataType ) for _ in range( num_inports  ) ]
    s.recv_const = RecvIfcRTL( DataType )
    s.recv_opt   = RecvIfcRTL( CtrlType )
    s.send_out   = [ SendIfcRTL( DataType ) for _ in range( num_outports ) ]

    s.to_mem_raddr   = [ SendIfcRTL( AddrType ) for _ in range( s.fu_list_size ) ]
    s.from_mem_rdata = [ RecvIfcRTL( DataType ) for _ in range( s.fu_list_size ) ]
    s.to_mem_waddr   = [ SendIfcRTL( AddrType ) for _ in range( s.fu_list_size ) ]
    s.to_mem_wdata   = [ SendIfcRTL( DataType ) for _ in range( s.fu_list_size ) ]

    # Components
    s.fu = [ FuList[i]( DataType, CtrlType, num_inports, num_outports,
             data_mem_size ) for i in range( s.fu_list_size ) ]

    # Connection
    for i in range( len( FuList ) ):
      s.to_mem_raddr[i]   //= s.fu[i].to_mem_raddr
      s.from_mem_rdata[i] //= s.fu[i].from_mem_rdata
      s.to_mem_waddr[i]   //= s.fu[i].to_mem_waddr
      s.to_mem_wdata[i]   //= s.fu[i].to_mem_wdata

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
          s.recv_in[j].rdy = b1( 0 )
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
    out_str = ",".join([str(x.msg) for x in s.send_out])
    recv_str = ",".join([str(x.msg) for x in s.recv_in])
    return f'[recv: {recv_str}] {opt_str} (const: {s.recv_const.msg}) ] = [out: {out_str}] (s.recv_opt.rdy: {s.recv_opt.rdy}, {OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]}, send[0].en: {s.send_out[0].en}) '

