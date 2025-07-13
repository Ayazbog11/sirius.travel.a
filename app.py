from flask import Flask, render_template, request, redirect, url_for
from models import db, Place, Review
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

# Создание базы данных при первом запуске
with app.app_context():
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    db.create_all()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница для ручного добавления нового места (форма)
@app.route('/add')
def add_place_page():
    return render_template('add_place.html')


# Страница со списком всех мест     с фильтрацией по категориям
@app.route('/places')
def places_list():
    selected_categories = request.args.getlist('category')  # список из GET-параметров

    # Список всех доступных категорий
    all_categories = ['Музей', 'Парк', 'Кафе', 'Развлечение']

    # Фильтрация по выбранным категориям
    if selected_categories:
        places = Place.query.filter(Place.category.in_(selected_categories)).all()
    else:
        places = Place.query.all()

    # Преобразуем объекты Place в словари для передачи
    place_dicts = []
    for place in places:
        place_dicts.append({
            'id': place.id,
            'name': place.name,
            'address': place.address,
            'category': place.category,
            'image': place.image,
            'latitude': getattr(place, 'latitude', None),
            'longitude': getattr(place, 'longitude', None)
        })

    # Рендерим HTML-шаблон с передачей всех нужных переменн
    return render_template(
        'places_list.html',
        places=place_dicts,
        all_categories=all_categories,
        selected_categories=selected_categories
    )



# Страница конкретного места: просмотр информации, форма для отзывов

@app.route('/place/<int:place_id>', methods=['GET', 'POST'])
def place_detail(place_id):
    place = Place.query.get_or_404(place_id)  # получаем объект Place или 404, если не найден
    if request.method == 'POST':

        # Обработка формы отзыва
        rating = int(request.form['rating'])
        comment = request.form['comment']

        # Создаём и сохраняем отзыв
        review = Review(place_id=place.id, rating=rating, comment=comment)
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('place_detail', place_id=place.id))
    return render_template('place_detail.html', place=place)

# Обработка POST-запроса добавления нового места (с координатами и изображением)

@app.route('/add_place', methods=['POST'])
def add_place():
    name = request.form['name']
    address = request.form['address']
    category = request.form['category']
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    image = request.files.get('image')

    # Сохраняем фото в отдельную папку
    filename = None
    if image:
        filename = image.filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_place = Place(
        name=name,
        address=address,
        category=category,
        image=filename,
        latitude=float(latitude) if latitude else None,
        longitude=float(longitude) if longitude else None
    )
    db.session.add(new_place)
    db.session.commit()

    return redirect(url_for('places_list'))


if __name__ == '__main__':
    app.run(debug=True)
