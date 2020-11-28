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


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('home.html', user=session['user'])

    username = request.form['username']
    cursor.execute('SELECT username FROM users WHERE username=%s', (username,))
    user = cursor.fetchone()
    if not user:
        return render_template('home.html', user=session['user'], errorMsg="No such user found")

    return redirect(url_for('profile', username=username))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    cursor.execute(
        'SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
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
        return redirect(url_for('home'))

    except:
        return render_template('signup.html', signupFail="Please try with new username")


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = session['user']

    if request.method == 'GET':
        cursor.execute(
            'SELECT name,email,contact FROM users WHERE username=%s', (username,))
        User = cursor.fetchone()
        if User == None:
            return redirect(url_for('login'))

        sql_query = "SELECT comments.*,blog_movie_user.blog_id,blog_movie_user.movie_id,heading,content FROM comments INNER JOIN comment_blog_user ON comments.comment_id=comment_blog_user.comment_id INNER JOIN blog_movie_user ON comment_blog_user.blog_id = blog_movie_user.blog_id INNER JOIN blogs ON blogs.blog_id = blog_movie_user.blog_id WHERE comment_blog_user.username = %s"
        cursor.execute(sql_query, (username,))
        comments = cursor.fetchall()
        comments = [
            {
                'comment_id': i[0],
                'comment':i[1],
                'published_on':i[2],
                'blog_id':i[3],
                'movie_id':i[4],
                'heading':i[5],
                'content':i[6]
            }
            for i in comments
        ]
        comment_size = len(comments)
        sql_query = "SELECT blogs.*,movies.movie_id,movies.name FROM blogs NATURAL JOIN blog_movie_user NATURAL JOIN movies WHERE username = %s"
        cursor.execute(sql_query, (username,))
        blogs = cursor.fetchall()
        blogs = [
            {
                'blog_id': i[0],
                'heading':i[1],
                'content':i[2],
                'published_on':i[3],
                'movie_id':i[4],
                'movie_name':i[5]

            }
            for i in blogs
        ]
        blog_size = len(blogs)
        return render_template('profile.html', user=username, session_user=user, name=User[0], email=User[1], contact=User[2], comments=comments, blogs=blogs, comment_size=comment_size, blog_size=blog_size)

    password = request.form['password']
    name = request.form['name']
    email = request.form['email']
    contact = request.form['contact']

    cursor.execute(
        'UPDATE users SET password=%s,name=%s,email=%s,contact=%s WHERE username=%s',
        (password, name, email, contact, user,)
    )
    db.commit()

    return redirect(url_for('profile', username=user))


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
        return redirect(url_for('home'))

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
        return redirect(url_for('movie', movie_id=movie_id))
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
    cursor.execute(sql_query, (name, duration,
                               language, release_date, movie_id,))
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


@app.route('/<movie_id>/blogs', methods=['GET', 'POST'])
def blogs(movie_id):
    user = session['user']

    if request.method == 'GET':
        cursor.execute(
            'SELECT blogs.* FROM blogs INNER JOIN blog_movie_user ON blogs.blog_id=blog_movie_user.blog_id WHERE blog_movie_user.movie_id=%s',
            (movie_id,)
        )
        blogs = cursor.fetchall()

        blogs = [
            {
                'blog_id': blog[0],
                'heading': blog[1],
                'content': blog[2],
                'published_on': blog[3]
            }
            for blog in blogs
        ]

        cursor.execute(
            'SELECT name FROM movies WHERE movie_id=%s', (movie_id,))
        movie = cursor.fetchone()[0]

        return render_template('blogs.html', user=user, blogs=blogs, movie=movie, movie_id=movie_id)

    heading = request.form['heading']
    content = request.form['content']

    cursor.execute(
        'INSERT INTO blogs(heading,content) VALUES(%s,%s)', (heading, content)
    )
    db.commit()

    cursor.execute(
        'INSERT INTO blog_movie_user VALUES(%s,%s,%s)', (
            cursor.lastrowid, movie_id, user)
    )
    db.commit()

    return redirect(url_for('blogs', movie_id=movie_id))


@app.route('/<movie_id>/blogs/<blog_id>', methods=['GET', 'POST'])
def blog(movie_id, blog_id):
    user = session['user']

    if request.method == 'GET':
        cursor.execute('SELECT blogs.*,username FROM blogs INNER JOIN blog_movie_user ON blogs.blog_id=blog_movie_user.blog_id WHERE blogs.blog_id=%s',
                       (blog_id,))
        blog = cursor.fetchone()

        blog = {
            'blog_id': blog[0],
            'heading': blog[1],
            'content': blog[2],
            'published_on': blog[3],
            'published_by': blog[4]
        }

        cursor.execute(
            'SELECT comments.*,username FROM comments INNER JOIN comment_blog_user ON comments.comment_id=comment_blog_user.comment_id WHERE blog_id=%s',
            (blog_id,)
        )
        comments = cursor.fetchall()

        comments = [
            {
                'comment_id': comment[0],
                'comment': comment[1],
                'published_on': comment[2],
                'published_by': comment[3]
            }
            for comment in comments
        ]

        return render_template('blog.html', blog=blog, comments=comments, user=user, movie_id=movie_id)

    comment = request.form['comment']

    cursor.execute(
        'INSERT INTO comments(comment) VALUES(%s)', (comment,)
    )
    db.commit()

    cursor.execute(
        'INSERT INTO comment_blog_user VALUES(%s,%s,%s)', (
            cursor.lastrowid, blog_id, user)
    )
    db.commit()

    return redirect(url_for('blog', movie_id=movie_id, blog_id=blog_id))


@app.route('/blogs', methods=['GET'])
def own_blogs():
    user = session['user']
    cursor.execute(
        'SELECT blogs.blog_id,blogs.heading,blog_movie_user.movie_id FROM blogs INNER JOIN blog_movie_user on blogs.blog_id=blog_movie_user.blog_id WHERE blog_movie_user.username=%s',
        (user,)
    )
    blogs = cursor.fetchall()
    blogs = [
        {
            'blog_id': blog[0],
            'heading': blog[1],
            'movie_id': blog[2]
        }
        for blog in blogs
    ]

    return render_template('own_blogs.html', blogs=blogs, user=user)


@app.route('/<movie_id>/edit_blog/<blog_id>', methods=['GET', 'POST'])
def edit_blog(movie_id, blog_id):
    user = session['user']
    cursor.execute('SELECT blogs.*,username FROM blogs INNER JOIN blog_movie_user ON blogs.blog_id=blog_movie_user.blog_id WHERE blogs.blog_id=%s',
                   (blog_id,))
    blog = cursor.fetchone()

    blog = {
        'blog_id': blog[0],
        'heading': blog[1],
        'content': blog[2],
        'published_on': blog[3],
        'published_by': blog[4]
    }
    if request.method == 'GET':

        return render_template('blog_edit.html', blog=blog, user=user, movie_id=movie_id)

    heading = request.form['heading']
    content = request.form['content']

    sql_query = "UPDATE blogs SET content=%s , heading=%s WHERE blog_id = %s"
    cursor.execute(sql_query, (content, heading, blog['blog_id'],))
    db.commit()

    return redirect(url_for('blog', movie_id=movie_id, blog_id=blog_id))


@app.route('/<movie_id>/edit_comment/<blog_id>/<comment_id>', methods=['GET', 'POST'])
def edit_comment(movie_id, blog_id, comment_id):
    user = session['user']
    cursor.execute(
        'SELECT comments.*,username FROM comments INNER JOIN comment_blog_user ON comments.comment_id=comment_blog_user.comment_id WHERE blog_id=%s AND comments.comment_id=%s',
        (blog_id, comment_id,)
    )
    comment = cursor.fetchone()
    comments = {
        'comment_id': comment[0],
        'comment': comment[1],
        'published_on': comment[2],
        'published_by': comment[3]
    }
    if request.method == 'GET':
        return render_template('comment_edit.html', comment=comments, movie_id=movie_id, blog_id=blog_id)
    comment = request.form['comment']
    sql_query = "UPDATE comments SET comment = %s WHERE comment_id=%s"
    cursor.execute(sql_query, (comment, comment_id,))
    db.commit()
    return redirect(url_for('blog', movie_id=movie_id, blog_id=blog_id))


@app.route('/<movie_id>/delete_blog/<blog_id>', methods=['GET'])
def delete_blog(movie_id, blog_id):
    if request.method == 'GET':
        sql_query = "DELETE FROM comments WHERE comment_id IN (SELECT comment_blog_user.comment_id FROM comment_blog_user WHERE comment_blog_user.blog_id = %s)"
        cursor.execute(sql_query, (blog_id,))
        db.commit()
        sql_query = "DELETE FROM blogs WHERE blog_id = %s"
        cursor.execute(sql_query, (blog_id,))
        db.commit()
        return redirect(url_for('blogs', movie_id=movie_id))


@app.route('/<movie_id>/delete_comment/<blog_id>/<comment_id>', methods=['GET'])
def delete_comment(movie_id, blog_id, comment_id):
    if request.method == 'GET':
        sql_query = "DELETE FROM comments WHERE comment_id=%s"
        cursor.execute(sql_query, (comment_id,))
        db.commit()
        return redirect(url_for('blog', movie_id=movie_id, blog_id=blog_id))


@app.route('/comments', methods=['GET', 'POST'])
def own_comments():
    if request.method == 'GET':
        user = session['user']
        sql_query = "SELECT comments.*,blog_movie_user.blog_id,blog_movie_user.movie_id,heading,content FROM comments INNER JOIN comment_blog_user ON comments.comment_id=comment_blog_user.comment_id INNER JOIN blog_movie_user ON comment_blog_user.blog_id = blog_movie_user.blog_id INNER JOIN blogs ON blogs.blog_id = blog_movie_user.blog_id WHERE comment_blog_user.username = %s"
        cursor.execute(sql_query, (user,))
        comment = cursor.fetchall()
        comment = [
            {
                'comment_id': i[0],
                'comment':i[1],
                'published_on':i[2],
                'blog_id':i[3],
                'movie_id':i[4],
                'heading':i[5],
                'content':i[6]
            }
            for i in comment
        ]
        return render_template('own_comments.html', comment=comment, user=user)


app.run(debug=True)
