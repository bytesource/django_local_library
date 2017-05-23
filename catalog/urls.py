from django.conf.urls import url
from . import views

urlpatterns = [
    # NOTE:
    # The matched URL is catalog/ + <empty string> 
    # Because we are in the catalog application, /catalog/ is assumed. 
    # views.index will be called if we receive an HTTP request with a URL of /catalog/
    # -- views.index : A function named index() in views.py
    #  -- name='index': Uniquely identifies this particular URL mapping.
    #     Used to reverse the mapping to a template:
    #     <a href="{% url 'index' %}">Home</a>.
    url(r'^$', views.index, name='index'),
    # /catalog/books/
    # We will be INHERITING from an EXISTING generic view function that 
    # already does most of what we want this view function to do.
    # as_view() does all the work of 
    # -- creating an instance of the class, 
    # -- and making sure that the right handler methods are called for incoming HTTP requests.
    url(r'^books/$', views.BookListView.as_view(), name='books'),
    # /catalog/book/<pk>
    # Caputured part is passed to the view function as a parameter named 'pk'.
    # NOTE: The GENERIC CLASS-BASED __detail__ view EXPECTS to be passed a parameter named pk.
    #       If you're writing our own function view you can use whatever parameter name you like.
    url(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),

    url(r'^authors/$', views.AuthorListView.as_view(), name='authors'),
    url(r'^author/(?P<pk>\d+)$', views.AuthorDetailView.as_view(), name='author-detail'),

]

urlpatterns += [
    url(r'^mybooks/$', views.LoanedBooksByUserListView.as_view(), name='my_borrowed'),
]

urlpatterns += [
    url(r'^borrowed/$', views.LoanedBooksListView.as_view(), name='borrowed'),
]

# Uses our form
urlpatterns += [
    url(r'^book/(?P<pk>[-\w]+)/renew/$', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
    url(r'^author/create/$', views.AuthorCreate.as_view(), name='author_create'),
    url(r'^author/(?P<pk>\d+)/update/$', views.AuthorUpdate.as_view(), name='author_update'),
    url(r'^author/(?P<pk>\d+)/delete/$', views.AuthorDelete.as_view(), name='author_delete'),
]

urlpatterns += [
    url(r'^book/create/$', views.BookCreate.as_view(),             name='book_create'),
    url(r'^book/(?P<pk>\d+)/update/$', views.BookUpdate.as_view(), name='book_update'),
    url(r'^book/(?P<pk>\d+)/delete/$', views.BookDelete.as_view(), name='book_delete'),
]

# Optional parameters:
# Passed to the view as named arguments.
'''
urlpatterns = [
    url(r'^/url/$', views.my_reused_view, {'my_template_name': 'some_path'}, name='aurl'),
    url(r'^/anotherurl/$', views.my_reused_view, {'my_template_name': 'another_path'}, name='anotherurl'),
]
'''
# NOTE: 
# In case the captured argument and a key in the options have the same name, 
# the arguments in the dictionary will be used instead of the arguments captured in the URL.
# https://docs.djangoproject.com/en/1.10/topics/http/urls/#views-extra-options
# NOTE: This behaviour is opposite to what was explained in the tutorial.