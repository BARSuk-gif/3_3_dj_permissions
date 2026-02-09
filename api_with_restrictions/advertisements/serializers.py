from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, AdvertisementStatusChoices, FavoriteAdvertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', 'updated_at')
        read_only_fields = ('creator', 'created_at', 'updated_at')

    def create(self, validated_data):
        """Метод для создания"""
       
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        request = self.context.get('request')
        user = request.user

        if not self.instance:   # Создание
            is_opening = data.get('status') == AdvertisementStatusChoices.OPEN
        else:   # Обновление
            is_opening = (
                self.instance.status == AdvertisementStatusChoices.CLOSED and 
                data.get('status') == AdvertisementStatusChoices.OPEN
            )
        
        # Если открываем новое объявление
        if is_opening:            
            # Подсчет открытых объявлений пользователя
            open_ads_count = Advertisement.objects.filter(
                creator=user,
                status=AdvertisementStatusChoices.OPEN
            ).count()
        
            # Если это обновление и текущее объявление уже OPEN, корректируем счетчик
            if self.isinstance and self.instance.status == AdvertisementStatusChoices.OPEN:
                open_ads_count -= 1
            
            # если кол-во открытых больше 10, то ошибка        
            if open_ads_count >= 10:
                raise serializers.ValidationError(
                    "У пользователя не может быть больше 10 открытых объявлений."
                )
                
        return data


class FavoriteAdvertisementSerializer(serializers.ModelSerializer):
    advertisement = AdvertisementSerializer(read_only=True)

    class Meta:
        model = FavoriteAdvertisement
        fields = ['id', 'advertisement', 'created_at']
