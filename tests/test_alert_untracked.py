from nbformat.v4.nbbase import new_notebook, new_markdown_cell
from jupytext import write
from jupytext.cli import jupytext, is_untracked


def test_is_untracked(tmpdir, cwd_tmpdir, tmp_repo):
    # make a test file
    file = "test.txt"
    tmpdir.join(file).write("test file\n")

    # untracked
    assert is_untracked(file)

    # added, not committed
    tmp_repo.git.add(file)
    assert not is_untracked(file)

    # committed
    tmp_repo.index.commit("test")
    assert not is_untracked(file)


def test_ignore_unmatched_ignores(tmpdir, cwd_tmpdir):
    # Unmatched file
    file = "test.txt"
    tmpdir.join(file).write("Hello\n")

    # Run jupytext
    status = jupytext(
        ["--from", "ipynb", "--to", "py:light", "--ignore-unmatched", file]
    )

    assert status == 0
    assert not tmpdir.join("test.py").exists()


def test_alert_untracked_alerts(tmpdir, cwd_tmpdir, tmp_repo, capsys):
    file = "test.py"
    tmpdir.join(file).write("print('hello')\n")

    # Run jupytext
    status = jupytext(["--from", ".py", "--to", "ipynb", "--alert-untracked", file])

    assert status != 0
    assert tmpdir.join("test.ipynb").exists()

    out = capsys.readouterr()
    assert "Output file test.ipynb is not tracked in the git index" in out.out


def test_alert_untracked_alerts_when_using_sync(tmpdir, cwd_tmpdir, tmp_repo, capsys):
    file = "test.py"
    tmpdir.join(file).write("print('hello')\n")

    tmpdir.join(".jupytext.toml").write('default_jupytext_formats = "ipynb,py"')

    # Run jupytext
    status = jupytext(["--sync", "--alert-untracked", str(file)])

    assert status != 0
    assert tmpdir.join("test.ipynb").exists()

    out = capsys.readouterr()
    assert "Output file test.ipynb is not tracked in the git index" in out.out


def test_alert_untracked_not_alerts_for_tracked(tmpdir, cwd_tmpdir, tmp_repo):
    # write test notebook
    nb = new_notebook(cells=[new_markdown_cell("A short notebook")])
    write(nb, "test.ipynb")

    # write existing output
    tmpdir.join("test.py").write("# Hello")

    # track output file
    tmp_repo.git.add("test.py")

    # Run jupytext
    status = jupytext(
        ["--from", "ipynb", "--to", "py:light", "--alert-untracked", "test.ipynb"]
    )

    assert status == 0