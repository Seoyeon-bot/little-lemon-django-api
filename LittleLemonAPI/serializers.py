# import 
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User 
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


class CategorySerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Category
        fields = ['id', 'slug', 'title']
        

class MenuItemSerializer(serializers.ModelSerializer): 
    category = CategorySerializer(read_only = True) # get 
    # category_id corresponds to the foreign key category.
    category_id = serializers.IntegerField(write_only = True)
    class Meta: 
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category','category_id'] 

class CartSerializer(serializers.ModelSerializer): 
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_id',
                  'quantity', 'unit_price', 'price']

        read_only_fields = ['user', 'menuitem', 'unit_price', 'price'] 

        validators = [
            UniqueTogetherValidator(queryset=Cart.objects.all(),fields=['user', 'menuitem']
            )
        ]

class OrderSerializer(serializers.ModelSerializer) : 
    user = serializers.StringRelatedField(read_only = True)
    delivery_crew = serializers.StringRelatedField(read_only = True)
    delivery_crew_id = serializers.IntegerField(write_only=True, required=False)

    class Meta: 
        model =Order
        fields = ['id','user', 'delivery_crew', 
                  'delivery_crew_id',
                  'status', 'total', 'date']
        read_only_fields = ['user', 'total', 'date']
      

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer()
    menuitem_id = serializers.IntegerField(write_only = True )
    order = OrderSerializer()
    order_id = serializers.IntegerField(write_only = True)
    class Meta: 
        model = OrderItem
        fields = ['id','order', 'order_id' ,'menuitem', 'menuitem_id' ,
                  'quantity', 'unit_price', 'price']
        validators = [
            UniqueTogetherValidator(queryset=OrderItem.objects.all(), fields=['order', 'menuitem'])
        ]


