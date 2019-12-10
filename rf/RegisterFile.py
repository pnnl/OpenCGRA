"""
==========================================================================
RegisterFile.py
==========================================================================
Register file for CGRA tile.

Author : Cheng Tan
  Date : Dec 10, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ..lib.opt_type     import *

class RegisterFile( Component ):

  def construct( s, DataType, nregs ):

    # Interface

    s.recv_data = RecvIfcRTL( DataType )
    s.send_out  = SendIfcRTL( DataType )

260     # Interface
261
262     s.xcel = XcelMinionIfcRTL( ReqType, RespType )
263
264     # Local parameters
265
266     s.data_nbits = max( ReqType.data_nbits, RespType.data_nbits )
267     DataType     = mk_bits( s.data_nbits )
268     s.nregs      = nregs
269
270     # Components
271
272     s.req_q = NormalQueueRTL( ReqType, num_entries=1 )
273     s.wen   = Wire( Bits1 )
274     s.reg_file = RegisterFile( DataType, nregs )(
275       raddr = { 0: s.req_q.deq.msg.addr },
276       rdata = { 0: s.xcel.resp.msg.data },
277       wen   = { 0: s.wen                },
278       waddr = { 0: s.req_q.deq.msg.addr },
279       wdata = { 0: s.req_q.deq.msg.data },
280     )
281     connect( s.xcel.req,            s.req_q.enq           )
282     connect( s.xcel.resp.msg.type_, s.req_q.deq.msg.type_ )

    @s.update
    def update_signal():
      s.recv_in0.rdy = s.send_out.rdy
      s.recv_in1.rdy = s.send_out.rdy
      s.send_out.en  = s.recv_in0.en and s.recv_in1.en

    @s.update
    def comb_logic():
      assert( not (s.recv_in0.msg.predicate==Bits1(1) and\
                   s.recv_in1.msg.predicate==Bits1(1)) )
      if s.recv_in0.msg.predicate == Bits1( 1 ):
        s.send_out.msg = s.recv_in0.msg
      elif s.recv_in1.msg.predicate == Bits1( 1 ):
        s.send_out.msg = s.recv_in1.msg

  def line_trace( s ):
    symbol0 = "#"
    symbol1 = "#"
    if s.recv_in0.msg.predicate == Bits1(1):
      symbol0 = "*"
      symbol1 = " "
    elif s.recv_in1.msg.predicate == Bits1(1):
      symbol0 = " "
      symbol1 = "*"
    return f'[{s.recv_in0.msg} {symbol0}] [{s.recv_in1.msg} {symbol1}] = [{s.send_out.msg}]'
