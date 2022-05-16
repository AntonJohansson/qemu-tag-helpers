#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Pass.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/IRBuilder.h"

using namespace llvm;

namespace {

struct TagHelpersPass : public ModulePass {
  static char ID;

  TagHelpersPass() : ModulePass(ID) {}

  bool runOnModule(Module &M) override {
    auto &Context = M.getContext();
    auto *PutsType = FunctionType::get(Type::getInt32Ty(Context), Type::getInt8PtrTy(Context), false);
    auto Callee = M.getOrInsertFunction("print_tagged_helper", PutsType);
    auto *Puts = cast<Function>(Callee.getCallee());

    bool modified = false;
    for (auto &F : M) {
        IRBuilder<> Builder(M.getContext());
        const auto &Name = F.getName();
        if (Name.startswith("helper_") && !F.isDeclaration()) {
            modified = true;
            Builder.SetInsertPoint(&F.getEntryBlock());
            auto *str = Builder.CreateGlobalStringPtr(Twine("|-- ").concat(Name).str());
            auto *Call = CallInst::Create(Puts, str);
            F.getEntryBlock().getInstList().push_front(Call);
        }
    }

    return true;
  }
};

} // namespace

char TagHelpersPass::ID = '\0';

static RegisterPass<TagHelpersPass>
  X("TagHelpersPass", "A pass that inserts a `puts` call to every helper function.", true, false);

static RegisterStandardPasses
  Y(PassManagerBuilder::EP_EarlyAsPossible,
    []([[maybe_unused]] PassManagerBuilder const &Builder,
       legacy::PassManagerBase &PM) { PM.add(new TagHelpersPass()); });
