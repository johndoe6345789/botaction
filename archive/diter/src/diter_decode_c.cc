#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cctype>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include <dlfcn.h>

#include <rapidjson/document.h>

namespace {

enum class ValueType {
  kNone,
  kString,
  kBytes,
  kBool,
  kInt,
};

struct Value {
  ValueType type = ValueType::kNone;
  std::string str;
  std::vector<uint8_t> bytes;
  bool boolean = false;
  uint64_t integer = 0;
};

struct ActionNode {
  std::string name;
  std::string action;
  std::unordered_map<std::string, std::string> params;
  std::unordered_map<std::string, std::string> outputs;
  bool optional = false;
};

struct Workflow {
  std::unordered_map<std::string, ActionNode> nodes;
  std::unordered_map<std::string, std::vector<std::string>> edges;
  std::unordered_map<std::string, Value> inputs;
};

struct DiterApi {
  void *handle = nullptr;
  void *(*create)() = nullptr;
  void (*destroy)(void *) = nullptr;
  void (*init)(void *) = nullptr;
  void (*set_key_hex)(void *, const char *) = nullptr;
  int (*write_dict)(void *, const uint8_t *, size_t) = nullptr;
  int (*write_chunk)(void *, const uint8_t *, size_t) = nullptr;
  int (*pump)(void *) = nullptr;
  const uint8_t *(*output)(void *, uint32_t *) = nullptr;
  void (*output_advance)(void *) = nullptr;
};

std::string workflow_default_path() {
  return "build/runbooks/diter_massive_workflow.json";
}

std::string read_text(const std::string &path) {
  std::ifstream file(path, std::ios::in | std::ios::binary);
  if (!file) {
    throw std::runtime_error("Failed to read file: " + path);
  }
  std::string contents((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
  return contents;
}

std::vector<uint8_t> read_bytes(const std::string &path) {
  std::ifstream file(path, std::ios::in | std::ios::binary);
  if (!file) {
    throw std::runtime_error("Failed to read file: " + path);
  }
  std::vector<uint8_t> data((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
  return data;
}

bool is_base64_char(char c) {
  return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
         (c >= '0' && c <= '9') || c == '+' || c == '/' || c == '=';
}

int base64_value(char c) {
  if (c >= 'A' && c <= 'Z') return c - 'A';
  if (c >= 'a' && c <= 'z') return c - 'a' + 26;
  if (c >= '0' && c <= '9') return c - '0' + 52;
  if (c == '+') return 62;
  if (c == '/') return 63;
  if (c == '=') return -2;
  return -1;
}

std::vector<uint8_t> base64_decode_clean(const std::string &input) {
  std::vector<uint8_t> out;
  out.reserve(input.size() * 3 / 4);
  int vals[4];
  int val_pos = 0;
  for (char c : input) {
    int v = base64_value(c);
    if (v == -1) {
      if (!is_base64_char(c)) {
        continue;
      }
      v = -1;
    }
    if (v == -1) {
      continue;
    }
    vals[val_pos++] = v;
    if (val_pos == 4) {
      if (vals[0] == -2 || vals[1] == -2) {
        break;
      }
      out.push_back(static_cast<uint8_t>((vals[0] << 2) | (vals[1] >> 4)));
      if (vals[2] != -2) {
        out.push_back(static_cast<uint8_t>(((vals[1] & 0x0f) << 4) | (vals[2] >> 2)));
      }
      if (vals[3] != -2 && vals[2] != -2) {
        out.push_back(static_cast<uint8_t>(((vals[2] & 0x03) << 6) | vals[3]));
      }
      val_pos = 0;
    }
  }
  return out;
}

bool is_hex_char(char c) {
  return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

std::string clean_hex(const std::string &text) {
  std::string out;
  out.reserve(text.size());
  for (char c : text) {
    if (is_hex_char(c)) {
      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(c))));
    }
  }
  if (out.size() >= 40) {
    out.resize(40);
  }
  return out;
}

std::string extract_key_hex(const std::string &text) {
  auto pos = text.find("module.exports");
  if (pos != std::string::npos) {
    auto eq = text.find('=', pos);
    if (eq != std::string::npos) {
      auto cur = text.find_first_not_of(" \t\r\n", eq + 1);
      if (cur != std::string::npos && (text[cur] == '"' || text[cur] == '\'')) {
        char quote = text[cur++];
        auto end = text.find(quote, cur);
        if (end != std::string::npos) {
          std::string candidate = clean_hex(text.substr(cur, end - cur));
          if (candidate.size() >= 40) {
            return candidate;
          }
        }
      }
    }
  }

  size_t run = 0;
  for (size_t i = 0; i < text.size(); i++) {
    if (is_hex_char(text[i])) {
      run++;
      if (run >= 40) {
        size_t start = i + 1 - run;
        return clean_hex(text.substr(start, run));
      }
    } else {
      run = 0;
    }
  }
  return "";
}

Value make_string(const std::string &value) {
  Value out;
  out.type = ValueType::kString;
  out.str = value;
  return out;
}

Value make_bytes(const std::vector<uint8_t> &data) {
  Value out;
  out.type = ValueType::kBytes;
  out.bytes = data;
  return out;
}

Value make_bool(bool value) {
  Value out;
  out.type = ValueType::kBool;
  out.boolean = value;
  return out;
}

Value make_int(uint64_t value) {
  Value out;
  out.type = ValueType::kInt;
  out.integer = value;
  return out;
}

std::string resolve_string(const std::unordered_map<std::string, Value> &context,
                           const std::string &value) {
  if (!value.empty() && value[0] == '@') {
    auto it = context.find(value.substr(1));
    if (it != context.end() && it->second.type == ValueType::kString) {
      return it->second.str;
    }
  }
  return value;
}

const Value *resolve_value(const std::unordered_map<std::string, Value> &context,
                           const std::string &value) {
  if (!value.empty() && value[0] == '@') {
    auto it = context.find(value.substr(1));
    if (it != context.end()) {
      return &it->second;
    }
    return nullptr;
  }
  return nullptr;
}

void apply_outputs(std::unordered_map<std::string, Value> &context,
                   const std::unordered_map<std::string, std::string> &outputs,
                   const std::unordered_map<std::string, Value> &result) {
  if (!outputs.empty()) {
    for (const auto &pair : outputs) {
      auto it = result.find(pair.first);
      if (it != result.end()) {
        context[pair.second] = it->second;
      }
    }
    return;
  }
  for (const auto &pair : result) {
    context[pair.first] = pair.second;
  }
}

void parse_outputs(const rapidjson::Value &outputs,
                   std::unordered_map<std::string, std::string> &out) {
  if (!outputs.IsObject()) {
    return;
  }
  for (auto it = outputs.MemberBegin(); it != outputs.MemberEnd(); ++it) {
    if (it->name.IsString() && it->value.IsString()) {
      out[it->name.GetString()] = it->value.GetString();
    }
  }
}

void parse_params(const rapidjson::Value &params, ActionNode &node) {
  if (!params.IsObject()) {
    return;
  }
  auto action_it = params.FindMember("action");
  if (action_it != params.MemberEnd() && action_it->value.IsString()) {
    node.action = action_it->value.GetString();
  }
  auto optional_it = params.FindMember("optional");
  if (optional_it != params.MemberEnd() && optional_it->value.IsBool()) {
    node.optional = optional_it->value.GetBool();
  }
  for (auto it = params.MemberBegin(); it != params.MemberEnd(); ++it) {
    if (!it->name.IsString()) {
      continue;
    }
    std::string key = it->name.GetString();
    if (key == "outputs" || key == "action" || key == "optional") {
      continue;
    }
    if (it->value.IsString()) {
      node.params[key] = it->value.GetString();
    } else if (it->value.IsBool()) {
      node.params[key] = it->value.GetBool() ? "true" : "false";
    } else if (it->value.IsInt64()) {
      node.params[key] = std::to_string(it->value.GetInt64());
    }
  }
  auto outputs_it = params.FindMember("outputs");
  if (outputs_it != params.MemberEnd()) {
    parse_outputs(outputs_it->value, node.outputs);
  }
}

void parse_nodes(const rapidjson::Value &nodes_value, Workflow &workflow) {
  if (!nodes_value.IsArray()) {
    return;
  }
  for (const auto &node_val : nodes_value.GetArray()) {
    if (!node_val.IsObject()) {
      continue;
    }
    auto name_it = node_val.FindMember("name");
    auto type_it = node_val.FindMember("type");
    if (name_it == node_val.MemberEnd() || !name_it->value.IsString()) {
      continue;
    }
    std::string name = name_it->value.GetString();
    std::string type = type_it != node_val.MemberEnd() && type_it->value.IsString()
      ? type_it->value.GetString()
      : "";
    if (type != "diter.action") {
      continue;
    }
    ActionNode node;
    node.name = name;
    auto params_it = node_val.FindMember("parameters");
    if (params_it != node_val.MemberEnd()) {
      parse_params(params_it->value, node);
    }
    workflow.nodes[name] = node;
  }
}

void parse_connections(const rapidjson::Value &connections_value, Workflow &workflow) {
  if (!connections_value.IsObject()) {
    return;
  }
  for (auto it = connections_value.MemberBegin(); it != connections_value.MemberEnd(); ++it) {
    if (!it->name.IsString() || !it->value.IsObject()) {
      continue;
    }
    std::string src = it->name.GetString();
    auto main_it = it->value.FindMember("main");
    if (main_it == it->value.MemberEnd() || !main_it->value.IsObject()) {
      continue;
    }
    auto idx_it = main_it->value.FindMember("0");
    if (idx_it == main_it->value.MemberEnd() || !idx_it->value.IsArray()) {
      continue;
    }
    for (const auto &target : idx_it->value.GetArray()) {
      if (!target.IsObject()) {
        continue;
      }
      auto node_it = target.FindMember("node");
      if (node_it != target.MemberEnd() && node_it->value.IsString()) {
        workflow.edges[src].push_back(node_it->value.GetString());
      }
    }
  }
}

void parse_meta_inputs(const rapidjson::Value &meta_value, Workflow &workflow) {
  if (!meta_value.IsObject()) {
    return;
  }
  auto inputs_it = meta_value.FindMember("inputs");
  if (inputs_it == meta_value.MemberEnd() || !inputs_it->value.IsObject()) {
    return;
  }
  for (auto it = inputs_it->value.MemberBegin(); it != inputs_it->value.MemberEnd(); ++it) {
    if (!it->name.IsString()) {
      continue;
    }
    std::string key = it->name.GetString();
    if (it->value.IsString()) {
      workflow.inputs[key] = make_string(it->value.GetString());
    } else if (it->value.IsBool()) {
      workflow.inputs[key] = make_bool(it->value.GetBool());
    } else if (it->value.IsInt64()) {
      workflow.inputs[key] = make_int(it->value.GetInt64());
    }
  }
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

void merge_workflow(const std::string &path, Workflow &workflow) {
  auto doc = load_json(path);
  if (!doc.IsObject()) {
    return;
  }
  auto nodes_it = doc.FindMember("nodes");
  if (nodes_it != doc.MemberEnd()) {
    parse_nodes(nodes_it->value, workflow);
  }
  auto connections_it = doc.FindMember("connections");
  if (connections_it != doc.MemberEnd()) {
    parse_connections(connections_it->value, workflow);
  }
  auto meta_it = doc.FindMember("meta");
  if (meta_it != doc.MemberEnd()) {
    parse_meta_inputs(meta_it->value, workflow);
  }
}

Workflow load_workflow(const std::string &path) {
  Workflow workflow;
  auto doc = load_json(path);
  if (!doc.IsObject()) {
    return workflow;
  }

  auto parts_it = doc.FindMember("parts");
  if (parts_it != doc.MemberEnd() && parts_it->value.IsArray()) {
    size_t slash = path.find_last_of("/\\");
    std::string base_dir = (slash == std::string::npos) ? "" : path.substr(0, slash);
    auto meta_it = doc.FindMember("meta");
    if (meta_it != doc.MemberEnd()) {
      parse_meta_inputs(meta_it->value, workflow);
    }
    for (const auto &part : parts_it->value.GetArray()) {
      if (!part.IsString()) {
        continue;
      }
      std::string part_path = part.GetString();
      if (!part_path.empty() && part_path[0] != '/' && !base_dir.empty()) {
        part_path = base_dir + "/" + part_path;
      }
      merge_workflow(part_path, workflow);
    }
    return workflow;
  }

  auto nodes_it = doc.FindMember("nodes");
  if (nodes_it != doc.MemberEnd()) {
    parse_nodes(nodes_it->value, workflow);
  }
  auto connections_it = doc.FindMember("connections");
  if (connections_it != doc.MemberEnd()) {
    parse_connections(connections_it->value, workflow);
  }
  auto meta_it = doc.FindMember("meta");
  if (meta_it != doc.MemberEnd()) {
    parse_meta_inputs(meta_it->value, workflow);
  }
  return workflow;
}

bool value_bool(const Value *value, bool fallback) {
  if (!value) {
    return fallback;
  }
  if (value->type == ValueType::kBool) {
    return value->boolean;
  }
  if (value->type == ValueType::kInt) {
    return value->integer != 0;
  }
  if (value->type == ValueType::kString) {
    return value->str == "true" || value->str == "1";
  }
  return fallback;
}

uint64_t value_int(const Value *value, uint64_t fallback) {
  if (!value) {
    return fallback;
  }
  if (value->type == ValueType::kInt) {
    return value->integer;
  }
  if (value->type == ValueType::kString) {
    return static_cast<uint64_t>(std::strtoull(value->str.c_str(), nullptr, 10));
  }
  return fallback;
}

std::string value_string(const Value *value) {
  if (!value) {
    return "";
  }
  if (value->type == ValueType::kString) {
    return value->str;
  }
  return "";
}

const std::vector<uint8_t> &value_bytes(const Value *value) {
  static const std::vector<uint8_t> empty;
  if (!value || value->type != ValueType::kBytes) {
    return empty;
  }
  return value->bytes;
}

DiterApi load_diter_api() {
  DiterApi api;
#if defined(__APPLE__)
  const char *lib_path = "build/diter_engine/libditer.dylib";
#else
  const char *lib_path = "build/diter_engine/libditer.so";
#endif

  api.handle = dlopen(lib_path, RTLD_LAZY);
  if (!api.handle) {
    const char *err = dlerror();
    std::string message = "Failed to load ";
    message += lib_path;
    if (err) {
      message += ": ";
      message += err;
    }
    message += "\nBuild it via: python scripts/run_diter_workflow.py --workflow build/runbooks/diter_decode_workflow.json";
    throw std::runtime_error(message);
  }
  api.create = reinterpret_cast<void *(*)()>(dlsym(api.handle, "diter_engine_create"));
  api.destroy = reinterpret_cast<void (*)(void *)>(dlsym(api.handle, "diter_engine_destroy"));
  api.init = reinterpret_cast<void (*)(void *)>(dlsym(api.handle, "diter_engine_init"));
  api.set_key_hex = reinterpret_cast<void (*)(void *, const char *)>(dlsym(api.handle, "diter_engine_set_key_hex"));
  api.write_dict = reinterpret_cast<int (*)(void *, const uint8_t *, size_t)>(dlsym(api.handle, "diter_engine_write_dict"));
  api.write_chunk = reinterpret_cast<int (*)(void *, const uint8_t *, size_t)>(dlsym(api.handle, "diter_engine_write_chunk"));
  api.pump = reinterpret_cast<int (*)(void *)>(dlsym(api.handle, "diter_engine_pump"));
  api.output = reinterpret_cast<const uint8_t *(*)(void *, uint32_t *)>(dlsym(api.handle, "diter_engine_output"));
  api.output_advance = reinterpret_cast<void (*)(void *)>(dlsym(api.handle, "diter_engine_output_advance"));

  if (!api.create || !api.destroy || !api.init || !api.set_key_hex || !api.write_dict ||
      !api.write_chunk || !api.pump || !api.output || !api.output_advance) {
    throw std::runtime_error("Failed to resolve DITER API symbols");
  }
  return api;
}

std::unordered_map<std::string, Value> action_read_text(const ActionNode &node,
                                                       const std::unordered_map<std::string, Value> &context) {
  auto it = node.params.find("path");
  if (it == node.params.end()) {
    throw std::runtime_error("read_text missing path");
  }
  auto path = resolve_string(context, it->second);
  std::unordered_map<std::string, Value> result;
  try {
    result["text"] = make_string(read_text(path));
  } catch (const std::exception &) {
    if (node.optional) {
      return result;
    }
    throw;
  }
  return result;
}

std::unordered_map<std::string, Value> action_read_bytes(const ActionNode &node,
                                                        const std::unordered_map<std::string, Value> &context) {
  auto it = node.params.find("path");
  if (it == node.params.end()) {
    throw std::runtime_error("read_bytes missing path");
  }
  auto path = resolve_string(context, it->second);
  std::unordered_map<std::string, Value> result;
  try {
    result["bytes"] = make_bytes(read_bytes(path));
  } catch (const std::exception &) {
    if (node.optional) {
      return result;
    }
    throw;
  }
  return result;
}

std::unordered_map<std::string, Value> action_parse_params(const ActionNode &node,
                                                           const std::unordered_map<std::string, Value> &context) {
  auto it = node.params.find("text");
  if (it == node.params.end()) {
    throw std::runtime_error("parse_params missing text");
  }
  auto text_value = resolve_string(context, it->second);
  rapidjson::Document doc;
  doc.Parse(text_value.c_str());
  if (doc.HasParseError()) {
    throw std::runtime_error("Failed to parse params JSON");
  }
  const rapidjson::Value *root = &doc;
  if (doc.IsArray() && !doc.Empty()) {
    root = &doc[0];
  }
  std::unordered_map<std::string, Value> result;
  if (root->IsObject()) {
    auto b_it = root->FindMember("b");
    if (b_it != root->MemberEnd() && b_it->value.IsString()) {
      result["dict_b64"] = make_string(b_it->value.GetString());
    }
    auto d_it = root->FindMember("d");
    if (d_it != root->MemberEnd()) {
      if (d_it->value.IsBool()) {
        result["needs_key"] = make_bool(d_it->value.GetBool());
      } else if (d_it->value.IsInt()) {
        result["needs_key"] = make_bool(d_it->value.GetInt() != 0);
      }
    }
  }
  return result;
}

std::unordered_map<std::string, Value> action_decode_dict(const ActionNode &node,
                                                         const std::unordered_map<std::string, Value> &context) {
  auto it = node.params.find("dict_b64");
  if (it == node.params.end()) {
    throw std::runtime_error("decode_dict missing dict_b64");
  }
  auto dict_value = resolve_string(context, it->second);
  std::string cleaned;
  cleaned.reserve(dict_value.size());
  for (char c : dict_value) {
    if (is_base64_char(c)) {
      cleaned.push_back(c);
    }
  }
  std::unordered_map<std::string, Value> result;
  result["dict_bytes"] = make_bytes(base64_decode_clean(cleaned));
  return result;
}

std::unordered_map<std::string, Value> action_extract_key_hex(const ActionNode &node,
                                                              const std::unordered_map<std::string, Value> &context) {
  auto it = node.params.find("text");
  if (it == node.params.end()) {
    throw std::runtime_error("extract_key_hex missing text");
  }
  auto text_value = resolve_string(context, it->second);
  std::unordered_map<std::string, Value> result;
  result["key_hex"] = make_string(extract_key_hex(text_value));
  return result;
}

std::unordered_map<std::string, Value> action_select_key(const ActionNode &node,
                                                        const std::unordered_map<std::string, Value> &context) {
  auto key_it = node.params.find("key_hex");
  auto fallback_it = node.params.find("fallback_key_hex");
  if (key_it == node.params.end() || fallback_it == node.params.end()) {
    throw std::runtime_error("select_key missing key_hex/fallback_key_hex");
  }
  auto key_hex = resolve_string(context, key_it->second);
  auto fallback = resolve_string(context, fallback_it->second);
  std::string selected = !key_hex.empty() ? key_hex : fallback;
  std::unordered_map<std::string, Value> result;
  result["key_hex"] = make_string(selected);
  return result;
}

std::unordered_map<std::string, Value> action_engine_decode(const ActionNode &node,
                                                            std::unordered_map<std::string, Value> &context) {
  auto binz_it = node.params.find("binz_bytes");
  auto dict_it = node.params.find("dict_bytes");
  auto needs_it = node.params.find("needs_key");
  auto key_it = node.params.find("key_hex");
  auto out_it = node.params.find("output_path");
  if (binz_it == node.params.end() || dict_it == node.params.end() ||
      needs_it == node.params.end() || key_it == node.params.end() ||
      out_it == node.params.end()) {
    throw std::runtime_error("engine_decode missing required params");
  }
  auto binz_value = resolve_value(context, binz_it->second);
  auto dict_value = resolve_value(context, dict_it->second);
  auto needs_key_value = resolve_value(context, needs_it->second);
  auto key_hex = resolve_string(context, key_it->second);
  auto output_path = resolve_string(context, out_it->second);

  if (!binz_value || !dict_value) {
    throw std::runtime_error("engine_decode missing binz/dict bytes");
  }
  if (value_bool(needs_key_value, false) && key_hex.empty()) {
    throw std::runtime_error("engine_decode requires key_hex but none provided");
  }

  uint64_t chunk_size = 10240;
  auto cs_it = context.find("chunk_size");
  if (cs_it != context.end()) {
    chunk_size = value_int(&cs_it->second, chunk_size);
  }
  const auto &binz_bytes = value_bytes(binz_value);
  const auto &dict_bytes = value_bytes(dict_value);

  DiterApi api = load_diter_api();
  void *engine = api.create();
  if (!engine) {
    throw std::runtime_error("Failed to create DITER engine");
  }
  if (!key_hex.empty()) {
    api.set_key_hex(engine, key_hex.c_str());
  }
  api.init(engine);
  if (!api.write_dict(engine, dict_bytes.data(), dict_bytes.size())) {
    api.destroy(engine);
    throw std::runtime_error("Dictionary pointer out of bounds");
  }
  api.pump(engine);

  std::ofstream out(output_path, std::ios::binary);
  if (!out) {
    api.destroy(engine);
    throw std::runtime_error("Failed to open output file");
  }

  for (size_t offset = 0; offset < binz_bytes.size(); offset += chunk_size) {
    size_t len = binz_bytes.size() - offset;
    if (len > chunk_size) {
      len = chunk_size;
    }
    if (!api.write_chunk(engine, binz_bytes.data() + offset, len)) {
      api.destroy(engine);
      throw std::runtime_error("Chunk pointer out of bounds");
    }
    int has_output = api.pump(engine);
    while (has_output) {
      uint32_t out_len = 0;
      const uint8_t *out_ptr = api.output(engine, &out_len);
      if (out_len && out_ptr) {
        out.write(reinterpret_cast<const char *>(out_ptr), out_len);
      }
      api.output_advance(engine);
      has_output = api.pump(engine);
    }
  }
  out.close();
  api.destroy(engine);

  std::unordered_map<std::string, Value> result;
  std::ifstream in(output_path, std::ios::binary | std::ios::ate);
  result["output_size"] = make_int(in ? static_cast<uint64_t>(in.tellg()) : 0);
  return result;
}

void execute_workflow(Workflow &workflow, std::unordered_map<std::string, Value> &context) {
  std::unordered_map<std::string, bool> has_incoming;
  for (const auto &pair : workflow.edges) {
    for (const auto &target : pair.second) {
      if (workflow.nodes.find(target) != workflow.nodes.end()) {
        has_incoming[target] = true;
      }
    }
  }
  std::vector<std::string> queue;
  for (const auto &pair : workflow.nodes) {
    if (!has_incoming[pair.first]) {
      queue.push_back(pair.first);
    }
  }

  std::unordered_map<std::string, bool> visited;
  while (!queue.empty()) {
    std::string name = queue.front();
    queue.erase(queue.begin());
    if (visited[name]) {
      continue;
    }
    visited[name] = true;
    auto node_it = workflow.nodes.find(name);
    if (node_it == workflow.nodes.end()) {
      continue;
    }
    const ActionNode &node = node_it->second;
    std::unordered_map<std::string, Value> result;
    if (node.action == "read_text") {
      result = action_read_text(node, context);
    } else if (node.action == "read_bytes") {
      result = action_read_bytes(node, context);
    } else if (node.action == "parse_params") {
      result = action_parse_params(node, context);
    } else if (node.action == "decode_dict") {
      result = action_decode_dict(node, context);
    } else if (node.action == "extract_key_hex") {
      result = action_extract_key_hex(node, context);
    } else if (node.action == "select_key") {
      result = action_select_key(node, context);
    } else if (node.action == "engine_decode") {
      result = action_engine_decode(node, context);
    } else {
      throw std::runtime_error("Unknown action: " + node.action);
    }
    apply_outputs(context, node.outputs, result);

    auto edge_it = workflow.edges.find(name);
    if (edge_it != workflow.edges.end()) {
      for (const auto &target : edge_it->second) {
        queue.push_back(target);
      }
    }
  }
}

}  // namespace

int main(int argc, char **argv) {
  std::string workflow_path;
  std::string params_path;
  std::string binz_path;
  std::string out_path;
  std::string key_hex;
  std::string key_source;
  std::string chunk_size;

  for (int i = 1; i < argc; i++) {
    std::string arg = argv[i];
    if (arg == "--workflow" && i + 1 < argc) {
      workflow_path = argv[++i];
    } else if (arg == "--params" && i + 1 < argc) {
      params_path = argv[++i];
    } else if (arg == "--binz" && i + 1 < argc) {
      binz_path = argv[++i];
    } else if (arg == "--out" && i + 1 < argc) {
      out_path = argv[++i];
    } else if (arg == "--key-hex" && i + 1 < argc) {
      key_hex = argv[++i];
    } else if (arg == "--key-source" && i + 1 < argc) {
      key_source = argv[++i];
    } else if (arg == "--chunk-size" && i + 1 < argc) {
      chunk_size = argv[++i];
    }
  }

  if (workflow_path.empty()) {
    workflow_path = workflow_default_path();
  }

  try {
    Workflow workflow = load_workflow(workflow_path);
    std::unordered_map<std::string, Value> context = workflow.inputs;
    if (!params_path.empty()) context["params_path"] = make_string(params_path);
    if (!binz_path.empty()) context["binz_path"] = make_string(binz_path);
    if (!out_path.empty()) context["out_path"] = make_string(out_path);
    if (!key_hex.empty()) context["key_hex"] = make_string(key_hex);
    if (!key_source.empty()) context["key_source_path"] = make_string(key_source);
    if (!chunk_size.empty()) context["chunk_size"] = make_int(std::strtoull(chunk_size.c_str(), nullptr, 10));

    execute_workflow(workflow, context);
    auto it = context.find("output_size");
    if (it != context.end() && it->second.type == ValueType::kInt) {
      std::cout << "Output bytes: " << it->second.integer << "\n";
    }
  } catch (const std::exception &exc) {
    std::cerr << "DITER workflow error: " << exc.what() << "\n";
    return 1;
  }
  return 0;
}
