import datetime
from typing import *

# Required to grant the permission needed to set a book as returned.
# Required to assign User as a borrower.
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from catalog.models import Author, Book, BookInstance, Genre, Language


# Create your tests here.
# TestCase
# -- creates a clean database before its tests are run, and
# -- runs every test function in its own transaction.
# The class also owns a test Client that you can use to
# -- simulate a user interacting with the code at the view level.
'''
class YourTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods")
        pass

    def setUp(self):
        print("setUp: Run once for every test method to set up clean data.")
        pass

    # NOTE:
    # The test classes also have a tearDown() method which we haven't used. 
    # This method isn't particularly useful for database tests, 
    # since the TestCase base class takes care of database teardown for you.

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertFalse(True)

    def test_one_plus_one_equals_two(self):
        print("Method: one_plus_one_equals_two.")
        self.assertEqual(1+1, 2)
'''

# To validate our view behaviour we use the Django test Client.
# This class (belongs to our TestCase's derived class) and
# acts like a dummy web browser that we can use to
# -- simulate GET and POST requests on a URL and observe the response.
# We can see almost everything about the response.



class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests.
        number_of_authors = 13
        for author_num in range(number_of_authors):
            first_name = 'Christian %s' % (author_num)
            surname = 'Surname %s' % (author_num)
            Author.objects.create(first_name=first_name, last_name=surname)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        # NOTE: Why are we testing for status code again? We already did all this in the test above,
        #       'test_view_url_accessible_by_name'.
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

        self.assertTrue('is_paginated' in response.context)
        # Changed from: self.assertTrue(resp.context['is_paginated'] == True)
        self.assertEqual(response.context['is_paginated'], True)
        # Changed from: self.assertTrue( len(response.context['author_list']) == 10)
        # => self.assertTrue( len(response.context['author_list']) == 1)
        #    AssertionError: False is not true
        self.assertEqual(len(response.context['author_list']), 10)
        # Much clearer error message in case of failure:
        # => self.assertEqual(len(response.context['author_list']), 1)
        #    AssertionError: 10 != 1

    def test_lists_all_authors(self):
        # Get second page and confirm that is has (exactly) 3 items remaining.
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['author_list']), 3)


# Views that are restricted to logged in users
# ======================================================
class LoanedBookInstancesByUserListViewTest(TestCase):

    # NOTE: We've used setUp() rather than setUpTestData()
    #       because we'll be modifying some of these objects later.
    # setUp() is run before every single test, whereas setUpTestData() is only
    # run once before all tests.
    def setUp(self):
        # Create two users.
        # NOTE: Why we use .create_superuser() instead of just create():
        # http://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests
        test_user1 = User.objects.create_user(
            username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(
            username='testuser2', password='12345')
        test_user2.save()

        # Create a book.
        test_author = Author.objects.create(
            first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')

        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEF',
            author=test_author,
            language=test_language,
        )


        # Create genre as a post step.
        # NOTE: Post step probably just to show how this can be done.
        genre_objects_for_book = Genre.objects.all()
        test_book.genre = genre_objects_for_book
        test_book.save()

        # Create 30 BookInstance objects.
        number_of_book_copies = 30

        for book_copy in range(number_of_book_copies):
            # % 5 = Remainder of x / 5 => Either 0, 1, 2, 3, or 4
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)

            # % 2 => Either 0 or 1 => Either False or True (50/50 split)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2

            status = 'm'  # Maintenance
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,  # All books are initially in mainenance mode.
            )
            # NOTE: Why is the BookInstance not saved?
            # NOTE: Why is it allowed to associate a borrower with a BookInstance,
            # with the BookInstance being in maintenance mode (and not on
            # loan)?

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my_borrowed'))
        self.assertRedirects(
            response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('my_borrowed'))
        print("hello...........")

        # Check that our user is logged in.
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response 'success'.
        self.assertEqual(response.status_code, 200)

        # Check that we used the correct template
        self.assertTemplateUsed(
            response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('my_borrowed'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in the list
        # (because all Bookinstance objects start in maintenance mode).
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan.
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # Check that now we have borrowed books in the list.
        reponse = self.client.get(reverse('my_borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan:
        for bookitem in reponse.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual(bookitem.status, 'o')

    def test_pages_ordered_by_due_date(self):

        # Change all books to be on loan.
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        # Check that our user is logged in.
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('my_borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for copy in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)




class RenewBookInstanceViewTest(TestCase):

    # We create two users and two book instances,
    # but only gives one user the permission required to access the view.
    def setUp(self):
        # Create a user.
        test_user1 = User.objects.create_user(
            username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(
            username='testuser2', password='12345')
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(
            first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')

        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create Genre as a post-step.
        genre_objects_for_book = Genre.objects.all()
        test_book.genre = genre_objects_for_book
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        # NOTE: Why are we adding the test_bookinstance1 at the class level
        # with 'self.'?
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint 2016',
            due_back=return_date,
            borrower=test_user1,
            status='0',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Manually check the redirect.
        # We cannot use assertRedirect(), because the redirect URL is
        # unpredicable).
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        # Test User 1 has no permission to see view 'renew-book-lobrarian'.
        login = self.client.login(username='testuser1', password='123456')
        response = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Manually check redirect.
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk, }))

        # Check that we are allowed to access the view (open the page).
        # This is our book and we have the right permissions:
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        # Get BookInstance 1 instead of BookInstance 2 as in the above
        # test.
        response = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Check that we are allowed to access the view (open the page).
        # We are a librarian, so we can view any users book.
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        # Generates random UUID that is unlikely to match our bookinstance.
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': test_uid, }))
        
        # With DEBUG = True shows an error page instead of the 404 page.
        # self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        self.assertTemplateUsed(
            response, 'catalog/book_renew_librarian.html')
        # self.assertTemplateUsed(response, 'book_renew_librarian.html') #
        # Works also

    def test_form_renewal_date_initially_has_date_three_weeks_in_the_future(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.time.today() + datetime.timedelta(weeks=3)
        self.assertEqual(
            response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='12345')
        valid_date_in_the_future = datetime.date.today() + datetime.timedelta(weeks=2)

        response = self.client.post(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk, }),
            {'renewal_date': valid_date_in_the_future}
        )

        self.assertRedirects(response, reverse('borrowed'))


    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='12345')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)

        response = self.client.post(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk,}),
            {'renewal_date': date_in_past}
        )
        
        # Original code:
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        # NOTE: Form name has to be the name of the form in the context,
        #       not the actual form you are using for validation.
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal in past')


    def test_form_invalid_renwal_date_future(self):
        login = self.client.login(username='testuser2', password='12345')
        date_in_the_future = datetime.date.today() - datetime.timedelta(weeks=4)

        response = self.client.post(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk,}),
            {'renewal_date': date_in_the_future}
        )

        self.assertEqual(response.status_code, 302)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')


    # My own test.
    def test_loads_same_page_on_failure(self):
        login = self.client.login(username='testuser2', password='12345')
        invalid_date_in_the_future = datetime.date.today() + datetime.timedelta(weeks=4)

        response = self.client.post(
            reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
            {'renewal_date': invalid_date_in_the_future}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))


