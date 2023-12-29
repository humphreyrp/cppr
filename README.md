# cppr

`cppr` (C-plus-plus REPL) - a simple REPL for C++

This application has only been tested on Ubuntu-22.04, but should be portable to any Linux OS.

Usage:

```
$ ./repl.py
> int a = 5;
> double b = 2;
> sizeof(b)
8
> a + b
7
> a * b
10
```

Configuration parameters accepted in `config.yaml`:
- `work_dir` - Target directory for intermediate results (default: `/tmp`)
- `compiler` - Compiler to use for compiling temporary application (default: `g++`)
- `default_headers` - Set of default header files to always include when compiling (default `[ "iostream" ]`)
