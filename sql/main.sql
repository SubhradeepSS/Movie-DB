DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS characters;

CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    name VARCHAR(255),
    duration INT,
    language VARCHAR(255),
    release_date DATE
);


CREATE TABLE ratings (
    rating_id INT PRIMARY KEY,
    rating INT,
    review VARCHAR(255),
    movie_id INT,
    rater VARCHAR(255),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
);