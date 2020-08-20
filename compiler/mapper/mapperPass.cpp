/*
 * ======================================================================
 * mapperPass.cpp
 * ======================================================================
 * Mapper pass implementation.
 *
 * Author : Cheng Tan
 *   Date : July 16, 2019
 */

#include <llvm/IR/Function.h>
#include <llvm/Pass.h>
#include <llvm/Analysis/LoopInfo.h>
#include <llvm/Analysis/LoopIterator.h>
#include <stdio.h>
#include "Mapper.h"

using namespace llvm;

namespace {

//  typedef pair<Value*, StringRef> DFGNode;
//  typedef pair<DFGNode, DFGNode> DFGEdge;
  struct mapperPass : public FunctionPass {

  public:
    static char ID;
    Mapper* mapper;
    mapperPass() : FunctionPass(ID) {}

    void getAnalysisUsage(AnalysisUsage &AU) const override {
      AU.addRequired<LoopInfoWrapperPass>();
      AU.addPreserved<LoopInfoWrapperPass>();
      AU.setPreservesAll();
    }

    bool runOnFunction(Function &t_F) override {

      // Set the target function and loop.
      map<string, list<int>*>* functionWithLoop = new map<string, list<int>*>();
      (*functionWithLoop)["_Z12ARENA_kerneliii"] = new list<int>();
      (*functionWithLoop)["_Z12ARENA_kerneliii"]->push_back(0);
      (*functionWithLoop)["_Z4spmviiPiS_S_"] = new list<int>();
      (*functionWithLoop)["_Z4spmviiPiS_S_"]->push_back(0);
      (*functionWithLoop)["_Z4spmvPiii"] = new list<int>();
      (*functionWithLoop)["_Z4spmvPiii"]->push_back(0);
      (*functionWithLoop)["adpcm_coder"] = new list<int>();
      (*functionWithLoop)["adpcm_coder"]->push_back(0);
      (*functionWithLoop)["adpcm_decoder"] = new list<int>();
      (*functionWithLoop)["adpcm_decoder"]->push_back(0);
      (*functionWithLoop)["fir"] = new list<int>();
      (*functionWithLoop)["fir"]->push_back(0);
//      (*functionWithLoop)["fir"].push_back(1);
      (*functionWithLoop)["latnrm"] = new list<int>();
      (*functionWithLoop)["latnrm"]->push_back(1);
      (*functionWithLoop)["fft"] = new list<int>();
      (*functionWithLoop)["fft"]->push_back(0);
      (*functionWithLoop)["BF_encrypt"] = new list<int>();
      (*functionWithLoop)["BF_encrypt"]->push_back(0);
      (*functionWithLoop)["susan_smoothing"] = new list<int>();
      (*functionWithLoop)["susan_smoothing"]->push_back(0);

//      (*functionWithLoop)["main"] = new list<int>();
//      (*functionWithLoop)["main"]->push_back(0);

      // Configuration for static CGRA.
      // int rows = 8;
      // int columns = 8;
      // bool isStaticElasticCGRA = true;
      // bool isTrimmedDemo = true;
      // int ctrlMemConstraint = 1;
      // int bypassConstraint = 3;
      // int regConstraint = 1;

      // Configuration for dynamic CGRA.
      int rows = 4;
      int columns = 4;
      bool isStaticElasticCGRA = false;
      bool isTrimmedDemo = true;
      int ctrlMemConstraint = 100;
      int bypassConstraint = 4;
      // FIXME: should not change this for now, it is the four directions by default
      int regConstraint = 4;
      bool heterogeneity = false;
//      bool heterogeneity = true;

      if (functionWithLoop->find(t_F.getName().str()) == functionWithLoop->end()) {
        errs()<<"[function \'"<<t_F.getName()<<"\' is not in our target list]\n";
        return false;
      }
      errs() << "==================================\n";
      errs()<<"[function \'"<<t_F.getName()<<"\' is one of our targets]\n";

      list<Loop*>* targetLoops = getTargetLoops(t_F, functionWithLoop);
      // TODO: will make a list of patterns/tiles to illustrate how the
      //       heterogeneity is
      DFG* dfg = new DFG(t_F, targetLoops, heterogeneity);
      CGRA* cgra = new CGRA(rows, columns, heterogeneity);
      cgra->setRegConstraint(regConstraint);
      cgra->setCtrlMemConstraint(ctrlMemConstraint);
      cgra->setBypassConstraint(bypassConstraint);
      mapper = new Mapper();

      // Show the count of different opcodes (IRs).
      errs() << "==================================\n";
      errs() << "[show opcode count]\n";
      dfg->showOpcodeDistribution();

      // Generate the DFG dot file.
      errs() << "==================================\n";
      errs() << "[generate dot for DFG]\n";
      dfg->generateDot(t_F, isTrimmedDemo);

      // Generate the DFG dot file.
      errs() << "==================================\n";
      errs() << "[generate JSON for DFG]\n";
      dfg->generateJSON();

      // Initialize the II.
      int ResMII = mapper->getResMII(dfg, cgra);
      errs() << "==================================\n";
      errs() << "[ResMII: " << ResMII << "]\n";
      int RecMII = mapper->getRecMII(dfg);
      errs() << "==================================\n";
      errs() << "[RecMII: " << RecMII << "]\n";
      int II = ResMII;
      if(II < RecMII)
        II = RecMII;

      // Heuristic algorithm (hill climbing) to get a valid mapping within
      // a acceptable II.
      bool success = false;
      if (!isStaticElasticCGRA) {
        errs() << "==================================\n";
        errs() << "[heuristic]\n";
        II = mapper->heuristicMap(cgra, dfg, II, isStaticElasticCGRA);
      }

      // Partially exhaustive search to try to map the DFG onto
      // the static elastic CGRA.

      if (isStaticElasticCGRA and !success) {
        errs() << "==================================\n";
        errs() << "[exhaustive]\n";
        II = mapper->exhaustiveMap(cgra, dfg, II, isStaticElasticCGRA);
      }

      // Show the mapping and routing results with JSON output.
      if (II == -1)
        errs() << "[fail]\n";
      else {
        mapper->showSchedule(cgra, dfg, II, isStaticElasticCGRA);
        errs() << "==================================\n";
        errs() << "[success]\n";
        errs() << "==================================\n";
        mapper->generateJSON(cgra, dfg, II, isStaticElasticCGRA);
        errs() << "[Output Json]\n";
      }
      errs() << "==================================\n";

      return false;
    }


