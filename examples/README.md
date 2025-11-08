# MiniLang Example Programs

## program1.minilang

Basic program demonstrating all core features: read, arithmetic, if-else, while loop.

**Inputs:** 3, 7  
**Expected output:**

```text
17
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
```

**Run:**

```powershell
python -m minilang_compiler.compiler .\examples\program1.minilang --run --inputs 3 7
```

---

## program2_nested_if.minilang

Nested if-else statements to test control flow depth.

**Inputs:** 5, 10  
**Expected output:**

```text
15
1
```

**Run:**

```powershell
python -m minilang_compiler.compiler .\examples\program2_nested_if.minilang --run --inputs 5 10
```

---

## program3_while_zero.minilang

While loop with zero iterations (condition false from start).

**Inputs:** 0  
**Expected output:**

```text
999
```

**Run:**

```powershell
python -m minilang_compiler.compiler .\examples\program3_while_zero.minilang --run --inputs 0
```

---

## program4_precedence.minilang

Operator precedence and associativity test (no input required).

**Expected output:**

```text
14
4
6
20
1
1
```

**Run:**

```powershell
python -m minilang_compiler.compiler .\examples\program4_precedence.minilang --run
```

---

## program5_echo.minilang

Simple IO echo test.

**Inputs:** 42, 7, 0  
**Expected output:**

```text
42
7
0
```

**Run:**

```powershell
python -m minilang_compiler.compiler .\examples\program5_echo.minilang --run --inputs 42 7 0
```
