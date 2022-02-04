import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_question(request, question_selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1)*QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in question_selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add(
      'Access-Control-Allow-Headers', 'Content-Type, Authorization, true' 
    )
    response.headers.add(
      'Access-Control-Allow-Methods', 'GET, PUT, POST, PATCH, DELETE, OPTIONS'
    )
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_question_list():
    question_selection = Question.query.order_by(Question.id).all()
    list_of_questions = paginate_question(request, question_selection)
    categories = Category.query.order_by(Category.id).all()

    if len(list_of_questions) == 0:
      abort(404)
    else:
      return jsonify({
        'success' : True,
        'list_of_questions' : list_of_questions,
        'total_questions' : len(question_selection),
        'current_category' : None,
        'categories' : [category.format() for category in categories]
      })


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories', methods=['GET'])
  def get_category_list():
    categories = Category.query.order_by(Category.id).all()
    
    return jsonify({
      'success' : True,
      'categories' : [category.format() for category in categories]
    })
  
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id==question_id).one_or_none()
      if question is None:
        abort(404)
      
      question.delete()
      
      return jsonify({
        'success' : True,
        'deleted_question' : question_id
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_new_question():
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    try:
      if 'question' in body and 'answer' in body:
        question = Question(question=new_question, answer=new_answer,\
          category=new_category, difficulty=new_difficulty)
        question.insert()

        return jsonify({
          'success' : True,
          'question_id' : question.id,
          'question_category' : question.category,
              })
      else:
        abort(400)

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def get_questions_using_searchterm():
    body = request.get_json()
    search_term = body.get('search_term', None)
    questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()
    
    return jsonify({
      'success' : True,
      'search_questions' : [question.format() for question in questions]
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/questions/<int:category_id>')
  def get_question_based_on_category(category_id):
    try:
      questions = Question.query.filter(Question.category==category_id).all()

      return jsonify({
        'success' : True,
        'questions' : [question.format() for question in questions]
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/questions/play', methods=['POST'])
  def get_questions_randomly():
    body = request.get_json()
    current_category = body.get('current_category', None)
    previous_questions = body.get('previous_questions', None)
    questions = Question.query.filter(Question.category==current_category).order_by(func.random()).all()
    selected_questions =[]

    if len(questions)==0:
      abort(404)

    for question in questions:
      if question.id not in previous_questions:
        selected_questions.append(question.format())

    if len(selected_questions) != 0:
      return jsonify({
        'success' : True,
        'previous_questions' : previous_questions,
        'questions_for_quiz' : selected_questions
      })

    else:
      print('there is no question anymore!')
      abort(404)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success' : False,
      'error' : 404,
      'message' : 'Not Found'
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success' : True,
      'error' : 405,
      'message' : 'Method Not Allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessible(error):
    return jsonify({
      'success' : True,
      'error' : 422,
      'message' : 'Unprocessable'
    }), 422
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success' : False,
      'error' : 400,
      'message' : 'Bad Request'
    }), 400

  return app

    