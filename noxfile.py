import nox

nox.options.reuse_existing_virtualenvs = True

SRC = ["aidial_client", "tests", "noxfile.py"]


@nox.session
def lint(session: nox.Session):
    """Runs linters and fixers"""
    try:
        session.run("poetry", "install", "--all-extras", external=True)
        session.run("poetry", "check", "--lock", "--strict", external=True)
        session.run("ruff", "check", *SRC)
        session.run("ruff", "format", "--check", *SRC)
        session.run("pyright", *SRC)
    except Exception:
        session.error(
            "linting has failed. Run 'make format' "
            "to fix formatting and fix other errors manually"
        )


@nox.session
def coverage(session: nox.Session) -> None:
    """Run tests and generate coverage report"""
    session.run("poetry", "install", external=True)
    session.run(
        "pytest",
        f"--cov={SRC[0]}",
        "--cov-report=xml",
        "--cov-report=term",
        "--ignore=tests/integration",
    )
    session.run("coverage", "html")


@nox.session
def format(session: nox.Session):
    """Runs linters and fixers"""
    session.run("poetry", "install", "--only", "lint", external=True)
    session.run("ruff", "check", "--fix", *SRC)
    session.run("ruff", "format", *SRC)


@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
@nox.parametrize("pydantic", ["1.10.17", "2.8.2"])
@nox.parametrize("httpx", ["0.25.0", "0.27.0"])
@nox.parametrize("openai", ["1.109.1", "2.26.0"])
@nox.parametrize("aiofiles", ["0.5.0", "24.1.0"])
def test(
    session: nox.Session, pydantic: str, httpx: str, openai: str, aiofiles: str
) -> None:
    """Runs tests"""
    session.run("poetry", "install", external=True)
    session.install(
        f"pydantic=={pydantic}",
        f"httpx=={httpx}",
        f"openai=={openai}",
        f"aiofiles=={aiofiles}",
    )
    session.run("pytest", "tests", "--ignore=tests/integration")


@nox.session(python=["3.11"])
@nox.parametrize("pydantic", ["1.10.17", "2.8.2"])
@nox.parametrize("openai", ["1.1.0", "1.51.0"])
@nox.parametrize("aiofiles", ["0.5.0", "24.1.0"])
def integration_test(
    session: nox.Session, pydantic: str, openai: str, aiofiles: str
) -> None:
    """Run integration tests"""
    session.run("poetry", "install", external=True)
    session.install(
        f"pydantic=={pydantic}",
        f"openai=={openai}",
        f"aiofiles=={aiofiles}",
    )
    session.run("pytest", "tests/integration")
