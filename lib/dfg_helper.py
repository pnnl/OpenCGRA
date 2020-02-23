"""
==========================================================================
dfg_helper.py
==========================================================================
Helper classes and functions to construct specific accelerator in FL and
RTL.

Author : Cheng Tan
  Date : Feb 14, 2020

"""

from .messages   import *
from .map_helper import *

import json

class Node:

  def __init__( s, id, FuType, opt, const_index, input_node, output_node ):
    s.id          = id
    s.fu_type     = FuType
    s.opt         = opt
    s.layer       = 0
    s.const_index = const_index
    s.num_const   = len( const_index )
    s.num_input   = len( input_node  )
    DataType      = mk_data( 16, 1 )
    s.input_node  = input_node
    s.input_value = [ DataType( 0, 0 ) ] * s.num_input

    # 2D array for output since there will be multiple results generated,
    # and each of them will route to different successors.
    s.output_node  = output_node
    s.num_output   = [ len( array ) for array in output_node ]
    s.output_value = [ [ DataType( 0, 0 ) for _ in array ]
                         for array in output_node ]

    # We manually or automatically pick one BRH node to insert a live_out
    # output, which will indicate the 'exit' point.
    s.live_out = 0

    # This is used to update the input value without consideration of the
    # ordering, which means the we cannot support 'partial' operation, such
    # as 'LE'.
    s.current_input_index = 0

    s.current_output_index = 0

  # ---------------------------------------------------------------------
  # Update output value which will affect the input value of its
  # successors.
  # ----------------------------------------------------------------------
  def updateOutput( s, i, j, value ):
    s.output_value[i][j] = value

  def updateInput( s, value ):
    s.input_value[s.current_input_index] = value
    s.current_input_index += 1
    if s.current_input_index == s.num_input:
      s.current_input_index = 0

def get_node( node_id, nodes ):
  for node in nodes:
    if node.id == node_id:
      return node
  return None

class DFG:

  def __init__( s, json_file_name, const_list, data_spm ):
    s.nodes       = []
    s.num_const   = 0
    s.num_input   = 0
#    s.num_output  = 0
    # We assume single liveout for now
    s.num_liveout = 1
    s.const_list  = const_list
    s.data_spm    = data_spm
    with open(json_file_name) as json_file:
      dfg = json.load(json_file)
      for i in range( len(dfg) ):
        node = Node( i,
                     getUnitType(dfg[i]['fu']),
                     getOptType(dfg[i]['opt']),
                     dfg[i]['in_const'],
                     dfg[i]['in'],
                     dfg[i]['out'] )
        s.nodes.append( node )
        max_layer = -1
        for input_node in node.input_node:
          pre_node = get_node( input_node, s.nodes )
          if( pre_node != None ):
            if pre_node.layer > max_layer:
              max_layer = pre_node.layer
        node.layer = max_layer + 1
          
        s.num_const  += node.num_const
        s.num_input  += node.num_input
#        s.num_output += node.num_output
        if 'live_out' in dfg[i].keys():
#        if dfg[i]['out2'] != None:
          node.live_out = 1
    s.layer_diff_list = [ 0 ] * s.num_input
    channel_index= 0
    for node in s.nodes:
      for node_id in node.input_node:
        layer_diff = node.layer - get_node( node_id, s.nodes ).layer
        if layer_diff > 0:
          s.layer_diff_list[channel_index] = layer_diff
        else:
          s.layer_diff_list[channel_index] = 1
        channel_index += 1

