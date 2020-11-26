DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS relation;


CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    name VARCHAR(255),
    duration INT,
    language VARCHAR(255),
    release_date DATE
);


CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255),
    name VARCHAR(255),
    email VARCHAR(255),
    contact VARCHAR(255)
);


CREATE TABLE ratings (
    rating_id INT PRIMARY KEY AUTO_INCREMENT,
    rating INT,
    review VARCHAR(255)
);


CREATE TABLE relation (
    movie_id INT,
    rating_id INT,
    username VARCHAR(255),
    FOREIGN KEY(movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY(rating_id) REFERENCES ratings(rating_id),
    FOREIGN KEY(username) REFERENCES users(username)
);