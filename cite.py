#!/usr/bin pyhton

"""
command:
if you want to create a new "bib" file:
    python cite.py <YOUR_LATEX>.aux
if you want to update the "bib" file:
    python cite.py <YOUR_LATEX>.bib
output:
<YOUR_LATEX>.bib

!first, compile the latex file to produce the .aux file!
then run the python command
then compile the latex file again

read aux file
    get citations
    seperate citaion for normal and arxiv and book
    make url
    get response
    seperate lines and edit:
        @ lable -> do
        title -> Capitalize
        authors -> get correct format of names
        journal -> hyperref with url
        pages -> correct if missing (not in this version!)
    replace the with updated ones
make the bibtex file

1) all the citations from one source should be used with the same label in the
latex file.
2) I assumed the citation in .aux is in lines which satarted \\citation{}, ex.:
    \\citation{isbn:9780521392938,arxiv:2011.01070v1}
3) how to cite in the text:
    - for a normal journal, use the "doi"  of the source ex.:
        \\cite{10.1016/0039-6028(93)91022-h}
    - for arxiv papres use the arxiv's label ex.: \\cite{arxiv:2011.01070v1}
    - for the book, use the ISBN of the book ex.: \\cite{isbn:9780521392938} !!
        always check the bib for the book, especially the "authors."
    - combanition of cites is also possible:
        \\cite{isbn:9780521392938,arxiv:2011.01070v1,
            10.1016/0039-6028(93)91022-h,\
            10.1088/0022-3719/16/9/005,isbn:9780122673511}
haven't tested it for the other styles of citation like: \\citep ...

for other examples:
    http://www.thamnos.de/misc/
        look-up-bibliographical-information-from-an-arxiv-id/
    https://gist.github.com/jrsmith3/5513926

One module should be installed for the books' bib:
    "isbnlib" [https://pypi.org/project/isbnlib/]
    use pip:
        pip install isbnlib
# updates:
    - using thread for downloading (now is around ten times faster!!)
SAEED AMIRI
"""

# pylint: disable=anomalous-backslash-in-string

import os
import re
import sys
import json
import time
import calendar
import concurrent.futures
from contextlib import contextmanager
from dataclasses import dataclass
import requests

# moduals for getting books' bibtex, it is easier then using "request"
from isbnlib import meta
from isbnlib.registry import bibformatters

start = time.perf_counter()

if len(sys.argv) == 1:
    sys.exit(__doc__)

STYLE: str = 'Harvard'


@dataclass
class Config:
    """configurations"""
    hyper_journal: bool = False
    print_month_year_fail: bool = False


