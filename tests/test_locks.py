"""El cerrojo exclusivo lo toman solo sus dueños; los sondeos usan LOCK_SH (retro 2026-11-06 de fix-0.4.1, P1).

Un sondeo con `LOCK_EX|LOCK_NB` choca con otro sondeo simultáneo y da por vivo un worker o servicio que no lo está
(la carrera de la 0.4.1: `queue._no_worker` se quedó así cuando `ec89eb0` pasó los demás a `LOCK_SH`)."""
import ast
import unittest
from pathlib import Path

GIMG = Path(__file__).resolve().parent.parent / "gimg"
# (archivo, función): quien toma el cerrojo para quedárselo, no para mirar si otro lo tiene
OWNERS = {
    ("fsutil.py", "lock"),             # lectura-modificación-escritura de un archivo
    ("fsutil.py", "try_lock"),         # lo mismo, sin esperar
    ("worker.py", "_single_worker"),   # worker.lock, el único worker
    ("service.py", "_single_instance"),  # serve.lock, el único servicio
    ("service.py", "ensure_running"),  # serve.replace.lock: un CLI a la vez reemplaza el servicio
}


def exclusive_locks():
    """{(archivo, función más interna)} de cada uso de `LOCK_EX` en gimg/."""
    found = set()
    for path in sorted(GIMG.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        def visit(node, owner):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                owner = node.name
            if isinstance(node, ast.Attribute) and node.attr == "LOCK_EX" or \
                    isinstance(node, ast.Name) and node.id == "LOCK_EX":
                found.add((str(path.relative_to(GIMG)), owner))
            for child in ast.iter_child_nodes(node):
                visit(child, owner)

        visit(tree, None)
    return found


class LockTests(unittest.TestCase):
    def test_only_the_owners_take_the_exclusive_lock(self):
        extra = exclusive_locks() - OWNERS
        self.assertFalse(extra, f"LOCK_EX fuera de sus dueños {sorted(extra)}: un sondeo usa "
                                "LOCK_SH|LOCK_NB; si es un dueño nuevo, añádelo a OWNERS con el porqué")

    def test_every_owner_still_takes_it(self):
        self.assertEqual(OWNERS - exclusive_locks(), set(), "OWNERS lista una función que ya no toma LOCK_EX")


if __name__ == "__main__":
    unittest.main()
