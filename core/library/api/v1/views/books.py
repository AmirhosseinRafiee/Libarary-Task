from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import connection
from ..serializers import BookSerializer, BookRatingSerializer


# def dictfetchall(cursor):
#     "Return all rows from a cursor as a dict"
#     columns = [col[0] for col in cursor.description]
#     return [dict(zip(columns, row)) for row in cursor.fetchall()]


class BookListAPIView(APIView):
    """
    API view to handle fetching and filtering a list of books.
    """
    available_filters = ['genre']  # Define available filters for books

    def get(self, request):
        """
        Handle GET request to retrieve a list of books, optionally filtered by genre.
        """
        user_id = request.user.id if request.user.is_authenticated else None
        filters, params = self._get_filters_and_params()
        query = self._get_query(filters, user_id)
        with connection.cursor() as cursor:
            cursor.execute(query, [user_id] + params)
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
                filters.append(f"books.{key_filter} = %s")
                params.append(val_filter)
        return filters, params

    def _get_query(self, filters, user_id):
        """
        Construct SQL query for fetching books with optional filters and user's rating.
        """
        base_query = """
            SELECT books.id, books.title, books.author, books.genre, reviews.rating
            FROM books
            LEFT JOIN reviews ON books.id = reviews.book_id AND reviews.user_id = %s
        """
        if not filters:
            return base_query  # Return base query if no filters
        query = f"{base_query} WHERE {' AND '.join(filters)}"
        return query

    def _get_paginated_response(self, books, request):
        """
        Return a paginated response for the list of books.
        """
        serializer_class = self._get_serializer_class()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(books, request)
        if page is not None:
            serializer = serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = serializer_class(books, many=True)
        return Response(serializer.data)

    def _get_serializer_class(self):
        if self.request.user.is_authenticated:
            return BookRatingSerializer
        return BookSerializer


class GenreBasedBookSuggestionAPIView(APIView):
    """
    API view to suggest books based on user's most reviewed genres.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to suggest books based on genre.
        """
        user_id = request.user.id
        favorite_genres = self._get_favorite_genres(user_id)

        if favorite_genres:
            suggested_books = self._get_books_by_genres(
                favorite_genres, user_id)
            serializer = BookSerializer(suggested_books, many=True)
            return Response(serializer.data)

        return Response({"message": "No suggestions available"}, status=status.HTTP_200_OK)

    def _get_favorite_genres(self, user_id):
        """
        Get the user's most reviewed genres ordered by the count.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT genre
                FROM books
                JOIN reviews ON books.id = reviews.book_id
                WHERE reviews.user_id = %s AND reviews.rating >= 4
                GROUP BY genre
                ORDER BY COUNT(*) DESC
            """, [user_id])
            return [row[0] for row in cursor.fetchall()]

    def _get_books_by_genres(self, genres, user_id):
        """
        Get books from the user's favorite genres, excluding books already reviewed by the user.
        """
        placeholders = ', '.join(['%s'] * len(genres))
        query = f"""
            SELECT id, title, author, genre
            FROM books
            WHERE genre IN ({placeholders}) AND id NOT IN (
                SELECT book_id FROM reviews WHERE user_id = %s
            )
            ORDER BY CASE genre
        """
        for idx, genre in enumerate(genres):
            query += f" WHEN %s THEN {idx}"
        query += " END"

        params = genres + [user_id] + genres

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


class AuthorBasedBookSuggestionAPIView(APIView):
    """
    API view to suggest books based on user's most reviewed authors.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to suggest books based on author.
        """
        user_id = request.user.id
        favorite_authors = self._get_favorite_authors(user_id)

        if favorite_authors:
            suggested_books = self._get_books_by_authors(
                favorite_authors, user_id)
            serializer = BookSerializer(suggested_books, many=True)
            return Response(serializer.data)

        return Response({"message": "No suggestions available"}, status=status.HTTP_200_OK)

    def _get_favorite_authors(self, user_id):
        """
        Get the user's most reviewed authors ordered by the count.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT author
                FROM books
                JOIN reviews ON books.id = reviews.book_id
                WHERE reviews.user_id = %s AND reviews.rating >= 4
                GROUP BY author
                ORDER BY COUNT(*) DESC
            """, [user_id])
            return [row[0] for row in cursor.fetchall()]

    def _get_books_by_authors(self, authors, user_id):
        """
        Get books from the user's favorite authors, excluding books already reviewed by the user.
        """
        placeholders = ', '.join(['%s'] * len(authors))
        query = f"""
            SELECT id, title, author, genre
            FROM books
            WHERE author IN ({placeholders}) AND id NOT IN (
                SELECT book_id FROM reviews WHERE user_id = %s
            )
            ORDER BY CASE author
        """
        for idx, author in enumerate(authors):
            query += f" WHEN %s THEN {idx}"
        query += " END"

        params = authors + [user_id] + authors

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


class RelatedUsersBookSuggestionAPIView(APIView):
    """
    API view to suggest books based on related users' ratings.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to suggest books based on related users' ratings.
        """
        user_id = request.user.id
        related_users_books = self._get_related_users_books(user_id)

        if related_users_books:
            serializer = BookSerializer(related_users_books, many=True)
            return Response(serializer.data)

        return Response({"message": "No suggestions available"}, status=status.HTTP_200_OK)

    def _get_related_users_books(self, user_id):
        """
        Get books rated highly by users related to the current user, ordered by the count of related users who rated each book.
        """
        with connection.cursor() as cursor:
            # Find books the current user rated 4 or higher
            cursor.execute("""
                SELECT book_id
                FROM reviews
                WHERE user_id = %s AND rating >= 4
            """, [user_id])
            user_high_rated_books = [row[0] for row in cursor.fetchall()]

            if not user_high_rated_books:
                return []

            placeholders = ', '.join(['%s'] * len(user_high_rated_books))

            # Find other users who rated these books 4 or higher
            cursor.execute(f"""
                SELECT DISTINCT user_id
                FROM reviews
                WHERE book_id IN ({placeholders}) AND rating >= 4 AND user_id != %s
            """, user_high_rated_books + [user_id])
            related_user_ids = [row[0] for row in cursor.fetchall()]

            if not related_user_ids:
                return []

            placeholders = ', '.join(['%s'] * len(related_user_ids))

            # Find books these related users rated 4 or higher that the current user hasn't rated,
            # and order by the count of related users who rated each book
            cursor.execute(f"""
                SELECT books.id, books.title, books.author, books.genre, COUNT(reviews.user_id) as related_user_count
                FROM books
                JOIN reviews ON books.id = reviews.book_id
                WHERE reviews.user_id IN ({placeholders}) AND reviews.rating >= 4
                AND books.id NOT IN (
                    SELECT book_id FROM reviews WHERE user_id = %s
                )
                GROUP BY books.id, books.title, books.author, books.genre
                ORDER BY related_user_count DESC
            """, related_user_ids + [user_id])
            return cursor.fetchall()
