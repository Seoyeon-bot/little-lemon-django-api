from django.shortcuts import render, get_object_or_404
from .models import Category, MenuItem, Cart,Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderItemSerializer, OrderSerializer
from rest_framework import generics, permissions, status
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters # Searching



# Create ListCreateAPIView to handle get and post requests
class CategoryView(generics.ListCreateAPIView): 
    queryset = Category.objects.all() 
    serializer_class = CategorySerializer

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all() 
    serializer_class = MenuItemSerializer
    # Enable filtering, searching, and ordering
    filterset_fields = ['title', 'price']
    search_fields = ['title', 'category__title']  # use related field lookup if 'category' is FK
    ordering_fields = ['title', 'price']

    # fetch the list of permissions to check - get customer and delivery (0) manager (0)
    def get_permissions(self):
        if self.request.method == 'GET': 
            return [permissions.IsAuthenticated()]
        # post put patch delete : return 403 unauthorized  post - manager(0) 201 created 
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # only manager can modify menu 
            return [IsManager()]
        return super().get_permissions() # Use parent class's defined method.

# check whether it is manager 
class IsManager(permissions.BasePermission): 
    def has_permission(self, request, view):
        # check user is logined, if yes check whether it belong to manager yes then true otherwise false 
        return (
            request.user 
            and  request.user.is_authenticated 
            and request.user.groups.filter(name='Manager').exists()
        )

# retrive smple item /menu-itmes/{menuItem} - new view for a single item (GET, PUT, PATCH, DELETE):
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all() 
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        if self.request.method == 'GET' :  
            return [permissions.IsAuthenticated()] 
        return [IsManager()] # only manger can modify the menu item 

# manager group users - list and add 
class ManagerUsersView(APIView): # used APIView for custom logic.
    permission_classes= [permissions.IsAdminUser]

    def get(self, request):  # gets all users in the “Manager” group and returns their usernames
        manager_group = Group.objects.get(name="Manager")
        users = manager_group.user_set.all() # get all users who belong to this group.
        usernames = [user.username for user in users] 
        user_data = [
            {"user id ": user.id, "username": user.username, "email": user.email}  # revised this so checkout.
            for user in users
        ]
        return Response(user_data)

    def post(self, request): 
        username = request.data.get("username")
        if not username : 
            return Response({"error" :"Username required"}
                            , status=status.HTTP_400_BAD_REQUEST)
        try : 
            user = User.objects.get(username = username)
            manager_group = Group.objects.get(name="Manager")
            manager_group.user_set.add(user) # add user to group
            return Response({"message": f"{username} added to Manager group"},
                             status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, 
                            status=status.HTTP_404_NOT_FOUND)
         

# maanger group remove user 
class ManagerUerDetailView(APIView) : 
    permission_classes = [permissions.IsAdminUser] # check whether user is manager

    def delete(self, request, user_id): 
        try : 
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name = "Manager")
            manager_group.user_set.remove(user)  # remove user from group
            return Response( 
                {"message": f"{user.username} removed from Manager group."}, 
                 status= status.HTTP_200_OK )
        except User.DoesNotExist :
            return Response(
                {"error": "User not found "}, 
                status= status.HTTP_404_NOT_FOUND
            )

# Delivery Crew 
class DeliveryCrewView(APIView): 
    permission_classes = [IsManager]

    # only manager can get all delivery crew 
    def get(self, request): 
        try: 
            # get delivery crew group instance 
            crew_group = Group.objects.get(name="Delivery-Crew")
            # acess all users in delivery crew and extract specific fields
            crew_members = crew_group.user_set.all().values("id", "username" ,"email")
            # convert queryset to list. 
            return Response({"delivery crew" : list(crew_members)}, status = status.HTTP_200_OK)
        except Group.DoesNotExist: 
            return Response({"error": "Delivery-Crew group not found"}, status=status.HTTP_404_NOT_FOUND)

    def post (self, request):
        username = request.data.get("username")
        if not username : 
            return Response({"error" : "Username required"}, status= status.HTTP_400_BAD_REQUEST )
        try : 
            user = User.objects.get(username = username )
            crew_group = Group.objects.get(name="Delivery-Crew")
            crew_group.user_set.add(user)
            return Response( {"message" : f"{username} added to Delivery-Crew Group. "}, status= status.HTTP_201_CREATED )
        except User.DoesNotExist: 
            return Response( {"error": "User not found"},  status= status.HTTP_404_NOT_FOUND )
        
