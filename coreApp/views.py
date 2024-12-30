from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Book, BookmarkedBook
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import ProfileForm
import requests
from django.shortcuts import render
from django.conf import settings
from .models import Book
import requests
from datetime import datetime
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views import View


@login_required
def bookmarked_books(request):
    # Fetch all bookmarked books for the user
    bookmarks = BookmarkedBook.objects.filter(user=request.user)
    # Pass only the books to the template for easier display
    books = [bookmark.book for bookmark in bookmarks]
    return render(request, 'bookmarked_books.html', {'books': books})


@login_required
def toggle_bookmark(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    bookmark, created = BookmarkedBook.objects.get_or_create(user=request.user, book=book)
    if not created:
        # If the bookmark already exists, delete it to "unbookmark"
        bookmark.delete()
    return redirect('catalog')  # Redirect back to catalog or wherever necessary

# Create your views here.
def index(request): 
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        username =request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/catalog')
        else:
            messages.info(request, 'Incorrect Username or Password')
            return redirect('login')

    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email Already Used')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username Already Used')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
                user.save()
                return redirect('login')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'register.html')



def catalog(request):
    API_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    try:
        # Search for Python and Django books
        response = requests.get(
            API_BASE_URL,
            params={
                'q': 'subject:python+django programming',
                'maxResults': 20,
                'orderBy': 'relevance',
                'printType': 'books'

            }
        )
        response.raise_for_status()
        books_data = response.json()

        # Process each book from the API
        for item in books_data.get('items', []):
            try:
                volume_info = item.get('volumeInfo', {})
                
                # Extract ISBN
                isbn = None
                for identifier in volume_info.get('industryIdentifiers', []):
                    if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                        isbn = identifier.get('identifier')
                        break
                
                # Skip if book already exists
                if isbn and Book.objects.filter(isbn=isbn).exists():
                    continue

                # Process publish date
                publish_date_str = volume_info.get('publishedDate', '')
                try:
                    if len(publish_date_str) == 4:  # Year only
                        publish_date = f"{publish_date_str}-01-01"
                    elif len(publish_date_str) == 7:  # Year and month
                        publish_date = f"{publish_date_str}-01"
                    else:
                        publish_date = publish_date_str
                except ValueError:
                    publish_date = None

                # Create book instance
                book = Book(
                    title=volume_info.get('title', 'Untitled'),
                    authors=', '.join(volume_info.get('authors', ['Unknown'])),
                    description=volume_info.get('description', 'No description available')[:150],
                    publish_date=publish_date,
                    isbn=isbn or 0,
                    publishers=volume_info.get('publisher', 'Unknown'),
                    summary=volume_info.get('description', 'No description available')
                )

                # Handle cover image
                image_links = volume_info.get('imageLinks', {})
                if image_links and 'thumbnail' in image_links:
                    try:
                        image_url = image_links['thumbnail']
                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            image_name = f"cover_{isbn or 'unknown'}.jpg"
                            book.cover_image.save(
                                image_name,
                                ContentFile(image_response.content),
                                save=False
                            )
                    except requests.RequestException:
                        # Continue without image if download fails
                        pass

                # Handle PDF/EPUB file if available
                access_info = item.get('accessInfo', {})
                if access_info.get('pdf', {}).get('isAvailable'):
                    try:
                        pdf_link = access_info['pdf'].get('acsTokenLink')
                        if pdf_link:
                            pdf_response = requests.get(pdf_link)
                            if pdf_response.status_code == 200:
                                file_name = f"book_{isbn or 'unknown'}.pdf"
                                book.file.save(
                                    file_name,
                                    ContentFile(pdf_response.content),
                                    save=False
                                )
                    except requests.RequestException:
                        # Continue without PDF if download fails
                        pass

                book.save()

            except Exception as e:
                print(f"Error processing book {volume_info.get('title', 'Unknown')}: {str(e)}")
                continue

    except requests.RequestException as e:
        print(f"Error fetching data from Google Books API: {str(e)}")
    
    # Retrieve all books from the database
    books = Book.objects.all().order_by('-publish_date')
    return render(request, 'catalog.html', {'books': books})


def search(request):
    if request.method == "POST":
        searchbar = request.POST.get('searchbar', '') 
        books = Book.objects.filter(title__icontains=searchbar) 
        context = {
            'books': books,
            'searchbar': searchbar
        }
    else:
        books = Book.objects.all()  
        context = {
            'books': books
        }
    
    return render(request, 'search.html', context)

