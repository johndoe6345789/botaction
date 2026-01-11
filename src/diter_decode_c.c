#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "diter_wasm_blob_wasm2c.h"

#define DITER_EXPORT_INIT w2c_diter__wasm__blob_mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l
#define DITER_EXPORT_LOAD_DICT w2c_diter__wasm__blob_dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI
#define DITER_EXPORT_LOAD_CHUNK w2c_diter__wasm__blob_heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl
#define DITER_EXPORT_PUMP w2c_diter__wasm__blob_GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW
#define DITER_EXPORT_OUT_PTR w2c_diter__wasm__blob_TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT
#define DITER_EXPORT_OUT_LEN w2c_diter__wasm__blob_bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg
#define DITER_EXPORT_OUT_ADVANCE w2c_diter__wasm__blob_FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN
#define DITER_EXPORT_SET_KEY w2c_diter__wasm__blob_Umlja1JvbGxlZDRV

#define DEFAULT_HEAP_BASE 83360u
#define DEFAULT_MAX_PAGES 8192u
#define CHUNK_SIZE 10240u

struct w2c_env {
  wasm_rt_memory_t memory;
  uint32_t heap_ptr;
};

wasm_rt_memory_t* w2c_env_memory(struct w2c_env* env) {
  return &env->memory;
}

void w2c_env_abort(struct w2c_env* env) {
  (void)env;
  fprintf(stderr, "DITER wasm abort\n");
  exit(1);
}

uint32_t w2c_env_sbrk(struct w2c_env* env, uint32_t increment) {
  uint32_t old = env->heap_ptr;
  uint64_t next = (uint64_t)old + increment;
  if (next > env->memory.size) {
    uint64_t needed = next - env->memory.size;
    uint64_t pages = (needed + 65535u) >> 16;
    uint64_t grown = wasm_rt_grow_memory(&env->memory, pages);
    if (grown == UINT64_MAX || grown == 0xffffffffu) {
      fprintf(stderr, "DITER wasm memory grow failed\n");
      exit(1);
    }
  }
  env->heap_ptr = (uint32_t)next;
  return old;
}

static void usage(const char* prog) {
  fprintf(stderr, "Usage: %s --binz FILE --params FILE --out FILE [--wasm FILE] [--key-hex HEX] [--key-source FILE]\n", prog);
}

static uint8_t* read_file(const char* path, size_t* out_len) {
  FILE* f = fopen(path, "rb");
  if (!f) {
    return NULL;
  }
  if (fseek(f, 0, SEEK_END) != 0) {
    fclose(f);
    return NULL;
  }
  long size = ftell(f);
  if (size < 0) {
    fclose(f);
    return NULL;
  }
  if (fseek(f, 0, SEEK_SET) != 0) {
    fclose(f);
    return NULL;
  }
  uint8_t* data = (uint8_t*)malloc((size_t)size);
  if (!data) {
    fclose(f);
    return NULL;
  }
  if (fread(data, 1, (size_t)size, f) != (size_t)size) {
    fclose(f);
    free(data);
    return NULL;
  }
  fclose(f);
  *out_len = (size_t)size;
  return data;
}

static int is_b64_char(char c) {
  return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
         (c >= '0' && c <= '9') || c == '+' || c == '/' || c == '=';
}

static char* clean_b64(const char* input, size_t len, size_t* out_len) {
  char* cleaned = (char*)malloc(len + 1);
  if (!cleaned) {
    return NULL;
  }
  size_t pos = 0;
  for (size_t i = 0; i < len; i++) {
    if (is_b64_char(input[i])) {
      cleaned[pos++] = input[i];
    }
  }
  cleaned[pos] = '\0';
  *out_len = pos;
  return cleaned;
}

static int b64_value(char c) {
  if (c >= 'A' && c <= 'Z') return c - 'A';
  if (c >= 'a' && c <= 'z') return c - 'a' + 26;
  if (c >= '0' && c <= '9') return c - '0' + 52;
  if (c == '+') return 62;
  if (c == '/') return 63;
  if (c == '=') return -2;
  return -1;
}

