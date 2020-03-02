"""
=========================================================================
Crossbar.py
=========================================================================

Author : Cheng Tan
  Date : Dec 8, 2019
"""

from pymtl3             import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL

from ..lib.opt_type     import *

class Crossbar( Component ):

  def construct( s, DataType, CtrlType,
                 num_inports = 5, num_outports = 5 ):

    OutType     = mk_bits( clog2( num_inports + 1 ) )

    # Interface

    s.recv_opt  = RecvIfcRTL( CtrlType )
    s.recv_data = [ RecvIfcRTL( DataType ) for _ in range ( num_inports  ) ]
    s.send_data = [ SendIfcRTL( DataType ) for _ in range ( num_outports ) ]

    # TODO: should include position information or not?
    # s.pos  = InPort( PositionType )

    # Routing logic
    @s.update
    def update_signal():
      out_rdy = b1( 0 )
      if s.recv_opt.msg.ctrl != OPT_START:
        for i in range( num_outports ):
          in_dir  = s.recv_opt.msg.outport[i]
          out_rdy = out_rdy | s.send_data[i].rdy
          if in_dir > OutType( 0 ):
            in_dir = in_dir - OutType( 1 )
            s.recv_data[in_dir].rdy = s.send_data[i].rdy
            s.send_data[i].en       = s.recv_data[in_dir].en
            s.send_data[i].msg      = s.recv_data[in_dir].msg
      else:
        for i in range( num_outports ):
          s.send_data[i].en = b1( 0 )
      s.recv_opt.rdy = out_rdy

  # Line trace
  def line_trace( s ):
    recv_str = "|".join([ str(x.msg) for x in s.recv_data ])
    out_str  = "|".join([ str(x.msg) for x in s.send_data ])
    return f"{recv_str} [{s.recv_opt.msg}] {out_str}"

