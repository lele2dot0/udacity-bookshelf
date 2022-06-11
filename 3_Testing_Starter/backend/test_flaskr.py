import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book


class BookTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_book = {"title": "Anansi Boys", "author": "Neil Gaiman", "rating": 5}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass


# @TODO: Write at least two tests for each endpoint - one each for success and error behavior.
#        You can feel free to write additional tests for nuanced functionality,
#        Such as adding a book without a rating, etc.
#        Since there are four routes currently, you should have at least eight tests.
# Optional: Update the book information in setUp to make the test database your own!
    def test_retrieve_paginated_books_sucess(self):
        res=self.client().get("/books")
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]))

    def test_404_request_page_beyond_range(self):
        res=self.client().get("/books?page=1250")
        data=json.loads(res.data)
          
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_rating_update(self):
        res=self.client().patch("/books/8", json={"rating": 4})
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 8).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(book.format()["rating"], 4)

    def test_400_failed_update(self):
        res=self.client().patch('/books/8')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_create_book(self):
        res=self.client().post('/books', json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["books"])
        self.assertTrue(data["total_books"])

    # def test_405_create_not_allowed(self):
    #     res=self.client().post('/books/80', json=self.new_book)
    #     data = json.loads(res.data)
    #     book = Book.query.filter(Book.id == 17).one_or_none()

    #     self.assertEqual(res.status_code, 405)
    #     self.assertEqual(data["success", False])
    #     self.assertEqual(data["message"], "method not allowed")

    def test_delete_book(self):
        res=self.client().get('/books/17')
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 17).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 17)
        self.assertEqual(data['books'])
        self.assertEqual(data['total_books'])
        self.assertEqual(book, None)

    # def test_422_book_does_not_exist(self):
    #     res=self.client().delete('/books/1000')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data['success', False])
    #     self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
