from ast import Or
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book, db

BOOKS_PER_SHELF = 8

def paginate_books(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1 )* BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

    @app.route('/books')
    def get_books():
        books = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request, books)

        body = request.get_json()
        print("Body is: ", body)
        
        if len(current_books) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'books': current_books,
            'total_books': len(books)
        })

    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    @app.route('/books/<int:book_id>', methods = ['PATCH'])
    def update_rating(book_id):
        
        book = Book.query.get(book_id)
        rating_object = request.json
        rating = rating_object["rating"]
        print(rating)
        
        if book is None:
            abort(404)
        else:    
            try:
                book.rating = rating
                db.session.commit()
                return jsonify({
                    'success': True
                })
            except:
                db.session.rollback()
                abort(400)
            finally:
                db.session.close
        
    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'
    @app.route('/books/<int:book_id>', methods = ['DELETE'])
    def delete_book(book_id):
        book = Book.query.get(book_id).one_or_none()
        
        if book is None:
            abort(404)

        try:
            db.session.delete(book)
            db.session.commit()

            books = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, books)

            return jsonify({
                'success':True,
                'deleted': book_id,
                'books': current_books,
                'total_books': len(books)
            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()  

    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.

    @app.route('/books/create', methods = ['POST'])
    def create_book():

        data = request.json


        try:
            book = Book(
                title = data['title'],
                author = data['author'], 
                rating = data['rating']
            )
            db.session.add(book)
            db.session.commit()

            books = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, books)
            book = current_books[-1]
            print(book)

            return jsonify({
                'success': True,
                'created': book.id,
                'books': current_books,
                'total_books': len(books)

            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "Bad Response"
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
            }), 404

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    return app
