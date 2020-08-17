"""
==========================================================================
FlexibleFu.py
==========================================================================
A flexible functional unit whose functionality can be parameterized.

Author : Cheng Tan
  Date : Dec 24, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs  import SendIfcRTL, RecvIfcRTL
from ...lib.opt_type     import *
from ...fu.single.MemUnit            import MemUnit
from ...fu.single.Alu    import Alu

class FlexibleFu( Component ):

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

    print("check fu recv num: ", num_inports)

    s.to_mem_raddr   = [ SendIfcRTL( AddrType ) for _ in range( s.fu_list_size ) ]
    s.from_mem_rdata = [ RecvIfcRTL( DataType ) for _ in range( s.fu_list_size ) ]
    s.to_mem_waddr   = [ SendIfcRTL( AddrType ) for _ in range( s.fu_list_size ) ]
    s.to_mem_wdata   = [ SendIfcRTL( DataType ) for _ in range( s.fu_list_size ) ]

#    s.to_mem_raddr   = SendIfcRTL( AddrType )
#    s.from_mem_rdata = RecvIfcRTL( DataType )
#    s.to_mem_waddr   = SendIfcRTL( AddrType )
#    s.to_mem_wdata   = SendIfcRTL( DataType )

    # Components

    s.fu = [ FuList[i]( DataType, CtrlType, num_inports, num_outports,
             data_mem_size ) for i in range( s.fu_list_size ) ]

    # Connection

#    has_one_mem_unit = False
    for i in range( len( FuList ) ):
#      if hasattr(s.fu[i], 'to_mem_raddr'):
#        has_one_mem_unit = True
#      if FuList[i] == MemUnit:
#        has_one_mem_unit = True
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
          s.fu[i].recv_in[j].msg = s.recv_in[j].msg
          s.fu[i].recv_in[j].en  = s.recv_in[j].en
          s.recv_in[j].rdy       = s.fu[i].recv_in[j].rdy or s.recv_in[j].rdy

        # send_out connection
        for j in range( num_outports ):
          if s.fu[i].send_out[j].en:
            s.send_out[j].msg = s.fu[i].send_out[j].msg
            s.send_out[j].en  = s.fu[i].send_out[j].en
          s.fu[i].send_out[j].rdy = s.send_out[j].rdy
#      print("in flexible s.fu[2].recv_opt.en: ", s.fu[2].recv_opt.en, "; s.recv_opt.rdy: ", s.recv_opt.rdy, "; s.fu[2].recv_in[0].en: ", s.fu[2].recv_in[0].en, "; s.recv_in[0].rdy: ", s.recv_in[0].rdy, "; s.recv_in[1].rdy: ", s.recv_in[1].rdy, "; ", s)

  def line_trace( s ):
    opt_str = " #"
    if s.recv_opt.en:
      opt_str = OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]
    out_str = ",".join([str(x.msg) for x in s.send_out])
    return f'[{s.recv_in[0].msg}] {opt_str} [{s.recv_in[1].msg} ({s.recv_const.msg}) ] = [{s.send_out[0].msg}] (s.recv_opt.rdy: {s.recv_opt.rdy}, {OPT_SYMBOL_DICT[s.recv_opt.msg.ctrl]}, send[0].en: {s.send_out[0].en}) (recv: {s.recv_in[0].msg}, {s.recv_in[1].msg}, {s.recv_in[2].msg}, {s.recv_in[3].msg})'

