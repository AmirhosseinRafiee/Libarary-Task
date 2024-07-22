from rest_framework import serializers
from django.db import connection


class ReviewAddSerializer(serializers.Serializer):
    """
    Serializer for adding a new review.
    """
    book_id = serializers.IntegerField()
    rating = serializers.IntegerField()

    def validate_book_id(self, value):
        # Validate if the book exists in the database.
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM books WHERE id = %s", [value])
            if cursor.fetchone() is None:
                raise serializers.ValidationError("Book does not exist")
        return value

    def validate_rating(self, value):
        # Validate if the rating is between 1 and 5.
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class ReviewUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating an existing review.
    """
    id = serializers.IntegerField()
    rating = serializers.IntegerField()

    def validate_rating(self, value):
        # Validate if the rating is between 1 and 5.
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
