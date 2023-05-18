from rest_framework.views import APIView, Response, Request
from rest_framework.pagination import PageNumberPagination
from .models import Pet
from groups.models import Group
from traits.models import Trait
from .serializers import PetSerializer
from django.shortcuts import get_object_or_404


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        trait_request = request.query_params.get("trait", None)
        pets = Pet.objects.all()
        results = self.paginate_queryset(pets, request)

        if trait_request:
            filtered_pets = []
            for pet in pets:
                for trait in pet.traits.values():
                    if trait_request in trait.values():
                        filtered_pets.append(pet)
            results = self.paginate_queryset(filtered_pets, request)

        pets_serializer = PetSerializer(instance=results, many=True)
        return self.get_paginated_response(pets_serializer.data)

    def post(self, request: Request):
        pet_data = PetSerializer(data=request.data)
        pet_data.is_valid(raise_exception=True)

        group_data: dict = pet_data.validated_data.pop("group")
        traits_data: dict = pet_data.validated_data.pop("traits")

        try:
            group_exist = Group.objects.get(**group_data)
        except Group.DoesNotExist:
            group_exist = Group.objects.create(**group_data)

        pet_created = Pet.objects.create(**pet_data.validated_data, group=group_exist)

        for trait in traits_data:
            traits_exist = Trait.objects.filter(name__iexact=trait["name"])

            for t in traits_exist:
                pet_created.traits.add(t)
            if not traits_exist:
                traits_exist = Trait.objects.create(**trait)
                pet_created.traits.add(traits_exist)

        formated_data = PetSerializer(
            instance=pet_created,
        )

        return Response(formated_data.data, 201)


class PetDetailsView(APIView):
    def get(self, request: Request, pet_id: int):
        pet = get_object_or_404(Pet, id=pet_id)
        pet_serializer = PetSerializer(pet)
        return Response(pet_serializer.data)

    def patch(self, request: Request, pet_id: int):
        pet = get_object_or_404(Pet, id=pet_id)
        pet_serializer = PetSerializer(data=request.data, partial=True)
        pet_serializer.is_valid(raise_exception=True)

        if "group" in pet_serializer.validated_data:
            group_data: dict = pet_serializer.validated_data.pop("group")
            try:
                group_exist = Group.objects.get(**group_data)
            except Group.DoesNotExist:
                group_exist = Group.objects.create(**group_data)
            pet.group = group_exist

        if "traits" in pet_serializer.validated_data:
            traits_data: dict = pet_serializer.validated_data.pop("traits")
            if traits_data:
                for trait in pet.traits.values():
                    traits_exist = Trait.objects.filter(name__iexact=trait["name"])
                    print(traits_exist)
                    pet.traits.remove(traits_exist[0])

            for trait in traits_data:
                traits_exist = Trait.objects.filter(name__iexact=trait["name"])
                for t in traits_exist:
                    pet.traits.add(t)
                if not traits_exist:
                    traits_exist = Trait.objects.create(**trait)
                    pet.traits.add(traits_exist)

        for key, value in pet_serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        pet_serializer = PetSerializer(pet)

        return Response(pet_serializer.data, 200)

    def delete(self, request: Request, pet_id: int):
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()
        return Response(status=204)
