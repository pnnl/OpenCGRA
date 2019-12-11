"""
==========================================================================
messages.py
==========================================================================
Collection of messages definition.

Convention: The fields/constructor arguments should appear in the order
            of [ payload_nbits, predicate_nbits ]

Author : Cheng Tan
  Date : Dec 3, 2019
"""
from pymtl3 import *

#=========================================================================
# Generic data message
#=========================================================================

def mk_data( payload_nbits=16, predicate_nbits=1, prefix="CGRAData" ):

  PayloadType   = mk_bits( payload_nbits   )
  PredicateType = mk_bits( predicate_nbits )

  new_name = f"{prefix}_{payload_nbits}_{predicate_nbits}"

  def str_func( s ):
    return f"{int(s.payload)}.{s.predicate}"

  return mk_bitstruct( new_name, {
      'payload'  : PayloadType,
      'predicate': PredicateType,
    },
    namespace = { '__str__': str_func }
  )

#=========================================================================
# Generic config message
#=========================================================================

def mk_config( config_nbits=16, prefix="CGRAConfig" ):

  ConfigType   = mk_bits( config_nbits   )

  new_name = f"{prefix}_{config_nbits}"

  def str_func( s ):
    return f"{s.config}"

  return mk_bitstruct( new_name, {
      'config'  : ConfigType,
    },
    namespace = { '__str__': str_func }
  )
