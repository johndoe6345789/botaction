#include "diter_rt.h"

#include <stdio.h>
#include <string.h>

#define WASM_RT_NO_MAX UINT64_MAX

static bool g_initialized = false;

void wasm_rt_init(void) {
  g_initialized = true;
}

bool wasm_rt_is_initialized(void) {
  return g_initialized;
}

void wasm_rt_free(void) {
  g_initialized = false;
}

static const char* trap_name(wasm_rt_trap_t code) {
  switch (code) {
    case WASM_RT_TRAP_OOB:
      return "out of bounds";
    case WASM_RT_TRAP_INT_OVERFLOW:
      return "integer overflow";
    case WASM_RT_TRAP_DIV_BY_ZERO:
      return "divide by zero";
    case WASM_RT_TRAP_INVALID_CONVERSION:
      return "invalid conversion";
    case WASM_RT_TRAP_UNREACHABLE:
      return "unreachable";
    case WASM_RT_TRAP_CALL_INDIRECT:
      return "call_indirect";
    case WASM_RT_TRAP_NULL_REF:
      return "null reference";
    case WASM_RT_TRAP_UNCAUGHT_EXCEPTION:
      return "uncaught exception";
    case WASM_RT_TRAP_UNALIGNED:
      return "unaligned access";
    case WASM_RT_TRAP_EXHAUSTION:
      return "exhaustion";
    default:
      return "trap";
  }
}

void wasm_rt_trap(wasm_rt_trap_t code) {
  fprintf(stderr, "DITER runtime trap: %s\n", trap_name(code));
  abort();
}

void wasm_rt_allocate_memory(wasm_rt_memory_t* memory,
                             uint64_t initial_pages,
                             uint64_t max_pages,
                             bool is64,
                             uint32_t page_size) {
  if (!memory) {
    return;
  }
  if (page_size == 0) {
    page_size = WASM_DEFAULT_PAGE_SIZE;
  }
  memory->page_size = page_size;
  memory->pages = initial_pages;
  memory->max_pages = max_pages ? max_pages : WASM_RT_NO_MAX;
  memory->size = memory->pages * memory->page_size;
  memory->is64 = is64;
  memory->data = (uint8_t*)calloc(1, (size_t)memory->size);
  if (!memory->data) {
    fprintf(stderr, "DITER runtime memory allocation failed\n");
    abort();
  }
  memory->data_end = memory->data + memory->size;
}

uint64_t wasm_rt_grow_memory(wasm_rt_memory_t* memory, uint64_t pages) {
  if (!memory || pages == 0) {
    return memory ? memory->pages : 0;
  }
  uint64_t old_pages = memory->pages;
  uint64_t new_pages = old_pages + pages;
  if (memory->max_pages != WASM_RT_NO_MAX && new_pages > memory->max_pages) {
    return UINT64_MAX;
  }
  uint64_t new_size = new_pages * memory->page_size;
  uint8_t* new_data = (uint8_t*)realloc(memory->data, (size_t)new_size);
  if (!new_data) {
    return UINT64_MAX;
  }
  if (new_size > memory->size) {
    memset(new_data + memory->size, 0, (size_t)(new_size - memory->size));
  }
  memory->data = new_data;
  memory->size = new_size;
  memory->pages = new_pages;
  memory->data_end = memory->data + memory->size;
  return old_pages;
}

void wasm_rt_free_memory(wasm_rt_memory_t* memory) {
  if (!memory) {
    return;
  }
  free(memory->data);
  memory->data = NULL;
  memory->data_end = NULL;
  memory->size = 0;
  memory->pages = 0;
  memory->max_pages = 0;
  memory->page_size = 0;
}

void wasm_rt_allocate_funcref_table(wasm_rt_funcref_table_t* table,
                                    uint32_t elements,
                                    uint32_t max_elements) {
  if (!table) {
    return;
  }
  table->size = elements;
  table->max_size = max_elements ? max_elements : UINT32_MAX;
  table->data = (wasm_rt_funcref_t*)calloc(elements, sizeof(wasm_rt_funcref_t));
  if (!table->data) {
    fprintf(stderr, "DITER runtime table allocation failed\n");
    abort();
  }
}

void wasm_rt_free_funcref_table(wasm_rt_funcref_table_t* table) {
  if (!table) {
    return;
  }
  free(table->data);
  table->data = NULL;
  table->size = 0;
  table->max_size = 0;
}
