// gcc main.c -o main.o && ./main.o
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include <locale.h>
#include <errno.h>
#define read get(reg, data[pos++])

wint_t
get(wchar_t *reg, wchar_t data)
{
    if (128210 <= data && data <= 128217) {
        return reg[data - 128210];
    }
    else {
        return data;
    }
}

void
put(wchar_t *reg, wchar_t key, wchar_t value)
{
    if (128210 <= key && key <= 128217) {
        reg[key - 128210] = value;
    }
}

wchar_t *
open_file(const char *name)
{
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
    while (offset < fsize) {
        if (!string[offset])
            offset++;
        else
            offset += mblen(string + offset, MB_CUR_MAX);
        len++;
    }
    printf("%lu bytes, %lu instructions\n", fsize, len);

    wchar_t *data = malloc((len + 1) * sizeof(wchar_t));
    fsize = len;
    offset = 0; len = 0;
    while (len < fsize) {
        if (!string[offset]) {
            offset++;
            data[len] = 0;
        }
        else
            offset += mbtowc(data + len, string + offset, MB_CUR_MAX);
        len++;
    }
    free(string);
    data[len] = 0;
    return data;
}

int
main()
{
    wchar_t ins, a, b, c, stack[1024], reg[8], *data;
    int stackOffset = 0;
    size_t pos = 0;

    data = open_file("bin");

    printf("->Starting...\n");
    while (ins = data[pos++]) {
        // printf("D>[%u](%lu)\n", ins, pos - 1);
        switch (ins) {
            case 127755:  // 🌋 stop execution and terminate the program
                fprintf(stderr, "X>Forced program exit\n");
                goto exit_label;
            case 128233:  // 📩 set register <a> to the value of <b>
                a = data[pos++];
                put(reg, a, read);
                break;
            case 128229:  // 📥 push <a> to the stack
                stack[stackOffset++] = read;
                break;
            case 128228:  // 📤 remove the top element from the stack and write it into <a>; empty stack = error
                if (!stackOffset) {
                    fprintf(stderr, "X>Tried return with empty stack\n");
                    goto exit_label;
                }
                a = data[pos++];
                b = stack[--stackOffset];
                put(reg, a, b);
                break;
            case 128108:  // 👬 set <a> to 1 if <b> is equal to <c>; else 0
                a = data[pos++];
                if (read == read)
                    put(reg, a, 1);
                else
                    put(reg, a, 0);
                break;
            case 128170:  // 💪 set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
                a = data[pos++];
                if (read > read)
                    put(reg, a, 1);
                else
                    put(reg, a, 0);
                break;
            case 128640:  // 🚀 jump to <a>
                pos = read;
                break;
            case 10067:  // ❓ if <a> is nonzero, jump to <b>
                if (read)
                    pos = read;
                else
                    pos++;
                break;
            case 10071:  // ❗ if <a> is zero, jump to <b>
                if (!read)
                    pos = read;
                else
                    pos++;
                break;
            case 10133:  // ➕ assign into <a> the sum of <b> and <c>
                a = data[pos++];
                b = read;
                c = read;
                put(reg, a, (b + c));
                break;
            case 10006:  // ✖ store into <a> the product of <b> and <c>
                a = data[pos++];
                b = read;
                c = read;
                put(reg, a, (b * c));
                break;
            case 10135:  // ➗ store into <a> the remainder of <b> divided by <c>
                a = data[pos++];
                b = read;
                c = read;
                if (!c) {
                    printf("Modulus by zero, exception incoming\n");
                    printf("D>[%u](%lu)\n", ins, pos - 1);
                }
                // printf("%u %% %u  = %u\n", b, c, (b + c) % c);
                put(reg, a, (b + c) % c);
                break;
            case 127344:  // 🅰 stores into <a> the bitwise and of <b> and <c>
                a = data[pos++];
                b = read;
                c = read;
                put(reg, a, b & c);
                break;
            case 127358:  // 🅾 stores into <a> the bitwise or of <b> and <c>
                a = data[pos++];
                b = read;
                c = read;
                put(reg, a, b | c);
                break;
            case 10134:  // ➖ stores bitwise inverse of <b> in <a>
                a = data[pos++];
                b = read;
                put(reg, a, ~b);
                break;
            case 128220:  // 📜 read memory at address <b> and write it to <a>
                a = data[pos++];
                b = read;
                put(reg, a, data[b]);
                break;
            case 128221:  // 📝 write the value from <b> into memory at address <a>
                a = read;
                b = read;
                data[a] = b;
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
                put(reg, data[pos++], getwchar());
                break;
            case 128284:  // 🔜 ignore next character
                pos++;
                break;
            case 9203:  // ⏳ no operation
                break;
            default:
                fprintf(stderr, "X>Unrecognized operation\n");
                fprintf(stderr, "X>[%u](%lu)\n", ins, pos - 1);
                free(data);
                exit(EXIT_FAILURE);
        }
    }
    exit_label:
    free(data);
    printf("->Finished processing the binary\n");
    return EXIT_SUCCESS;
}