# delivery crew - remove user 
class DeliveryCrewDetailView(APIView):
    permission_classes = [IsManager] # check whether user is manager 

    # only manager can delete {user_id} delivery crew
    def delete(self, request, user_id ): #  removes that specific user from Delivery Crew 
        try : 
            user = User.objects.get(id=user_id) 
            crew_group = Group.objects.get(name="Delivery-Crew")
            crew_group.user_set.remove(user)
            return Response( {"message": f"User '{user.username}' (ID {user.id}) removed from Delivery Crew group."},status=status.HTTP_200_OK )
        except User.DoesNotExist: 
            return Response(  {"error": "User not found"},  status = status.HTTP_404_NOT_FOUND )
        except Group.DoesNotExist: 
            return Response({"error" :"Delivery-Crew group not found. "}, status=status.HTTP_404_NOT_FOUND)

class CartView(generics.ListCreateAPIView): 
    serializer_class = CartSerializer
    # all methods require login.
    permission_classes = [permissions.IsAuthenticated] 
    
    # get : return only that user's cart items 
    def get_queryset(self):
        return Cart.objects.filter(user = self.request.user)
    
    # post : authomatically sets cart for that user 
    def create(self, request, *args, **kwargs):
        user = request.user
        print("perform_create CALLED for user:", user)
        # get json data value where key is menuitem_id 
        menuitem_id = self.request.data.get('menuitem_id')
        quantity = int(self.request.data.get('quantity', 1)) # default quatity value = 1 
        
        # handle error 
        if not menuitem_id: 
            return Response({'error': 'menuitem_id is required'}, status=400)
        
        # get menuitem 
        try : 
            menuitem = get_object_or_404(MenuItem, id = menuitem_id)
        except MenuItem.DoesNotExist: 
            return Response({'error': 'Menu item not found'}, status= status.HTTP_404_NOT_FOUND)
        
        unit_price = menuitem.price
        total_price = unit_price * quantity

        # Checks if the (user, menuitem) already exists. yes-> update quantity, no -> create new row
        # cart has unique validation for user and menuitem
        cart_item, created = Cart.objects.get_or_create(
            user = user, menuitem = menuitem, 
            defaults={'quantity': quantity, 'unit_price' : unit_price, 'price': total_price}
        )
        # menu item already exist then update count 
        if not created:  # created = false 
            cart_item.quantity +=quantity 
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()
       
        serializer = CartSerializer(cart_item) # pass a model instance (cart_item)
        return Response(
            serializer.data , status=status.HTTP_201_CREATED
        ) # convert cart_item into python dictionary format using .data 


    # delete all items for that user 
    def delete(self, reqeust, *args, **kwargs): 
        user = reqeust.user 
        Cart.objects.filter(user=user).delete() 

        print(f"{self.request.user} successfuly  deleted all item")
        return Response( {"message": "All items deleted from your card."} , status=status.HTTP_204_NO_CONTENT )


