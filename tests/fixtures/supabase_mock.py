"""Mock for Supabase client to avoid actual database calls in tests."""

from typing import Any, Dict, List, Optional


class MockSupabaseResponse:
    """Mock Supabase response object."""

    def __init__(
        self, data: Optional[List[Dict[str, Any]]] = None, count: Optional[int] = None
    ):
        self.data = data if data is not None else []
        self.count = count if count is not None else len(self.data) if data else 0


class MockSupabaseQuery:
    """Mock Supabase query builder."""

    def __init__(
        self,
        table_name: str,
        mock_data: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ):
        self.table_name = table_name
        self.mock_data = mock_data or {}
        self._filters = {}
        self._select_fields = "*"
        self._order_by = None
        self._order_desc = False
        self._range_start = None
        self._range_end = None
        self._in_filters = {}

    def select(
        self, fields: str = "*", count: Optional[str] = None
    ) -> "MockSupabaseQuery":
        """Mock select method."""
        self._select_fields = fields
        self._count = count
        return self

    def eq(self, column: str, value: Any) -> "MockSupabaseQuery":
        """Mock equality filter."""
        self._filters[column] = value
        return self

    def in_(self, column: str, values: List[Any]) -> "MockSupabaseQuery":
        """Mock IN filter."""
        self._in_filters[column] = values
        return self

    def filter(self, filter_str: str) -> "MockSupabaseQuery":
        """Mock filter method."""
        self._filter_str = filter_str
        return self

    def order(self, column: str, desc: bool = False) -> "MockSupabaseQuery":
        """Mock order method."""
        self._order_by = column
        self._order_desc = desc
        return self

    def range(self, start: int, end: int) -> "MockSupabaseQuery":
        """Mock range/pagination."""
        self._range_start = start
        self._range_end = end
        return self

    def single(self) -> "MockSupabaseQuery":
        """Mock single result."""
        self._single = True
        return self

    def insert(self, data: Dict[str, Any]) -> "MockSupabaseQuery":
        """Mock insert method."""
        self._insert_data = data
        return self

    def update(self, data: Dict[str, Any]) -> "MockSupabaseQuery":
        """Mock update method."""
        self._update_data = data
        return self

    def execute(self) -> MockSupabaseResponse:
        """Mock execute method - returns filtered data from mock_data."""
        table_data = self.mock_data.get(self.table_name, [])

        # Apply filters
        filtered_data = table_data
        if self._filters:
            filtered_data = [
                item
                for item in filtered_data
                if all(item.get(k) == v for k, v in self._filters.items())
            ]

        # Apply IN filters
        if self._in_filters:
            for column, values in self._in_filters.items():
                filtered_data = [
                    item for item in filtered_data if item.get(column) in values
                ]

        # Handle insert
        if hasattr(self, "_insert_data"):
            return MockSupabaseResponse(data=[self._insert_data])

        # Handle update
        if hasattr(self, "_update_data"):
            # For updates, return the updated data
            if filtered_data:
                updated_item = {**filtered_data[0], **self._update_data}
                return MockSupabaseResponse(data=[updated_item])
            return MockSupabaseResponse(data=[])

        # Apply range/pagination
        if self._range_start is not None and self._range_end is not None:
            filtered_data = filtered_data[self._range_start : self._range_end + 1]

        # Return count if requested
        if hasattr(self, "_count") and self._count:
            return MockSupabaseResponse(data=[], count=len(filtered_data))

        return MockSupabaseResponse(data=filtered_data)


class MockSupabaseClient:
    """Mock Supabase client."""

    def __init__(self, mock_data: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self.mock_data = mock_data or {}

    def table(self, table_name: str) -> MockSupabaseQuery:
        """Mock table method."""
        return MockSupabaseQuery(table_name, self.mock_data)

    def set_mock_data(self, table_name: str, data: List[Dict[str, Any]]):
        """Helper to set mock data for a table."""
        self.mock_data[table_name] = data
