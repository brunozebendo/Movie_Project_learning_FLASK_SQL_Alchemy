"""O objetivo do código é criar um site com uma lista de filmes que podem ser classificados,excluídos
e incluídos, ele vai exibir um card com a imagem do filme e com a nota e ao se passar o mouse por cima
 ele vai virar e atrás terão dois botões, um para atualizar o review, outra para deletar. Ainda vai ser
 utilizada uma API que vai buscar as informações do título em outro site quando o usuário digitar o nome do filme
 vai aparecer uma lista de filmes, o usuário vai selecionar o correto e o id dessa seleção vai trazer as informações
 para preencher o card.
 O site vai usar todas as bibliotecas abaixo, Flask para criar sites com o Python,
render_template para lidar com o html, redirect e url_for para redirecionar a rota, request
para requisitar informações, bootstrap para já trabalhar com templates pré construidas, SQLAlchemy
para trabalhar com banco de dados, ou seja, para guardar as informações, wtf para trabalhar com formulários
e seus validadores
O site está abrindo, mas a parte do banco de dados dá erro na linha db.create_all() e não acho o motivo, alguns
 vídeos do youtube mostram o comando sendo dado em um terminal e não no próprio código"""

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
"""aqui, a inicialização dos Flask, da secret key para o wtform e do Bootstrap"""
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

"""criando a base de dados"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLACHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

"""criando a tabela, lembrando que para cada item da tabela é necessário estabelecer o tipo, a quantidade
de caracteres, se é o único item com aquele descrição e se o preenchimento pode ser nulo"""


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)


db.create_all()

## After adding the new_movie the code needs to be commented out/deleted.
## So you are not trying to add the same movie twice.
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"

db.session.add(new_movie)
db.session.commit()
"""aqui o código criando as variáveis para lidar com os campos na rota add, que serão somente o título
e o botão de submit"""
class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")
"""aqui a rota para adicionar um novo filme, o form recebe a classe e depois o render template lida com
a o html da rota, onde o form é o formulário criado pelo wtform. Depois, o if admite o formulário quando
validado, a variável recebe a informação do título que vem do add.html, então, a variável requer a informação
da API do site, transforma em um dicionário json e retorna as informações para o select.html. Portanto,
ele pega o título no /add, pede as informações do título na API e devolve a informação para o select.html"""

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()

    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY,"query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", options=data)

    return render_template("add.html", form=form)

@app.route("/")
def home():
    """a págima home vai ordernar os filmes de acordo com a nota de cada um, para isso o comando
    order_by do SQLAlchemy, depois o for loop vai posicionar o filme ao reverso, ou seja, do
    maior para o menor na listagem."""
    # This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)




"""aqui a rota para quando o botão de delete for pressionado, a função vai obter o id do filme, primeiro
o get 'pega' o id, passa para a variável movie_id, depois a variável movie recebe o movie_id já localizado
dentro do banco de dados Movie e a próxima linha o deleta, então o pedido é comitado e a rota é redirecionada
para a página inicial"""
@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    de.session.commit()
    return redirect(url_for("home"))
"""aqui a rota para econtrar o filme depois que ele é selecionado no href, usando o id do filme
é criado um 'dicionário' que irá usar as respostas obtidas da API, transformadas em um json, 
para preencher os campos do novo filme, depois a rota será desviada para a rota inicial, já com o filme adicionado"""
@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        #The language parameter is optional, if you were making the website for a different audience
        #e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            #The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
