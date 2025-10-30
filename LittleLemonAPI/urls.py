from django.urls import path,include 
#Djoser and token authentication URLs
from . import views 

urlpatterns = [ 
    path('category/', views.CategoryView.as_view()), 
    # Implement proper filtering, pagination and sorting capabilities
    # http://127.0.0.1:8000/api/menu-items?ordering=price/ in insonima with admin token 
    path('menu-items/', views.MenuItemView.as_view(), name='menu-items'),  
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='single-menu-item'),


    # /api/cart/menu-itmes/ 
    path('cart/menu-items/', views.CartView.as_view(), name='cart-menu-items'),
    
    #/api/orders/ 
    #/api/ordes/{orderId}
    # Implement proper filtering, pagination and sorting capabilities
    path('orders/', views.OrderView.as_view()), 
    path('orders/<int:pk>/', views.OrderItemView.as_view()),
 
    # --- User Group Management (Managers / Delivery Crew) ---
    # api/groups/manager/users 
    # api/groups/manager/users/{userId}
    path('groups/manager/users/', views.ManagerUsersView.as_view()), 
    path('groups/manager/users/<int:user_id>/', views.ManagerUerDetailView.as_view()), 

    # api/groups/delivery-crew/users 
    # api/groups/delivery-crew/users/{userId}
    path('groups/delivery-crew/users/', views.DeliveryCrewView.as_view()), 
    path('groups/delivery-crew/users/<int:user_id>/', views.DeliveryCrewDetailView.as_view()),

    # --- Authentication and Registration (via Djoser) ---
    path('users/', include('djoser.urls')),   # /api/users, /api/users/me/
    path('token/login/', include('djoser.urls.authtoken')),  # /token/login/

]