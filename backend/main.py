from flask import Flask, request
import mysql.connector as sql

app = Flask(__name__)
db = sql.connect(host="localhost", user="root", password="subhradeep", database="project")
cursor = db.cursor()

@app.route('/movie', methods=['GET', 'POST'])
def getAllMovies():
    if request.method == 'GET':
        sqlQuery = "SELECT * from movie"
        cursor.execute(sqlQuery)
        movies = cursor.fetchall()
        movies = [
            {
                'movieId': movie[0],
                'name': movie[1],
                'duration': movie[2],
                'language': movie[3],
                'startTime': movie[4],
                'endTime': movie[5]
            }
            for movie in movies
        ]

        return {
            'Movies': movies
        }

    else:
        movie = request.json
        sqlQuery = "INSERT INTO movie VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sqlQuery, (
            movie['movieId'], movie['name'], movie['duration'], movie['language'], movie['startTime'], movie['endTime']
        ))
        db.commit()

        return {
            "Response": "Movie added successfully to database"
        }


@app.route('/movie/<movieId>', methods=['GET', 'DELETE', 'PUT'])
def getMovie(movieId):
    if request.method == 'GET':
        sqlQuery = "SELECT * FROM movie WHERE movieId=%s"
        cursor.execute(sqlQuery, (movieId,))

        try:
            movie = cursor.fetchall()[0]

            return {
                'Movie': {
                    'movieId': movie[0],
                    'name': movie[1],
                    'duration': movie[2],
                    'language': movie[3],
                    'startTime': movie[4],
                    'endTime': movie[5]
                }
            }
        except:
            return {
                'Response': "Movie with given movieId is not present"
            }
    
    elif request.method == 'DELETE':
        sqlQuery = "DELETE FROM movie WHERE movieId=%s"
        cursor.execute(sqlQuery, (movieId,))
        db.commit()

        return {
            'Response': "Movie deleted succesfully"
        }

    else:
        data = request.json

        if 'name' in data:
            sqlQuery = "UPDATE movie SET name=%s WHERE movieId=%s"
            cursor.execute(sqlQuery, (data['name'], movieId))

        if 'duration' in data:
            sqlQuery = "UPDATE movie SET duration=%s WHERE movieId=%s"
            cursor.execute(sqlQuery, (data['duration'], movieId))

        if 'language' in data:
            sqlQuery = "UPDATE movie SET language=%s WHERE movieId=%s"
            cursor.execute(sqlQuery, (data['language'], movieId))

        if 'startTime' in data:
            sqlQuery = "UPDATE movie SET startTime=%s WHERE movieId=%s"
            cursor.execute(sqlQuery, (data['startTime'], movieId))

        if 'endTime' in data:
            sqlQuery = "UPDATE movie SET endTime=%s WHERE movieId=%s"
            cursor.execute(sqlQuery, (data['endTime'], movieId))

        db.commit()

        return {
            'Response': "Movie updated succesfully"
        }


app.run(debug=True)