from django.shortcuts import render, redirect
from DojoReads_app.models import User, Book, Author, Review
from django.contrib import messages
import bcrypt

# Create your views here.
def index(request):
    context = {
        'all_users':User.objects.all()
    }
    return render(request, "register_login.html", context)

def register(request):
     # include some logic to validate user input before adding them to the database!
    if request.method == "POST":
        errors = User.objects.validate_registration(request.POST)
        if len(errors) > 0:
            for key, errormsg in errors.items():
                messages.error(request, errormsg)
            return redirect("/")
        else:
            password = request.POST['password_txt']
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()  # create the hash    
            print(pw_hash)      # prints something like b'$2b$12$sqjyok5RQccl9S6eFLhEPuaRaJCcH3Esl2RWLm/cimMIEnhnLb7iC'    
            # be sure you set up your database so it can store password hashes this long (60 characters)
            # make sure you put the hashed password in the database, not the one from the form!
            new_user=User.objects.create(
                first_name=request.POST['first_name_txt'],
                last_name=request.POST['last_name_txt'],
                email=request.POST['email_txt'],
                password=pw_hash
            )
            request.session['user_id'] = new_user.id
            request.session['user_name'] = f'{new_user.first_name} {new_user.last_name}'
            return redirect("/books") # never render on a post, always redirect!
    return redirect("/")

def login(request):
    if request.method =='POST':
        # see if the username provided exists in the database
        user = User.objects.filter(email=request.POST['email_txt']) # why are we using filter here instead of get?
        if user: # note that we take advantage of truthiness here: an empty list will return false
            logged_user = user[0]
            # assuming we only have one user with this username, the user would be first in the list we get back
            # of course, we should have some logic to prevent duplicates of usernames when we create users
            # use bcrypt's check_password_hash method, passing the hash from our database and the password from the form
            if bcrypt.checkpw(request.POST['password_txt'].encode(), logged_user.password.encode()):
                # if we get True after checking the password, we may put the user id in session
                request.session['user_id'] = logged_user.id
                request.session['user_name'] = f'{logged_user.first_name} {logged_user.last_name}'
                # never render on a post, always redirect!
                return redirect("/books")
            else:
                messages.error(request, "Incorrect password.")
        else:
            messages.error(request, "Incorrect username.")
            return redirect("/")
        # if we didn't find anything in the database by searching by username or if the passwords don't match, 
        # redirect back to a safe route
    return redirect("/")

def logout(request):
    request.session.flush()
    return redirect("/")

def displayBooks (request):
    context = {
        'first_three_reviews':Review.objects.all().order_by("-created_at")[:3],
        'remaining_reviews':Review.objects.all().order_by("-created_at") [3:],
        'all_books':Book.objects.all()
    }
    return render(request, "books_list.html", context)

def getAddBookPage(request):
    context = {
        'all_authors':Author.objects.all()
    }
    return render(request, "add_book.html", context)

def addBook(request):
    if request.method =='POST':
        errors = Book.objects.validate_data(request.POST)
        if len(errors) > 0:
            for key, errormsg in errors.items():
                messages.error(request, errormsg)
            return redirect("/add_book_page")
        else:
            if not len(request.POST['authors_sel']) == 0:
                exist_author = Author.objects.get(id=request.POST['authors_sel'])
                author_fn = exist_author.first_name
                author_ln = exist_author.last_name
            else:
                author_fn = ['author_fn_txt']
                author_ln = ['author_ln_txt']

            new_book = Book.objects.create(
                title=request.POST['title_txt'],
                author=Author.objects.create(
                    first_name=author_fn,
                    last_name=author_ln,
                )
            )
            Review.objects.create(
                user=User.objects.get(id=request.session['user_id']),
                book = new_book,
                content = request.POST['review_txt'],
                rating=request.POST['rating_sel']
            )
            return redirect ("/books/"+str(new_book.id))
    return redirect("/")

def displayBook(request, book_id):
    context = {
        'book':Book.objects.get(id=book_id),
    }
    return render(request, "book_detail.html", context)

def addReview(request, book_id):
    if request.method == "POST":
        errors = Review.objects.validate_data(request.POST)
        if len(errors) > 0:
            for key, errormsg in errors.items():
                messages.error(request, errormsg)
            return redirect("/books/"+str(book_id))
        else:
            Review.objects.create(
                user=User.objects.get(id=request.session['user_id']),
                book = Book.objects.get(id=book_id),
                content = request.POST['review_txt'],
                rating=request.POST['rating_sel']
            )
            return redirect("/books/"+str(book_id))
    return redirect("/")

def displayUser(request, user_id):
    context = {
        'user':User.objects.get(id=user_id),
    }
    return render(request, "user_detail.html", context)

def deleteReview(request, review_id):
    del_review = Review.objects.get(id=review_id)
    book_id = del_review.book.id
    del_review.delete()
    return redirect ("/books/"+str(book_id))

