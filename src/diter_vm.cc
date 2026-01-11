#include "diter_vm.h"

#include <rapidjson/document.h>

#include <cstddef>
#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace {

struct Instruction {
  std::string function;
  std::string op;
  std::string dest;
  std::string text;
};

struct VmState {
  std::vector<Instruction> instructions;
  std::unordered_map<std::string, uint64_t> op_counts;
  std::vector<uint8_t> dict;
  std::vector<uint8_t> chunk;
  std::string key_hex;
  size_t executed = 0;
};

std::string read_text(const std::string &path) {
  std::ifstream file(path, std::ios::in | std::ios::binary);
  if (!file) {
    throw std::runtime_error("Failed to read file: " + path);
  }
  std::string contents((std::istreambuf_iterator<char>(file)),
                       std::istreambuf_iterator<char>());
  return contents;
}

rapidjson::Document load_json(const std::string &path) {
  rapidjson::Document doc;
  std::string content = read_text(path);
  doc.Parse(content.c_str());
  if (doc.HasParseError()) {
    throw std::runtime_error("Failed to parse JSON: " + path);
  }
  return doc;
}

void parse_nodes(const rapidjson::Value &nodes_value, VmState &state) {
  if (!nodes_value.IsArray()) {
    return;
  }
  for (const auto &node_val : nodes_value.GetArray()) {
    if (!node_val.IsObject()) {
      continue;
    }
    auto type_it = node_val.FindMember("type");
    if (type_it == node_val.MemberEnd() || !type_it->value.IsString()) {
      continue;
    }
    if (std::string(type_it->value.GetString()) != "llvm.instruction") {
      continue;
    }
    auto params_it = node_val.FindMember("parameters");
    if (params_it == node_val.MemberEnd() || !params_it->value.IsObject()) {
      continue;
    }
    const auto &params = params_it->value;
    Instruction inst;
    auto fn_it = params.FindMember("function");
    if (fn_it != params.MemberEnd() && fn_it->value.IsString()) {
      inst.function = fn_it->value.GetString();
    }
    auto op_it = params.FindMember("op");
    if (op_it != params.MemberEnd() && op_it->value.IsString()) {
      inst.op = op_it->value.GetString();
    }
    auto dest_it = params.FindMember("dest");
    if (dest_it != params.MemberEnd() && dest_it->value.IsString()) {
      inst.dest = dest_it->value.GetString();
    }
    auto text_it = params.FindMember("text");
    if (text_it != params.MemberEnd() && text_it->value.IsString()) {
      inst.text = text_it->value.GetString();
    }
    state.instructions.push_back(std::move(inst));
  }
}

void merge_workflow(const std::string &path, VmState &state) {
  auto doc = load_json(path);
  if (!doc.IsObject()) {
    return;
  }
  auto nodes_it = doc.FindMember("nodes");
  if (nodes_it != doc.MemberEnd()) {
    parse_nodes(nodes_it->value, state);
  }
}

VmState load_workflow(const std::string &path) {
  VmState state;
  auto doc = load_json(path);
  if (!doc.IsObject()) {
    return state;
  }

  auto parts_it = doc.FindMember("parts");
  if (parts_it != doc.MemberEnd() && parts_it->value.IsArray()) {
    size_t slash = path.find_last_of("/\\");
    std::string base_dir = (slash == std::string::npos) ? "" : path.substr(0, slash);
    for (const auto &part : parts_it->value.GetArray()) {
      if (!part.IsString()) {
        continue;
      }
      std::string part_path = part.GetString();
      if (!part_path.empty() && part_path[0] != '/' && !base_dir.empty()) {
        part_path = base_dir + "/" + part_path;
      }
      merge_workflow(part_path, state);
    }
    return state;
  }

  auto nodes_it = doc.FindMember("nodes");
  if (nodes_it != doc.MemberEnd()) {
    parse_nodes(nodes_it->value, state);
  }
  return state;
}

}  // namespace

struct DiterVm {
  VmState state;
};

DiterVm* diter_vm_create(const char* runbook_path) {
  if (!runbook_path || !*runbook_path) {
    return nullptr;
  }
  DiterVm* vm = new DiterVm();
  try {
    vm->state = load_workflow(runbook_path);
  } catch (...) {
    delete vm;
    return nullptr;
  }
  return vm;
}

void diter_vm_destroy(DiterVm* vm) {
  delete vm;
}

void diter_vm_load_inputs(DiterVm* vm,
                          const uint8_t* dict,
                          size_t dict_len,
                          const uint8_t* chunk,
                          size_t chunk_len,
                          const char* key_hex) {
  if (!vm) {
    return;
  }
  vm->state.dict.assign(dict, dict + dict_len);
  vm->state.chunk.assign(chunk, chunk + chunk_len);
  vm->state.key_hex = key_hex ? key_hex : "";
}

void diter_vm_execute(DiterVm* vm) {
  if (!vm) {
    return;
  }
  vm->state.op_counts.clear();
  for (const auto &inst : vm->state.instructions) {
    vm->state.op_counts[inst.op]++;
  }
  vm->state.executed = vm->state.instructions.size();
}

size_t diter_vm_instruction_count(const DiterVm* vm) {
  if (!vm) {
    return 0;
  }
  return vm->state.instructions.size();
}
