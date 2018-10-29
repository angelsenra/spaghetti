// gcc main.c -o main.o && ./main.o
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include <locale.h>
#include <errno.h>
#define read get(data[pos++], reg)

wint_t get(wchar_t data, wchar_t *reg) {
    switch (data) {
        case 128210:  // 📒
            return reg[0];
        case 128211:  // 📓
            return reg[1];
        case 128212:  // 📔
            return reg[2];
        case 128213:  // 📕
            return reg[3];
        case 128214:  // 📖
            return reg[4];
        case 128215:  // 📗
            return reg[5];
        case 128216:  // 📘
            return reg[6];
        case 128217:  // 📙
            return reg[7];
    }
    return data;
}

void put(wchar_t *data, wchar_t *reg, wchar_t key, wchar_t value) {
    switch (key) {
        case 128210:  // 📒
            reg[0] = value;
            break;
        case 128211:  // 📓
            reg[1] = value;
            break;
        case 128212:  // 📔
            reg[2] = value;
            break;
        case 128213:  // 📕
            reg[3] = value;
            break;
        case 128214:  // 📖
            reg[4] = value;
            break;
        case 128215:  // 📗
            reg[5] = value;
            break;
        case 128216:  // 📘
            reg[6] = value;
            break;
        case 128217:  // 📙
            reg[7] = value;
            break;
        /* This should be done using wmem: 16 a b
        default:
            data[key] = value;*/
    }
}

wchar_t * open_file(const char *name) {
    FILE *f;
    printf("Opening the file\n");
    if ((!setlocale(LC_ALL, "en_US.utf8")) ||
       (NULL == (f = fopen(name, "rb")))) {
        perror("Could not set the locale or open the file\n");
        exit(EXIT_FAILURE);
    }
    fseek(f, 0, SEEK_END);
    size_t fsize = ftell(f);
    fseek(f, 0, SEEK_SET);

    char *string = malloc(fsize);
    fread(string, fsize, 1, f);
    fclose(f);

    size_t offset = 0, len = 0;
    while (string[offset] != 0) {
        offset += mblen(string + offset, MB_CUR_MAX);
        len++;
    }
    printf("[%lu]b [%lu]instructions\n", fsize, len);

    wchar_t *data = malloc((len + 1) * sizeof(wchar_t));
    offset = 0; len = 0;
    while (string[offset] != 0) {
        offset += mbtowc(data + len, string + offset, MB_CUR_MAX);
        len++;
    }
    free(string);
    data[len] = 0;
    return data;
}

int main() {
    wchar_t ins, a, b, c, stack[1024], reg[8], *data;
    int stackOffset = 0;
    size_t pos = 0;

    data = open_file("main.bin");

    printf("->Starting...\n");
    while (ins = data[pos++]) {
        switch (ins) {
            case 128282:  // 🔚 stop execution and terminate the program
                fprintf(stderr, "X>Forced program exit\n");
                goto exit_label;
            case 128233:  // 📩 push <a> to the stack
                stack[stackOffset++] = read;
                break;
            case 128108:  // 👬 set <a> to 1 if <b> is equal to <c>; else 0
                a = data[pos++];
                if (read == read)
                    put(data, reg, a, 1);
                else
                    put(data, reg, a, 0);
                break;
            case 128640:  // 🚀 jump to <a>
                pos = read;
                break;
            case 10067:  // ❓ if <a> is nonzero, jump to <b>
                if (read)
                    pos = read;
                break;
            case 10071:  // ❗ if <a> is zero, jump to <b>
                if (!read)
                    pos = read;
                else
                    pos++;
                break;
            case 127344:  // 🅰 stores into <a> the bitwise and of <b> and <c>
                a = data[pos++];
                b = read;
                c = read;
                put(data, reg, a, b & c);
                break;
            case 127358:  // 🅾 stores into <a> the bitwise or of <b> and <c>
                a = data[pos++];
                b = read;
                c = read;
                put(data, reg, a, b | c);
                break;
            case 128225:  // 📡 write the address of the next instruction to the stack and jump to <a>
                a = read;
                stack[stackOffset++] = pos;
                pos = a;
                break;
            case 128171:  // 💫 remove the top element from the stack and jump to it; empty stack = halt
                if (!stackOffset) {
                    fprintf(stderr, "X>Tried return with empty stack\n");
                    goto exit_label;
                }
                pos = stack[--stackOffset];
                break;
            case 128250:  // 📺 write the character <a> to the terminal
                putwchar(read);
                break;
            case 127929:  // 🎹 read a character from the terminal to <a>
                put(data, reg, data[pos++], getwchar());
                break;
            case 128284:  // 🔜 ignore next character
                pos++;
                break;
            default:
                fprintf(stderr, "X>Unrecognized operation\n");
                fprintf(stderr, "X>[%u](%lu)\n", data, pos);
                free(data);
                exit(EXIT_FAILURE);
        }
    }
    exit_label:
    free(data);
    printf("->Finished processing the binary\n");
    return EXIT_SUCCESS;
}
