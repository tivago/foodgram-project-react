class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if user.favorite_user.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                data={'detail': 'Этот рецепт уже есть в избранном!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return data