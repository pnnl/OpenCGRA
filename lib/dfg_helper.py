"""
==========================================================================
dfg_helper.py
==========================================================================
Helper classes and functions to construct specific accelerator in FL and
RTL.

Author : Cheng Tan
  Date : Feb 14, 2020

"""

from .opt_type           import *
from .messages           import *
from ..fu.single.Alu     import Alu
from ..fu.single.Shifter import Shifter
from ..fu.single.Logic   import Logic
from ..fu.single.Mul     import Mul
from ..fu.single.MemUnit import MemUnit
from ..fu.single.Comp    import Comp
from ..fu.single.Phi     import Phi
from ..fu.single.Branch  import Branch

import json

class Node:

  def __init__( s, id, FuType, opt, const_index, input_node, output_node ):
    s.id          = id
    s.fu_type     = FuType
    s.opt         = opt
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
      print(dfg)
      for i in range( len(dfg) ):
        node = Node( i,
                     getUnitType(dfg[i]['fu']),
                     getOptType(dfg[i]['opt']),
                     dfg[i]['in_const'],
                     dfg[i]['in'],
                     dfg[i]['out'] )
        s.nodes.append( node )
        s.num_const  += node.num_const
        s.num_input  += node.num_input
#        s.num_output += node.num_output
        if 'live_out' in dfg[i].keys():
#        if dfg[i]['out2'] != None:
          node.live_out = 1

  def get_node( s, id ):
    for e in s.nodes:
      if e.id == id:
        return e
    return None

# -----------------------------------------------------------------------
# Global dictionary for UnitType and OptType
# -----------------------------------------------------------------------

unit_map = { "Alu"             : Alu,
             "Mul"             : Mul,
             "Phi"             : Phi,
             "Comp"            : Comp,
             "Branch"          : Branch,
             "Logic"           : Logic,
             "Shifter"         : Shifter,
             "MemUnit"         : MemUnit }

opt_map  = { "OPT_START"       : OPT_START,
             "OPT_NAH"         : OPT_NAH,
             "OPT_ADD"         : OPT_ADD,
             "OPT_ADD_CONST"   : OPT_ADD_CONST,
             "OPT_INC"         : OPT_INC,
             "OPT_SUB"         : OPT_SUB,
             "OPT_LLS"         : OPT_LLS,
             "OPT_LRS"         : OPT_LRS,
             "OPT_MUL"         : OPT_MUL,
             "OPT_OR"          : OPT_OR,
             "OPT_XOR"         : OPT_XOR,
             "OPT_AND"         : OPT_AND,
             "OPT_NOT"         : OPT_NOT,
             "OPT_LD"          : OPT_LD,
             "OPT_STR"         : OPT_STR,
             "OPT_EQ"          : OPT_EQ,
             "OPT_LE"          : OPT_LE,
             "OPT_BRH"         : OPT_BRH,
             "OPT_PHI"         : OPT_PHI,
             "OPT_MUL_ADD"     : OPT_MUL_ADD,
             "OPT_MUL_SUB"     : OPT_MUL_SUB,
             "OPT_MUL_LLS"     : OPT_MUL_LLS,
             "OPT_MUL_LRS"     : OPT_MUL_LRS,
             "OPT_MUL_ADD_LLS" : OPT_MUL_ADD_LLS,
             "OPT_MUL_SUB_LLS" : OPT_MUL_SUB_LLS,
             "OPT_MUL_SUB_LRS" : OPT_MUL_SUB_LRS }

def getUnitType( fu_name ):
  return unit_map[ fu_name ]

def getOptType( opt_name ):
  return opt_map[ opt_name ]

