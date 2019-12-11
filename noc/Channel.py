#=========================================================================
# Channel.py
#=========================================================================
# channel module for connecting crossbar to form network. This simple
# channel has a queue/register to hold the data.
#
# Author : Cheng Tan
#   Date : Dec 11, 2019

from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL

class Channel( Component ):
  def construct(s, PacketType ):

    # Interface
    s.recv  = RecvIfcRTL( PacketType )
    s.send  = SendIfcRTL( PacketType )

    # Component

    s.register = NormalQueueRTL( PacketType, 2 )

    # Connections

    s.recv.rdy //= s.register.enq.rdy

    @s.update
    def process():
      s.register.enq.msg = s.recv.msg
      s.register.enq.en  = s.recv.en and s.register.enq.rdy

      s.send.msg         = s.register.deq.msg
      s.send.en          = s.send.rdy and s.register.deq.rdy
      s.register.deq.en  = s.send.en

  def line_trace( s ):
    trace = '>' + s.register.line_trace() + '>'
    return f"{s.recv.msg}({trace}){s.send.msg}"

