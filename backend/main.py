from flask import Flask, request
import mysql.connector as sql

app = Flask(__name__)
db = sql.connect(host="localhost", user="root", password="subhradeep", database="project")
cursor = db.cursor()

@app.route('/movie', methods=['GET', 'POST'])
def Movies():
    if request.method == 'GET':
        sqlQuery = "SELECT * from movie"
        cursor.execute(sqlQuery)
        movies = cursor.fetchall()
        movies = [
            {
                'movie_id': movie[0],
                'name': movie[1],
                'duration': movie[2],
                'language': movie[3],
                'release': movie[4]
            }
            for movie in movies
        ]

        return {
            'Movies': movies
        }

    else:
        movie = request.json
        sqlQuery = "INSERT INTO movie VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sqlQuery, (
            movie['movie_id'], movie['name'], movie['duration'], movie['language'], movie['release_date']
        ))
        db.commit()

        return {
            "Response": "Movie added successfully to database"
        }


@app.route('/movie/<movie_id>', methods=['GET', 'DELETE', 'PUT'])
def Movie(movie_id):
    if request.method == 'GET':
        sqlQuery = "SELECT * FROM movie WHERE movie_id=%s"
        cursor.execute(sqlQuery, (movie_id,))

        try:
            movie = cursor.fetchall()[0]

            return {
                'Movie': {
                    'movie_id': movie[0],
                    'name': movie[1],
                    'duration': movie[2],
                    'language': movie[3],
                    'release_date': movie[4]
                }
            }
        except:
            return {
                'Response': "Movie with given movie_id is not present"
            }
    
    elif request.method == 'DELETE':
        sqlQuery = "DELETE FROM movie WHERE movie_id=%s"
        cursor.execute(sqlQuery, (movie_id,))
        db.commit()

        return {
            'Response': "Movie deleted succesfully"
        }

    else:
        data = request.json

        if 'name' in data:
            sqlQuery = "UPDATE movie SET name=%s WHERE movie_id=%s"
            cursor.execute(sqlQuery, (data['name'], movie_id))

        if 'duration' in data:
            sqlQuery = "UPDATE movie SET duration=%s WHERE movie_id=%s"
            cursor.execute(sqlQuery, (data['duration'], movie_id))

        if 'language' in data:
            sqlQuery = "UPDATE movie SET language=%s WHERE movie_id=%s"
            cursor.execute(sqlQuery, (data['language'], movie_id))

        if 'release_date' in data:
            sqlQuery = "UPDATE movie SET release_date=%s WHERE movie_id=%s"
            cursor.execute(sqlQuery, (data['release_date'], movie_id))


        db.commit()

        return {
            'Response': "Movie updated succesfully"
        }


app.run(debug=True)