def do_firstname(authors,
                 arxiv=None
                 ) -> list:
    """remove initat and trailing characters, also considering the
    umlats: \u00C0-\u017F
    """
    # pylint: disable=too-many-statements
    def convert_name(authors):
        """Convert a single name from 'Lastname, Firstname' to
        'Firstname Lastname'"""
        converted_names = []
        for name in authors:
            # Split on the comma and strip any extra whitespace
            last_name, first_name = name.split(', ')
            # Swap positions and create 'Firstname Lastname'
            full_name = f"{first_name} {last_name}"
            converted_names.append(full_name)
        return converted_names

    def process_inorder_names(authors):
        # removing the "author" and/or trailing "c"
        authors = re.sub('(author| c ,)', '', authors)

        # make a list of authors' names
        authors = " ".join(authors.split())

        # dropping the sapacces from the list
        authors = re.sub(', ', ',', authors).split(',')
        authors = [author.strip() for author in authors if author]
        return authors

    def make_name_list(authors):
        """doing "FirstName MidelName(s) LastName" ->
        "F. M1. M2. ... LastName"
        """
        names = []
        for name in authors:
            author_name = []
            name = re.sub(r"^'|'$", '', name)
            # split the name
            all_name = name.split(" ")
            # keep the first letter of all-name beside lastName
            for part in all_name[:-1]:
                if part[0].isupper():
                    author_name.append(f'{part[0]}.')
                else:
                    author_name.append(f' {part}')
            # apoend the lastName
            if all_name[-1].isupper():
                all_name[-1] = all_name[-1].title()
            author_name.append(f' {all_name[-1]}')
            # append the author_name to the others
            names.append("".join(author_name))
        return names

    def do_spcial_char(authors):
        """convert the special characters to latex"""
        spcial_char_map = {ord('ä'): '\\"a',
                           ord('ü'): '\\"u',
                           ord('ö'): '\\"o',
                           ord('ß'): '\ss'}
        return authors.translate(spcial_char_map)

    def do_and(authors) -> list:
        """counting number of authors, seperated by "and" and replace them
        with "{,}" so latex will print them correctly
        if there is mpre then 1, replace them with "{,}" so latex will
        print them
        """
        and_count = authors.count(' and ')
        if and_count > 1:
            authors = re.sub(' and', '{,}', authors, count=and_count-1)
            authors = re.sub(' and', '{,} and', authors, count=1)

        return authors

    # removing the sapacces from the list
    spaces: str = '{\hspace{0.167em}}'
    if spaces in authors:
        authors = authors.replace(spaces, " ")
    comma = authors.count(',') - 1
    ands = authors.count(' and ')

    # authors = re.sub('[^\u00C0-\u017FA-Za-z0-9,]+', ' ', authors)
    if arxiv is None and authors.startswith('['):
        authors = authors[1:-2]

    # remove "and" and "author" and the trailing "c" from the list for
    # now then will put them back
    # baring the names: rmoving "and"
    if ands > 0:
        authors = authors.split(' and ')
        authors = convert_name(authors)
    else:
        if comma > 0:
            authors = re.sub('( and| and )', '', authors)
        if comma == 0:
            authors = re.sub('( and| and )', ',', authors)

        authors = process_inorder_names(authors)

    names = make_name_list(authors)

    if len(names) == 1:
        authors = f'{names[0]}'
    # joining the name of the authors, if more then 1 by and
    elif len(names) >= 2:
        authors = f'{" and ".join(names)}'

    authors = do_spcial_char(authors)
    if STYLE != 'Harvard':
        authors = do_and(authors)

    return authors


def pretty_title(title) -> list:
    """seperate the "title" make a list and capitalize them"""
    title = re.sub('^{', '', title)
    # print(title,file=sys.stderr)
    # replacing {\textendash} with real dash "-" !!!
    title = re.sub(r'{\\textendash}', '-', title)
    # lowering the cases except the one wich have "-" between them
    title = [
        item.lower() if "-" not in item else item for item in title.split(" ")]
    title[-1] = title[-1].strip('.')
    # capitalized the first word
    title = \
        [item.capitalize() if i == 0 else item for i, item in enumerate(title)]
    # put item with "-" inside curly bracket {} so latex understad it
    title = [f'{{{item}}}' if "-" in item and len(item) > 2 else item for
             item in title]
    return " ".join(title)


def make_dictionary(cite) -> dict:
    """make a dictionary from the bibtex"""
    return {item.split("=")[0].strip(): item.split("=")[1].strip() for
            item in cite if '=' in item}


def print_stderr(*args, **kwargs):
    """print to stderr"""
    print(*args, file=sys.stderr, **kwargs)


@contextmanager
def open_file(fname, mode):
    """open the file"""
    try:
        f_read = open(fname, mode, encoding='utf-8')
        yield f_read
    except FileNotFoundError:
        sys.exit(f"NO Such a FILE as '{fname}'")
    finally:
        f_read.close()


def check_file_exist(fname: str) -> None:
    """check if the file exist"""
    if not os.path.exists(fname):
        sys.exit(f"\n\tNO Such a FILE as '{fname}'\n"
                 f"\tFirst compile the latex file to produce the `aux` file\n")


