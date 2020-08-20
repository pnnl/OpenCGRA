/*
 * ======================================================================
 * DFGNode.cpp
 * ======================================================================
 * DFG node implementation.
 *
 * Author : Cheng Tan
 *   Date : Feb 12, 2020
 */

#include "DFGNode.h"

DFGNode::DFGNode(int t_id, Instruction* t_inst, StringRef t_stringRef) {
  m_id = t_id;
  m_inst = t_inst;
  m_stringRef = t_stringRef;
  m_predNodes = NULL;
  m_succNodes = NULL;
  m_opcodeName = t_inst->getOpcodeName();
  m_isMapped = false;
  m_numConst = 0;
  m_optType = "";
  m_combined = false;
  m_isPatternRoot = false;
  m_patternRoot = NULL;
  m_critical = false;
  m_patternNodes = new list<DFGNode*>();
  initType();
}

int DFGNode::getID() {
  return m_id;
}

void DFGNode::setID(int t_id) {
  m_id = t_id;
}

void DFGNode::setCritical() {
  m_critical = true;
}

bool DFGNode::isCritical() {
  return m_critical;
}

bool DFGNode::isMapped() {
  return m_isMapped;
}

void DFGNode::setMapped() {
  m_isMapped = true;
}

void DFGNode::clearMapped() {
  m_isMapped = false;
}

Instruction* DFGNode::getInst() {
  return m_inst;
}

StringRef DFGNode::getStringRef() {
  return m_stringRef;
}

bool DFGNode::isCall() {
  if (m_opcodeName.compare("call") == 0)
    return true;
  return false;
}

bool DFGNode::isLoad() {
  if (m_opcodeName.compare("load") == 0)
    return true;
  return false;
}

bool DFGNode::isStore() {
  if (m_opcodeName.compare("store") == 0)
    return true;
  return false;
}

bool DFGNode::isBranch() {
  if (m_opcodeName.compare("br") == 0)
    return true;
  return false;
}

bool DFGNode::isPhi() {
  if (m_opcodeName.compare("phi") == 0)
    return true;
  return false;
}

bool DFGNode::isOpt(string t_opt) {
  if (m_opcodeName.compare(t_opt) == 0)
    return true;
  return false;
}

bool DFGNode::isMul() {
  if (m_opcodeName.compare("fmul") == 0 or
      m_opcodeName.compare("mul") == 0)
    return true;
  return false;
}

bool DFGNode::isAdd() {
  if (m_opcodeName.compare("getelementptr") == 0 or
      m_opcodeName.compare("add") == 0  or
      m_opcodeName.compare("fadd") == 0 or
      m_opcodeName.compare("sub") == 0  or
      m_opcodeName.compare("fsub") == 0)
    return true;
  return false;
}

bool DFGNode::isCmp() {
  if (m_opcodeName.compare("icmp") == 0)
    return true;
  return false;
}

bool DFGNode::isBitcast() {
  if (m_opcodeName.compare("bitcast") == 0)
    return true;
  return false;
}

bool DFGNode::isGetptr() {
  if (m_opcodeName.compare("getelementptr") == 0)
    return true;
  return false;
}

bool DFGNode::hasCombined() {
  return m_combined;
}

void DFGNode::setCombine() {
  m_combined = true;
}

void DFGNode::addPatternPartner(DFGNode* t_patternNode) {
  m_isPatternRoot = true;
  m_patternRoot = this;
  m_patternNodes->push_back(t_patternNode);
  t_patternNode->setPatternRoot(this);
  m_opcodeName += t_patternNode->getOpcodeName();
}

list<DFGNode*>* DFGNode::getPatternNodes() {
  return m_patternNodes;
}

void DFGNode::setPatternRoot(DFGNode* t_patternRoot) {
  m_patternRoot = t_patternRoot;
}

DFGNode* DFGNode::getPatternRoot() {
  return m_patternRoot;
}

bool DFGNode::isPatternRoot() {
  return m_isPatternRoot;
}

string DFGNode::getOpcodeName() {
  return m_opcodeName;
}

string DFGNode::getFuType() {
  return m_fuType;
}

string DFGNode::getJSONOpt() {
  return m_optType;
}

