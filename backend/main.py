from flask import Flask, request, render_template, url_for, redirect, session
import mysql.connector as sql
from credentials import CREDENTIALS

app = Flask(__name__)

app.secret_key = CREDENTIALS['secret_key']

db = sql.connect(
    host=CREDENTIALS['host'],
    user=CREDENTIALS['user'],
    password=CREDENTIALS['password'],
    database=CREDENTIALS['database']
)
cursor = db.cursor()


@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html', user=session['user'])


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
    user = cursor.fetchone()
    if user:
        session['user'] = username
        return redirect(url_for('home'))

    return render_template('login.html', loginFail="Invalid Credentials")


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


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
        cursor.execute('INSERT INTO users VALUES (%s,%s,%s,%s,%s)',
                       (username, password, name, email, contact))
        db.commit()
        session['user'] = username
        return redirect(url_for('home', user=username))

    except:
        return render_template('signup.html', signupFail="Please try with new username")


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = session['user']

    if request.method == 'GET':
        cursor.execute('SELECT name,email,contact FROM users WHERE username=%s', (user,))
        User = cursor.fetchone()
        return render_template('profile.html', user=user, name=User[0], email=User[1], contact=User[2])

    password = request.form['password']
    name = request.form['name']
    email = request.form['email']
    contact = request.form['contact']

    cursor.execute(
        'UPDATE users SET password=%s,name=%s,email=%s,contact=%s WHERE username=%s',
        (password, name, email, contact, user,)
    )
    db.commit()

    return redirect(url_for('profile'))


@app.route('/movies', methods=['GET'])
def movies():
    user = session['user']

    sqlQuery = "SELECT * from movies"
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

    for movie in movies:
        cursor.execute(
            "SELECT AVG(rating) FROM ratings INNER JOIN relation ON relation.rating_id=ratings.rating_id WHERE movie_id=%s",
            (movie['movie_id'],)
        )
        movie['avg_rating'] = cursor.fetchone()[0]

    return render_template('movies.html', movies=movies, user=user)


@app.route('/addMovie', methods=['GET', 'POST'])
def addMovie():
    user = session['user']
    if user != 'admin':
        return redirect(url_for('home', user=user))

    if request.method == 'GET':
        return render_template('addmovie.html')

    movie_id = request.form['movie_id']
    name = request.form['name']
    duration = request.form['duration']
    language = request.form['language']
    release_date = request.form['release_date']

    sqlQuery = "INSERT INTO movies VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sqlQuery, (movie_id, name,
                              duration, language, release_date))
    db.commit()

    return render_template('addmovie.html', movieAdded="Added movie to database successfully")


@app.route('/movie/<movie_id>', methods=['GET', 'POST'])
def movie(movie_id):
    user = session['user']

    if request.method == 'GET':
        cursor.execute("SELECT * FROM movies WHERE movie_id=%s", (movie_id,))
        movie = cursor.fetchone()
        movie = {
            'movie_id': movie[0],
            'name': movie[1],
            'duration': movie[2],
            'language': movie[3],
            'release_date': movie[4]
        }

        cursor.execute(
            "SELECT AVG(rating) FROM ratings INNER JOIN relation ON relation.rating_id=ratings.rating_id WHERE movie_id=%s",
            (movie['movie_id'],)
        )
        movie['avg_rating'] = cursor.fetchone()[0]

        cursor.execute(
            'SELECT ratings.*,relation.username FROM ratings INNER JOIN relation ON ratings.rating_id=relation.rating_id WHERE relation.movie_id=%s AND relation.username=%s',
            (movie_id, user,)
        )
        # user_of_rating
        ratings = cursor.fetchall()
        ratings = [
            {
                'id': rating[0],
                'rating': rating[1],
                'review': rating[2],
                'user_of_rating':rating[3]
            }
            for rating in ratings
        ]
        cursor.execute(
            'SELECT ratings.*,relation.username FROM ratings INNER JOIN relation ON ratings.rating_id=relation.rating_id WHERE relation.movie_id=%s',
            (movie_id,)
        )
        all_ratings = cursor.fetchall()
        all_ratings = [
            {
                'id': rating[0],
                'rating': rating[1],
                'review': rating[2],
                'user_of_rating':rating[3]
            }
            for rating in all_ratings
        ]
        size = len(ratings)
        return render_template('movie.html', movie=movie, ratings=ratings, user=user, size=size, all_ratings=all_ratings)

    rating = request.form['rating']
    review = request.form['review']
    cursor.execute(
        "INSERT INTO ratings(rating,review) VALUES(%s,%s)", (rating, review,)
    )
    db.commit()
    cursor.execute("INSERT INTO relation VALUES(%s,%s,%s)",
                   (movie_id, cursor.lastrowid, user))
    db.commit()

    return redirect(url_for('movie', movie_id=movie_id))


@app.route('/ratings', methods=['GET'])
def ratings():
    user = session['user']

    cursor.execute(
        "SELECT ratings.rating,ratings.review,movies.name,ratings.rating_id,movies.movie_id FROM relation INNER JOIN ratings ON ratings.rating_id=relation.rating_id INNER JOIN movies ON movies.movie_id=relation.movie_id WHERE relation.username=%s",
        (user,)
    )
    res = cursor.fetchall()
    res = [
        {
            'rating': r[0],
            'review': r[1],
            'movie_name': r[2],
            'rating_id':r[3],
            'movie_id':r[4]
        }
        for r in res
    ]

    return render_template('ratings.html', ratings=res, user=user)


