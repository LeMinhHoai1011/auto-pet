#pragma once
#include <map>
#include <string>
#include <vector>
#include <cstring>
class Preferences {
public:
    static bool failWrites;
    static std::map<std::string, std::vector<unsigned char>> data;
    void begin(const char*, bool) {}
    bool isKey(const char* key) { return data.count(key); }
    size_t getBytesLength(const char* key) { return data[key].size(); }
    size_t getBytes(const char* key, void* out, size_t size) {
        if (data[key].size() != size) return 0;
        memcpy(out, data[key].data(), size); return size;
    }
    size_t putBytes(const char* key, const void* value, size_t size) {
        if (failWrites) return 0;
        const auto* bytes = static_cast<const unsigned char*>(value);
        data[key] = std::vector<unsigned char>(bytes, bytes + size); return size;
    }
    uint32_t getUInt(const char* key, uint32_t fallback) {
        uint32_t value; return getBytes(key, &value, sizeof(value)) ? value : fallback;
    }
    size_t putUInt(const char* key, uint32_t value) { return putBytes(key, &value, sizeof(value)); }
};