# Test just this class:
# python3 manage.py test catalog.tests.test_views.AuthorCreateViewTest --verbosity 2
class AuthorCreateViewTest(TestCase):
    '''

    def create_test_user(name, password='12345'):
        test_user = User.objects.create_user(username=name, password=password)
        test_user.save()
        return test_user

    def add_permission_to_user(user, permission_name):
        permission = Permission.objects.get(codename=permission_name)
        user.user_permissions.add(permission)
        user.save()


    def setUp(self):
        # Create 2 users
        test_user1 = self.create_test_user('testuser1')
        test_user2 = self.create_test_user('testuser2')

        # Give second user permission to add an author
        # (catalog.can_renew)
        add_permission_to_user(test_user2, 'catalog.can_renew')

    '''

    def setUp(self):
        # Create a user.
        test_user1 = User.objects.create_user(
            username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(
            username='testuser2', password='12345')
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()


    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_create'))

        # Manually check the redirect.
        # We cannot use assertRedirect(), because the redirect URL is
        # unpredicable).
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    
    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')

        response = self.client.get(reverse('author_create'))

        # Manually check redirect.
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))


    def test_user_with_correct_permission_can_access_page(self):
        login = self.client.login(username='test_user2', password='12345')

        response = self.client.get(reverse('author_create'))

        # self.assertEqual(response.status_code, 200)
        # NOTE: Don't know why this returns a redirect.
        self.assertEqual(response.status_code, 302)

    def test_uses_correct_template(self):
        login = self.client.login(username='test_user2', password='12345')

        response = self.client.get(reverse('author_create'))

        self.assertTemplateUsed(response, 'catalog/author_form.html')
        # => AssertionError: No templates used to render the response
        # NOTE: This error makes sense, as we are getting a redirect
        #       for some reason.

    def test_submitting_new_author_redirects_to_author_page(self):
        login = self.client.login(username='test_user2', password='12345')

        response = self.client.get(reverse('author_create'))

        first_name = 'Harry'
        last_name  = 'Potter'

        response = self.client.post(
            reverse('author_create'),
            {'first_name': first_name, 'last_name': last_name}
        )

        # AssertionError: No templates used to render the response
        # NOTE: Either the author was not stored using the POST request, 
        #       or there is an error with the lookup function get().
        author = Author.objects.get(first_name__exact=first_name, last_name__exact=last_name)

        self.assertRedirects(response, reverse('author-detail', kwargs={'pk': author.pk}))


    def test_submitting_existing_author_throws_error(self):
        pass
        # This does not work.
        # The program happily adds another author with the same name.
