@app.route('/movie_edit/<movie_id>', methods=['GET', 'POST'])
def movie_edit(movie_id):
    user = session['user']

    if user != 'admin':
        return redirect(url_for('movie', user=user, movie_id=movie_id))
    if request.method == 'GET':
        sql_query = "SELECT * FROM movies WHERE movie_id = %s"
        cursor.execute(sql_query, (movie_id,))
        movie = cursor.fetchone()
        movie = {
            'movie_id': movie[0],
            'name': movie[1],
            'duration': movie[2],
            'language': movie[3],
            'release_date': movie[4]
        }
        return render_template('movie_edit.html', movie=movie, user=user)

    name = request.form['name']
    duration = request.form['duration']
    language = request.form['language']
    release_date = request.form['release_date']

    sql_query = " UPDATE movies SET name = %s , duration = %s,language = %s,release_date =%s WHERE movie_id = %s"
    cursor.execute(sql_query, (name, duration, language, release_date, movie_id,))
    db.commit()
    return redirect(url_for('movies'))


@app.route('/movie_delete/<movie_id>', methods=['GET'])
def movie_delete(movie_id):
    user = session['user']
    sql_query = "DELETE FROM movies WHERE movie_id = %s"
    cursor.execute(sql_query, (movie_id,))
    db.commit()
    return redirect(url_for('movies'))


@app.route('/rating_edit/<movie_id>/<rating_id>', methods=['GET', 'POST'])
def rating_edit(movie_id, rating_id):
    user = session['user']

    if request.method == 'GET':
        cursor.execute(
            'SELECT ratings.* FROM ratings INNER JOIN relation ON ratings.rating_id=relation.rating_id WHERE relation.movie_id=%s AND relation.username=%s',
            (movie_id, user,)
        )
        ratings = cursor.fetchone()
        ratings = {
            'rating': ratings[1],
            'review': ratings[2]
        }
        cursor.execute("SELECT * FROM movies WHERE movie_id=%s", (movie_id,))
        movie = cursor.fetchone()
        movie = {
            'movie_id': movie[0],
            'name': movie[1],
            'duration': movie[2],
            'language': movie[3],
            'release_date': movie[4]
        }
        return render_template('rating_edit.html', ratings=ratings, user=user, movie_id=movie_id, movie=movie)
    
    rating = request.form['rating']
    review = request.form['review']
    sql_query = "UPDATE ratings SET rating =%s ,review =%s WHERE rating_id=%s"
    cursor.execute(sql_query, (rating, review, rating_id,))
    db.commit()
    return redirect(url_for('movie', movie_id=movie_id))


@app.route('/rating_delete/<movie_id>/<rating_id>', methods=['GET'])
def rating_delete(movie_id, rating_id):
    user = session['user']
    sql_query = "DELETE FROM ratings WHERE rating_id = %s"
    cursor.execute(sql_query, (rating_id,))
    db.commit()
    return redirect(url_for('movie', movie_id=movie_id))


@app.route('/all_ratings/<movie_id>', methods=['GET'])
def all_ratings(movie_id):
    user = session['user']
    cursor.execute(
        'SELECT ratings.*,relation.username FROM ratings INNER JOIN relation ON ratings.rating_id=relation.rating_id WHERE relation.movie_id=%s',
        (movie_id,)
    )
    all_ratings = cursor.fetchall()
    all_ratings = [
        {
            'id': rating[0],
            'rating': rating[1],
            'review': rating[2],
            'user_of_rating':rating[3],
        }
        for rating in all_ratings
    ]
    cursor.execute(
        'SELECT name FROM movies WHERE movie_id=%s',
        (movie_id,)
    )
    temp = cursor.fetchall()
    name = "Temp"
    for i in temp:
        name = i[0]
    
    return render_template('all_ratings.html', ratings=all_ratings, user=user, movie_name=name, movie_id=movie_id)


@app.route('/rating_delete_in_view_your/<movie_id>/<rating_id>', methods=['GET'])
def rating_delete_in_view_your(movie_id, rating_id):
    user = session['user']
    sql_query = "DELETE FROM ratings WHERE rating_id = %s"
    cursor.execute(sql_query, (rating_id,))
    db.commit()
    return redirect(url_for('ratings'))


@app.route('/all_users', methods=['GET'])
def all_users():
    user = session['user']
    sql_query = "SELECT * FROM users WHERE username != %s"
    cursor.execute(sql_query, (user,))
    users = cursor.fetchall()
    users = [
        {
            'username': i[0],
            'name':i[2],
            'email':i[3],
            'contact':i[4]
        }
        for i in users
    ]
    return render_template('all_users.html', users=users, user=user)


@app.route('/delete_user/<user_name>', methods=['GET'])
def delete_user(user_name):
    user = session['user']

    if request.method == 'GET':
        sql_query = "DELETE FROM users WHERE username = %s"
        cursor.execute(sql_query, (user_name,))
        db.commit()
        return redirect(url_for('all_users'))


app.run(debug=True)