# first reading the "aux" tex output file
class Aux2Url:
    """
    readling 'aux' file, get 'doi' and make 'url'
    """
    doi_list: list
    arxiv: list
    journals: list
    book: list

    def __init__(self, auxfile) -> None:
        self.auxfile = auxfile

    def read_aux(self) -> list:
        """read the 'aux' file"""
        with open_file(self.auxfile, 'r') as aux:
            aux_lines = aux.readlines()
        aux_lines = [
            line.strip() for line in aux_lines if line.startswith("\citation")]
        # seperate citaion from multi citted
        aux_lines = [re.sub('(\\\citation{|})', '', line).split(",") for line
                     in aux_lines]
        # remove the duplicates
        self.doi_list = \
            list(set(cite.strip() for line in aux_lines for cite in line))

    def check_journals(self) -> list:
        """check the "doi" and seperate them"""
        self.read_aux()
        # lowering the letter cases, just in case!
        self.doi_list = [doi.lower() for doi in self.doi_list]
        # seperate the arXiv ones, since it has different headers
        self.arxiv = [doi for doi in self.doi_list if doi.startswith("arxiv")]
        # books which are cited with "isbn:"
        self.book = [isbn for isbn in self.doi_list if isbn.startswith("isbn")]
        # normal journals
        self.journals = [
            doi for doi in self.doi_list if doi not in self.arxiv or self.book]
        self.journals = [doi for doi in self.journals if '/' in doi]
        # if updating "bib" file
        self.arxiv = [doi for doi in self.arxiv if doi not in ARXIV]
        self.book = [isbn for isbn in self.book if isbn not in BOOK]
        self.journals = [doi for doi in self.journals if doi not in JOURNALS]

    def make_url(self) -> list:
        """make the url for the "doi" and "arxiv" and "isbn" """
        self.check_journals()
        # make "url" for both:
        self.arxiv = [
            f'http://export.arxiv.org/api/query?id_list={doi.split(":")[-1]}'
            for doi in self.arxiv]
        self.journals = [f'http://dx.doi.org/{doi}' for doi in self.journals]
        self.book = [isbn.split(":")[1] for isbn in self.book]
        return self.arxiv, self.journals, self.book


class RequestCite:
    """
    make the headers and request
    """
    requested: str
    jrnl_header: str
    header: str

    def __init__(self) -> str:
        self.jrnl_header = {'accept': 'application/x-bibtex'}
        self.arx_header = None
        self.isbn_header = None

    def get_header(self, url, src) -> None:
        """set the header for the request"""
        self.header = \
            self.jrnl_header if src == 'journals' else self.arx_header
    # self.header = self.jrnl_header if src == 'journals' else self.arx_header
        print(f"Request for: {url}", file=sys.stderr)

    def do_request(self, url, src) -> str:
        """get the response from the server"""
        # pylint: disable=broad-exception-caught
        self.get_header(url, src)
        try:
            self.requested = requests.get(url, headers=self.header, timeout=10)
        except requests.exceptions.RequestException as err:
            print_stderr(f"Error: {err}")
            sys.exit(f'Wrong "{url}" or Busy server')
        try:
            self.requested.encoding = 'utf-8'
            # return the text as a list
            return self.requested.text
        except Exception as err:
            print_stderr(f"Error: {err}")
            sys.exit(f'Wrong "{url}" or Busy server')