class OrderView(generics.ListCreateAPIView): 
    serializer_class = OrderSerializer 
    # only logged in user can see their own order. or manager 
    permission_classes = [permissions.IsAuthenticated]
    
    # Enable filtering, searching, and ordering
    filterset_fields = ['title', 'price']
    search_fields = ['title', 'category__title']  # use related field lookup if 'category' is FK
    ordering_fields = ['title', 'price']


    def get_queryset(self):
        user = self.request.user
        # staff or manager can see order 
        if user.is_staff or user.groups.filter(name="Manager").exists():
            return Order.objects.all() 
        # Deivery Crew → can only see orders assigned to them
        elif user.groups.filter(name="Delivery-Crew").exists(): 
            return Order.objects.filter(delivery_crew = user) # delivery_crew is from order model col
        else: 
            # otherwise show only that user's order 
            return Order.objects.filter(user = user)

    # post method 
    def perform_create(self,serializer) : 
        user = self.request.user  # gets the currently authenticated user
        # get all item for this user 
        cart_items = Cart.objects.filter(user = user)
        
        if not cart_items.exists():
            raise serializer.ValidationError("Your cart is empty.")
      
        # passing extra keyword arguments (user and total) to override or supplement the data
        order = serializer.save(user=user, total=0) # as placeholder total = 0
        
        # moving data from Cart → OrderItem table
        order_total = 0 
        for item in cart_items: 
            OrderItem.objects.create(
                order=order,
                menuitem= item.menuitem,
                quantity = item.quantity,
                unit_price = item.unit_price, 
                price= item.price
            )
            order_total += item.price
        
        # update order table's total 
        order.total = order_total 
        order.save()  # writes the change to the database

        #clear cart 
        cart_items.delete() 
        
        # return response 
        return Response( {"message": "Order created and cart cleared successfully."},status=status.HTTP_201_CREATED )
        
# don;t use list create api view if you want to do more than get post 
class OrderItemView(generics.RetrieveUpdateDestroyAPIView): 
   
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated] # logined user  
    queryset = Order.objects.all()

    # user can see only their order 
    def get_queryset(self):
        user = self.request.user
        order_id = self.kwargs['pk'] # Get the value of pk (primary key) from the URL

        # check if the order belongs to this user 
        order = get_object_or_404(Order, id=order_id)
        if order.user != user : 
            raise PermissionDenied("You do not have permission to view this order.")
        
        # return all items for that specific order 
        return OrderItem.objects.filter(order=order)

    # customer put, patch
    def update(self, request, *args, **kwargs ): 
        user = request.user 
        order_id = kwargs.get("pk") # get {orderId} from url 
        
        # get the order by id 
        order = get_object_or_404(Order, id = order_id)

         # delivery-crew can updated order status to 0 or 1 
        if user.groups.filter(name="Delivery-Crew").exists(): 
            
            # Ensure this delivery crew is assigned to this order
            if order.delivery_crew != user:
                raise PermissionDenied("You can only update orders assigned to you.")

            updated_order_status = request.data.get("status") # get from posted delivery status 
            if updated_order_status is None: 
                return Response( {"error": "Status field is required."},status=status.HTTP_400_BAD_REQUEST)
            order.status = updated_order_status
            order.save()
            return Response({"message": f"Order {order_id} status updated to {updated_order_status}."},status=status.HTTP_200_OK)
        # Managers — can assign delivery crew or update status
        elif user.groups.filter(name="Manager").exists(): 
             # update delivery_crew or status if provided 
            delivery_crew_id =  request.data.get("delivery-crew")
            status_value = request.data.get("status")  # get from user

            if delivery_crew_id: 
                order.delivery_crew_id = delivery_crew_id
            if status_value is not None: 
                order.status = status_value
            order.save() 
            return Response({"message": f"Order {order_id} updated successfully."},status=status.HTTP_200_OK)

        else: # customer - not allowed to update 
            raise PermissionDenied("You are not allowed to update this order.")
        

    # manager can delet this order 
    def delete(self, request, *args, **kwargs): 
        user = request.user 
        order_id = kwargs.get("pk")  # from path('orders/<int:pk>/'

        # only managers can delete orders 
        if not user.groups.filter(name="Manager").exists():  
            raise PermissionDenied("Only managers can delete orders.")
        
        order = get_object_or_404(Order, id=order_id ) # fetch single object or reutrn 404 error

        # delete all realted order items
        OrderItem.objects.filter(order = order).delete() 

        # delete order itself 
        order.delete() 

        return Response({"message": f"Order {order_id} and all related items were deleted successfully."},status=status.HTTP_204_NO_CONTENT)
    
