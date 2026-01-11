#ifndef DITER_RT_H
#define DITER_RT_H

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifndef WABT_BIG_ENDIAN
#if defined(__BYTE_ORDER__) && (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)
#define WABT_BIG_ENDIAN 1
#else
#define WABT_BIG_ENDIAN 0
#endif
#endif

#ifndef WASM_DEFAULT_PAGE_SIZE
#define WASM_DEFAULT_PAGE_SIZE 65536
#endif

#ifndef WASM_RT_SANITY_CHECKS
#define WASM_RT_SANITY_CHECKS 0
#endif

#ifndef WASM_RT_USE_SEGUE
#define WASM_RT_USE_SEGUE 0
#endif

#ifndef WASM_RT_SEGUE_FREE_SEGMENT
#define WASM_RT_SEGUE_FREE_SEGMENT 0
#endif

#ifndef WASM_RT_MEMCHECK_GUARD_PAGES
#define WASM_RT_MEMCHECK_GUARD_PAGES 0
#endif

#ifndef WASM_RT_MEMCHECK_BOUNDS_CHECK
#define WASM_RT_MEMCHECK_BOUNDS_CHECK 1
#endif

#ifndef WASM_RT_STACK_DEPTH_COUNT
#define WASM_RT_STACK_DEPTH_COUNT 0
#endif

#ifndef WASM_RT_MAX_CALL_STACK_DEPTH
#define WASM_RT_MAX_CALL_STACK_DEPTH 0
#endif

#ifndef WASM_RT_CHECK_BASE
#define WASM_RT_CHECK_BASE(mem) ((void)0)
#endif

#ifndef LIKELY
#define LIKELY(x) (x)
#endif

#ifndef UNLIKELY
#define UNLIKELY(x) (x)
#endif

#ifndef wasm_rt_memcpy
#define wasm_rt_memcpy memcpy
#endif

typedef enum {
  WASM_RT_TRAP_NONE,
  WASM_RT_TRAP_OOB,
  WASM_RT_TRAP_INT_OVERFLOW,
  WASM_RT_TRAP_DIV_BY_ZERO,
  WASM_RT_TRAP_INVALID_CONVERSION,
  WASM_RT_TRAP_UNREACHABLE,
  WASM_RT_TRAP_CALL_INDIRECT,
  WASM_RT_TRAP_NULL_REF,
  WASM_RT_TRAP_UNCAUGHT_EXCEPTION,
  WASM_RT_TRAP_UNALIGNED,
  WASM_RT_TRAP_EXHAUSTION,
} wasm_rt_trap_t;

typedef enum {
  WASM_RT_I32,
  WASM_RT_I64,
  WASM_RT_F32,
  WASM_RT_F64,
  WASM_RT_V128,
  WASM_RT_FUNCREF,
  WASM_RT_EXTERNREF,
  WASM_RT_EXNREF,
} wasm_rt_type_t;

typedef void (*wasm_rt_function_ptr_t)(void);

typedef struct wasm_rt_tailcallee_t {
  void (*fn)(void** instance_ptr, void* tail_call_stack, struct wasm_rt_tailcallee_t* next);
} wasm_rt_tailcallee_t;

typedef const char* wasm_rt_func_type_t;

typedef struct {
  wasm_rt_func_type_t func_type;
  wasm_rt_function_ptr_t func;
  wasm_rt_tailcallee_t func_tailcallee;
  void* module_instance;
} wasm_rt_funcref_t;

#define wasm_rt_funcref_null_value \
  ((wasm_rt_funcref_t){NULL, NULL, {NULL}, NULL})

typedef void* wasm_rt_externref_t;

#define wasm_rt_externref_null_value ((wasm_rt_externref_t){NULL})

typedef struct {
  uint8_t* data;
  uint8_t* data_end;
  uint32_t page_size;
  uint64_t pages;
  uint64_t max_pages;
  uint64_t size;
  bool is64;
} wasm_rt_memory_t;

typedef struct {
  wasm_rt_funcref_t* data;
  uint32_t max_size;
  uint32_t size;
} wasm_rt_funcref_table_t;

typedef struct {
  wasm_rt_externref_t* data;
  uint32_t max_size;
  uint32_t size;
} wasm_rt_externref_table_t;

void wasm_rt_init(void);
bool wasm_rt_is_initialized(void);
void wasm_rt_free(void);

void wasm_rt_trap(wasm_rt_trap_t code);

void wasm_rt_allocate_memory(wasm_rt_memory_t* memory,
                             uint64_t initial_pages,
                             uint64_t max_pages,
                             bool is64,
                             uint32_t page_size);
uint64_t wasm_rt_grow_memory(wasm_rt_memory_t* memory, uint64_t pages);
void wasm_rt_free_memory(wasm_rt_memory_t* memory);

void wasm_rt_allocate_funcref_table(wasm_rt_funcref_table_t* table,
                                    uint32_t elements,
                                    uint32_t max_elements);
void wasm_rt_free_funcref_table(wasm_rt_funcref_table_t* table);

#ifdef __cplusplus
}
#endif

#endif
