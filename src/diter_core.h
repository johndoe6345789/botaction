/* Generated from wasm2c output; hand-refactored wrapper naming. */
#ifndef DITER_CORE_H
#define DITER_CORE_H

#include "diter_rt.h"

#include <stdint.h>

#ifndef WASM_RT_CORE_TYPES_DEFINED
#define WASM_RT_CORE_TYPES_DEFINED
typedef uint8_t u8;
typedef int8_t s8;
typedef uint16_t u16;
typedef int16_t s16;
typedef uint32_t u32;
typedef int32_t s32;
typedef uint64_t u64;
typedef int64_t s64;
typedef float f32;
typedef double f64;
#endif

#ifdef __cplusplus
extern "C" {
#endif

struct diter_env;
extern wasm_rt_memory_t* diter_env_memory(struct diter_env*);

typedef struct diter_core {
  struct diter_env* env_instance;
  /* import: 'env' 'memory' */
  wasm_rt_memory_t *env_memory;
  u32 stack_ptr;
  wasm_rt_funcref_table_t func_table;
} diter_core;

void diter_core_instantiate(diter_core*, struct diter_env*);
void diter_core_free(diter_core*);
wasm_rt_func_type_t diter_core_get_func_type(uint32_t param_count, uint32_t result_count, ...);

/* import: 'env' 'abort' */
void diter_env_abort(struct diter_env*);

/* import: 'env' 'sbrk' */
u32 diter_env_sbrk(struct diter_env*, u32);

extern const u64 diter_core_min_env_memory;
extern const u64 diter_core_max_env_memory;
extern const u8 diter_core_is64_env_memory;
extern const u32 diter_core_pagesize_env_memory;

/* export: '__wasm_call_ctors' */
void diter_core_0x5F_wasm_call_ctors(diter_core*);

/* export: 'heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl' */
u32 diter_core_heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl(diter_core*, u32);

/* export: 'mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l' */
void diter_core_mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l(diter_core*);

/* export: 'Umlja1JvbGxlZDRV' */
u32 diter_core_Umlja1JvbGxlZDRV(diter_core*, u32, u32);

/* export: 'dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI' */
u32 diter_core_dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI(diter_core*, u32);

/* export: 'GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW' */
u32 diter_core_GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW(diter_core*);

/* export: 'FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN' */
void diter_core_FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN(diter_core*);

/* export: 'bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg' */
u32 diter_core_bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg(diter_core*);

/* export: 'TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT' */
u32 diter_core_TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT(diter_core*);

/* Friendly aliases for the exported decode pipeline. */
static inline void diter_core_init(diter_core* core) {
  diter_core_mV2ZXIgZ29ubmEgbGV0IHlvdSBkb3duCk5l(core);
}

static inline u32 diter_core_alloc_key(diter_core* core, u32 offset, u32 length) {
  return diter_core_Umlja1JvbGxlZDRV(core, offset, length);
}

static inline u32 diter_core_load_dict(diter_core* core, u32 length) {
  return diter_core_dmVyIGdvbm5hIHJ1biBhcm91bmQgYW5kI(core, length);
}

static inline u32 diter_core_load_chunk(diter_core* core, u32 length) {
  return diter_core_heSBnb29kYnllCk5ldmVyIGdvbm5hIHRl(core, length);
}

static inline u32 diter_core_pump(diter_core* core) {
  return diter_core_GRlc2VydCB5b3UKTmV2ZXIgZ29ubmEgbW(core);
}

static inline u32 diter_core_out_ptr(diter_core* core) {
  return diter_core_TmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAKT(core);
}

static inline u32 diter_core_out_len(diter_core* core) {
  return diter_core_bGwgYSBsaWUgYW5kIGh1cnQgeW91Cg(core);
}

static inline void diter_core_out_advance(diter_core* core) {
  diter_core_FrZSB5b3UgY3J5Ck5ldmVyIGdvbm5hIHN(core);
}

#ifdef __cplusplus
}
#endif

#endif  /* DITER_CORE_H */
