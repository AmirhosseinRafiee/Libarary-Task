from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import connection
from ..serializers import BookSerializer


# def dictfetchall(cursor):
#     "Return all rows from a cursor as a dict"
#     columns = [col[0] for col in cursor.description]
#     return [dict(zip(columns, row)) for row in cursor.fetchall()]


class BookListView(APIView):
    """
    API view to handle fetching and filtering a list of books.
    """
    available_filters = ['genre']  # Define available filters for books

    def get(self, request):
        """
        Handle GET request to retrieve a list of books, optionally filtered by genre.
        """
        filters, params = self._get_filters_and_params()
        query = self._get_query(filters)
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            books = cursor.fetchall()  # Fetch all books based on the query
        return self._get_paginated_response(books, request)

    def _get_filters_and_params(self):
        """
        Build SQL filters and parameters based on query parameters.
        """
        filters = []
        params = []
        for key_filter in self.available_filters:
            # Get filter value from request
            val_filter = self.request.GET.get(key_filter)
            if val_filter:
                filters.append(f"{key_filter} = %s")
                params.append(val_filter)
        return filters, params

    def _get_query(self, filters):
        """
        Construct SQL query for fetching books with optional filters.
        """
        base_query = "SELECT id, title, author, genre FROM books"
        if not filters:
            return base_query  # Return base query if no filters
        query = f"{base_query} WHERE {' AND '.join(filters)}"
        return query

    def _get_paginated_response(self, books, request):
        """
        Return a paginated response for the list of books.
        """
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(books, request)
        if page is not None:
            serializer = BookSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
