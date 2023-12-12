from rest_framework import serializers
from .models import average_buy,transaction

class average_buySerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    date=serializers.DateField()
    company=serializers.CharField()
    average_price=serializers.FloatField()
    balance_quantity=serializers.IntegerField()


class transactionSerializer(serializers.ModelSerializer):

    class Meta:
        model=transaction
        fields=['date','company','trade_type','quantity','price']
    
    def create(self,validated_data):
        
        return transaction.objects.create(**validated_data)

