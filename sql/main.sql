CREATE TABLE IF NOT EXISTS movies (
    movie_id INT PRIMARY KEY,
    name VARCHAR(255),
    duration INT,
    language VARCHAR(255),
    release_date DATE
);


CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255),
    name VARCHAR(255),
    email VARCHAR(255),
    contact VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS ratings (
    rating_id INT PRIMARY KEY AUTO_INCREMENT,
    rating INT,
    review VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS relation (
    movie_id INT,
    rating_id INT,
    username VARCHAR(255),
    FOREIGN KEY(movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY(rating_id) REFERENCES ratings(rating_id) ON DELETE CASCADE,
    FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS blogs (
    blog_id INT PRIMARY KEY AUTO_INCREMENT,
    heading VARCHAR(255),
    content TEXT
);


CREATE TABLE IF NOT EXISTS comments (
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    comment VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS blog_user (
    username VARCHAR(255),
    blog_id INT,
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (blog_id) REFERENCES blogs(blog_id)
);


CREATE TABLE IF NOT EXISTS comment_blog_user (
    comment_id INT,
    blog_id INT,
    username VARCHAR(255),
    FOREIGN KEY (comment_id) REFERENCES comments(comment_id),
    FOREIGN KEY (blog_id) REFERENCES blogs(blog_id),
    FOREIGN KEY (username) REFERENCES users(username)
);


CREATE TABLE IF NOT EXISTS blog_movie (
    blog_id INT,
    movie_id INT,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (blog_id) REFERENCES blogs(blog_id)
);