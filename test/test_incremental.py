import time

from sphinx.cmd.build import build_main


def _write_docs(srcdir):
    srcdir.mkdir()
    (srcdir / "conf.py").write_text(
        "\n".join(
            [
                'extensions = ["sphinx_tags", "myst_parser"]',
                "tags_create_tags = True",
                'tags_extension = ["md"]',
                "",
            ]
        ),
        encoding="utf8",
    )
    (srcdir / "index.md").write_text(
        "\n".join(
            [
                "# Index",
                "",
                "```{toctree}",
                "page",
                "_tags/tagsindex",
                "```",
                "",
            ]
        ),
        encoding="utf8",
    )
    (srcdir / "page.md").write_text(
        "\n".join(
            [
                "# Tagged Page",
                "",
                "```{tags} Alpha, Beta",
                "```",
                "",
            ]
        ),
        encoding="utf8",
    )


def _build(srcdir, doctreedir, outdir):
    args = ["-q", "-b", "text", "-d", str(doctreedir), str(srcdir), str(outdir)]
    assert build_main(args) == 0


def test_incremental_build_does_not_rewrite_unchanged_tag_sources(tmp_path):
    srcdir = tmp_path / "src"
    doctreedir = tmp_path / "doctrees"
    outdir = tmp_path / "out"
    _write_docs(srcdir)

    _build(srcdir, doctreedir, outdir)
    tag_sources = sorted((srcdir / "_tags").glob("*.md"))
    assert [path.name for path in tag_sources] == [
        "Alpha.md",
        "Beta.md",
        "tagsindex.md",
    ]
    mtimes = {path.name: path.stat().st_mtime_ns for path in tag_sources}

    time.sleep(0.01)
    _build(srcdir, doctreedir, outdir)

    assert {path.name: path.stat().st_mtime_ns for path in tag_sources} == mtimes


def test_incremental_build_removes_stale_tag_sources(tmp_path):
    srcdir = tmp_path / "src"
    doctreedir = tmp_path / "doctrees"
    outdir = tmp_path / "out"
    _write_docs(srcdir)
    _build(srcdir, doctreedir, outdir)

    stale = srcdir / "_tags" / "Old.md"
    stale.write_text("# Old tag\n", encoding="utf8")

    _build(srcdir, doctreedir, outdir)

    assert not stale.exists()