void DFGNode::initType() {
  if (isLoad()) {
    m_optType = "OPT_LD";
    m_fuType = "MemUnit";
  } else if (isStore()) {
    m_optType = "OPT_STR";
    m_fuType = "MemUnit";
  } else if (isBranch()) {
    m_optType = "OPT_BRH";
    m_fuType = "Branch";
  } else if (isPhi()) {
    m_optType = "OPT_PHI";
    m_fuType = "Phi";
  } else if (isCmp()) {
    m_optType = "OPT_EQ";
    m_fuType = "Comp";
  } else if (isBitcast()) {
    m_optType = "OPT_NAH";
    m_fuType = "Alu";
  } else if (isGetptr()) {
    m_optType = "OPT_ADD";
    m_fuType = "Alu";
  } else if (m_opcodeName.compare("add") == 0) {
    m_optType = "OPT_ADD";
    m_fuType = "Alu";
  } else if (m_opcodeName.compare("fadd") == 0) {
    m_optType = "OPT_ADD";
    m_fuType = "Alu";
  } else if (m_opcodeName.compare("sub") == 0) {
    m_optType = "OPT_SUB";
    m_fuType = "Alu";
  } else if (m_opcodeName.compare("fsub") == 0) {
    m_optType = "OPT_SUB";
    m_fuType = "Alu";
  } else if (m_opcodeName.compare("xor") == 0) {
    m_optType = "OPT_XOR";
    m_fuType = "Alu";
  } else if (m_opcodeName.compare("or") == 0) {
    m_optType = "OPT_OR";
    m_fuType = "Logic";
  } else if (m_opcodeName.compare("and") == 0) {
    m_optType = "OPT_AND";
    m_fuType = "Logic";
  } else if (m_opcodeName.compare("mul") == 0) {
    m_optType = "OPT_MUL";
    m_fuType = "Mul";
  } else if (m_opcodeName.compare("fmul") == 0) {
    m_optType = "OPT_MUL";
    m_fuType = "Mul";
  } else if (m_opcodeName.compare("shl") == 0) {
    m_optType = "OPT_SHL";
    m_fuType = "Shift";
  } else if (m_opcodeName.compare("lshr") == 0) {
    m_optType = "OPT_LSR";
    m_fuType = "Shift";
  } else if (m_opcodeName.compare("ashr") == 0) {
    m_optType = "OPT_ASR";
    m_fuType = "Shift";
  } else {
    m_optType = "Unfamiliar: " + m_opcodeName;
    m_fuType = "Unknown";
  }
}

list<DFGNode*>* DFGNode::getPredNodes() {
  if (m_predNodes != NULL)
    return m_predNodes;

  m_predNodes = new list<DFGNode*>();
  for (DFGEdge* edge: m_inEdges) {
    assert(edge->getDst() == this);
    m_predNodes->push_back(edge->getSrc());
  }
  if (isBranch()) {
    list<DFGNode*>* m_tempNodes = new list<DFGNode*>();
    for (DFGNode* node: *m_predNodes) {
      // make sure the CMP node is the last one in the predecessors,
      // so the JSON file will get the correct ordering.
      if (!node->isCmp()) {
        m_tempNodes->push_back(node);
      }
    }
    for (DFGNode* node: *m_predNodes) {
      if (node->isCmp()) {
        m_tempNodes->push_back(node);
      }
    }
    m_predNodes = m_tempNodes;
  }
  return m_predNodes;
}

list<DFGNode*>* DFGNode::getSuccNodes() {
  if (m_succNodes != NULL)
    return m_succNodes;

  m_succNodes = new list<DFGNode*>();
  for (DFGEdge* edge: m_outEdges) {
    assert(edge->getSrc() == this);
    m_succNodes->push_back(edge->getDst());
  }
  return m_succNodes;
}

void DFGNode::setInEdge(DFGEdge* t_dfgEdge) {
  if (find(m_inEdges.begin(), m_inEdges.end(), t_dfgEdge) ==
      m_inEdges.end())
    m_inEdges.push_back(t_dfgEdge);
}

void DFGNode::setOutEdge(DFGEdge* t_dfgEdge) {
  if (find(m_outEdges.begin(), m_outEdges.end(), t_dfgEdge) ==
      m_outEdges.end())
    m_outEdges.push_back(t_dfgEdge);
}

void DFGNode::cutEdges() {
  m_inEdges.clear();
  m_outEdges.clear();

  if (m_predNodes != NULL) {
    m_predNodes = NULL;
  }
  if (m_succNodes != NULL) {
    m_succNodes = NULL;
  }
}

bool DFGNode::isSuccessorOf(DFGNode* t_dfgNode) {
  list<DFGNode*>* succNodes = t_dfgNode->getSuccNodes();
  if (find (succNodes->begin(), succNodes->end(), this) != succNodes->end())
    return true;
  return false;
}

bool DFGNode::isPredecessorOf(DFGNode* t_dfgNode) {
  list<DFGNode*>* predNodes = t_dfgNode->getPredNodes();
  if (find (predNodes->begin(), predNodes->end(), this) != predNodes->end())
    return true;
  return false;
}

bool DFGNode::isOneOfThem(list<DFGNode*>* t_pattern) {
  if (find (t_pattern->begin(), t_pattern->end(), this) != t_pattern->end())
    return true;
  return false;
}

void DFGNode::addConst() {
  ++m_numConst;
}

void DFGNode::removeConst() {
  --m_numConst;
}

int DFGNode::getNumConst() {
  return m_numConst;
}
