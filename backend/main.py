from flask import Flask, request, render_template, url_for, redirect
import mysql.connector as sql
from credentials import CREDENTIALS

app = Flask(__name__)
db = sql.connect(
        host=CREDENTIALS['host'],
        user=CREDENTIALS['user'],
        password=CREDENTIALS['password'],
        database=CREDENTIALS['database']
    )
cursor = db.cursor()

@app.route('/<user>/home', methods=['GET'])
def home(user):
    return render_template('home.html', user=user)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    
    cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
    user = cursor.fetchone()
    if user:
        return redirect(url_for('home', user=username))

    return render_template('login.html', loginFail="Invalid Credentials")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    email = request.form['email']
    contact = request.form['contact']

    try:
        cursor.execute('INSERT INTO users VALUES (%s,%s,%s,%s,%s)', (username, password, name, email, contact))
        db.commit()
        return redirect(url_for('home', user=username))

    except:
        return render_template('signup.html', signupFail="Please try with new username")


@app.route('/movies', methods=['GET'])
def movies():
    sqlQuery = "SELECT * from movie"
    cursor.execute(sqlQuery)
    movies = cursor.fetchall()
    movies = [
        {
            'movie_id': movie[0],
            'name': movie[1],
            'duration': movie[2],
            'language': movie[3],
            'release_date': movie[4]
        }
        for movie in movies
    ]

    return render_template('movies.html', movies=movies)


@app.route('/<user>/addMovie', methods=['GET', 'POST'])
def addMovie(user):
    if user != 'admin':
        return redirect('home', user=user)

    if request.method == 'GET':
        return render_template('addmovie.html')

    movie_id = request.form['movie_id']
    name = request.form['name']
    duration = request.form['duration']
    language = request.form['language']
    release_date = request.form['release_date']

    sqlQuery = "INSERT INTO movie VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sqlQuery, (movie_id, name, duration, language, release_date))
    db.commit()

    return render_template('addmovie.html', movieAdded="Added movie to database successfully")


@app.route('/movie/<movie_id>', methods=['GET'])
def movie(movie_id):
    cursor.execute('SELECT * FROM movies WHERE movie_id=%s', (movie_id))
    movie = cursor.fetchone()
    movie = {
            'movie_id': movie[0],
            'name': movie[1],
            'duration': movie[2],
            'language': movie[3],
            'release_date': movie[4]
        }

    cursor.execute(
        'SELECT ratings.* FROM ratings INNER JOIN relation ON ratings.rating_id=relation.rating_id WHERE relation.movie_id=%s',
        (movie_id)
        )
    ratings = cursor.fetchall()
    ratings = [
        {
            'rating': rating[1],
            'review': rating[2]
        }
        for rating in ratings
    ]

    return render_template('movie.html', movie=movie, ratings=ratings)


@app.route('/<user>/ratings', methods=['GET'])
def ratings(user):
    pass


app.run(debug=True)