#ifndef DITER_ENGINE_H
#define DITER_ENGINE_H

#include <stddef.h>
#include <stdint.h>

typedef struct DiterEngine DiterEngine;

DiterEngine* diter_engine_create(void);
void diter_engine_destroy(DiterEngine* engine);

void diter_engine_init(DiterEngine* engine);
void diter_engine_set_key_hex(DiterEngine* engine, const char* key_hex);

int diter_engine_write_dict(DiterEngine* engine, const uint8_t* data, size_t len);
int diter_engine_write_chunk(DiterEngine* engine, const uint8_t* data, size_t len);

int diter_engine_pump(DiterEngine* engine);
const uint8_t* diter_engine_output(DiterEngine* engine, uint32_t* out_len);
void diter_engine_output_advance(DiterEngine* engine);

#endif