    list<Loop*>* getTargetLoops(Function& t_F, map<string, list<int>*>* t_functionWithLoop) {
      int targetLoopID = 0;
      list<Loop*>* targetLoops = new list<Loop*>();
      while((*t_functionWithLoop).at(t_F.getName().str())->size() > 0) {
        targetLoopID = (*t_functionWithLoop).at(t_F.getName().str())->front();
        (*t_functionWithLoop).at(t_F.getName().str())->pop_front();

        // Specify the particular loop we are focusing on.
        // TODO: move the following to another .cpp file.
        LoopInfo &LI = getAnalysis<LoopInfoWrapperPass>().getLoopInfo();
        int tempLoopID = 0;
        Loop* current_loop = NULL;
        for(LoopInfo::iterator loopItr=LI.begin();
            loopItr!= LI.end(); ++loopItr) {
//          targetLoops.push_back(*loopItr);
          current_loop = *loopItr;
          if (tempLoopID == targetLoopID) {
            while (!current_loop->getSubLoops().empty()) {
              errs()<<"*** detected nested loop ... size: "<<current_loop->getSubLoops().size()<<"\n";
              // TODO: might change '0' to a reasonable index
              current_loop = current_loop->getSubLoops()[0];
            }
            targetLoops->push_back(current_loop);
            errs()<<"*** reach target loop ID: "<<tempLoopID<<"\n";
            break;
          }
          ++tempLoopID;
        }
        if (targetLoops->size() == 0) {
          errs()<<"... no loop detected in the target kernel ...\n";
        }
      }
      errs()<<"... detected loops.size(): "<<targetLoops->size()<<"\n";
      return targetLoops;
    }

  };
}

char mapperPass::ID = 0;
static RegisterPass<mapperPass> X("mapperPass", "DFG Pass Analyse", false, false);