def dashboard (request):
    return render(request, 'dashboard.html')


def load_book(request, pk):
    book = Book.objects.get(id=pk)  
    context = {'book': book}  
    return render(request, 'book_detail.html', context)


def logout (request):
    auth.logout(request)
    return redirect('/')


@login_required
def settings(request):
    return render(request, 'settings.html')

@login_required
def password_change(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Prevent session invalidation
            messages.success(request, 'Password changed successfully.')
            return redirect('password_change')  # Redirect to the same page to avoid form resubmission
        else:
            messages.error(request, 'Please correct the errors above.')
    else:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'password_change.html', {
        'password_form': password_form,
    })

@login_required
def profile_update(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_update')  # Redirect to the same page to avoid form resubmission
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = ProfileForm(instance=request.user)

    return render(request, 'profile_update.html', {
        'profile_form': profile_form,
    })


class GoogleBooksAPIView(View):
    API_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def get(self, request):
        try:
            # Get search query from request parameters
            query = request.GET.get('q', '')
            if not query:
                return JsonResponse({'error': 'Search query is required'}, status=400)

            # Make request to Google Books API
            response = requests.get(
                self.API_BASE_URL,
                params={
                    'q': query,
                    'key': 'AIzaSyB0YlOmp3mXgl7kX9EACc7cgl14atmzDZw',
                    'maxResults': 40 # Maximum allowed by the API
                }
            )
            response.raise_for_status()
            books_data = response.json()

            saved_books = []
            errors = []

            for item in books_data.get('items', []):
                try:
                    volume_info = item.get('volumeInfo', {})
                    
                    # Extract ISBN
                    isbn = None
                    for identifier in volume_info.get('industryIdentifiers', []):
                        if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                            isbn = identifier.get('identifier')
                            break

                    # Skip if book already exists
                    if isbn and Book.objects.filter(isbn=isbn).exists():
                        continue

                    # Process publish date
                    publish_date_str = volume_info.get('publishedDate', '')
                    try:
                        # Handle different date formats
                        if len(publish_date_str) == 4:  # Year only
                            publish_date = datetime.strptime(publish_date_str, '%Y').date()
                        elif len(publish_date_str) == 7:  # Year and month
                            publish_date = datetime.strptime(publish_date_str, '%Y-%m').date()
                        else:
                            publish_date = datetime.strptime(publish_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        publish_date = None

                    # Create book instance
                    book = Book(
                        title=volume_info.get('title', 'Untitled'),
                        authors=', '.join(volume_info.get('authors', ['Unknown'])),
                        description=volume_info.get('description', '')[:150],  # Truncate to match model max_length
                        publish_date=publish_date,
                        isbn=isbn or 0,  # Default to 0 if no ISBN available
                        publishers=volume_info.get('publisher', 'Unknown'),
                        summary=volume_info.get('description')
                    )

                    # Handle cover image
                    image_links = volume_info.get('imageLinks', {})
                    if image_links and 'thumbnail' in image_links:
                        image_url = image_links['thumbnail']
                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            image_name = f"cover_{isbn or 'unknown'}.jpg"
                            book.cover_image.save(
                                image_name,
                                ContentFile(image_response.content),
                                save=False
                            )

                    # Handle PDF/EPUB file if available
                    access_info = item.get('accessInfo', {})
                    if access_info.get('pdf', {}).get('isAvailable'):
                        pdf_link = access_info['pdf'].get('acsTokenLink')
                        if pdf_link:
                            pdf_response = requests.get(pdf_link)
                            if pdf_response.status_code == 200:
                                file_name = f"book_{isbn or 'unknown'}.pdf"
                                book.file.save(
                                    file_name,
                                    ContentFile(pdf_response.content),
                                    save=False
                                )

                    book.save()
                    saved_books.append({
                        'title': book.title,
                        'authors': book.authors,
                        'isbn': book.isbn
                    })

                except Exception as e:
                    errors.append(f"Error processing book {volume_info.get('title', 'Unknown')}: {str(e)}")

            return JsonResponse({
                'message': f'Successfully processed {len(saved_books)} books',
                'saved_books': saved_books,
                'errors': errors
            })

        except requests.RequestException as e:
            return JsonResponse({
                'error': f'Error fetching data from Google Books API: {str(e)}'
            }, status=500)
        except Exception as e:
            return JsonResponse({
                'error': f'Unexpected error: {str(e)}'
            }, status=500)

    def post(self, request):
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    #http://127.0.0.1:8000/api/books/search/?q=python+programming