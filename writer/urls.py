from django.urls import path
from . import views
urlpatterns = [
    path("writer-dashboard/",views.writer_dashboard,name="writer-dashboard"),
    path('create-article/',views.create_article,name="create-article"),
    path('update-article/<int:id>/', views.update_article, name="update-article"),
    path('delete-article/<int:id>/', views.delete_article, name="delete-article"),
    path('create-standard-article/',views.create_standard_article,name="create-standard-article"),
    path('create-collection/',views.create_collection,name="create-collection"),
    path('ranks',views.writer_ranks,name="writer-ranks"),
    # path('update-collection/<int:id>/',views.update_collection,name="update-collection"),
    # path('delete-collection/<int:id>/',views.delete_collection,name="delete-collection"),
]