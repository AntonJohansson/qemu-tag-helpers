#include <stdio.h>
int print_tagged_helper(const char *str) {
    fputs(str, stderr);
    fputs("\n", stderr);
}
