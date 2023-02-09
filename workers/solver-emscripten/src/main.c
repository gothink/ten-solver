#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <emscripten.h>
#include "equation_map.h"

// Basic types and decls.
typedef   signed char        int8_t;
typedef unsigned char       uint8_t;
typedef          short      int16_t;
typedef unsigned short     uint16_t;
typedef          int        int32_t;
typedef unsigned int       uint32_t;
typedef          long long  int64_t;
typedef unsigned long long uint64_t;

typedef unsigned long size_t;
typedef unsigned char byte;
typedef unsigned int uint;

#define NULL ((void*)0)

float solve(const char* expr, const int* eq_map) {
  float stack[4];
  int top = -1;
  for (int i = 0; i < strlen(expr); i++) {
    if (expr[i] >= 'a' && expr[i] <= 'd') {
      // Push the corresponding integer from eq_map to stack
      stack[++top] = eq_map[expr[i] - 'a'];
    } else if (expr[i] == '+' || expr[i] == '-' || expr[i] == '*' || expr[i] == '/') {
      float op2 = stack[top--];
      float op1 = stack[top--];
      switch (expr[i]) {
        case '+': stack[++top] = op1 + op2; break;
        case '-': stack[++top] = op1 - op2; break;
        case '*': stack[++top] = op1 * op2; break;
        case '/':
          if (op2 == 0) {
            printf("Error: Division by zero\n");
            continue;
          }
          stack[++top] = op1 / op2;
          break;
      }
    }
  }
  return stack[top];
}

// const int eq_map[] = {5, 8, 9};
// const int pattern = 3;
// const int target = 10;
char** EMSCRIPTEN_KEEPALIVE get_solutions(int pattern, const int* eq_map, const int target) {
  printf("pattern: %d\n", pattern);
  if (pattern < 0 || pattern > 4) {
    pattern = 4;
  }
  // char solutions[sizes[pattern]][10];
  char** solutions = (char**)malloc(sizes[pattern]);
  for (int i = 0; i < sizes[pattern]; i++) {
    float solution = solve(pf_list[pattern][i], eq_map);
    if (solution == (float)target) {
      solutions[i] = (char*)malloc(sizeof(char) * (strlen(eq_list[pattern][i]) + 1));
      for (int j = 0; j < strlen(eq_list[pattern][i]); j++) {
        if (eq_list[pattern][i][j] >= 'a' && eq_list[pattern][i][j] <= 'd') {
            solutions[i][j] = eq_map[eq_list[pattern][i][j] - 'a'] + '0';
        } else {
            solutions[i][j] = eq_list[pattern][i][j];
        }
      }
      solutions[i][strlen(eq_list[pattern][i])] = '\0';
    }
  }
  return solutions;
}