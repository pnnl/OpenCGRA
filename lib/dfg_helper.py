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
from ..fu.single.Alu     import Alu
from ..fu.single.Shifter import Shifter
from ..fu.single.Logic   import Logic
from ..fu.single.Mul     import Mul
from ..fu.single.MemUnit import MemUnit
from ..fu.single.Comp    import Comp
from ..fu.single.Phi     import Phi
from ..fu.single.Branch  import Branch

import json

class Element:

  def __init__( s, id, FuType, opt, const_index, input_element, output_element ):
    s.id             = id
    s.fu_type        = FuType
    s.opt            = opt
    s.const_index    = const_index
    s.input_element  = input_element
    s.output_element = output_element
    s.num_const      = len(const_index)
    s.num_input      = len(input_element)
    s.num_output     = len(output_element)
    s.current_input_index = 0
    s.input_value    = [ None ] * len(input_element)
    print("input value: ", s.input_value)
    s.output_value   = [ None ] * len(output_element)

  # ---------------------------------------------------------------------
  # Update output value which will affect the input value of its
  # successors.
  # ----------------------------------------------------------------------
  def updateOutput( s, output_index, value ):
    s.output_value[output_index] = value

  def updateInput( s, value ):
    s.input_value[s.current_input_index] = value
    s.current_input_index += 1
    if s.current_input_index == s.num_input:
      s.current_input_index = 0

class DFG:

  def __init__( s, json_file_name ):
    s.elements    = []
    s.num_const   = 0
    s.num_input   = 0
    s.num_output  = 0
    s.num_liveout = 1
    with open(json_file_name) as json_file:
      dfg = json.load(json_file)
      print(dfg)
      for i in range( len(dfg) ):
        element = Element( i, getUnitType(dfg[i]['fu']),
                           getOptType(dfg[i]['opt']),
                           dfg[i]['in_const'], dfg[i]['in'],
                           dfg[i]['out'] )
        s.elements.append( element )
        s.num_const  += element.num_const
        s.num_input  += element.num_input
        s.num_output += element.num_output

  def get_element( s, _id ):
    for e in s.elements:
      if e.id == _id:
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

