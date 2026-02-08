from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Advertisement, FavoriteAdvertisement
from .serializers import AdvertisementSerializer, FavoriteAdvertisementSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .filters import AdvertisementFilter


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends =[DjangoFilterBackend]
    filterset_class = AdvertisementFilter

    def get_queryset(self):
        """Переопределение queryset для фильтрации по статусу DRAFT"""
        queryset = super().get_queryset()

        # для неавторизированных пользователей только open и closed
        if not self.request.user.is_authenticated:
            queryset = queryset.exclude(status='DRAFT')
        # для авторизованных все, кроме чужих draft
        else:
            queryset = queryset.exclude(
                status='DRAFT',
                creator__id__ne=self.request.user.id
            )
        
        return queryset

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            if self.request.user and self.request.user.is_staff:
                return [IsAdminUser()]
            else:
                return [IsAuthenticated(), IsOwnerOrReadOnly()]       
        
        return []
    
    def perform_destroy(self, instance):
        # Проверка уже выполнена в permissions, можно удалять
        instance.delete()

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        advertisement = self.get_object()
        user = request.user

        if metod == 'POST':
            if advertisement.creator == user:
                return Response(
                    {'error': 'Нельзя добавить свое объявление в избранное'},
                    status=400
                )
            favorite, created = FavoriteAdvertisement.objects.get_or_create(
                user=user,
                advertisement=advertisement,
            )

            if created:
                serializer = FavoriteAdvertisementSerializer(favorite)
                return Response(serializer.data, status=201)
            return Response({'error': 'Уже в избранном'}, status=400)
    
        elif request.method == 'DELETE':
            FavoriteAdvertisement.objects.filter(
                user=user,
                advertisement=advertisement,
            ).delete()
            return Response(status=204)
        
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        favorites = FavoriteAdvertisement.objects.filter(user=request.user)
        serializer = FavoriteAdvertisementSerializer(favorites, many=True)
        return Response(serializer.data)
            
