#include "diter_vm.h"

#include <rapidjson/document.h>

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
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
  uint64_t env_instance_addr = 0;
  uint64_t instance_addr = 0;
  uint64_t env_mem_addr = 0;
  uint64_t linear_mem_base = 0;
  uint64_t linear_mem_size = 0;
  uint64_t heap_ptr = 0;
  Value last_return_value{};
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

void ensure_memory(VmState &state, size_t size) {
  if (state.memory.size() < size) {
    state.memory.resize(size, 0);
  }
}

void load_data_segments(VmState &state, const std::string &path) {
  auto doc = load_json(path);
  if (!doc.IsObject()) {
    return;
  }
  auto segs_it = doc.FindMember("segments");
  if (segs_it == doc.MemberEnd() || !segs_it->value.IsArray()) {
    return;
  }
  for (const auto &seg : segs_it->value.GetArray()) {
    if (!seg.IsObject()) {
      continue;
    }
    auto off_it = seg.FindMember("offset");
    auto bytes_it = seg.FindMember("bytes");
    if (off_it == seg.MemberEnd() || bytes_it == seg.MemberEnd()) {
      continue;
    }
    if (!off_it->value.IsUint64() || !bytes_it->value.IsArray()) {
      continue;
    }
    uint64_t offset = off_it->value.GetUint64();
    uint64_t base = state.linear_mem_base + offset;
    ensure_memory(state, base + bytes_it->value.Size());
    for (rapidjson::SizeType i = 0; i < bytes_it->value.Size(); i++) {
      if (bytes_it->value[i].IsUint()) {
        state.memory[base + i] = static_cast<uint8_t>(bytes_it->value[i].GetUint());
      }
    }
  }
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

void store_u32(VmState &state, uint64_t addr, uint32_t value) {
  ensure_memory(state, addr + 4);
  state.memory[addr + 0] = static_cast<uint8_t>(value & 0xff);
  state.memory[addr + 1] = static_cast<uint8_t>((value >> 8) & 0xff);
  state.memory[addr + 2] = static_cast<uint8_t>((value >> 16) & 0xff);
  state.memory[addr + 3] = static_cast<uint8_t>((value >> 24) & 0xff);
}

void store_u64(VmState &state, uint64_t addr, uint64_t value) {
  ensure_memory(state, addr + 8);
  for (size_t i = 0; i < 8; i++) {
    state.memory[addr + i] = static_cast<uint8_t>((value >> (i * 8)) & 0xff);
  }
}

void init_instance_layout(VmState &state) {
  state.linear_mem_base = 0;
  state.linear_mem_size = 8 * 1024 * 1024;
  state.instance_addr = state.linear_mem_size + 0x1000;
  state.env_instance_addr = state.instance_addr + 0x100;
  state.env_mem_addr = state.instance_addr + 0x200;
  state.heap_ptr = 0x140000;

  ensure_memory(state, state.env_mem_addr + 0x200);

  store_u64(state, state.instance_addr + 0, state.env_instance_addr);
  store_u64(state, state.instance_addr + 8, state.env_mem_addr);
  store_u32(state, state.instance_addr + 16, 83360u);
  store_u32(state, state.instance_addr + 20, 0);
  store_u64(state, state.instance_addr + 24, 0);
  store_u32(state, state.instance_addr + 32, 0);
  store_u32(state, state.instance_addr + 36, 0);

  store_u64(state, state.env_mem_addr + 0, state.linear_mem_base);
  store_u64(state, state.env_mem_addr + 8, state.linear_mem_base + state.linear_mem_size);
  store_u32(state, state.env_mem_addr + 16, 65536);
  store_u64(state, state.env_mem_addr + 24, state.linear_mem_size / 65536);
  store_u64(state, state.env_mem_addr + 32, 8192);
  store_u64(state, state.env_mem_addr + 40, state.linear_mem_size);
  state.memory[state.env_mem_addr + 48] = 0;

  state.stack_top = state.linear_mem_base + state.linear_mem_size + 0x1000;
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

std::string strip_trailing(const std::string &token) {
  size_t end = token.size();
  while (end > 0) {
    char c = token[end - 1];
    if (c == ',' || c == ')' || c == ':') {
      end--;
      continue;
    }
    break;
  }
  return token.substr(0, end);
}

std::string strip_leading(const std::string &token) {
  size_t start = 0;
  while (start < token.size()) {
    char c = token[start];
    if (c == '(' || c == ',') {
      start++;
      continue;
    }
    break;
  }
  return token.substr(start);
}

std::string strip_punct(const std::string &token) {
  return strip_trailing(strip_leading(token));
}

std::vector<std::string> parse_call_args(const std::string &text) {
  auto open = text.find('(');
  auto close = text.rfind(')');
  if (open == std::string::npos || close == std::string::npos || close <= open) {
    return {};
  }
  std::string args = text.substr(open + 1, close - open - 1);
  std::vector<std::string> out;
  std::string current;
  int parens = 0;
  for (char c : args) {
    if (c == '(') parens++;
    if (c == ')') parens--;
    if (c == ',' && parens == 0) {
      if (!current.empty()) {
        out.push_back(current);
        current.clear();
      }
      continue;
    }
    current.push_back(c);
  }
  if (!current.empty()) {
    out.push_back(current);
  }
  return out;
}

Value parse_last_token(const std::unordered_map<std::string, Value> &regs,
                       const std::string &arg) {
  auto tokens = split_tokens(arg);
  if (tokens.empty()) {
    return {};
  }
  std::string last = strip_punct(tokens.back());
  return parse_operand(regs, last);
}

bool parse_indices(const std::unordered_map<std::string, Value> &regs,
                   const std::vector<std::string> &tokens,
                   std::vector<uint64_t> &indices) {
  indices.clear();
  for (size_t i = 0; i + 1 < tokens.size(); i++) {
    if (tokens[i].rfind("i", 0) == 0) {
      Value idx = parse_operand(regs, strip_punct(tokens[i + 1]));
      indices.push_back(idx.u);
    }
  }
  return !indices.empty();
}

uint64_t struct_field_offset(const std::string &type_name, uint64_t field) {
  if (type_name == "%struct.diter_core") {
    static const uint64_t offsets[] = {0, 8, 16, 24};
    return field < 4 ? offsets[field] : 0;
  }
  if (type_name == "%struct.wasm_rt_memory_t") {
    static const uint64_t offsets[] = {0, 8, 16, 24, 32, 40, 48};
    return field < 7 ? offsets[field] : 0;
  }
  if (type_name == "%struct.wasm_rt_funcref_table_t") {
    static const uint64_t offsets[] = {0, 8, 12};
    return field < 3 ? offsets[field] : 0;
  }
  return 0;
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
    std::string type = type_idx < tokens.size() ? strip_punct(tokens[type_idx]) : "i8";
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
    std::string value_token = strip_punct(tokens[2]);
    std::string ptr_token = strip_punct(tokens.back());
    Value val = parse_operand(frame.regs, value_token);
    Value ptr = parse_operand(frame.regs, ptr_token);
    size_t size = type_size_bytes(strip_punct(tokens[1]));
    store_value(state, ptr.u, val, size);
    return;
  }

  if (inst.op == "load") {
    // "%x = load i32, ptr %y"
    if (tokens.size() < 4) return;
    std::string ptr_token = strip_punct(tokens.back());
    Value ptr = parse_operand(frame.regs, ptr_token);
    size_t size = type_size_bytes(strip_punct(tokens[2]));
    Value val = load_value(state, ptr.u, size);
    frame.regs[inst.dest] = val;
    return;
  }

  if (inst.op == "getelementptr") {
    // "getelementptr i8, ptr %p, i32 %idx"
    uint64_t base = 0;
    size_t elem_size = 1;
    std::string type_name;
    for (size_t i = 0; i < tokens.size(); i++) {
      if (tokens[i] == "getelementptr" && i + 1 < tokens.size()) {
        type_name = strip_punct(tokens[i + 1]);
        elem_size = type_size_bytes(type_name);
      }
      if (tokens[i] == "ptr" && i + 1 < tokens.size()) {
        Value ptr = parse_operand(frame.regs, strip_punct(tokens[i + 1]));
        base = ptr.u;
      }
    }
    std::vector<uint64_t> indices;
    parse_indices(frame.regs, tokens, indices);
    if (type_name.rfind("%struct.", 0) == 0 && indices.size() >= 2 && indices[0] == 0) {
      uint64_t offset = struct_field_offset(type_name, indices[1]);
      frame.regs[inst.dest] = {base + offset};
      return;
    }
    uint64_t index = indices.empty() ? 0 : indices.back();
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

  if (inst.op == "bitcast" || inst.op == "ptrtoint" || inst.op == "inttoptr") {
    if (tokens.size() < 3) return;
    Value val = parse_operand(frame.regs, strip_punct(tokens.back()));
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
    else if (pred == "slt") result = static_cast<int64_t>(lhs.u) < static_cast<int64_t>(rhs.u);
    else if (pred == "sgt") result = static_cast<int64_t>(lhs.u) > static_cast<int64_t>(rhs.u);
    else if (pred == "sle") result = static_cast<int64_t>(lhs.u) <= static_cast<int64_t>(rhs.u);
    else if (pred == "sge") result = static_cast<int64_t>(lhs.u) >= static_cast<int64_t>(rhs.u);
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
    init_instance_layout(vm->state);
    load_data_segments(vm->state, "build/diter_core_data_segments.json");
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
  init_instance_layout(vm->state);
  load_data_segments(vm->state, "build/diter_core_data_segments.json");
  size_t dict_base = vm->state.linear_mem_base + 0x10000;
  size_t chunk_base = vm->state.linear_mem_base + 0x20000;
  size_t key_base = vm->state.linear_mem_base + 0x30000;
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

      auto args = parse_call_args(inst.text);
      if (callee == "diter_env_abort") {
        throw std::runtime_error("VM abort");
      }
      if (callee == "diter_env_memory" && args.size() >= 1) {
        if (!inst.dest.empty()) {
          frame.regs[inst.dest] = {vm->state.env_mem_addr};
        }
        continue;
      }
      if (callee == "diter_env_sbrk" && args.size() >= 2) {
        auto incr = parse_last_token(frame.regs, args[1]);
        uint64_t old = vm->state.heap_ptr;
        vm->state.heap_ptr += incr.u;
        ensure_memory(vm->state, vm->state.heap_ptr + 16);
        if (!inst.dest.empty()) frame.regs[inst.dest] = {old};
        continue;
      }
      if (callee == "wasm_rt_allocate_funcref_table") {
        if (!inst.dest.empty()) frame.regs[inst.dest] = {0};
        continue;
      }
      if (callee.find("llvm.memcpy") != std::string::npos && args.size() >= 3) {
        auto dest = parse_last_token(frame.regs, args[0]);
        auto src = parse_last_token(frame.regs, args[1]);
        auto len = parse_last_token(frame.regs, args[2]);
        ensure_memory(vm->state, dest.u + len.u);
        ensure_memory(vm->state, src.u + len.u);
        std::memmove(&vm->state.memory[dest.u], &vm->state.memory[src.u], len.u);
        if (!inst.dest.empty()) frame.regs[inst.dest] = {0};
        continue;
      }
      if (callee.find("llvm.memset") != std::string::npos && args.size() >= 3) {
        auto dest = parse_last_token(frame.regs, args[0]);
        auto val = parse_last_token(frame.regs, args[1]);
        auto len = parse_last_token(frame.regs, args[2]);
        ensure_memory(vm->state, dest.u + len.u);
        std::memset(&vm->state.memory[dest.u], static_cast<int>(val.u & 0xff), len.u);
        if (!inst.dest.empty()) frame.regs[inst.dest] = {0};
        continue;
      }

      if (!callee.empty() && vm->state.functions.find(callee) != vm->state.functions.end()) {
        Frame next;
        next.func = callee;
        next.saved_stack_top = vm->state.stack_top;
        next.ret_dest = inst.dest;
        for (size_t i = 0; i < args.size(); i++) {
          std::string reg_name = "%" + std::to_string(i);
          next.regs[reg_name] = parse_last_token(frame.regs, args[i]);
        }
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
      } else if (stack.empty()) {
        vm->state.last_return_value = ret_value;
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

uint64_t diter_vm_call(DiterVm* vm, const char* func, const uint64_t* args, size_t arg_count) {
  if (!vm || !func) {
    return 0;
  }
  auto it = vm->state.functions.find(func);
  if (it == vm->state.functions.end()) {
    return 0;
  }
  vm->state.last_return_value = {};
  Frame entry;
  entry.func = func;
  entry.saved_stack_top = vm->state.stack_top;
  for (size_t i = 0; i < arg_count; i++) {
    std::string reg_name = "%" + std::to_string(i);
    entry.regs[reg_name] = {args[i]};
  }
  std::vector<Frame> stack;
  stack.push_back(std::move(entry));

  while (!stack.empty()) {
    Frame &frame = stack.back();
    auto fn_it = vm->state.functions.find(frame.func);
    if (fn_it == vm->state.functions.end()) {
      stack.pop_back();
      continue;
    }
    auto &func_state = fn_it->second;
    if (frame.pc >= func_state.insts.size()) {
      vm->state.stack_top = frame.saved_stack_top;
      stack.pop_back();
      if (!stack.empty() && !frame.ret_dest.empty()) {
        stack.back().regs[frame.ret_dest] = {0};
      } else if (stack.empty()) {
        vm->state.last_return_value = {0};
      }
      continue;
    }
    Instruction inst = func_state.insts[frame.pc++];

    if (inst.op == "call") {
      std::string callee;
      auto at = inst.text.find("@");
      if (at != std::string::npos) {
        auto end = inst.text.find("(", at);
        callee = inst.text.substr(at + 1, end == std::string::npos ? std::string::npos : end - at - 1);
      }
      auto call_args = parse_call_args(inst.text);
      if (callee == "diter_env_abort") {
        throw std::runtime_error("VM abort");
      }
      if (callee == "diter_env_memory" && call_args.size() >= 1) {
        if (!inst.dest.empty()) {
          frame.regs[inst.dest] = {vm->state.env_mem_addr};
        }
        continue;
      }
      if (callee == "diter_env_sbrk" && call_args.size() >= 2) {
        auto incr = parse_last_token(frame.regs, call_args[1]);
        uint64_t old = vm->state.heap_ptr;
        vm->state.heap_ptr += incr.u;
        ensure_memory(vm->state, vm->state.heap_ptr + 16);
        if (!inst.dest.empty()) {
          frame.regs[inst.dest] = {old};
        }
        continue;
      }
      if (callee == "wasm_rt_allocate_funcref_table") {
        if (!inst.dest.empty()) frame.regs[inst.dest] = {0};
        continue;
      }
      if (callee.find("llvm.memcpy") != std::string::npos && call_args.size() >= 3) {
        auto dest = parse_last_token(frame.regs, call_args[0]);
        auto src = parse_last_token(frame.regs, call_args[1]);
        auto len = parse_last_token(frame.regs, call_args[2]);
        ensure_memory(vm->state, dest.u + len.u);
        ensure_memory(vm->state, src.u + len.u);
        std::memmove(&vm->state.memory[dest.u], &vm->state.memory[src.u], len.u);
        if (!inst.dest.empty()) frame.regs[inst.dest] = {0};
        continue;
      }
      if (callee.find("llvm.memset") != std::string::npos && call_args.size() >= 3) {
        auto dest = parse_last_token(frame.regs, call_args[0]);
        auto val = parse_last_token(frame.regs, call_args[1]);
        auto len = parse_last_token(frame.regs, call_args[2]);
        ensure_memory(vm->state, dest.u + len.u);
        std::memset(&vm->state.memory[dest.u], static_cast<int>(val.u & 0xff), len.u);
        if (!inst.dest.empty()) frame.regs[inst.dest] = {0};
        continue;
      }
      if (!callee.empty() && vm->state.functions.find(callee) != vm->state.functions.end()) {
        Frame next;
        next.func = callee;
        next.saved_stack_top = vm->state.stack_top;
        next.ret_dest = inst.dest;
        for (size_t i = 0; i < call_args.size(); i++) {
          std::string reg_name = "%" + std::to_string(i);
          next.regs[reg_name] = parse_last_token(frame.regs, call_args[i]);
        }
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
        auto it_label = func_state.labels.find(target);
        if (it_label != func_state.labels.end()) {
          frame.pc = it_label->second;
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
      } else if (stack.empty()) {
        vm->state.last_return_value = ret_value;
      }
      continue;
    }

    execute_instruction(vm->state, frame, inst);
    vm->state.executed++;
  }

  return vm->state.last_return_value.u;
}

const uint8_t* diter_vm_memory(const DiterVm* vm) {
  if (!vm) return nullptr;
  return vm->state.memory.data();
}

size_t diter_vm_memory_size(const DiterVm* vm) {
  if (!vm) return 0;
  return vm->state.memory.size();
}

uint64_t diter_vm_instance_ptr(const DiterVm* vm) {
  if (!vm) return 0;
  return vm->state.instance_addr;
}

uint64_t diter_vm_env_ptr(const DiterVm* vm) {
  if (!vm) return 0;
  return vm->state.env_instance_addr;
}

uint64_t diter_vm_linear_base(const DiterVm* vm) {
  if (!vm) return 0;
  return vm->state.linear_mem_base;
}
