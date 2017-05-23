from django.contrib import admin

# Register your models here.
from .models import Book, BookInstance, Author, Language, Genre

# Call admin.site.register to register each model.

# admin.site.register(Book)
# admin.site.register(BookInstance)
# admin.site.register(Author)
admin.site.register(Language)
admin.site.register(Genre)

# Change how a model is displayed in the admin interface.
# The ModelAdmin class is the representation of a model in the admin interface.
# => Define a ModelAdmin class and register it with the model.
# ========================================================

class BookInline(admin.TabularInline):
    model = Book

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    
    # List what fields to be displayed.
    # Fields inside a tuple will be displayed horizontally (next to each other).
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

    inlines = [BookInline]

# Register the admin class with the associated model.
admin.site.register(Author, AuthorAdmin)



# Declare inlines of type 
# -- TabularInline (horizonal layout) or 
# -- StackedInline (vertical layout, just like the default model layout)
# and include with 'inlines = [InlineClass] in another model.
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

@admin.register(Book) # => Decorator. Does the same as admin.site.register()
class BookAdmin(admin.ModelAdmin):

    # 'author' is a ForeignKey Field => __str__ of 'Author' model will be displayed
    # 'genre' is a ManyToMany Field, Django does not display these automatically, so 
    #  we add a function 'display_genre' to the 'Book' model to retrieve thoses values.
    list_display = ('title', 'author', 'display_genre')

    # Book Instances will be displayed inline at the bottom of each book's detail view. 
    # NOTE: 3 placeholder (non-exiting) entries are automatically added to the list that cannot be removed,
    #       limiting the value of the inline display.
    # 
    inlines      = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):

    list_display = ('id', 'book', 'status', 'borrower', 'due_back')

    list_filter = ('status', 'due_back')

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    # to be displayed on the details view page.
    fieldsets = (
        (
            None, # Header
            {'fields': ('book', 'imprint', 'id')}
        ),
        (
            'Availablility', 
            {'fields': (
                # Fields to displayed horizontally are put in and EXTRA tuple. 
                # (Don't forget to add the comma at the end.)
                ('status', 'due_back', 'borrower'),
            )}
        ),
    )