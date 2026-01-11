#include "diter_vm.h"

#include <rapidjson/document.h>

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <sstream>
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

struct Value {
  uint64_t u = 0;
};

struct Function {
  std::string name;
  std::vector<Instruction> insts;
  std::unordered_map<std::string, size_t> labels;
};

struct Frame {
  std::string func;
  size_t pc = 0;
  std::unordered_map<std::string, Value> regs;
  std::string last_label;
  std::string prev_label;
  std::string ret_dest;
  size_t saved_stack_top = 0;
};

struct VmState {
  std::vector<Instruction> instructions;
  std::unordered_map<std::string, Function> functions;
  std::vector<std::string> function_order;
  std::unordered_map<std::string, uint64_t> op_counts;
  std::vector<uint8_t> memory;
  size_t stack_top = 0;
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

std::string op_from_text(const std::string &text) {
  if (!text.empty() && text.back() == ':') {
    return "label";
  }
  auto eq = text.find('=');
  if (eq != std::string::npos) {
    std::string right = text.substr(eq + 1);
    std::istringstream iss(right);
    std::string op;
    iss >> op;
    return op;
  }
  std::istringstream iss(text);
  std::string op;
  iss >> op;
  return op;
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
    auto text_it = params.FindMember("text");
    if (text_it != params.MemberEnd() && text_it->value.IsString()) {
      inst.text = text_it->value.GetString();
    }
    inst.op = op_from_text(inst.text);
    auto dest_it = params.FindMember("dest");
    if (dest_it != params.MemberEnd() && dest_it->value.IsString()) {
      inst.dest = dest_it->value.GetString();
    } else {
      auto eq = inst.text.find('=');
      if (eq != std::string::npos) {
        std::string left = inst.text.substr(0, eq);
        std::istringstream iss(left);
        iss >> inst.dest;
      }
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
  if (state.functions.empty()) {
    Function *current = nullptr;
    for (const auto &inst : state.instructions) {
      if (current == nullptr || current->name != inst.function) {
        state.function_order.push_back(inst.function);
        state.functions[inst.function] = Function{inst.function};
        current = &state.functions[inst.function];
      }
      current->insts.push_back(inst);
    }
    for (auto &pair : state.functions) {
      auto &func = pair.second;
      for (size_t i = 0; i < func.insts.size(); i++) {
        const auto &inst = func.insts[i];
        if (inst.op == "label") {
          std::string label = inst.text;
          if (!label.empty() && label.back() == ':') {
            label.pop_back();
          }
          if (!label.empty() && label[0] == '%') {
            label = label.substr(1);
          }
          func.labels[label] = i;
        }
      }
    }
  }
  return state;
}

size_t type_size_bytes(const std::string &type) {
  auto trim = [](std::string &value) {
    size_t start = value.find_first_not_of(" \t");
    size_t end = value.find_last_not_of(" \t");
    if (start == std::string::npos) {
      value.clear();
      return;
    }
    value = value.substr(start, end - start + 1);
  };
  if (type == "i1" || type == "i8") return 1;
  if (type == "i16") return 2;
  if (type == "i32") return 4;
  if (type == "i64") return 8;
  if (type == "ptr") return 8;
  if (!type.empty() && type[0] == '[') {
    auto x = type.find('x');
    auto end = type.find(']');
    if (x != std::string::npos && end != std::string::npos) {
      size_t count = std::stoull(type.substr(1, x - 1));
      std::string elem = type.substr(x + 1, end - x - 1);
      trim(elem);
      return count * type_size_bytes(elem);
    }
  }
  return 8;
}

std::string normalize_label(const std::string &label) {
  std::string out = label;
  if (!out.empty() && out.back() == ',') out.pop_back();
  if (!out.empty() && out.back() == ':') out.pop_back();
  if (!out.empty() && out[0] == '%') out = out.substr(1);
  return out;
}

Value parse_operand(const std::unordered_map<std::string, Value> &regs,
                    const std::string &token) {
  if (token.empty()) {
    return {};
  }
  if (token[0] == '%') {
    auto it = regs.find(token);
    if (it != regs.end()) {
      return it->second;
    }
    return {};
  }
  if (token == "null") {
    return {};
  }
  char *end = nullptr;
  if (!token.empty() && token[0] == '-') {
    int64_t value = std::strtoll(token.c_str(), &end, 0);
    if (end && end != token.c_str()) {
      return {static_cast<uint64_t>(value)};
    }
  } else {
    uint64_t value = std::strtoull(token.c_str(), &end, 0);
    if (end && end != token.c_str()) {
      return {value};
    }
  }
  return {};
}

void ensure_memory(VmState &state, size_t size) {
  if (state.memory.size() < size) {
    state.memory.resize(size, 0);
  }
}

void store_value(VmState &state, uint64_t addr, Value value, size_t size) {
  ensure_memory(state, addr + size);
  for (size_t i = 0; i < size; i++) {
    state.memory[addr + i] = static_cast<uint8_t>((value.u >> (i * 8)) & 0xff);
  }
}

Value load_value(const VmState &state, uint64_t addr, size_t size) {
  Value out;
  if (addr + size > state.memory.size()) {
    return out;
  }
  uint64_t value = 0;
  for (size_t i = 0; i < size; i++) {
    value |= static_cast<uint64_t>(state.memory[addr + i]) << (i * 8);
  }
  out.u = value;
  return out;
}

std::vector<std::string> split_tokens(const std::string &text) {
  std::vector<std::string> tokens;
  std::istringstream iss(text);
  std::string token;
  while (iss >> token) {
    tokens.push_back(token);
  }
  return tokens;
}

void execute_instruction(VmState &state, Frame &frame, const Instruction &inst) {
  state.op_counts[inst.op]++;
  const auto tokens = split_tokens(inst.text);
  if (tokens.empty()) {
    return;
  }

  if (inst.op == "label") {
    frame.last_label = normalize_label(tokens[0]);
    return;
  }

  if (inst.op == "alloca") {
    // "%x = alloca i32, align 4"
    size_t type_idx = 0;
    for (size_t i = 0; i < tokens.size(); i++) {
      if (tokens[i] == "alloca") {
        type_idx = i + 1;
        break;
      }
    }
    std::string type = type_idx < tokens.size() ? tokens[type_idx] : "i8";
    size_t size = type_size_bytes(type);
    size_t align = 8;
    auto align_it = inst.text.find("align");
    if (align_it != std::string::npos) {
      align = std::strtoull(inst.text.substr(align_it + 5).c_str(), nullptr, 10);
      if (align == 0) align = 1;
    }
    size_t aligned = (state.stack_top + align - 1) / align * align;
    state.stack_top = aligned + size;
    frame.regs[inst.dest] = {static_cast<uint64_t>(aligned)};
    return;
  }

  if (inst.op == "store") {
    // "store i32 %x, ptr %y"
    if (tokens.size() < 4) return;
    std::string value_token = tokens[2];
    if (value_token.back() == ',') value_token.pop_back();
    std::string ptr_token = tokens[4];
    if (ptr_token.back() == ',') ptr_token.pop_back();
    Value val = parse_operand(frame.regs, value_token);
    Value ptr = parse_operand(frame.regs, ptr_token);
    size_t size = type_size_bytes(tokens[1]);
    store_value(state, ptr.u, val, size);
    return;
  }

  if (inst.op == "load") {
    // "%x = load i32, ptr %y"
    if (tokens.size() < 4) return;
    std::string ptr_token = tokens[4];
    if (ptr_token.back() == ',') ptr_token.pop_back();
    Value ptr = parse_operand(frame.regs, ptr_token);
    size_t size = type_size_bytes(tokens[2]);
    Value val = load_value(state, ptr.u, size);
    frame.regs[inst.dest] = val;
    return;
  }

  if (inst.op == "getelementptr") {
    // "getelementptr i8, ptr %p, i32 %idx"
    uint64_t base = 0;
    size_t elem_size = 1;
    for (size_t i = 0; i < tokens.size(); i++) {
      if (tokens[i] == "getelementptr" && i + 1 < tokens.size()) {
        elem_size = type_size_bytes(tokens[i + 1]);
      }
      if (tokens[i] == "ptr" && i + 1 < tokens.size()) {
        Value ptr = parse_operand(frame.regs, tokens[i + 1]);
        base = ptr.u;
      }
    }
    uint64_t index = 0;
    for (size_t i = 0; i < tokens.size(); i++) {
      if (tokens[i].rfind("i", 0) == 0 && i + 1 < tokens.size()) {
        Value idx = parse_operand(frame.regs, tokens[i + 1]);
        index = idx.u;
      }
    }
    frame.regs[inst.dest] = {base + index * elem_size};
    return;
  }

  if (inst.op == "add" || inst.op == "sub" || inst.op == "and" || inst.op == "xor") {
    // "%x = add i32 %a, %b"
    if (tokens.size() < 5) return;
    Value lhs = parse_operand(frame.regs, tokens[3]);
    std::string rhs_token = tokens[4];
    if (rhs_token.back() == ',') rhs_token.pop_back();
    Value rhs = parse_operand(frame.regs, rhs_token);
    uint64_t result = 0;
    if (inst.op == "add") result = lhs.u + rhs.u;
    if (inst.op == "sub") result = lhs.u - rhs.u;
    if (inst.op == "and") result = lhs.u & rhs.u;
    if (inst.op == "xor") result = lhs.u ^ rhs.u;
    frame.regs[inst.dest] = {result};
    return;
  }

  if (inst.op == "mul" || inst.op == "or" || inst.op == "shl" ||
      inst.op == "lshr" || inst.op == "ashr") {
    if (tokens.size() < 5) return;
    Value lhs = parse_operand(frame.regs, tokens[3]);
    std::string rhs_token = tokens[4];
    if (rhs_token.back() == ',') rhs_token.pop_back();
    Value rhs = parse_operand(frame.regs, rhs_token);
    uint64_t result = 0;
    if (inst.op == "mul") result = lhs.u * rhs.u;
    if (inst.op == "or") result = lhs.u | rhs.u;
    if (inst.op == "shl") result = lhs.u << rhs.u;
    if (inst.op == "lshr") result = lhs.u >> rhs.u;
    if (inst.op == "ashr") result = static_cast<uint64_t>(static_cast<int64_t>(lhs.u) >> rhs.u);
    frame.regs[inst.dest] = {result};
    return;
  }

  if (inst.op == "zext") {
    // "%x = zext i8 %a to i32"
    if (tokens.size() < 4) return;
    Value val = parse_operand(frame.regs, tokens[3]);
    frame.regs[inst.dest] = val;
    return;
  }

  if (inst.op == "sext" || inst.op == "trunc") {
    if (tokens.size() < 4) return;
    Value val = parse_operand(frame.regs, tokens[3]);
    frame.regs[inst.dest] = val;
    return;
  }

  if (inst.op == "select") {
    // "%x = select i1 %cond, i32 %a, i32 %b"
    if (tokens.size() < 7) return;
    std::string cond_token = tokens[3];
    if (cond_token.back() == ',') cond_token.pop_back();
    Value cond = parse_operand(frame.regs, cond_token);
    std::string true_token = tokens[4];
    if (true_token.back() == ',') true_token.pop_back();
    std::string false_token = tokens[6];
    Value chosen = cond.u ? parse_operand(frame.regs, true_token)
                          : parse_operand(frame.regs, false_token);
    frame.regs[inst.dest] = chosen;
    return;
  }

  if (inst.op == "icmp") {
    // "%x = icmp eq i32 %a, %b"
    if (tokens.size() < 6) return;
    std::string pred = tokens[2];
    Value lhs = parse_operand(frame.regs, tokens[4]);
    std::string rhs_token = tokens[5];
    if (rhs_token.back() == ',') rhs_token.pop_back();
    Value rhs = parse_operand(frame.regs, rhs_token);
    uint64_t result = 0;
    if (pred == "eq") result = lhs.u == rhs.u;
    else if (pred == "ne") result = lhs.u != rhs.u;
    else if (pred == "ult") result = lhs.u < rhs.u;
    else if (pred == "ugt") result = lhs.u > rhs.u;
    else if (pred == "ule") result = lhs.u <= rhs.u;
    else if (pred == "uge") result = lhs.u >= rhs.u;
    frame.regs[inst.dest] = {result};
    return;
  }

  if (inst.op == "phi") {
    // "%x = phi i32 [ %a, %label1 ], [ %b, %label2 ]"
    size_t pos = 0;
    while (true) {
      pos = inst.text.find('[', pos);
      if (pos == std::string::npos) {
        break;
      }
      auto end = inst.text.find(']', pos);
      if (end == std::string::npos) {
        break;
      }
      std::string slice = inst.text.substr(pos + 1, end - pos - 1);
      auto comma = slice.find(',');
      if (comma != std::string::npos) {
        std::string value_token = slice.substr(0, comma);
        std::string label_token = slice.substr(comma + 1);
        std::istringstream vss(value_token);
        std::string vtok;
        vss >> vtok;
        std::istringstream lss(label_token);
        std::string ltok;
        lss >> ltok;
        std::string label = normalize_label(ltok);
        if (!frame.prev_label.empty() && label == frame.prev_label) {
          frame.regs[inst.dest] = parse_operand(frame.regs, vtok);
          return;
        }
      }
      pos = end + 1;
    }
    return;
  }

  if (inst.op == "call") {
    return;
  }

  if (inst.op == "br") {
    return;
  }

  if (inst.op == "ret") {
    return;
  }
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
  vm->state.memory.clear();
  vm->state.stack_top = 0;
  size_t dict_base = 0x10000;
  size_t chunk_base = 0x20000;
  size_t key_base = 0x30000;
  ensure_memory(vm->state, key_base + 128);
  if (!vm->state.dict.empty()) {
    ensure_memory(vm->state, dict_base + vm->state.dict.size());
    std::copy(vm->state.dict.begin(), vm->state.dict.end(), vm->state.memory.begin() + dict_base);
  }
  if (!vm->state.chunk.empty()) {
    ensure_memory(vm->state, chunk_base + vm->state.chunk.size());
    std::copy(vm->state.chunk.begin(), vm->state.chunk.end(), vm->state.memory.begin() + chunk_base);
  }
  if (!vm->state.key_hex.empty()) {
    ensure_memory(vm->state, key_base + vm->state.key_hex.size());
    std::copy(vm->state.key_hex.begin(), vm->state.key_hex.end(), vm->state.memory.begin() + key_base);
  }
}

void diter_vm_execute(DiterVm* vm) {
  if (!vm) {
    return;
  }
  vm->state.op_counts.clear();
  if (vm->state.function_order.empty()) {
    return;
  }
  Frame entry;
  entry.func = vm->state.function_order.front();
  entry.saved_stack_top = vm->state.stack_top;
  std::vector<Frame> stack;
  stack.push_back(std::move(entry));

  while (!stack.empty()) {
    Frame &frame = stack.back();
    auto fn_it = vm->state.functions.find(frame.func);
    if (fn_it == vm->state.functions.end()) {
      stack.pop_back();
      continue;
    }
    auto &func = fn_it->second;
    if (frame.pc >= func.insts.size()) {
      vm->state.stack_top = frame.saved_stack_top;
      stack.pop_back();
      if (!stack.empty() && !frame.ret_dest.empty()) {
        stack.back().regs[frame.ret_dest] = {0};
      }
      continue;
    }

    Instruction inst = func.insts[frame.pc++];

    if (inst.op == "call") {
      std::string callee;
      auto at = inst.text.find("@");
      if (at != std::string::npos) {
        auto end = inst.text.find("(", at);
        callee = inst.text.substr(at + 1, end == std::string::npos ? std::string::npos : end - at - 1);
      }
      if (!callee.empty() && vm->state.functions.find(callee) != vm->state.functions.end()) {
        Frame next;
        next.func = callee;
        next.saved_stack_top = vm->state.stack_top;
        next.ret_dest = inst.dest;
        stack.push_back(std::move(next));
        continue;
      }
      if (!inst.dest.empty()) {
        frame.regs[inst.dest] = {0};
      }
      continue;
    }

    if (inst.op == "br") {
      auto tokens = split_tokens(inst.text);
      std::string target;
      if (tokens.size() >= 3 && tokens[1] == "label") {
        target = tokens[2];
      } else if (tokens.size() >= 7 && tokens[1] == "i1") {
        std::string cond_token = tokens[2];
        if (cond_token.back() == ',') cond_token.pop_back();
        Value cond = parse_operand(frame.regs, cond_token);
        std::string true_label = tokens[4];
        std::string false_label = tokens[6];
        target = (cond.u != 0) ? true_label : false_label;
      }
      if (!target.empty()) {
        frame.prev_label = frame.last_label;
        target = normalize_label(target);
        auto it = func.labels.find(target);
        if (it != func.labels.end()) {
          frame.pc = it->second;
        }
      }
      continue;
    }

    if (inst.op == "ret") {
      Value ret_value{};
      auto tokens = split_tokens(inst.text);
      if (tokens.size() >= 3) {
        ret_value = parse_operand(frame.regs, tokens[2]);
      }
      vm->state.stack_top = frame.saved_stack_top;
      stack.pop_back();
      if (!stack.empty() && !frame.ret_dest.empty()) {
        stack.back().regs[frame.ret_dest] = ret_value;
      }
      continue;
    }

    execute_instruction(vm->state, frame, inst);
    vm->state.executed++;
  }
}

size_t diter_vm_instruction_count(const DiterVm* vm) {
  if (!vm) {
    return 0;
  }
  return vm->state.instructions.size();
}
