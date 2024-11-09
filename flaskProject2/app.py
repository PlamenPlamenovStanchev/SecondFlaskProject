from flask import Flask, request
from flask_restful import Resource,Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from flask_migrate import Migrate
from decouple import config

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://"
                                         f"{config('DB_USER')}:"
                                         f"{config('DB_PASS')}@"
                                         f"{config('DB_HOST')}:"
                                         f"{config('DB_PORT')}/"
                                         f"{config('DB_NAME')}")

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)
api = Api(app)
migrate = Migrate(app, db)


class BookModel(db.Model):
    __tablename__ = 'books'

    # pk = db.Column(db.Integer, primary_key = True)
    # title = db.Column(db.String, nullable = False)
    # author = db.Column(db.String, nullable = False)
    # sqlalchemy version 2

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(50), nullable=False)
    # genre: Mapped[str] = mapped_column(String(30), nullable=False)
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=True)
    reader: Mapped['ReaderModel'] = relationship(back_populates='books')
    # sqlalchemy version 3

    def __repr__(self):
        return f"<{self.id}> {self.title} from {self.author}"

    def to_dict(self):
        return {'id': self.id,
                'title': self.title,
                'author': self.author}

class ReaderModel(db.Model):
    __tablename__ = 'readers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    books: Mapped[list['BookModel']] = relationship(back_populates='reader')

class BooksResource(Resource):
    def get(self):
        # books = BookModel.query.all() sqlalchemy version 2
        books = db.session.execute(db.select(BookModel)).scalars()
        return [b.to_dict() for b in books]


    def post(self):
        data = request.get_json()
        book = BookModel(**data)
        db.session.add(book)
        db.session.commit()
        return book.to_dict(), 201

class BookResource(Resource):
    def get(self, id):
        book = BookModel.query.get(id)
        return book.to_dict()

    def put(self, id):
        data = request.get_json()
        book = BookModel.query.get(id)
        if book:
            if 'title' in data:
                book.title = data['title']
            db.session.commit()
            return book.to_dict()
        else:
            return {"message": "Book not found"}, 404


    def delete(self, id):
        book = BookModel.query.get(id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return book.to_dict()
        else:
            return {"message": "Book not found"}, 404



api.add_resource(BooksResource, '/books')
api.add_resource(BookResource, "/books/<int:id>")



# with app.app_context():
#     db.create_all()
# with migration there is no need for last two lines