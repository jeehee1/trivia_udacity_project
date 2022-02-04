import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.wrappers import response

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', '1231', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question' : 'What is it called the big clock building in london?',
            'answer' : 'BigBen',
            'category' : "4",
            'difficulty' : 1
        }

        self.previous_questions_info={
            'current_category' : "2",
            'previous_questions' : [11, 12, 13, 14, 15, 16, 17, 18]
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['list_of_questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['current_category'], None)

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    # def test_delete_a_question_by_question_id(self):
    #     res = self.client().delete('/questions/23')
    #     data = json.loads(res.data)
    #     question = Question.query.filter(Question.id==23).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['deleted_question'], 23)
    #     self.assertEqual(question, None)

    def test_create_a_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question_id'])
        self.assertTrue(data['question_category'])

    # def test_422_if_form_is_invalid(self):
    #     res = self.client().post('/questions', json)
    #     data = json.loads(res.data)

    def test_get_questions_by_search_term(self):
        res = self.client().post('/questions/search', json={'search_term':'first'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['search_questions']))

    def test_404_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_question_based_on_category(self):
        res = self.client().get('/questions/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_get_questions_randomly(self):
        res = self.client().post('/questions/play', \
            json=self.previous_questions_info)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['previous_questions']))
        self.assertTrue(len(data['questions_for_quiz']))




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()