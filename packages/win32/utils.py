import os
import importlib


def extract_imports(paths):
    imps = []

    # TODO: refactor
    for path in paths:
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith('.py'):
                    with open(os.path.join(root, name), "r", encoding='utf-8') as fh:
                        for line in fh.readlines():
                            if line.strip().startswith("import "):
                                modules = line[7:].strip().split(",")
                                imps.extend(modules)
                            elif line.strip().startswith("from "):
                                module = line[5:].strip().split(" import ")[0]
                                imps.append(module)

    res = []

    for module in set(imps):
        module = module.strip()
        # exclude relative imports
        if not module.startswith("."):
            try:
                importlib.import_module(module)
            except ImportError:
                pass
            else:
                res.append(module)

    return res