from django.shortcuts import render

# Permissions
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

# Create your views here.
from .models import Book, Author, BookInstance, Genre 

def index(request):
    """
    View function for home page of site. 
    """
    # Generate counts of some of the main objects. 
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    # TODO: Test if we can use num_instances.filter(status__exact='a').count() below.
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count() # NOTE: The 'all()' is implied by default.
    
    # "Challenge yourself"
    num_genres = Genre.objects.all().count()
    # __icontains (contains, case insensitive)
    num_python_books = Book.objects.filter(title__icontains='Python').count()

    # Number of visits to this view, as counted in the session variable.
    # get(key, 'default value if key is not present')
    # NOTE: By default, Django only saves to the session database and sends the session cookie to the client
    #       when the session has been modified (assigned) or deleted.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    # Render the HTML template index.html with the data in the context variable. 
    return render(
        request,
        'index.html', # /locallibrary/catalog/templates/index.html
        context={'num_books': num_books,
                 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors,
                 'num_genres': num_genres,
                 'num_python_books': num_python_books,
                 'num_visits': num_visits,
        },
    ) 

from django.views import generic 

class BookListView(generic.ListView):
    model = Book # NOTE: Shorthand for queryset = Book.objects.all()

    # Variable accessible in template: model_name_list (here: book_list)
    # NOTE: According to the documentation at: https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-display/
    #  the default name 'object_list' is always available in a template.

    # Paginate
    # The different pages are accessed using GET parameters:
    # /catalog/books/?page=2.
    paginate_by = 20
    # Next: Add support for pagination to the base HTML template.

    # Looks for the template /locallibrary/catalog/templates/catalog/book_list.html
    # /project_name/application_name/templates/application_name/model_name_list.html   #  (but did not work anymore with a custom context_object_name.)

    # Extend/change default behavior:
    # New name for the list as a template variable (instead of default 'book_list').
    context_object_name = 'my_book_list' 
    # Get 5 books containing the title 'war'.
    # queryset = Book.objects.filter(title__icontains='war')[:5] 

    # Alternative to queryset = ...:
    # Overriding the get_queryset() method.
    '''
    def get_queryset(self):
        return Book.objects.filter(title__icontains='war')[:5]
    '''

    # Specify your own template name and location (relative to 'catalog/templates').
    # NOTE: As we defined a custom queryset, in practice we'd also use a custom template name.
    #       Otherwise the generic view would use the same template as the “vanilla” object list, 
    #       which might not be what we want.
    # NOTE: But here we still use the default name (book_list).
    # template_name = 'books/my_arbitrary_template_name_list.html'

    # Override get_context_data() in order to pass additional context variables to the template:
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context.
        context = super(BookListView, self).get_context_data(**kwargs)
        # Add new/altered context as a key/value pair:
        context['some_data'] = 'This is just some data.'

        # Return altered context.
        return context


class BookDetailView(generic.DetailView):
    model = Book

    # By default looks for the following template:
    # /locallibrary/catalog/templates/catalog/book_detail.html

    # Book object accessible in template as one of the following:
    # - object
    # - book (= Model name)



# NOTE: The DetailView class automatically raises an Http404 exception,
#       should the book with the pk not exist in the database.
# In a non-class view function, you have to implement this behaviour yourself.
'''
def book_detail_view(request, pk):
    try:
        book_id = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        raise Http404("Book does not exist")

    # Convenience function that does the same as the code above:
    # book_id = get_object_or_404(Book, pk=pk)

    return render(
        request,
        'catalog/book_detail.html',
        context={'book': book_id}
    )
'''

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author


# LoginRequiredMixin: Restrict access to logged-in users
from django.contrib.auth.mixins import LoginRequiredMixin

#NOTE: For function-based views use:
# from django.contrib.auth.decorators import login_required