static uint8_t* base64_decode(const char* input, size_t len, size_t* out_len) {
  size_t alloc = (len * 3) / 4 + 4;
  uint8_t* out = (uint8_t*)malloc(alloc);
  if (!out) {
    return NULL;
  }
  size_t out_pos = 0;
  int vals[4];
  size_t val_pos = 0;
  for (size_t i = 0; i < len; i++) {
    int v = b64_value(input[i]);
    if (v == -1) {
      continue;
    }
    vals[val_pos++] = v;
    if (val_pos == 4) {
      if (vals[0] == -2 || vals[1] == -2) {
        break;
      }
      out[out_pos++] = (uint8_t)((vals[0] << 2) | (vals[1] >> 4));
      if (vals[2] != -2) {
        out[out_pos++] = (uint8_t)(((vals[1] & 0x0f) << 4) | (vals[2] >> 2));
      }
      if (vals[3] != -2 && vals[2] != -2) {
        out[out_pos++] = (uint8_t)(((vals[2] & 0x03) << 6) | vals[3]);
      }
      val_pos = 0;
    }
  }
  *out_len = out_pos;
  return out;
}

static char* extract_json_string(const char* text, const char* key) {
  size_t key_len = strlen(key);
  const char* cur = text;
  while ((cur = strstr(cur, key)) != NULL) {
    cur += key_len;
    while (*cur && *cur != ':') cur++;
    if (!*cur) break;
    cur++;
    while (*cur && isspace((unsigned char)*cur)) cur++;
    if (*cur != '"' && *cur != '\'') continue;
    char quote = *cur++;
    size_t cap = strlen(cur) + 1;
    char* out = (char*)malloc(cap);
    if (!out) return NULL;
    size_t pos = 0;
    while (*cur && *cur != quote) {
      if (*cur == '\\') {
        cur++;
        if (!*cur) break;
        if (*cur == 'n' || *cur == 'r' || *cur == 't') {
          out[pos++] = '\n';
          cur++;
          continue;
        }
        out[pos++] = *cur++;
        continue;
      }
      out[pos++] = *cur++;
    }
    out[pos] = '\0';
    return out;
  }
  return NULL;
}

static int extract_json_bool(const char* text, const char* key, int* out) {
  size_t key_len = strlen(key);
  const char* cur = text;
  while ((cur = strstr(cur, key)) != NULL) {
    cur += key_len;
    while (*cur && *cur != ':') cur++;
    if (!*cur) break;
    cur++;
    while (*cur && isspace((unsigned char)*cur)) cur++;
    if (strncmp(cur, "true", 4) == 0 || *cur == '1') {
      *out = 1;
      return 1;
    }
    if (strncmp(cur, "false", 5) == 0 || *cur == '0') {
      *out = 0;
      return 1;
    }
  }
  return 0;
}

static int is_hex_char(char c) {
  return (c >= '0' && c <= '9') ||
         (c >= 'a' && c <= 'f') ||
         (c >= 'A' && c <= 'F');
}

static char* extract_key_hex(const char* text) {
  const char* mod = strstr(text, "module.exports");
  if (mod) {
    const char* eq = strchr(mod, '=');
    if (eq) {
      const char* cur = eq + 1;
      while (*cur && isspace((unsigned char)*cur)) cur++;
      if (*cur == '"' || *cur == '\'') {
        char quote = *cur++;
        size_t cap = strlen(cur) + 1;
        char* extracted = (char*)malloc(cap);
        if (!extracted) return NULL;
        size_t pos = 0;
        while (*cur && *cur != quote) {
          if (*cur == '\\') {
            cur++;
            if (!*cur) break;
            extracted[pos++] = *cur++;
            continue;
          }
          extracted[pos++] = *cur++;
        }
        extracted[pos] = '\0';
        size_t len = strlen(extracted);
        char* cleaned = (char*)malloc(len + 1);
        if (!cleaned) {
          free(extracted);
          return NULL;
        }
        size_t out_pos = 0;
        for (size_t i = 0; i < len; i++) {
          if (is_hex_char(extracted[i])) {
            cleaned[out_pos++] = (char)tolower((unsigned char)extracted[i]);
          }
        }
        cleaned[out_pos] = '\0';
        free(extracted);
        if (out_pos >= 40) {
          cleaned[40] = '\0';
          return cleaned;
        }
        free(cleaned);
      }
    }
  }
  size_t len = strlen(text);
  size_t run = 0;
  for (size_t i = 0; i < len; i++) {
    if (is_hex_char(text[i])) {
      run++;
    } else {
      if (run >= 40) {
        size_t start = i - run;
        char* out = (char*)malloc(41);
        if (!out) return NULL;
        size_t pos = 0;
        for (size_t j = start; j < i && pos < 40; j++) {
          if (is_hex_char(text[j])) {
            out[pos++] = (char)tolower((unsigned char)text[j]);
          }
        }
        out[pos] = '\0';
        return out;
      }
      run = 0;
    }
  }
  return NULL;
}

