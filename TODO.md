# Endpoints

## GET

    /search
        filter
            Book
            Author
            Genre
            Category
            Bookshelf
    /book/id
    /author/id
    /bookshelf/id
        
## POST

    /book
    /bookshelf
    /book/shelf

## PUT 

    /book
    /book/review
    /book/shelf
    /bookshelf

# Database

## Tables

### Users

id
name
email
display_name
profile_picture (add later)



```SQL
CREATE TABLE IF NOT EXISTS users
(
    id  smallint primary key,
    first_name varchar(25),
    last_name varchar(25),
    email varchar(100),
    display_name varchar(25)
)
```

### Books

id
name
isbn
author
publish_date
description

```SQL
CREATE TABLE IF NOT EXISTS books
(
    id varchar(36) primary key,
    name varchar(75),
    seies varchar(100),
    isbn varchar(13),
    author varchar (50),
    author_reverse varchar(50),
    publish_date date,
    publish_year smallint,
    description varchar(500),
    category varchar[],
    genre varchar[]
)

CREATE INDEX idx_books_name ON books(name)
CREATE INDEX idx_books_series ON books(series)
CREATE INDEX idx_books_author ON books(author)
CREATE INDEX idx_books_author_reverse ON books(author_reverse)
CREATE INDEX idx_books_date ON books(publish_date)
CREATE INDEX idx_books_date ON books(publish_year)
CREATE INDEX idx_books_genre ON books USING gin (genre)
CREATE INDEX idx_books_category ON books USING gin (category)
```

### Bookshelves

id
name
user
description
category
books

```SQL
CREATE TABLE IF NOT EXISTS bookshelves
(
    id varchar(36) primary key,
    name varchar(40),
    user smallint references users(id),
    category varcahr
    description varchar(100),
    books varchar(36)[] references books(id),
    category varchar[]
)

CREATE INDEX 
```

