#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "diter_engine.h"
#define CHUNK_SIZE 10240u

static void usage(const char* prog) {
  fprintf(stderr, "Usage: %s --binz FILE --params FILE --out FILE [--key-hex HEX] [--key-source FILE]\n", prog);
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

int main(int argc, char** argv) {
  const char* binz_path = NULL;
  const char* params_path = NULL;
  const char* out_path = NULL;
  const char* key_hex = NULL;
  const char* key_source = NULL;

  for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "--binz") == 0 && i + 1 < argc) {
      binz_path = argv[++i];
    } else if (strcmp(argv[i], "--params") == 0 && i + 1 < argc) {
      params_path = argv[++i];
    } else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) {
      out_path = argv[++i];
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

  DiterEngine* engine = diter_engine_create();
  if (!engine) {
    fprintf(stderr, "Failed to initialize DITER engine\n");
    free(dict_bytes);
    return 1;
  }

  if (d_flag) {
    diter_engine_set_key_hex(engine, key_hex);
  }

  diter_engine_init(engine);
  if (!diter_engine_write_dict(engine, dict_bytes, dict_len)) {
    fprintf(stderr, "Dictionary pointer out of bounds\n");
    free(dict_bytes);
    diter_engine_destroy(engine);
    return 1;
  }
  free(dict_bytes);
  diter_engine_pump(engine);

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
    if (!diter_engine_write_chunk(engine, binz_bytes + offset, chunk_len)) {
      fprintf(stderr, "Chunk pointer out of bounds\n");
      fclose(out);
      free(binz_bytes);
      diter_engine_destroy(engine);
      return 1;
    }
    int has_output = diter_engine_pump(engine);
    while (has_output) {
      uint32_t out_len = 0;
      const uint8_t* out_ptr = diter_engine_output(engine, &out_len);
      if (out_len && out_ptr) {
        fwrite(out_ptr, 1, out_len, out);
      }
      diter_engine_output_advance(engine);
      has_output = diter_engine_pump(engine);
    }
  }

  fclose(out);
  free(binz_bytes);
  free(owned_key);
  diter_engine_destroy(engine);
  return 0;
}