static uint32_t read_leb_u32(const uint8_t* data, size_t size, size_t* offset, int* ok) {
  uint32_t result = 0;
  uint32_t shift = 0;
  while (*offset < size && shift < 32) {
    uint8_t byte = data[(*offset)++];
    result |= ((uint32_t)(byte & 0x7f)) << shift;
    if ((byte & 0x80) == 0) {
      *ok = 1;
      return result;
    }
    shift += 7;
  }
  *ok = 0;
  return 0;
}

static int32_t read_leb_s32(const uint8_t* data, size_t size, size_t* offset, int* ok) {
  int32_t result = 0;
  uint32_t shift = 0;
  uint8_t byte = 0;
  while (*offset < size && shift < 32) {
    byte = data[(*offset)++];
    result |= ((int32_t)(byte & 0x7f)) << shift;
    shift += 7;
    if ((byte & 0x80) == 0) {
      break;
    }
  }
  if (*offset >= size && (byte & 0x80)) {
    *ok = 0;
    return 0;
  }
  if (shift < 32 && (byte & 0x40)) {
    result |= -((int32_t)1 << shift);
  }
  *ok = 1;
  return result;
}

static int read_string(const uint8_t* data, size_t size, size_t* offset, char** out_str) {
  int ok = 0;
  uint32_t len = read_leb_u32(data, size, offset, &ok);
  if (!ok || *offset + len > size) return 0;
  char* s = (char*)malloc(len + 1);
  if (!s) return 0;
  memcpy(s, data + *offset, len);
  s[len] = '\0';
  *offset += len;
  *out_str = s;
  return 1;
}

static void parse_wasm(const uint8_t* data, size_t size, uint32_t* heap_base, uint32_t* mem_min) {
  if (size < 8) return;
  if (memcmp(data, "\0asm", 4) != 0) return;
  size_t off = 8;
  while (off < size) {
    uint8_t id = data[off++];
    int ok = 0;
    uint32_t section_size = read_leb_u32(data, size, &off, &ok);
    if (!ok || off + section_size > size) return;
    size_t section_end = off + section_size;
    if (id == 2) {
      uint32_t count = read_leb_u32(data, size, &off, &ok);
      if (!ok) break;
      for (uint32_t i = 0; i < count && off < section_end; i++) {
        char* mod = NULL;
        char* name = NULL;
        if (!read_string(data, size, &off, &mod)) break;
        if (!read_string(data, size, &off, &name)) {
          free(mod);
          break;
        }
        free(mod);
        free(name);
        if (off >= section_end) break;
        uint8_t kind = data[off++];
        if (kind == 0x02) {
          uint8_t flags = data[off++];
          uint32_t min = read_leb_u32(data, size, &off, &ok);
          if (!ok) break;
          *mem_min = min;
          if (flags & 0x01) {
            read_leb_u32(data, size, &off, &ok);
          }
        } else {
          if (kind == 0x00) {
            read_leb_u32(data, size, &off, &ok);
          } else if (kind == 0x01) {
            if (off < size) {
              off++;
            }
            if (off < size) {
              uint8_t flags = data[off++];
              read_leb_u32(data, size, &off, &ok);
              if (flags & 0x01) {
                read_leb_u32(data, size, &off, &ok);
              }
            }
          } else if (kind == 0x03) {
            if (off + 1 < size) {
              off += 2;
            } else {
              off = section_end;
            }
          }
        }
      }
    } else if (id == 6) {
      uint32_t count = read_leb_u32(data, size, &off, &ok);
      if (!ok) break;
      for (uint32_t i = 0; i < count && off < section_end; i++) {
        if (off + 2 > section_end) break;
        uint8_t valtype = data[off++];
        uint8_t mut = data[off++];
        (void)valtype;
        (void)mut;
        uint8_t opcode = data[off++];
        if (opcode == 0x41) {
          int ok_s = 0;
          int32_t value = read_leb_s32(data, size, &off, &ok_s);
          if (ok_s && value > 0) {
            *heap_base = (uint32_t)value;
          }
        }
        while (off < section_end && data[off] != 0x0b) {
          off++;
        }
        if (off < section_end && data[off] == 0x0b) {
          off++;
        }
        if (i == 0) break;
      }
    }
    off = section_end;
  }
}

