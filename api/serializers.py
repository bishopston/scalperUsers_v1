from rest_framework import serializers
from option_pricing.models import Option, Optionsymbol, Future, Futuresymbol

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('date', 'closing_price', 'change', 'volume', 'max', 'min', 'trades', 'fixing_price', 'open_interest',)
        depth = 1

    def to_representation(self, instance):
        representation = super(OptionSerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%#d-%#m-%Y")
        return representation

class OptionSymbolSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    optiontype = serializers.CharField(source='get_optiontype_display')

    class Meta:
        model = Optionsymbol
        fields = ('symbol', 'asset', 'optiontype', 'strike', 'expmonthdate', 'options',)

    def to_representation(self, instance):
        representation = super(OptionSymbolSerializer, self).to_representation(instance)
        representation['expmonthdate'] = instance.expmonthdate.strftime("%#d-%#m-%Y")
        return representation

""" class OptionAssetSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    optiontype = serializers.CharField(source='get_optiontype_display')

    class Meta:
        model = Optionsymbol
        fields = ('symbol', 'asset', 'optiontype', 'strike', 'expmonthdate', 'options',)

    def to_representation(self, instance):
        representation = super(OptionSymbolSerializer, self).to_representation(instance)
        representation['expmonthdate'] = instance.expmonthdate.strftime("%#d-%#m-%Y")
        return representation """

class FutureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Future
        fields = ('date', 'closing_price', 'change', 'volume', 'max', 'min', 'trades', 'fixing_price', 'open_interest',)
        depth = 1

    def to_representation(self, instance):
        representation = super(FutureSerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%#d-%#m-%Y")
        return representation

class FutureSymbolSerializer(serializers.ModelSerializer):
    futures = FutureSerializer(many=True, read_only=True)

    class Meta:
        model = Futuresymbol
        fields = ('symbol', 'asset', 'expmonthdate', 'futures',)

    def to_representation(self, instance):
        representation = super(FutureSymbolSerializer, self).to_representation(instance)
        representation['expmonthdate'] = instance.expmonthdate.strftime("%#d-%#m-%Y")
        return representation

""" class FutureAssetSerializer(serializers.ModelSerializer):
    futures = FutureSerializer(many=True, read_only=True)

    class Meta:
        model = Futuresymbol
        fields = ('symbol', 'asset', 'expmonthdate', 'futures',)

    def to_representation(self, instance):
        representation = super(FutureSymbolSerializer, self).to_representation(instance)
        representation['expmonthdate'] = instance.expmonthdate.strftime("%#d-%#m-%Y")
        return representation """