# Anti-Unification in Python

This repository provides:

- A **first-order** anti-unification module (`first-order-AU.py`)
- An **experimental higher-order** anti-unification module for λ-terms (`higher-order-AU.py`)

Both are small, dependency-free, and meant as building blocks for
symbolic pattern discovery, analogy, and structure induction.

---

## 1. First-Order Anti-Unification (`first-order-AU.py`)

Implements classic **Plotkin** first-order anti-unification (least general generalization, LGG).

### Term Language

- `Const(name)` — constants, e.g. `Const("a")`, `Const("c_1")`
- `Var(name)`   — variables, e.g. `Var("X0")`
- `Func(symbol, args)` — function symbols, e.g.
  - `Func("f", (Const("a"), Const("b")))`
  - `Func("T", (Const("c_1"), Const("-1")))`

### Core Functions

- `anti_unify(t1, t2)`  
  Returns `(G, env)` where `G` is the LGG of `t1` and `t2`, and
  `env` maps pattern variables in `G` to pairs `(t1_subterm, t2_subterm)`.

- `anti_unify_list(ts1, ts2)`  
  Position-wise anti-unification of two lists of terms.

### Example

```python
from anti_unification import Const, Func, anti_unify, term_to_str

t1 = Func("f", (Const("a"), Func("g", (Const("b"),))))
t2 = Func("f", (Const("c"), Func("g", (Const("d"),))))

g, env = anti_unify(t1, t2)

print("Generalization:", term_to_str(g))
for v, (u1, u2) in env.items():
    print(v.name, "->", term_to_str(u1), ",", term_to_str(u2))
```


Example output:

```text
Generalization: f(X0, g(X1))
X0 -> a , c
X1 -> b , d
```

---

## 2. Higher-Order Anti-Unification (`higher-order-AU.py`)

Provides a **restricted higher-order anti-unification** for λ-terms:

* Variables can stand for **functions** (higher-order).
* We explicitly handle **lambda binders** and bound-variable context.
* On mismatches, the algorithm generates a fresh higher-order variable
  applied to the current bound variables, e.g. `F x1 ... xn`.

### Higher-Order Term Language

* `Const(name)` — constants
* `Var(name)`   — variables (may be higher-order)
* `App(fun, arg)` — application, e.g. `App(Const("f"), Var("x"))` for `f x`
* `Lam(var, body)` — lambda abstraction, `Lam("x", body)` for `λx. body`

### Core Function

* `ho_anti_unify(t1, t2)`
  Returns `(G, env)` where:

  * `G` is a higher-order generalization (possibly with variables applied to bound vars).
  * `env` maps each higher-order variable `F` to the pair `(t1_subterm, t2_subterm)`.

This is *not* a full HDTP implementation, but a practical higher-order AU core
you can plug into theory-projection or analogy systems.

### Example

```python
from ho_anti_unification import Const, Var, App, Lam, ho_anti_unify, term_to_str

# λx. f x   and   λx. g x
t1 = Lam("x", App(Const("f"), Var("x")))
t2 = Lam("x", App(Const("g"), Var("x")))

g, env = ho_anti_unify(t1, t2)

print("t1:", term_to_str(t1))
print("t2:", term_to_str(t2))
print("HO lgg:", term_to_str(g))
for F, (u1, u2) in env.items():
    print(F.name, "->", term_to_str(u1), ",", term_to_str(u2))
```

You should see a result where a fresh higher-order variable captures the
difference between `f` and `g` in a λ-context, e.g. something like:

```text
HO lgg: (λx. F0 x)
F0 -> (λx. f x) , (λx. g x)
```

(modulo printing details).

---

## 3. Use Cases

* Symbolic pattern discovery in structured data (e.g. musical motives).
* Template extraction and analogy-making (HDTP-style projection).
* Grammar and structure learning from examples.
* As a building block for ILP, theorem proving, or MIR research.

Both modules are deliberately small and hackable, so you can adapt them
to your own term language, scoring heuristics, or domain-specific
variations.

---

## 4. Requirements

Pure Python, no external dependencies.

---

## 5. License

Free to use, modify, and extend.
