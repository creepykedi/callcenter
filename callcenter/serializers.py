from rest_framework import serializers
from .models import Main, Table, Contractor, Sources


class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class SourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sources
        fields = '__all__'


class MainSerializer(serializers.ModelSerializer):
    project = ContractorSerializer(read_only=True)
    source = SourcesSerializer(read_only=True)
    related_model = TableSerializer(read_only=True)

    class Meta:
        model = Main
        fields = '__all__'