static void write_key(struct w2c_env* env, w2c_diter__wasm__blob* instance, const char* key_hex) {
  char cleaned[41];
  size_t pos = 0;
  for (size_t i = 0; key_hex[i] && pos < 40; i++) {
    if (is_hex_char(key_hex[i])) {
      cleaned[pos++] = (char)tolower((unsigned char)key_hex[i]);
    }
  }
  while (pos < 40) cleaned[pos++] = '0';
  cleaned[40] = '\0';

  uint32_t ptr = DITER_EXPORT_SET_KEY(instance, 0, 40);
  if (ptr + 40 > env->memory.size) {
    fprintf(stderr, "Key pointer out of bounds\n");
    exit(1);
  }
  for (size_t i = 0; i < 10; i++) {
    for (size_t j = 0; j < 4; j++) {
      env->memory.data[ptr + i * 4 + j] = (uint8_t)cleaned[i * 4 + j];
    }
  }
}

int main(int argc, char** argv) {
  const char* binz_path = NULL;
  const char* params_path = NULL;
  const char* out_path = NULL;
  const char* wasm_path = NULL;
  const char* key_hex = NULL;
  const char* key_source = NULL;

  for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "--binz") == 0 && i + 1 < argc) {
      binz_path = argv[++i];
    } else if (strcmp(argv[i], "--params") == 0 && i + 1 < argc) {
      params_path = argv[++i];
    } else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) {
      out_path = argv[++i];
    } else if (strcmp(argv[i], "--wasm") == 0 && i + 1 < argc) {
      wasm_path = argv[++i];
    } else if (strcmp(argv[i], "--key-hex") == 0 && i + 1 < argc) {
      key_hex = argv[++i];
    } else if (strcmp(argv[i], "--key-source") == 0 && i + 1 < argc) {
      key_source = argv[++i];
    } else {
      usage(argv[0]);
      return 1;
    }
  }

  if (!binz_path || !params_path || !out_path) {
    usage(argv[0]);
    return 1;
  }

  size_t params_len = 0;
  uint8_t* params_data = read_file(params_path, &params_len);
  if (!params_data) {
    fprintf(stderr, "Failed to read params file\n");
    return 1;
  }
  uint8_t* params_resized = (uint8_t*)realloc(params_data, params_len + 1);
  if (!params_resized) {
    free(params_data);
    fprintf(stderr, "Failed to parse params file\n");
    return 1;
  }
  params_data = params_resized;
  params_data[params_len] = '\0';

  char* b64 = extract_json_string((char*)params_data, "\"b\"");
  if (!b64) {
    fprintf(stderr, "Failed to parse params.b\n");
    free(params_data);
    return 1;
  }

  int d_flag = 0;
  extract_json_bool((char*)params_data, "\"d\"", &d_flag);

  size_t b64_clean_len = 0;
  char* b64_clean = clean_b64(b64, strlen(b64), &b64_clean_len);
  free(b64);
  if (!b64_clean) {
    fprintf(stderr, "Failed to clean base64\n");
    free(params_data);
    return 1;
  }
  size_t dict_len = 0;
  uint8_t* dict_bytes = base64_decode(b64_clean, b64_clean_len, &dict_len);
  free(b64_clean);
  free(params_data);
  if (!dict_bytes) {
    fprintf(stderr, "Failed to decode base64\n");
    return 1;
  }

  char* owned_key = NULL;
  if (d_flag && !key_hex && key_source) {
    size_t key_len = 0;
    uint8_t* key_data = read_file(key_source, &key_len);
    if (key_data) {
      uint8_t* key_resized = (uint8_t*)realloc(key_data, key_len + 1);
      if (!key_resized) {
        free(key_data);
        fprintf(stderr, "Failed to parse key source\n");
        free(dict_bytes);
        return 1;
      }
      key_data = key_resized;
      key_data[key_len] = '\0';
      char* extracted = extract_key_hex((char*)key_data);
      free(key_data);
      if (extracted) {
        key_hex = extracted;
        owned_key = extracted;
      }
    }
  }
  if (d_flag && !key_hex) {
    fprintf(stderr, "DITER key required but not provided\n");
    free(dict_bytes);
    return 1;
  }

  uint32_t heap_base = DEFAULT_HEAP_BASE;
  uint32_t mem_min = wasm2c_diter__wasm__blob_min_env_memory;
  if (wasm_path) {
    size_t wasm_len = 0;
    uint8_t* wasm_bytes = read_file(wasm_path, &wasm_len);
    if (wasm_bytes) {
      parse_wasm(wasm_bytes, wasm_len, &heap_base, &mem_min);
      free(wasm_bytes);
    }
  }

  uint32_t aligned = ((heap_base + 65535u) >> 16) << 16;
  uint32_t total_bytes = 262144u + aligned;
  uint32_t initial_pages = total_bytes >> 16;
  if (initial_pages < mem_min) {
    initial_pages = mem_min;
  }
  uint32_t max_pages = DEFAULT_MAX_PAGES;
  if (max_pages < initial_pages) {
    max_pages = initial_pages;
  }

  wasm_rt_init();
  struct w2c_env env;
  wasm_rt_allocate_memory(&env.memory,
                          initial_pages,
                          max_pages,
                          wasm2c_diter__wasm__blob_is64_env_memory != 0,
                          wasm2c_diter__wasm__blob_pagesize_env_memory);
  env.heap_ptr = heap_base;

  w2c_diter__wasm__blob instance;
  wasm2c_diter__wasm__blob_instantiate(&instance, &env);
  w2c_diter__wasm__blob_0x5F_wasm_call_ctors(&instance);

  if (d_flag) {
    write_key(&env, &instance, key_hex);
  }

  DITER_EXPORT_INIT(&instance);
  uint32_t dict_ptr = DITER_EXPORT_LOAD_DICT(&instance, (uint32_t)dict_len);
  if ((uint64_t)dict_ptr + dict_len > env.memory.size) {
    fprintf(stderr, "Dictionary pointer out of bounds\n");
    free(dict_bytes);
    return 1;
  }
  memcpy(env.memory.data + dict_ptr, dict_bytes, dict_len);
  free(dict_bytes);
  DITER_EXPORT_PUMP(&instance, 0);

  size_t binz_len = 0;
  uint8_t* binz_bytes = read_file(binz_path, &binz_len);
  if (!binz_bytes) {
    fprintf(stderr, "Failed to read binz file\n");
    return 1;
  }

  FILE* out = fopen(out_path, "wb");
  if (!out) {
    fprintf(stderr, "Failed to open output file\n");
    free(binz_bytes);
    return 1;
  }

  for (size_t offset = 0; offset < binz_len; offset += CHUNK_SIZE) {
    size_t chunk_len = binz_len - offset;
    if (chunk_len > CHUNK_SIZE) chunk_len = CHUNK_SIZE;
    uint32_t chunk_ptr = DITER_EXPORT_LOAD_CHUNK(&instance, (uint32_t)chunk_len);
    if ((uint64_t)chunk_ptr + chunk_len > env.memory.size) {
      fprintf(stderr, "Chunk pointer out of bounds\n");
      fclose(out);
      free(binz_bytes);
      return 1;
    }
    memcpy(env.memory.data + chunk_ptr, binz_bytes + offset, chunk_len);
    uint32_t has_output = DITER_EXPORT_PUMP(&instance, 1);
    while (has_output) {
      uint32_t out_ptr = DITER_EXPORT_OUT_PTR(&instance);
      uint32_t out_len = DITER_EXPORT_OUT_LEN(&instance);
      if (out_len) {
        if ((uint64_t)out_ptr + out_len > env.memory.size) {
          fprintf(stderr, "Output pointer out of bounds\n");
          fclose(out);
          free(binz_bytes);
          return 1;
        }
        fwrite(env.memory.data + out_ptr, 1, out_len, out);
      }
      DITER_EXPORT_OUT_ADVANCE(&instance);
      has_output = DITER_EXPORT_PUMP(&instance, 0);
    }
  }

  fclose(out);
  free(binz_bytes);
  free(owned_key);
  wasm2c_diter__wasm__blob_free(&instance);
  wasm_rt_free_memory(&env.memory);
  return 0;
}
