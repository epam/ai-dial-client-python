import nox

nox.options.reuse_existing_virtualenvs = True

SRC = "."


def format_with_args(session: nox.Session, *args):
    session.run("autoflake", *args)
    session.run("isort", *args)
    session.run("black", *args)


@nox.session
def lint(session: nox.Session):
    """Runs linters and fixers"""
    try:
        session.run("poetry", "install", external=True)
        session.run("poetry", "check", "--lock", external=True)
        session.run("pyright", SRC)
        session.run("flake8", SRC)
        session.run("codespell", SRC)
        format_with_args(session, SRC, "--check")
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
        f"--cov={SRC}",
        "--cov-report=xml",
        "--cov-report=term",
        "--ignore=tests/integration",
    )
    session.run("coverage", "html")


@nox.session
def format(session: nox.Session):
    """Runs linters and fixers"""
    session.run("poetry", "install", external=True)
    format_with_args(session, SRC)


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
@nox.parametrize("pydantic", ["1.10.17", "2.8.2"])
@nox.parametrize("httpx", ["0.25.0", "0.27.0"])
@nox.parametrize("openai", ["1.0.0", "1.51.0"])
def test(session: nox.Session, pydantic: str, httpx: str, openai: str) -> None:
    """Runs tests"""
    session.run("poetry", "install", external=True)
    session.install(
        f"pydantic=={pydantic}",
        f"httpx=={httpx}",
        f"openai=={openai}",
    )
    session.run("pytest", "tests", "--ignore=tests/integration")


@nox.session(python=["3.11"])
@nox.parametrize("pydantic", ["1.10.17", "2.8.2"])
@nox.parametrize("openai", ["1.0.0", "1.51.0"])
def integration_test(session: nox.Session, pydantic: str, openai: str) -> None:
    """Run integration tests"""
    session.run("poetry", "install", external=True)
    session.install(
        f"pydantic=={pydantic}",
        f"openai=={openai}",
    )
    session.run("pytest", "tests/integration")
