from typing import TypeVar, Optional, Iterable, Callable
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
import parsy

books = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings",
    "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah",
    "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes",
    "Song of Songs", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah",
    "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah",
    "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians",
    "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon",
    "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John",
    "3 John", "Jude", "Revelation"
]

book = parsy.alt(*[parsy.string(x) for x in books])

number = parsy.regex('[0-9]+').map(int)

chapter = number

verse_single = number

verse_range = parsy.seq(
    start = number,
    _dash = parsy.string('-'),
    end = number,
).map(lambda x: range(x['start'], x['end'] + 1))

verse = parsy.alt(verse_range, verse_single)

def surrounded_by(start: str, inner: parsy.Parser, end: str) -> parsy.Parser:
    return parsy.seq(
        _before = parsy.string(start),
        content = inner,
        _after = parsy.string(end),
    ).map(lambda x: x['content'])

version = surrounded_by('(', parsy.regex('[a-zA-Z]*'), ')')

@dataclass
class ResolvedVerse:
    number: int
    content: str

@dataclass
class ResolvedChapter:
    version: str
    book: str
    number: int
    verses: list[ResolvedVerse]

T = TypeVar('T')
def find(f: Callable[[T], bool], iter: Iterable[T]) -> Optional[T]:
    return next((x for x in iter if f(x)), None)

@dataclass
class BibleReference:
    book: str
    chapter: int
    verse: int | range
    version: str

    def resolve(self) -> ResolvedChapter:
        tree = ET.parse(Path('bible-translations', f'{self.version}.xml'))
        bible = tree.getroot()
        book_num = str(self.book_number())
        book = find(lambda x: x.attrib['number'] == book_num, bible.iter('book'))
        assert book is not None
        chapter = find(lambda x: x.attrib['number'] == str(self.chapter), book.iter('chapter'))
        assert chapter is not None

        if isinstance(self.verse, int):
            verse = find(lambda x: int(x.attrib['number']) == self.verse, chapter.iter('verse'))
            assert verse is not None
            verses = [verse]
        else:
            verses = list(filter(lambda x: int(x.attrib['number']) in self.verse, chapter.iter('verse')))

        return ResolvedChapter(
            version = self.version,
            book = self.book,
            number = self.chapter,
            verses = [ResolvedVerse(int(x.attrib['number']), str(x.text)) for x in verses],
        )

    def book_number(self) -> int:
        return books.index(self.book) + 1

bible_reference = parsy.seq(
    book = book,
    _ws1 = parsy.string(' '),
    chapter = chapter,
    _colon = parsy.string(':'),
    verse = verse,
    _ws2 = parsy.string(' '),
    version = version,
).map(lambda x: BibleReference(x['book'], x['chapter'], x['verse'], x['version']))

def parse(input: str) -> BibleReference:
    return bible_reference.parse(input)