class Arxiv2Bib:
    """
    make a citation like the one from other journlas
    """
    # pylint: disable=too-many-instance-attributes
    _bib: dict[str, str]
    authors: list[str]
    title: str
    bibtex: str
    html: list
    catag: list[str]
    year: list[str]
    url: str

    def __init__(self, url) -> list:
        self._cit = RequestCite()
        html = self._cit.do_request(url, 'arxiv').split('\n')
        self.html = [item.strip() for item in html]
        self.url = url

    def get_eprint(self) -> int:
        """get the eprint"""
        return self.url.split("=")[1]

    def cock_strudel(self) -> str:
        """set the misc situation"""
        return f'@misc{{arxiv:{self.get_eprint()},'

    def get_title(self) -> list:
        """get the title"""
        i_index = [i for i, item in enumerate(self.html) if
                   item.startswith('<title>')][0]
        f_index = [i for i, item in enumerate(self.html) if
                   item.endswith('</title>') and i >= i_index][0]
        self.title = self.html[i_index:f_index+1]
        if len(self.title) > 1:
            self.title = " ".join(self.title)
        else:
            self.title = self.title[0]
        self.title = re.sub('</title>', "", re.sub('<title>', "", self.title))
        self.title = [item.lower() if "-" not in item else item for item in
                      self.title.split(" ")]
        self.title = [item.capitalize() if i == 0 else item for i, item in
                      enumerate(self.title)]
        return " ".join(self.title)

    def get_authors(self) -> list:
        """set the authors names"""
        self.authors = [re.sub('<name>', '', name) for name in self.html if
                        name.startswith('<name>')]
        self.authors = [re.sub('</name>', '', name) for name in self.authors]
        self.authors = " , ".join(self.authors)
        return do_firstname(self.authors, arxiv=ARXIV)

    def get_date(self) -> int:
        """line breaking:
        <updated>2020-11-02T14:00:00Z</updated>
        """
        self.year = [re.sub('<updated>', '', item) for item in self.html if
                     item.startswith("<updated>")][0]
        return self.year.split("-")

    def get_category(self) -> str:
        """ line breaking:
        <category term="cond-mat.mtrl-sci" scheme
        ="http://arxiv.org/schemas/atom"/>"""
        self.catag = [item.split("term=")[1].split(' ')[0] for item in
                      self.html if item.startswith("<category term=")][0]
        return self.catag.replace('"', '')

    def make_dic(self) -> list:
        """set the html"""
        self._bib = {
            'title': f'{{{self.get_title()}}},',
            'author': f'{{{self.get_authors()}}},',
            'year': f'{{{self.get_date()[0]}}},',
            'month': f'{{{calendar.month_abbr[int(self.get_date()[1])]}.}},',
            'eprint': f'{{{self.get_eprint()}}},',
            'howpublished': '{{arXiv}},',
            'note': (f'{{\href{{https://arxiv.org/abs/{self.get_eprint()}}}'
                     f'{{{self.get_category()}}}}} ')
            }
        self._bib = [f'{key} = {self._bib[key]}' for key in self._bib]
        self._bib.append("}")
        return self._bib

    def set_bibtex(self) -> str:
        """print the bibtex"""
        print(f'{self. cock_strudel()}')
        for item in self.make_dic():
            print(f'\t{item}')


