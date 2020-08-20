/*
 * ======================================================================
 * DFGEdge.h
 * ======================================================================
 * DFG edge implementation header file.
 *
 * Author : Cheng Tan
 *   Date : July 19, 2019
 */

#ifndef DFGEdge_H
#define DFGEdge_H

#include <llvm/Support/raw_ostream.h>
#include <llvm/Support/FileSystem.h>

#include "DFGNode.h"

using namespace llvm;

class DFGNode;

class DFGEdge
{
  private:
    int m_id;
    DFGNode *m_src;
    DFGNode *m_dst;
    bool m_isBackCtrlEdge;

  public:
    DFGEdge(int, DFGNode*, DFGNode*);
    void setID(int);
    int getID();
    DFGNode* getSrc();
    DFGNode* getDst();
    void connect(DFGNode*, DFGNode*);
    DFGNode* getConnectedNode(DFGNode*);
    bool isBackCtrlEdge();
    void setBackCtrlEdge();
};

#endif
