from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Tuple, Dict, List

# ============
# Term syntax
# ============

@dataclass(frozen=True)
class Var:
    name: str           # e.g. "X0"

@dataclass(frozen=True)
class Const:
    name: str           # e.g. "a", "c1"

@dataclass(frozen=True)
class Func:
    symbol: str         # e.g. "f", "T", "G"
    args: Tuple["Term", ...]

Term = Union[Var, Const, Func]


# ======================
# Pretty-print helpers
# ======================

def term_to_str(t: Term) -> str:
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Const):
        return t.name
    return f"{t.symbol}(" + ", ".join(term_to_str(a) for a in t.args) + ")"


# ==================================
# Anti-unification (least general generalization)
# ==================================

class AUState:
    def __init__(self) -> None:
        self.counter = 0

    def fresh_var(self) -> Var:
        v = Var(f"X{self.counter}")
        self.counter += 1
        return v


def anti_unify(
    t1: Term,
    t2: Term,
    st: AUState | None = None,
    env: Dict[Var, Tuple[Term, Term]] | None = None,
) -> Tuple[Term, Dict[Var, Tuple[Term, Term]]]:
    """
    First-order anti-unification (Plotkin):
      - returns (G, env) where G is the lgg of t1 and t2
      - env maps each Var in G to (t1-subterm, t2-subterm)
    """
    if st is None:
        st = AUState()
    if env is None:
        env = {}

    # identical -> itself
    if t1 == t2:
        return t1, env

    # same function symbol & arity -> anti-unify arguments
    if isinstance(t1, Func) and isinstance(t2, Func):
        if t1.symbol == t2.symbol and len(t1.args) == len(t2.args):
            new_args: List[Term] = []
            for a1, a2 in zip(t1.args, t2.args):
                g, env = anti_unify(a1, a2, st, env)
                new_args.append(g)
            return Func(t1.symbol, tuple(new_args)), env

    # otherwise: introduce / reuse a variable
    # try to reuse an existing var for the same pair (t1,t2)
    for v, (u1, u2) in env.items():
        if u1 == t1 and u2 == t2:
            return v, env

    v = st.fresh_var()
    env[v] = (t1, t2)
    return v, env


def anti_unify_list(
    ts1: List[Term],
    ts2: List[Term]
) -> Tuple[List[Term], Dict[Var, Tuple[Term, Term]]]:
    """
    Anti-unify two lists of terms position-wise (same length).
    """
    if len(ts1) != len(ts2):
        raise ValueError("Lists must have same length for anti_unify_list")

    st = AUState()
    env: Dict[Var, Tuple[Term, Term]] = {}
    out: List[Term] = []

    for a, b in zip(ts1, ts2):
        g, env = anti_unify(a, b, st, env)
        out.append(g)
    return out, env


# ============
# Example
# ============

if __name__ == "__main__":
    # f(a, g(b))  and  f(c, g(d))
    t1 = Func("f", (Const("a"), Func("g", (Const("b"),))))
    t2 = Func("f", (Const("c"), Func("g", (Const("d"),))))

    g, env = anti_unify(t1, t2)
    print("t1:", term_to_str(t1))
    print("t2:", term_to_str(t2))
    print("lgg:", term_to_str(g))
    print("env:")
    for v, (u1, u2) in env.items():
        print(f"  {v.name} -> ({term_to_str(u1)}, {term_to_str(u2)})")

    # list example
    s1 = [Const("a"), Func("h", (Const("b"), Const("c")))]
    s2 = [Const("x"), Func("h", (Const("y"), Const("c")))]
    g_list, env2 = anti_unify_list(s1, s2)
    print("list lgg:", [term_to_str(t) for t in g_list])
