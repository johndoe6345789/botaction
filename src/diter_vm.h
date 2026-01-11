#ifndef DITER_VM_H
#define DITER_VM_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct DiterVm DiterVm;

DiterVm* diter_vm_create(const char* runbook_path);
void diter_vm_destroy(DiterVm* vm);
void diter_vm_load_inputs(DiterVm* vm,
                          const uint8_t* dict,
                          size_t dict_len,
                          const uint8_t* chunk,
                          size_t chunk_len,
                          const char* key_hex);
void diter_vm_execute(DiterVm* vm);
size_t diter_vm_instruction_count(const DiterVm* vm);

#ifdef __cplusplus
}
#endif

#endif
