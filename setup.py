# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from setuptools import Distribution, setup
from setuptools.command.build_py import build_py as _build_py
from distutils.ccompiler import new_compiler
from distutils.sysconfig import customize_compiler


ROOT = Path(__file__).resolve().parent
LIBBIOSYNTAX = ROOT / "vendor" / "libbiosyntax"


def _library_name() -> str:
    if sys.platform == "darwin":
        return "libbiosyntax.dylib"
    if os.name == "nt":
        return "biosyntax.dll"
    return "libbiosyntax.so"


class build_py(_build_py):
    def run(self) -> None:
        super().run()
        if os.environ.get("BIOSYNTAX_SKIP_BUNDLED_BUILD"):
            self.announce("skipping bundled libbiosyntax build", level=2)
            return
        self._build_libbiosyntax()

    def _build_libbiosyntax(self) -> None:
        source = LIBBIOSYNTAX / "src" / "biosyntax.c"
        include_dir = LIBBIOSYNTAX / "include"
        if not source.exists():
            raise FileNotFoundError(f"missing vendored source: {source}")
        if not include_dir.exists():
            raise FileNotFoundError(f"missing vendored include directory: {include_dir}")

        build_cmd = self.get_finalized_command("build")
        build_temp = Path(build_cmd.build_temp) / "libbiosyntax"
        build_temp.mkdir(parents=True, exist_ok=True)

        target_dir = Path(self.build_lib) / "biosyntax"
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(target_dir / "__pycache__", ignore_errors=True)
        target = target_dir / _library_name()

        compiler = new_compiler(compiler=getattr(self, "compiler", None))
        customize_compiler(compiler)

        extra_preargs = []
        if compiler.compiler_type == "unix":
            extra_preargs.append("-std=c99")

        self.announce(f"building bundled libbiosyntax: {target}", level=2)
        objects = compiler.compile(
            [str(source)],
            output_dir=str(build_temp),
            include_dirs=[str(include_dir)],
            extra_preargs=extra_preargs,
        )
        compiler.link_shared_object(objects, str(target))


class BinaryDistribution(Distribution):
    def has_ext_modules(self) -> bool:
        return True


setup(cmdclass={"build_py": build_py}, distclass=BinaryDistribution)
