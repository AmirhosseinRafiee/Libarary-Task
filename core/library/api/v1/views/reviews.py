from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection, IntegrityError
from rest_framework.permissions import IsAuthenticated
from ..serializers import ReviewAddSerializer, ReviewUpdateSerializer


class AddReviewView(GenericAPIView):
    """
    API view for adding a new review.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewAddSerializer

    def post(self, request):
        serializer = ReviewAddSerializer(data=request.data)
        if serializer.is_valid():
            book_id = serializer.validated_data['book_id']
            user_id = request.user.id
            rating = serializer.validated_data['rating']

            try:
                with connection.cursor() as cursor:
                    # Insert new review into the database
                    cursor.execute(
                        "INSERT INTO reviews (book_id, user_id, rating) VALUES (%s, %s, %s)",
                        [book_id, user_id, rating]
                    )
                return Response({"message": "Review added"}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                # Handle case where review already exists
                return Response({"error": "Review already exists for this book by the user"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateReviewView(GenericAPIView):
    """
    API view for updating an existing review.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewUpdateSerializer

    def put(self, request):
        serializer = ReviewUpdateSerializer(data=request.data)
        if serializer.is_valid():
            review_id = serializer.validated_data['id']
            rating = serializer.validated_data['rating']
            user_id = request.user.id

            with connection.cursor() as cursor:
                # Update review in the database
                cursor.execute(
                    """
                    UPDATE reviews
                    SET rating = %s
                    WHERE id = %s AND user_id = %s
                    """,
                    [rating, review_id, user_id]
                )
                rows_affected = cursor.rowcount

            # Check if the review was updated
            if rows_affected == 0:
                return Response({"error": "Review not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Review updated"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteReviewView(APIView):
    """
    API view for deleting a review.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, review_id):
        user_id = request.user.id

        with connection.cursor() as cursor:
            # Delete review from the database
            cursor.execute(
                """
                DELETE FROM reviews
                WHERE id = %s AND user_id = %s
                """,
                [review_id, user_id]
            )
            rows_affected = cursor.rowcount

        # Check if the review was deleted
        if rows_affected == 0:
            return Response({"error": "Review not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Review deleted"}, status=status.HTTP_200_OK)
