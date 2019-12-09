"""
==========================================================================
routing_table.py
==========================================================================
Routing table used for routing across crossbars.

Convention: The fields/constructor arguments should appear in the order
            of [ inports_nbits, outports_nbits ]

Author : Cheng Tan
  Date : Dec 9, 2019
"""
from pymtl3 import *

#=========================================================================
# Generic routing table
#=========================================================================

def mk_routing_table( num_inports = 5, num_outports = 5, prefix="routing_table" ):

  InportsType   = mk_bits( num_inports  )
  OutportsType  = mk_bits( num_outports )

  new_name = f"{prefix}_{num_inports}_{num_outports}"

  def str_func( s ):
    out_str = ''
    for i in range( num_outports ):
      if i != 0:
        out_str += '|'
      out_str += str(s.outport[i])
    return f"{out_str}"

  field_dict = {}
#  for i in range( num_outports ):
  field_dict[ 'outport' ] = [ InportsType for _ in range( num_outports ) ]

  return mk_bitstruct( new_name, field_dict,
    namespace = { '__str__': str_func }
  )