class Jour2Bib:
    """
    modifying bibtex from normal journals
    """
    # pylint: disable=too-many-instance-attributes
    bib: dict[str, str]
    bib_text: list
    doi: str
    title: str
    bibtex: str
    html: str
    journal: str

    def __init__(self, url) -> None:
        self.url = url
        self.config = Config()
        self.make_html(url)

    def make_html(self, url: str) -> None:
        """make the html string"""
        self._cit = RequestCite()
        html = self._cit.do_request(url, 'journals').split('\n')
        self.html = [item.strip() for item in html if item][0]

        self.strudel = self.html.split("{")[0]

    def set_bibtex(self) -> str:
        """print bibtex"""
        # pylint: disable=broad-exception-caught
        try:
            self.update_bib()
        except Exception as err:
            print_stderr(f'\n!Unable to update for {self.url} with {err}\n')
        try:
            print(self.cock_strudel())
        except Exception as err:
            print_stderr(f'\n!Unable to cook for {self.url} with {err}\n')
        try:
            for item in self.bib_text:
                print(f'\t{item}')
        except Exception as err:
            print_stderr(f'\n!Unable to append for {self.url} with {err}\n')

    def update_bib(self) -> None:
        """set the dict by updating the bibtex"""
        self.bib: dict = self.string_dict_to_dict(self.html)

        self.bib_text: dict[str, str] = self.bib.copy()
        self.bib_text.pop('entry_type')

        self.bib_text['author'] = self.get_authors()

        self.bib_text['title'] = self.get_title()
        exist_keys: list[str] = [str(item) for item in list(self.bib.keys())]
        # self.check_bib()
        if self.strudel.split("@")[1] == 'article':
            self.bib_text['journal'] = self.get_hyper_journal()
            self.bib_text['title'] = self.bib_text['title']
        elif self.strudel.split("@")[1] == 'misc':
            self.bib_text['note'] = self.get_hyper_journal()
            self.bib_text['title'] = self.bib_text['title'] + ','
        else:
            self.bib_text['publisher'] = self.get_hyper_journal()

        if 'year' in exist_keys:
            year: str = re.sub('{|}|,|"', '', self.bib['year'])
            self.bib_text['year'] = f'{year}'
        elif self.config.print_month_year_fail:
            print_stderr(f'No "year" for {self.url}')

        if 'month' in exist_keys:
            self.bib_text['month'] = self.titlecase(self.bib['month'])
        elif self.config.print_month_year_fail:
            print_stderr(f'No "month" for {self.url}')

        self.bib_text = \
            [f'{key} = {{{self.bib_text[key]}}},' for key in self.bib_text]
        self.strudel += "{"
        self.bib_text.append("}")

    def string_dict_to_dict(self, bib_str: str) -> dict:
        """make a dictionary from the bibtex"""
        # pylint: disable=broad-exception-caught
        try:
            bib_str = str(self.html)
            entry_type_key, entries_str = bib_str.split(',', 1)
            entry_type_key = entry_type_key.strip()

            # Find all key-value pairs
            entries = re.findall(r'(\w+)=\{([^}]+)\}', entries_str)

            bib_dict = \
                {'entry_type': entry_type_key[:entry_type_key.index('{')]}
            bib_dict.update({key: value.strip() for key, value in entries})

            return bib_dict
        except Exception:
            print(f'There is something wrong with the entery:\n{self.html}\n',
                  file=sys.stderr)
            return {}

    def cock_strudel(self) -> str:
        """make "@article" with "doi" as the label for the bibtex"""
        self.doi = re.sub('}', '', self.bib["DOI"])
        # self.paper = lambda paper: expression
        return f'{self.strudel}{self.doi},'

    def get_title(self) -> list:
        """change capitalization of the title"""
        self.title = self.bib['title']
        return f'{pretty_title(self.title)}'

    def get_authors(self) -> list:
        """change the format of authors names"""
        authors = self.bib['author']
        return f'{do_firstname(authors)}'

    def get_hyper_journal(self) -> str:
        """hyperref the journals"""
        # some papers or jouranls "bibtex" dosent have "url",
        # its easier to make it!
        self.doi = re.sub('{|}|,|"', "", self.bib['DOI'])
        self.url = f"https://doi.org/{self.doi}"
        if self.config.hyper_journal:
            if self.strudel.split("@")[1] == 'article':
                self.journal = self.bib['journal']
                return f"\href{{{self.url}}}{self.journal}"
            self.journal = self.bib['publisher'][:-1]
            return f"\href{{{self.url}}}{self.journal}"
        return self.bib['journal']

    def titlecase(self, string_in: str) -> str:
        """capitalize the first letter of the month"""
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                      lambda mo: mo.group(0).capitalize(), string_in)

    def check_bib(self) -> str:
        """Check if the required fields are present in the bib entry."""
        required_fields = ['author', 'title']

        for field_i in required_fields:
            if field_i not in self.bib:
                print(f'\n"{field_i}" is missing for {self.url}\nNot added'
                      f' to the "bib" file:\n{self.bib.keys()}\n',
                      file=sys.stderr)

    def _make_dictionary(self, cite) -> dict:
        """make a dictionary from the bibtex"""
        cite = re.split(r',(?=[^{}]*{[^{}]*}$)', cite.strip())
        return {key.strip(): value.strip() for item in cite
                if '=' in item for key, value in (item.split("=", 1),)}


