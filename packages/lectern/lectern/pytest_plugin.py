try:
    from pytest_insta import Fmt
except ImportError:
    pass
else:
    from pathlib import Path

    from lectern import Document

    class FmtPackText(Fmt[Document]):
        extension = ".pack.txt"

        def load(self, path: Path) -> Document:
            return Document(path=path)

        def dump(self, path: Path, value: Document):
            value.save(path)

    class FmtPackMarkdown(Fmt[Document]):
        extension = ".pack.md"

        def load(self, path: Path) -> Document:
            return Document(path=path)

        def dump(self, path: Path, value: Document):
            value.save(path)

    class FmtPackMarkdownExternalFiles(Fmt[Document]):
        extension = ".pack.md_external_files"

        def load(self, path: Path) -> Document:
            return Document(path=path / "README.md")

        def dump(self, path: Path, value: Document):
            path.mkdir(exist_ok=True)
            value.save(path / "README.md", external_files=path)
