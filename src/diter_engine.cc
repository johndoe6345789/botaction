#include "diter_engine.h"

#include <stdlib.h>

#include <string>
#include <vector>

#include "diter_vm.h"

namespace {

const char* default_runbook_path() {
  return "build/runbooks/diter_llvm_workflow.json";
}

}  // namespace

struct DiterEngine {
  DiterVm* vm = nullptr;
  std::vector<uint8_t> dict;
  std::vector<uint8_t> chunk;
  std::string key_hex;
  std::vector<uint8_t> output;
  bool executed = false;
};

DiterEngine* diter_engine_create(void) {
  const char* runbook = getenv("DITER_RUNBOOK");
  if (!runbook || !*runbook) {
    runbook = default_runbook_path();
  }

  DiterEngine* engine = new DiterEngine();
  engine->vm = diter_vm_create(runbook);
  if (!engine->vm) {
    delete engine;
    return nullptr;
  }
  return engine;
}

void diter_engine_destroy(DiterEngine* engine) {
  if (!engine) return;
  diter_vm_destroy(engine->vm);
  delete engine;
}

void diter_engine_init(DiterEngine* engine) {
  if (!engine) return;
  engine->executed = false;
  engine->output.clear();
}

void diter_engine_set_key_hex(DiterEngine* engine, const char* key_hex) {
  if (!engine || !key_hex) return;
  engine->key_hex = key_hex;
}

int diter_engine_write_dict(DiterEngine* engine, const uint8_t* data, size_t len) {
  if (!engine || !data || !len) return 0;
  engine->dict.assign(data, data + len);
  return 1;
}

int diter_engine_write_chunk(DiterEngine* engine, const uint8_t* data, size_t len) {
  if (!engine || !data || !len) return 0;
  engine->chunk.assign(data, data + len);
  return 1;
}

int diter_engine_pump(DiterEngine* engine) {
  if (!engine) return 0;
  if (!engine->executed) {
    diter_vm_load_inputs(engine->vm,
                         engine->dict.data(),
                         engine->dict.size(),
                         engine->chunk.data(),
                         engine->chunk.size(),
                         engine->key_hex.c_str());
    diter_vm_execute(engine->vm);
    engine->executed = true;
  }
  return 0;
}

const uint8_t* diter_engine_output(DiterEngine* engine, uint32_t* out_len) {
  if (!engine || !out_len) return nullptr;
  *out_len = static_cast<uint32_t>(engine->output.size());
  if (engine->output.empty()) {
    return nullptr;
  }
  return engine->output.data();
}

void diter_engine_output_advance(DiterEngine* engine) {
  if (!engine) return;
  engine->output.clear();
}