class Book2Bib:
    """
    get bib for books
    """

    authors: list[str]
    title: str
    bibtex: str
    html: str

    def __init__(self, isbn) -> int:
        self.isbn = isbn
        print(f"Citting for isbn: {self.isbn}", file=sys.stderr)

    # now you can use the service
    def get_html(self):
        """pass"""
        service = 'openl'
        self.bibtex = bibformatters['bibtex']
        return self.bibtex(meta(self.isbn, service))

    def make_dic(self) -> dict:
        """pass"""
        self.html = self.get_html().split("\n")
        html = [item.strip() for item in self.html]
        return make_dictionary(html)
    # change capitalization of the title

    def get_title(self) -> list:
        """pass"""
        self.title = self.make_dic()['title']
        return f'{{{pretty_title(self.title)}'

    def cock_strudel(self) -> str:
        """pass"""
        return f'@book{{isbn:{self.isbn},'

    def get_authors(self) -> list:
        """pass"""
        self.authors = self.make_dic()['author']
        return f'{{{do_firstname(self.authors)}}},'

    def update_bib(self) -> list:
        """set the dict"""
        bib: dict[str, str] = self.make_dic()
        bib_tex: dict[str, str] = {}
        bib_tex['author'] = self.get_authors()
        bib_tex['title'] = self.get_title()
        bib_tex['publisher'] = f"{bib['publisher']},"
        bib_tex['note'] = f'{{ISBN: {self.isbn}}},'
        bib_tex = [f'{key} = {bib[key]}' for key in bib]
        bib_tex.append("}")
        return bib_tex

    def set_bibtex(self) -> str:
        """write the bibtex"""
        bib = self.update_bib()
        print(self.cock_strudel())
        for i in bib:
            print(f'\t{i}')


class ReadBib:
    """
    Reading excisting 'bib' file to update
    """
    line: str
    identity: str

    def __init__(self, fname) -> None:
        self.fname = fname
        del fname

    def read_bib(self) -> list:
        """read the input"""
        with open_file(self.fname, 'r') as f_in:
            for line in f_in:
                if line.startswith('@'):
                    self.get_identity(line)

    def get_identity(self, line) -> str:
        """set the indentity"""
        self.line = line
        self.identity = self.line.split("{")[1][:-2].strip()
        self.get_list(self.identity)

    def get_list(self, identity) -> list:
        """get the lists"""
        if identity.startswith('arxiv'):
            ARXIV.append(identity)
        elif identity.startswith('isbn'):
            BOOK.append(identity)
        elif '/' in identity:
            JOURNALS.append(identity)
        else:
            pass

    def return_list(self) -> list:
        """read input"""
        self.read_bib()
        return ARXIV, JOURNALS, BOOK


