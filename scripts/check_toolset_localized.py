"""Small script to validate ToolsetInfo accepts string and dict for display_name/description.

This script avoids importing the package-level `aidial_client` package (which pulls
in other third-party deps) by reading the `types/toolset.py` source, replacing the
top-level package imports with local stubs that provide `ExtraAllowModel` and
`Features` backed by pydantic BaseModel, and executing the modified source in an
isolated namespace.
"""
import sys
import pathlib

import pydantic


def _load_toolset_info_class():
    project_root = pathlib.Path(__file__).resolve().parents[1]
    toolset_path = project_root / "aidial_client" / "types" / "toolset.py"
    src = toolset_path.read_text(encoding="utf-8")

    # Replace package-level imports with local stubs that rely on pydantic.BaseModel
    src = src.replace(
        "from aidial_client._internal_types._model import ExtraAllowModel",
        "ExtraAllowModel = pydantic.BaseModel",
    )
    src = src.replace(
        "from aidial_client.types.deployment import Features",
        "class Features(pydantic.BaseModel):\n    pass",
    )

    ns: dict = {"pydantic": pydantic}
    exec(compile(src, str(toolset_path), "exec"), ns)
    return ns["ToolsetInfo"]


def check():
    ToolsetInfo = _load_toolset_info_class()
    try:
        obj1 = ToolsetInfo.model_validate({
            "id": "x",
            "toolset": "y",
            "display_name": {"en": "Foo", "fr": "Foo FR"},
        })
    except Exception as e:
        print("FAIL: display_name dict validation failed:", e)
        return 1

    try:
        obj2 = ToolsetInfo.model_validate({
            "id": "x",
            "toolset": "y",
            "display_name": "Foo",
            "description": "A description",
        })
    except Exception as e:
        print("FAIL: display_name string validation failed:", e)
        return 1

    print("PASS: Both validations succeeded")
    print("obj1.display_name:", obj1.display_name)
    print("obj2.display_name:", obj2.display_name)
    return 0


if __name__ == "__main__":
    sys.exit(check())

