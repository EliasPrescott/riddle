from typing import final, override
from docutils import nodes
from collections.abc import Iterable

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import ExtensionMetadata
import bible_ref_parser


def render_ref_nodes(chapter_ref: bible_ref_parser.ResolvedChapter) -> Iterable[nodes.Node]:
    for verse in chapter_ref.verses:
        yield nodes.superscript(text=str(verse.number) + " ")
        yield nodes.Text(verse.content + " ")


@final
class BibleRefDirective(SphinxDirective):
    has_content = True

    def _generate_nodes(self) -> Iterable[nodes.Node]:
        for raw_ref in self.content:
            if raw_ref == '':
                continue
            parsed_ref = bible_ref_parser.parse(raw_ref)
            ref = parsed_ref.resolve()
            ref_nodes = render_ref_nodes(ref)
            yield nodes.block_quote('', *[
                nodes.paragraph('', '', *ref_nodes),
                nodes.attribution(text=raw_ref),
            ])

    @override
    def run(self) -> list[nodes.Node]:
        x = list(self._generate_nodes())
        return x


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive('bible-ref', BibleRefDirective)

    return {
        'version': '1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
