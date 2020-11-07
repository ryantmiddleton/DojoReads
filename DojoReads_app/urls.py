from django.urls import path     
from . import views

urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('books', views.displayBooks),
    path('add_book_page', views.getAddBookPage),
    path('add_book', views.addBook),
    path('books/<int:book_id>', views.displayBook), 
    path('add_review/<int:book_id>', views.addReview),
    path('user_page/<int:user_id>', views.displayUser),
    path('delete_review/<int:review_id>', views.deleteReview)

]