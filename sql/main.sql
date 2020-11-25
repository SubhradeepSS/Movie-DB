DROP TABLE movie;

CREATE TABLE movie (
    movieId INT PRIMARY KEY,
    name VARCHAR(255),
    duration INT,
    language VARCHAR(255),
    startTime INT,
    endTime INT
);


INSERT INTO movie VALUES
(1, "Endgame", 180, "English", 1800, 1980),
(2, "3 idiots", 150, "Hindi", 2000, 2150),
(3, "Joker", 100, "English", 1600, 1700);