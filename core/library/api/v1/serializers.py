from rest_framework import serializers
from django.db import connection


class BookSerializer(serializers.Serializer):
    """
    Serializer for book details.
    """
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=200)
    genre = serializers.CharField(max_length=50)

    def to_representation(self, instance):
        # Custom representation of book data.
        return {
            'id': instance[0],
            'title': instance[1],
            'author': instance[2],
            'genre': instance[3],
        }


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
