from __future__ import print_function

import os
from pathlib import Path

from compas_invocations2 import build
from compas_invocations2 import docs
from compas_invocations2 import style
from compas_invocations2 import tests
from compas_invocations2 import grasshopper
from invoke import Collection

import compas_pb
from compas_pb.invocations import generate_proto_classes

ns = Collection(
    docs.help,
    style.check,
    style.lint,
    style.format,
    docs.docs,
    docs.linkcheck,
    tests.test,
    tests.testdocs,
    build.build_cpython_ghuser_components,
    build.prepare_changelog,
    build.clean,
    build.release,
    grasshopper.yakerize,
    grasshopper.update_gh_header,
    generate_proto_classes,
)
ns.configure(
    {
        "base_folder": os.path.dirname(__file__),
        "ghuser_cpython": {
            "prefix": "COMPAS EVE: ",
            "source_dir": "src/compas_eve/ghpython/components",
            "target_dir": "src/compas_eve/ghpython/components/ghuser",
        },
        "proto_folder": Path("./src") / "compas_eve" / "proto",
        "proto_include_paths": [Path("./src") / "compas_eve" / "proto", compas_pb.PROTOBUF_DEFS],
        "proto_out_folder": Path("./src") / "compas_eve" / "proto",
    }
)
