#include "diter_engine.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "diter_wasm_blob_wasm2c.h"
#include "wasm-rt.h"

#define DEFAULT_HEAP_BASE 83360u
#define DEFAULT_MAX_PAGES 8192u

struct w2c_env {
  wasm_rt_memory_t memory;
  uint32_t heap_ptr;
};

struct DiterEngine {
  struct w2c_env env;
  w2c_diter__wasm__blob instance;
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

static void init_memory(struct w2c_env* env) {
  uint32_t heap_base = DEFAULT_HEAP_BASE;
  uint32_t mem_min = wasm2c_diter__wasm__blob_min_env_memory;

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

  wasm_rt_allocate_memory(&env->memory,
                          initial_pages,
                          max_pages,
                          wasm2c_diter__wasm__blob_is64_env_memory != 0,
                          wasm2c_diter__wasm__blob_pagesize_env_memory);
  env->heap_ptr = heap_base;
}

static void write_key_hex(struct DiterEngine* engine, const char* key_hex) {
  char cleaned[41];
  size_t pos = 0;
  for (size_t i = 0; key_hex[i] && pos < 40; i++) {
    if (isxdigit((unsigned char)key_hex[i])) {
      cleaned[pos++] = (char)tolower((unsigned char)key_hex[i]);
    }
  }
  while (pos < 40) cleaned[pos++] = '0';
  cleaned[40] = '\0';

  uint32_t ptr = w2c_diter__wasm__blob_Umlja1JvbGxlZDRV(&engine->instance, 0, 40);
  if ((uint64_t)ptr + 40 > engine->env.memory.size) {
    fprintf(stderr, "Key pointer out of bounds\n");
    exit(1);
  }
  for (size_t i = 0; i < 40; i++) {
    engine->env.memory.data[ptr + i] = (uint8_t)cleaned[i];
  }
}

DiterEngine* diter_engine_create(void) {
  wasm_rt_init();
  struct DiterEngine* engine = (struct DiterEngine*)calloc(1, sizeof(struct DiterEngine));
  if (!engine) {
    return NULL;
  }
  init_memory(&engine->env);
  wasm2c_diter__wasm__blob_instantiate(&engine->instance, &engine->env);
  w2c_diter__wasm__blob_0x5F_wasm_call_ctors(&engine->instance);
  return engine;
}

void diter_engine_destroy(DiterEngine* engine) {
  if (!engine) return;
  wasm2c_diter__wasm__blob_free(&engine->instance);
  wasm_rt_free_memory(&engine->env.memory);
  free(engine);
}

void diter_engine_init(DiterEngine* engine) {
  if (!engine) return;
  w2c_diter__wasm__blob_mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l(&engine->instance);
}

void diter_engine_set_key_hex(DiterEngine* engine, const char* key_hex) {
  if (!engine || !key_hex) return;
  write_key_hex(engine, key_hex);
}

int diter_engine_write_dict(DiterEngine* engine, const uint8_t* data, size_t len) {
  if (!engine || !data || !len) return 0;
  uint32_t ptr = w2c_diter__wasm__blob_dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI(
      &engine->instance, (uint32_t)len);
  if ((uint64_t)ptr + len > engine->env.memory.size) {
    return 0;
  }
  memcpy(engine->env.memory.data + ptr, data, len);
  return 1;
}

int diter_engine_write_chunk(DiterEngine* engine, const uint8_t* data, size_t len) {
  if (!engine || !data || !len) return 0;
  uint32_t ptr = w2c_diter__wasm__blob_heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl(
      &engine->instance, (uint32_t)len);
  if ((uint64_t)ptr + len > engine->env.memory.size) {
    return 0;
  }
  memcpy(engine->env.memory.data + ptr, data, len);
  return 1;
}

int diter_engine_pump(DiterEngine* engine) {
  if (!engine) return 0;
  return (int)w2c_diter__wasm__blob_GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW(&engine->instance);
}

const uint8_t* diter_engine_output(DiterEngine* engine, uint32_t* out_len) {
  if (!engine || !out_len) return NULL;
  uint32_t ptr = w2c_diter__wasm__blob_TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT(&engine->instance);
  uint32_t len = w2c_diter__wasm__blob_bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg(&engine->instance);
  if (len == 0) {
    *out_len = 0;
    return NULL;
  }
  if ((uint64_t)ptr + len > engine->env.memory.size) {
    fprintf(stderr, "Output pointer out of bounds\n");
    exit(1);
  }
  *out_len = len;
  return engine->env.memory.data + ptr;
}

void diter_engine_output_advance(DiterEngine* engine) {
  if (!engine) return;
  w2c_diter__wasm__blob_FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN(&engine->instance);
}
