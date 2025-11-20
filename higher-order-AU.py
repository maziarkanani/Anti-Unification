# ho_anti_unification.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List, Union

# =========================
# Higher-order term syntax
# =========================

@dataclass(frozen=True)
class Var:
    name: str  # can be higher-order

@dataclass(frozen=True)
class Const:
    name: str

@dataclass(frozen=True)
class App:
    fun: "Term"
    arg: "Term"

@dataclass(frozen=True)
class Lam:
    var: str          # bound variable name
    body: "Term"

Term = Union[Var, Const, App, Lam]


# =========================
# Pretty-printing
# =========================

def term_to_str(t: Term) -> str:
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Const):
        return t.name
    if isinstance(t, Lam):
        return f"(λ{t.var}. {term_to_str(t.body)})"
    if isinstance(t, App):
        # flatten application for nicer printing
        head, args = _spine(t)
        parts = [term_to_str(head)] + [term_to_str(a) for a in args]
        return "(" + " ".join(parts) + ")"
    raise TypeError(t)


def _spine(t: Term) -> Tuple[Term, List[Term]]:
    """Decompose t into head and argument list: (((f a) b) c) -> (f, [a,b,c])."""
    args: List[Term] = []
    while isinstance(t, App):
        args.append(t.arg)
        t = t.fun
    args.reverse()
    return t, args


# =========================
# Higher-order AU state
# =========================

class HOAUState:
    def __init__(self) -> None:
        self.counter = 0

    def fresh_var(self, prefix: str = "F") -> Var:
        v = Var(f"{prefix}{self.counter}")
        self.counter += 1
        return v


# =========================
# Higher-order anti-unify
# =========================

Env = Dict[Var, Tuple[Term, Term]]

def ho_anti_unify(t1: Term, t2: Term) -> Tuple[Term, Env]:
    """
    Restricted higher-order anti-unification for lambda terms.

    - Variables may stand for functions.
    - We respect lambda binders (Lam).
    - On mismatches, we create a fresh higher-order variable applied
      to the current bound variables in scope (λ-context).
    """
    st = HOAUState()
    env: Env = {}
    gen, env = _ho_au(t1, t2, ctx=[], st=st, env=env)
    return gen, env


def _ho_au(
    t1: Term,
    t2: Term,
    ctx: List[Var],
    st: HOAUState,
    env: Env,
) -> Tuple[Term, Env]:
    # identical terms → themselves
    if t1 == t2:
        return t1, env

    # both lambdas: α-rename to a common bound variable name and recurse
    if isinstance(t1, Lam) and isinstance(t2, Lam):
        fresh_name = _fresh_bound_name(t1.var, t2.var)
        v = Var(fresh_name)

        body1 = _subst_bound(t1.body, t1.var, v)
        body2 = _subst_bound(t2.body, t2.var, v)

        gen_body, env = _ho_au(body1, body2, ctx + [v], st, env)
        return Lam(fresh_name, gen_body), env

    # try rigid-rigid constant heads with same symbol
    h1, args1 = _spine(t1)
    h2, args2 = _spine(t2)

    if (
        isinstance(h1, Const) and
        isinstance(h2, Const) and
        h1.name == h2.name and
        len(args1) == len(args2)
    ):
        # rigid head, same symbol → AU arguments
        new_args: List[Term] = []
        for a1, a2 in zip(args1, args2):
            g, env = _ho_au(a1, a2, ctx, st, env)
            new_args.append(g)
        return _rebuild_app(h1, new_args), env

    # mismatch case (flex-flex or flex-rigid etc.)
    # reuse variable if this exact pair seen before
    for v, (u1, u2) in env.items():
        if u1 == t1 and u2 == t2:
            return _apply_ctx(v, ctx), env

    # introduce fresh higher-order variable F, applied to all bound vars in ctx
    F = st.fresh_var()
    env[F] = (t1, t2)
    return _apply_ctx(F, ctx), env


def _apply_ctx(f: Var, ctx: List[Var]) -> Term:
    """Build F x1 ... xn given current bound-variable context."""
    t: Term = f
    for v in ctx:
        t = App(t, v)
    return t


def _rebuild_app(head: Term, args: List[Term]) -> Term:
    t: Term = head
    for a in args:
        t = App(t, a)
    return t


def _fresh_bound_name(x: str, y: str) -> str:
    if x == y:
        return x
    return "z"  # simple, safe choice; could be smarter


def _subst_bound(t: Term, old: str, v: Var) -> Term:
    """
    Capture-avoiding substitution for bound variables:
    replace bound variable name 'old' with Var v inside t.
    Assumes no nested shadowing of 'old' other than the binding we're processing.
    """
    if isinstance(t, Var):
        if t.name == old:
            return v
        return t
    if isinstance(t, Const):
        return t
    if isinstance(t, App):
        return App(_subst_bound(t.fun, old, v), _subst_bound(t.arg, old, v))
    if isinstance(t, Lam):
        if t.var == old:
            # this Lam introduces a new binding for 'old'; stop
            return t
        return Lam(t.var, _subst_bound(t.body, old, v))
    raise TypeError(t)


# =========================
# Example usage
# =========================

if __name__ == "__main__":
    # Example 1: λx. f x   and   λx. g x
    t1 = Lam("x", App(Const("f"), Var("x")))
    t2 = Lam("x", App(Const("g"), Var("x")))

    g, env = ho_anti_unify(t1, t2)
    print("t1:", term_to_str(t1))
    print("t2:", term_to_str(t2))
    print("HO lgg:", term_to_str(g))
    print("Env:")
    for F, (u1, u2) in env.items():
        print(f"  {F.name} ↦ ({term_to_str(u1)}, {term_to_str(u2)})")

    # Example 2: λx. T (G x)   and   λy. T (H y)
    t3 = Lam("x", App(Const("T"), App(Const("G"), Var("x"))))
    t4 = Lam("y", App(Const("T"), App(Const("H"), Var("y"))))

    g2, env2 = ho_anti_unify(t3, t4)
    print("\nExample 2:")
    print("t3:", term_to_str(t3))
    print("t4:", term_to_str(t4))
    print("HO lgg:", term_to_str(g2))
    print("Env:")
    for F, (u1, u2) in env2.items():
        print(f"  {F.name} ↦ ({term_to_str(u1)}, {term_to_str(u2)})")
