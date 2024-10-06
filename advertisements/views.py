from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers  import AdvertisementSerializer, UserSerializer
from .models import Advertisement, FavoriteAdvertisement
from .permissions import IsOwner
from .filters import AdvertisementFilter


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений.
    администратор может удалять и менять объявления, но не может удалять или менять черновики (статус = DRAFT)
    владелец объявления может все
    Аутентифицированный пользователь может получать все объявления, кроме черновиков (статус  = DRAFT), не может менять или удалять чужие объявления
    Не аутентифицированный пользователь может только просматривать объявления, кроме черновиков (статус = DRAFT)
    """
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filterset_class = AdvertisementFilter

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_to_favorites(self, request, pk=None):
        """Добавить объявление в избранное."""
        advertisement = self.get_object()
        if advertisement.creator == request.user:
            return Response({'detail': 'Нельзя добавить своё объявление в избранное.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if FavoriteAdvertisement.objects.filter(user=request.user, advertisement=advertisement).exists():
            return Response({'detail': 'Объявление уже добавлено в избранное.'}, status=status.HTTP_400_BAD_REQUEST)
        FavoriteAdvertisement.objects.create(user=request.user, advertisement=advertisement)
        return Response({'detail': 'Объявление добавлено в избранное.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_favorite(self, request):
        """Получить избранные объявления."""
        favorites_adv = Advertisement.objects.filter(favorited_by__user=request.user.id)
        serializer = AdvertisementSerializer(favorites_adv, many=True)
        return Response(serializer.data)

    def list(self, request):
        """Получение списка объявлений"""
        if request.user.is_authenticated:
            user_advertisiments = Advertisement.objects.filter(creator=request.user)
            other_advertisiments = Advertisement.objects.filter(status__in=["OPEN", "CLOSED"])
            queryset = user_advertisiments | other_advertisiments
            serializer = AdvertisementSerializer(queryset, many=True)
            return Response(serializer.data)
        queryset = Advertisement.objects.filter(status__in=["OPEN", "CLOSED"])
        serializer = AdvertisementSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Поулчение конкретного объявления по id"""
        advertisement = self.get_object()
        if advertisement.status == "DRAFT" and advertisement.creator != request.user:
            return Response({"detail:":"Нет такого объявления."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdvertisementSerializer(advertisement)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Полное обновление объявления PUT"""
        advertisement = self.get_object()
        if advertisement.status == "DRAFT" and advertisement.creator != request.user:
            return Response({"detail:":"Нет такого объявления."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(advertisement, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаление объявления"""
        advertisement = self.get_object()
        if advertisement.status == "DRAFT" and advertisement.creator != request.user:
            return Response({"detail:": "Нет такого объявления."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(advertisement)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление объявления (PATCH)."""
        advertisement = self.get_object()
        if advertisement.status == "DRAFT" and advertisement.creator != request.user:
            return Response({"detail:": "Нет такого объявления."},status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(advertisement, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        return []
