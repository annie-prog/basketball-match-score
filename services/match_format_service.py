"""
Service layer for handling match format operations.
"""

from data.database import read_query
from data.models import MatchFormat

def all_formats():
    """
    Retrieve all match formats from the database.
    Returns:
        Generator of MatchFormat instances for all match formats.
    """
    query = read_query("SELECT * from match_format")
    return (MatchFormat(id=t[0], name=t[1]) for t in query)

def get_by_id(match_format_id: int) -> MatchFormat | None:
    """
    Retrieve a match format by its ID.
    Returns:
        MatchFormat or None: The MatchFormat instance if found, otherwise None.
    """
    format_data = read_query(
        '''SELECT id, name
           FROM match_format
           WHERE id = %s''', (match_format_id,)
    )
    return next((MatchFormat.from_query_result(*row) for row in format_data), None)

def sort(categories: list[MatchFormat], *, attribute="name", reverse=False) -> list[MatchFormat]:
    """
    Sort a list of match formats by the given attribute.
    Returns:
        list[MatchFormat]: The sorted list of match formats.
    """
    if attribute == 'name':
        def sort_fn(f: MatchFormat):
            return f.name
    else:
        raise ValueError(f"Unsupported attribute for sorting: {attribute}")

    return sorted(categories, key=sort_fn, reverse=reverse)
