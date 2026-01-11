#include "diter_engine.h"

#include <stdlib.h>
#include <string.h>

#include <string>
#include <vector>

#include "diter_vm.h"

namespace {

const char* default_runbook_path() {
  return "build/runbooks/diter_llvm_workflow.json";
}

const char* kCallCtors = "diter_core_0x5F_wasm_call_ctors";
const char* kInit = "diter_core_mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l";
const char* kAllocKey = "diter_core_Umlja1JvbGxlZDRV";
const char* kLoadDict = "diter_core_dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI";
const char* kLoadChunk = "diter_core_heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl";
const char* kPump = "diter_core_GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW";
const char* kOutPtr = "diter_core_TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT";
const char* kOutLen = "diter_core_bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg";
const char* kOutAdvance = "diter_core_FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN";

}  // namespace

struct DiterEngine {
  DiterVm* vm = nullptr;
  uint64_t instance_ptr = 0;
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
  engine->instance_ptr = diter_vm_instance_ptr(engine->vm);
  if (engine->instance_ptr) {
    uint64_t args[1] = {engine->instance_ptr};
    diter_vm_call(engine->vm, kCallCtors, args, 1);
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
  if (engine->instance_ptr) {
    uint64_t args[1] = {engine->instance_ptr};
    diter_vm_call(engine->vm, kInit, args, 1);
  }
}

void diter_engine_set_key_hex(DiterEngine* engine, const char* key_hex) {
  if (!engine || !key_hex) return;
  engine->key_hex = key_hex;
  if (!engine->instance_ptr) return;
  uint64_t args[3] = {engine->instance_ptr, 0, 40};
  uint64_t ptr = diter_vm_call(engine->vm, kAllocKey, args, 3);
  const uint8_t* memory = diter_vm_memory(engine->vm);
  size_t mem_size = diter_vm_memory_size(engine->vm);
  if (ptr + 40 <= mem_size && memory) {
    for (size_t i = 0; i < 40; i++) {
      const char c = key_hex[i] ? key_hex[i] : '0';
      const_cast<uint8_t*>(memory)[ptr + i] = static_cast<uint8_t>(c);
    }
  }
}

int diter_engine_write_dict(DiterEngine* engine, const uint8_t* data, size_t len) {
  if (!engine || !data || !len) return 0;
  if (!engine->instance_ptr) return 0;
  uint64_t args[2] = {engine->instance_ptr, static_cast<uint64_t>(len)};
  uint64_t ptr = diter_vm_call(engine->vm, kLoadDict, args, 2);
  const uint8_t* memory = diter_vm_memory(engine->vm);
  size_t mem_size = diter_vm_memory_size(engine->vm);
  if (ptr + len > mem_size || !memory) {
    return 0;
  }
  memcpy(const_cast<uint8_t*>(memory) + ptr, data, len);
  return 1;
}

int diter_engine_write_chunk(DiterEngine* engine, const uint8_t* data, size_t len) {
  if (!engine || !data || !len) return 0;
  if (!engine->instance_ptr) return 0;
  uint64_t args[2] = {engine->instance_ptr, static_cast<uint64_t>(len)};
  uint64_t ptr = diter_vm_call(engine->vm, kLoadChunk, args, 2);
  const uint8_t* memory = diter_vm_memory(engine->vm);
  size_t mem_size = diter_vm_memory_size(engine->vm);
  if (ptr + len > mem_size || !memory) {
    return 0;
  }
  memcpy(const_cast<uint8_t*>(memory) + ptr, data, len);
  return 1;
}

int diter_engine_pump(DiterEngine* engine) {
  if (!engine) return 0;
  if (!engine->instance_ptr) return 0;
  uint64_t args[1] = {engine->instance_ptr};
  uint64_t result = diter_vm_call(engine->vm, kPump, args, 1);
  return static_cast<int>(result);
}

const uint8_t* diter_engine_output(DiterEngine* engine, uint32_t* out_len) {
  if (!engine || !out_len) return nullptr;
  if (!engine->instance_ptr) return nullptr;
  uint64_t args[1] = {engine->instance_ptr};
  uint64_t ptr = diter_vm_call(engine->vm, kOutPtr, args, 1);
  uint64_t len = diter_vm_call(engine->vm, kOutLen, args, 1);
  const uint8_t* memory = diter_vm_memory(engine->vm);
  size_t mem_size = diter_vm_memory_size(engine->vm);
  if (!memory || ptr + len > mem_size || len == 0) {
    *out_len = 0;
    return nullptr;
  }
  *out_len = static_cast<uint32_t>(len);
  return memory + ptr;
}

void diter_engine_output_advance(DiterEngine* engine) {
  if (!engine) return;
  if (!engine->instance_ptr) return;
  uint64_t args[1] = {engine->instance_ptr};
  diter_vm_call(engine->vm, kOutAdvance, args, 1);
}