class Isbn2Bib:
    """
    getting books bibtex from "https://www.googleapis.com/"
    """
    bib: list[str]
    _cite: "RequestCite"
    url: str

    def __init__(self, isbn) -> None:
        self.isbn = isbn
        self.fields = ['authors', 'editor', 'title', 'chapter', 'publisher',
                       'year', 'subtitle', 'volume', 'number', 'series',
                       'address', 'edition', 'month', 'note', 'infoLink',
                       'publishedDate']
        self.dirt = ['authors', 'infoLink', 'publishedDate']
        del isbn

    def cock_strudel(self) -> str:
        """return the isbn in style"""
        return f'@book{{isbn:{self.isbn},'

    def get_bib(self):
        """get the bib"""
        self.url = \
            f'https://www.googleapis.com/books/v1/volumes?q=isbn:{self.isbn}'
        self._cite = RequestCite()
        obj = self._cite.do_request(url=self.url, src='isbn')
        text = json.loads(obj)
        self.bib = self.update_bib(text['items'][0]['volumeInfo'])
        return self.bib

    def update_bib(self, text) -> dict:
        """make the bib"""
        self.bib = \
            {key: value for (key, value) in text.items() if key in self.fields}
        # solving Ashcroft bibtex problem
        ashcroft = 0
        for i in range(len(self.bib['authors'])):
            word: str = self.bib['authors'][i].split(' ')
            if 'Ashcroft' in word:
                ashcroft = 1
        self.bib['author'] = \
            do_firstname(str(self.bib['authors'])) if ashcroft == 0 else \
            do_firstname(str(self.bib['authors'][1:]))
        self.bib['year'] = self.bib['publishedDate']
        self.bib['url'] = self.bib['infoLink']
        if "subtitle" in self.bib:
            self.bib['title'] = \
                f"{self.bib['title']}: {pretty_title(self.bib['subtitle'])}"
        self.bib['note'] = f"\href{{{self.bib['url']}}}{{ISBN:{self.isbn}}}"
        for key in self.dirt:
            self.bib.pop(key, None)
        return self.bib

    def make_bib(self) -> None:
        """make the bibtex from the dictionary"""
        self.get_bib()
        self.bib = [f'{key} = {{{self.bib[key]}}}' for key in self.bib]

    def set_bibtex(self) -> None:
        """write the bibtex"""
        # pylint: disable=broad-except
        try:
            self.make_bib()
            print(self.cock_strudel())
            for i, item in enumerate(self.bib):
                if i != len(self.bib) - 1:
                    print(f"\t{item + ','}")
                else:
                    print(f"\t{item}")
            print("\t}")
        except Exception as _:
            print(f"CANT GET {self.isbn} FROM GOOGLE API", file=sys.stderr)
            book_bib = Book2Bib(self.isbn)
            book_bib.set_bibtex()


def get_arxiv(url):
    """Get the url info"""
    tabel = Arxiv2Bib(url)
    tabel.set_bibtex()


def get_journals(url):
    """Get the url info"""
    tabel = Jour2Bib(url)
    tabel.set_bibtex()


def get_book(isbn):
    """Get the url info"""
    tabel = Isbn2Bib(isbn)
    tabel.set_bibtex()


SOURCE = sys.argv[1].split('.', maxsplit=1)[0]
ARXIV, JOURNALS, BOOK = [], [], []

check_file_exist(SOURCE + '.aux')

# pylint: disable=consider-using-with
if sys.argv[1].split(".")[1] == 'aux':
    print(f"creating: {SOURCE}.bib", file=sys.stderr)
    BIBFILE = SOURCE + '.bib'
    sys.stdout = open(BIBFILE, 'w', encoding='utf8')
elif sys.argv[1].split(".")[1] == 'bib':
    print(f"updating: {SOURCE}.bib", file=sys.stderr)
    BIB = ReadBib(sys.argv[1])
    ARXIV, JOURNALS, BOOK = BIB.return_list()
    BIBFILE = sys.argv[1]
    sys.stdout = open(BIBFILE, '+a', encoding='utf8')


AUX = Aux2Url(SOURCE + '.aux')
ARXIV, JOURNALS, BOOK = AUX.make_url()


with concurrent.futures.ThreadPoolExecutor() as executor:
    j_papers = executor.map(get_journals, JOURNALS)
    x_papers = executor.map(get_arxiv, ARXIV)
    bok_isbn = executor.map(get_book, BOOK)
sys.stdout = sys.__stdout__
finish = time.perf_counter()
print(f'\nDONE IN {finish-start:.3f} second(s)\n')
