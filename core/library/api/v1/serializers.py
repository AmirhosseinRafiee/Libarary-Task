from rest_framework import serializers

class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=200)
    genre = serializers.CharField(max_length=50)

    def to_representation(self, instance):
        return {
            'id': instance[0],
            'title': instance[1],
            'author': instance[2],
            'genre': instance[3],
        }

