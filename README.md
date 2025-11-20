Anti-Unification in Python

This repository provides a simple, clean implementation of first-order anti-unification (least general generalization, LGG) in Python.
It supports:

Constants (Const("a"))

Variables (Var("X0"))

Function terms (Func("f", (...)))

Anti-unifying single terms and lists of terms

Returning both the generalization and the substitution pairs

The implementation follows the classic Plotkin formulation of LGG.

File Structure
anti_unification.py


Contains all term definitions, pretty-printing, and the anti-unification algorithm.

Quick Example
from anti_unification import Const, Func, anti_unify, term_to_str

t1 = Func("f", (Const("a"), Func("g", (Const("b"),))))
t2 = Func("f", (Const("c"), Func("g", (Const("d"),))))

g, env = anti_unify(t1, t2)

print("Generalization:", term_to_str(g))
print("Env:", {v.name: (term_to_str(x), term_to_str(y)) for v,(x,y) in env.items()})


Output (structure may vary):

Generalization: f(X0, g(X1))
Env: {'X0': ('a','c'), 'X1': ('b','d')}

List Anti-Unification
from anti_unification import Const, Func, anti_unify_list

s1 = [Const("a"), Func("h", (Const("b"), Const("c")))]
s2 = [Const("x"), Func("h", (Const("y"), Const("c")))]

g_list, env = anti_unify_list(s1, s2)


This computes position-wise generalizations of sequences.

Use Cases

Pattern discovery

Template extraction

Structure inference

Symbolic reasoning / analogy preprocessing

Music-structure pattern mining (e.g., variation templates)

Requirements

Pure Python.
No external dependencies.

License

Free to use and extend.
