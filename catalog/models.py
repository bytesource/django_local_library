from django.db import models
# Import the User model, so User is available to subsequent code that makes use of it.
from django.contrib.auth.models import User

# http://stackoverflow.com/questions/30471812/global-name-reverse-is-not-defined
from django.core.urlresolvers import reverse
from datetime import date # Used in 'is_overdue' function

# Create your models here.
class Genre(models.Model):
    """
    Model representing a book genre (e.g. Science Fiction, Non Fiction). 
    """

    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """

        return self.name


# =============================================================================

class Language(models.Model):
    """
    Model representing the language a book is written in (e.g. English, German, Chinese). 
    """
    # NOTE: A language can be associated to MANY books.

    name = models.CharField(max_length=200, help_text="Enter the language the book is written in.")

    def __str__(self):
        """
        String for representing the model object (in Admin site etc.)
        """

        return self.name




# =============================================================================

class Book(models.Model):
    """
    Model representing a book (but not a specific copy of a book).
    """

    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because book can only have one author, but authors can have multiple books. 
    # NOTE: This is not true, somtimes a book is written by several authors. 
    #       => Should be ManyToManyField intead.
    # Author as a string (for now) rather than object because it hasn't been declared yet in the file.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn    = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre   = models.ManyToManyField(Genre, help_text="Select a genre for this book.")
    # ManyToManyField used because genre can contain many books. Books can cover many genres. 
    # Genre class has already been defined, so we can specify the object above. 

    # A book is associated with ONE and only ONE langage => ForeignKey
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """
        String for representing the Model object. 
        """
        
        return self.title

    # https://docs.djangoproject.com/en/1.8/ref/urlresolvers/#reverse
    def get_absolute_url(self):
        """
        Returns the url to access a particular book instance. 
        """
        return reverse('book-detail', args=[str(self.id)])  
        # Returns an URL that can be used to access a detail record for this model 
        # (for this to work we will have to 
        # -- Define a URL mapping that has the name 'book-detail' (name='book-detail')
        # -- Define an associated view.
        # -- Define an associated template.


    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre in Admin.
        """
         
        # Get first 3 genres and join to a string.
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])

    display_genre.short_description = 'Genre'



# =============================================================================

import uuid # Required for unique book instances.

class BookInstance(models.Model):
    """
    Model representing a specific copy of a book (i.e. that can be borrowed from the library). 
    """

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        help_text="Unique ID for this particular book accross whole library.",
    )

    # ForeignKey (one-to many) 
    book = models.ForeignKey(
        'Book',
        on_delete=models.SET_NULL,
        null=True,
    )

    imprint = models.CharField(max_length=200)

    due_back = models.DateField(null=True, blank=True)
    # Set to Null when the book is available, because then there is no due date.

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1, 
        choices=LOAN_STATUS, 
        blank=True,  # If no value given, the default value is used.
        default='d', # Because a book will initially be created unavailable before being stocked on the shelve.
        help_text="Book Availability",
    )

    borrower = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Add a property that we can call from our templates
    # from datetime import date # Called at the top of the file
    @property
    def is_overdue(self):
        if date.today() > self.due_back:
            return True
        return False


    class Meta:
        ordering = ["due_back"]

        # Assign permission to "Librarian" group in the Admin site.
        permissions = (
            ("can_mark_returned", "Set book as returned"),
            ("can_renew",         "Renew book on loan"),
        )
        # Next Permission Steps:
        # =========================
        # NOTE 1: After running the migrations, the new permissions will be selectable 
        #         in the Admin for each group: http://127.0.0.1:8000/admin/auth/group/
        # NOTE 2: Templates: Check for permission with {{ perms.catalog.can_mark_returned }}
        # NOTE 3: Views
        # - Class-based: 
        # --------------------------
        #   from django.contrib.auth.mixins import PermissionRequiredMixin
        #   class MyView(PermissionRequiredMixin, View):
        #       permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
        # - Function-based:
        # --------------------------
        #   from django.contrib.auth.decorators import permission_required
        #   @permission_required('catalog.can_mark_returned')
        #   @permission_required('catalog.can_edit')
        #   def my_view(request):
        # NOTE: Testing for  a permission also tests for authentication.

    
    def __str__(self):
        """
        String for representing the Model object. 
        """

        return '%s (%s)' % (self.id, self.book.title)


# =============================================================================

class Author(models.Model):
    """
    Model representing the author.
    """

    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True) # Date of birth might be unknown. 
    date_of_death = models.DateField('Died', null=True, blank=True)
    # NOTE: What does 'Died' mean? Does it specify the only choice?


    # https://docs.djangoproject.com/en/1.8/ref/urlresolvers/#reverse
    def get_absolute_url(self):
        """
        Returns the url to access a particular author instance. 
        """

        return reverse('author-detail', args=[str(self.id)])


    def __str__(self):
        """
        String for representing the Model object. 
        """

        return '%s, %s' % (self.last_name, self.first_name)