# @login_required
# def my_view(request):
#     #[...]

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    # Optional: 
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to' # instead of 'next' parameter value.

    '''
    Generic class-based view listing books on loan to current user.
    '''

    model=BookInstance
    # We override the default template_name, because
    # we may end up having a few different lists of BookInstance records, 
    # with different views and templates.
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

# See top of page:
# from django.contrib.auth.mixins import PermissionRequiredMixin
# NOTE: Testing for a permission also tests for authentication.
# For more details on permissions, see comments with Meta class of Bookinstance model.
class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model         = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed.html'
    paginate      = 20

    permission_required = ('catalog.can_mark_returned')

    queryset = BookInstance.objects.filter(status__exact='o').order_by('due_back')


# from django.contrib.auth.decorators import permission_required # Moved to top of page.
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime

from .forms import RenewBookForm

@permission_required("catalog.can_renew")
def renew_book_librarian(request, pk):

    book_inst = get_object_or_404(BookInstance, pk = pk)

    # Is this is a POST request, then process the form data.
    if request.method == 'POST':

        # Create a form instance and populate it with the data from the request:
        form = RenewBookForm(request.POST)
        
        # NOTE: If the form data is not valid, render() will be called at the bottom
        #       with the form object in the context containing all the error messages. 
        if form.is_valid():
            # Process the data in form.cleaned_data as required 
            # (Here we just write it to the model due_back field).
            # NOTE: The data returned by form.cleaned_data is
            # sanitised, validated, and converted into Python-friendly types.
            # (The data in request.POST[...] is not.)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # Redirect to a new URL:
            # Creates a status code 302 redirect to a specified URL.
            # NOTE: 
            # reverse: Generates a URL from 
            # -- a URL configuration name and 
            # -- a set of arguments. 
            # It is the Python equivalent of the 'url' tag that we've been using in our templates.
            return HttpResponseRedirect(reverse('borrowed'))

    # If this is a GET (or any other method) request, create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(
        request,
        'catalog/book_renew_librarian.html',
        {'form': form, 'bookinst': book_inst}
    )


# Generic Editing Views
# ==================================
# Generic editing views avoid boilerplate by:
# -- Handling the "view" behaviour
# -- Automatically creating the form class (a ModelForm) for you from the model.
# (There is also the FormView class that handles most of the view behaviour, 
#  but you still need to add a Form yourself.)

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls               import reverse_lazy
from .models                   import Author

# NOTE: CreateView, UpdateView
# On success CreateView and Updateview by default redirect 
# to a page displaying the newly created/edited model item, 
# which in this case is the Author detail view.
# (Override success_url to redirect to a different page.)

# NOTE: CreateView, UpdateView
# CreateView and UpdateView use the same template, which is <model_name>_form.html, 
# (locallibrary/catalog/templates/author_form.html in this case.)
# Suffix 'form' can be overridden with:
# template_name_suffix = '_other_suffix'

# URL set in catalog/urls.py: author/create
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '12/10/2016',}

    permission_required = ('catalog.can_renew')

# URL set in catalog/urls.py: author/pk/update
class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = ('catalog.can_renew')

# NOTE: This view's template does not display any fields, so we don't provide any.
# NOTE: Default template name: <model_name>_confirm_delete.html
#       '_confirm_delete' suffix can be overriden by assigning a value to template_name_suffix.
# URL set in catalog/urls.py: author/pk/delete
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = ('catalog.can_renew')
    # NOTE: No obvious default redirect page in Django, so we need to provide on ourselves:
    success_url = reverse_lazy('authors')
    # reverse_lazy = Lazily executed version of reverse(), 
    # used here because we're providing an URL to a class-based view attribute.

# Challenge Youself:
# Create views, templates, and urls to update Book entry.

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = ('catalog.can_renew')
    # Default template: book_form.html

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = ('catalog.can_renew')
    # Default template: book_form.html

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = ('catalog.can_renew')
    success_url = reverse_lazy('books')
    # Default template: book_confirm_delete.html

# TODO: Create templates, urls patterns and 'edit' and 'delete' links
