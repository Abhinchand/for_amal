import re


class Search:
    """
    Class filtering user search keywords. Returns the boolean value based on the search query. Keywords may contain numeric, uppercase, lowercase. eg. Protein name: Cry1Aa1. User can able to use keywords like following

    Cry10* -> wildcard search should work

    Cry -> should list all cry category

    Cry1 -> must not return Cry10. Only Cry1's.

    Cry10 -> must not return Cry1. Only Cry10's

    Cry10A -> must return all Cry10A i.e Cry10Aa to Cry10Az

    Cry10Aa -> must return all Cry10Aa i.e Cry10Aa1 to Cry10Aa100

    Cry10Aa1 -> must return only Cry10Aa1

    """

    def __init__(self, search_keyword: str):
        """
        Parameters
        ----------
        arg: str
            The search keyword: protein name

        Returns
        -------
        bool
            The return value. True for success, False otherwise

        """

        self.search_keyword = search_keyword

    def is_fullname(self):
        try:
            name = re.match(
                r"^[A-Za-z][A-Za-z]{2}\d{1,3}[A-Za-z][A-Za-z]\d{1,3}$",
                self.search_keyword,
            ).group()
            if name:
                return True
        except Exception:
            return False

    def is_uppercase(self):
        try:
            name = re.match(
                r"^[A-Za-z][A-Za-z]{2}\d{1,3}[A-Za-z]$",
                self.search_keyword,
            ).group()
            if name:
                return True
        except Exception:
            return False

    def is_lowercase(self):
        try:
            name = re.match(
                r"^[A-Za-z][A-Za-z]{2}\d{1,3}[A-Za-z][A-Za-z]$",
                self.search_keyword,
            ).group()
            if name:
                return True
        except Exception:
            return False

    def is_single_digit(self):
        try:
            name = re.match(
                r"^[A-Za-z][A-Za-z]{2}\d{1}$", self.search_keyword).group()
            if name:
                return True
        except Exception:
            return False

    def is_double_digit(self):
        try:
            name = re.match(
                r"^[A-Za-z][A-Za-z]{2}\d{2}$", self.search_keyword).group()
            if name:
                return True
        except Exception:
            return False

    def is_triple_digit(self):
        try:
            name = re.match(
                r"^[A-Za-z][A-Za-z]{2}\d{3}$", self.search_keyword).group()
            if name:
                return True
        except Exception:
            return False

    def is_three_letter(self):
        try:
            name = re.match(
                r"^[A-Za-z][A-Za-z]{2}$", self.search_keyword).group()
            if name:
                return True
        except Exception:
            return False

    def is_three_letter_case(self):
        try:
            name = re.match(
                r"^[A-Za-z][A-Za-z]{2}$", self.search_keyword).group()
            if name:
                return True
        except Exception:
            return False

    def digit_length(self):
        name = re.split("([0-9]+)", self.search_keyword)
        try:
            length_number = len(str(name[1]))
            return length_number
        except Exception:
            return False

    def is_wildcard(self):
        if "*" in self.search_keyword:
            return True
        else:
            return False

    def fulltext(self):
        text_length = len(self.search_keyword)
        text_isalpha = self.search_keyword.isalpha()
        rules = [text_length > 5, text_isalpha]
        if all(rules):
            return True
        else:
            return False

    def bthur0001_55730(self):
        s = "bthur0001_55730"
        if re.search(r"\b" + self.search_keyword + r"\b", s):
            return True
        else:
            return False


def filter_one_name(proteins):
    filtered_protein = []
    for protein in proteins:
        k = re.split("([0-9]+)", protein.name)
        if int(k[1]) // 10 == 0:
            filtered_protein.append(protein)
    return filtered_protein


def filter_one_oldname(proteins):
    filtered_protein = []
    for protein in proteins:
        k = re.split("([0-9]+)", protein.oldname)
        if int(k[1]) // 10 == 0:
            filtered_protein.append(protein)
        else:
            pass
    return filtered_protein


class SearchOldname:
    def __init__(self, search_keyword):
        self.search_keyword = search_keyword


def _sorted_nicely(l, sort_key=None):
    """Sort the given iterable in the way that humans expect. https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""

    def convert(text):
        return int(text) if text.isdigit() else text

    if sort_key is None:

        def alphanum_key(key):
            return [convert(c) for c in re.split("([0-9]+)", key)]

    else:

        def alphanum_key(key):
            return [convert(c) for c in re.split("([0-9]+)", getattr(key, sort_key))]

    return sorted(l, key=alphanum_key)
