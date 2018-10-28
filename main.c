// gcc main.c -o main.o && ./main.o
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include <locale.h>
#define read get(f, reg)

wint_t get(FILE *f, wint_t *reg) {
    wint_t data;
    switch (data = fgetwc(f)) {
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

void put(FILE *f, wint_t *reg, wint_t key, wint_t value) {
    // printf("%u->%u", key, value);
    switch (key) {
        case 128210:  // 📒
            reg[0] = value;
            return;
        case 128211:  // 📓
            reg[1] = value;
            return;
        case 128212:  // 📔
            reg[2] = value;
            return;
        case 128213:  // 📕
            reg[3] = value;
            return;
        case 128214:  // 📖
            reg[4] = value;
            return;
        case 128215:  // 📗
            reg[5] = value;
            return;
        case 128216:  // 📘
            reg[6] = value;
            return;
        case 128217:  // 📙
            reg[7] = value;
            return;
    }
    fpos_t pos;
    fgetpos(f, &pos);
    fseek(f, key, SEEK_SET);
    fputwc(value, f);
    fsetpos(f, &pos);
}

int main () {
    wint_t data, a, b, c, stack[1024], reg[8];
    int stackOffset = 0;
    long pos;

    FILE *f;
    char *locale = setlocale(LC_ALL, "en_US.utf8");
    f = fopen("main.bin", "r");
    pos = ftell(f);
    printf("->Starting...\n");
    while ((data = read) != WEOF) {
        // printf(".>");putwchar(data);printf("[%u](%lu)\n", data, pos);
        switch (data) {
            case 128282:  // 🔚 stop execution and terminate the program
                fprintf(stderr, "X>Forced program exit\n");
                goto exit_label;
            case 128233:  // 📩 push <a> to the stack
                stack[stackOffset++] = read;
                break;
            case 128108:  // 👬 set <a> to 1 if <b> is equal to <c>; else 0
                a = fgetwc(f);
                if (read == read)
                    put(f, reg, a, 1);
                else
                    put(f, reg, a, 0);
                break;
            case 128640:  // 🚀 jump to <a>
                fseek(f, read, SEEK_SET);
                break;
            case 10067:  // ❓ if <a> is nonzero, jump to <b>
                if (read)
                    fseek(f, read, SEEK_SET);
                break;
            case 10071:  // ❗ if <a> is zero, jump to <b>
                if (!read)
                    fseek(f, read, SEEK_SET);
                else
                    read;
                break;
            case 127344:  // 🅰 stores into <a> the bitwise and of <b> and <c>
                a = fgetwc(f);
                b = read;
                c = read;
                put(f, reg, a, b & c);
                break;
            case 128250:  // 📺 write the character <a> to the terminal
                putwchar(read);
                break;
            case 127929:  // 🎹 read a character from the terminal to <a>
                put(f, reg, fgetwc(f), getwchar());
                break;
            case 128284:  // 🔜 ignore next character
                read;
                break;
            default:
                fprintf(stderr, "X>Unrecognized operation\n");
                fprintf(stderr, "X>[%u](%lu)\n", data, pos);
                exit(-1);
        }
        pos = ftell(f);
    }
    fclose(f);
    exit_label:
    printf("->Finished processing the binary\n");
    return EXIT_SUCCESS;
}
