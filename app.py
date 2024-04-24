import os
from os.path import join, dirname
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from pymongo import MongoClient, DESCENDING

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

connect_string = 'mongodb://anisah:user@ac-ehbabt3-shard-00-00.ikc58s9.mongodb.net:27017,ac-ehbabt3-shard-00-01.ikc58s9.mongodb.net:27017,ac-ehbabt3-shard-00-02.ikc58s9.mongodb.net:27017/?ssl=true&replicaSet=atlas-dpl8po-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(connect_string)
db = client.db_fg2

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def save_image(image):
    if image:
        save_to = 'static/uploads'
        if not os.path.exists(save_to):
            os.makedirs(save_to)
        
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        
        ext = image.filename.split('.')[-1]
        filename = f'fruit-{mytime}-{ext}'
        image.save(f"{save_to}/{filename}")
        return filename
    return None

def delete_image(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)

@app.route('/')
def home():
    fruit_collection = list(db.fruits.find().sort('_id', DESCENDING))
    return render_template('dashboard.html', fruit_collection=fruit_collection)

@app.route('/fruits')
def fruits():
    fruit_collection = list(db.fruits.find().sort('_id', DESCENDING))
    return render_template('fruits.html', fruit_collection=fruit_collection)

@app.route('/fruit/add', methods=['GET', 'POST'])
def add_fruit():
    if request.method == 'GET':
        return render_template('add-fruit.html')
    else:
        name = request.form.get('name')
        price = int(request.form.get('price'))
        description = request.form.get('description')
        image = request.files['image']
        filename = save_image(image)
        
        db.fruits.insert_one({
            'name': name, 'price': price, 'description': description, 'image': filename
        })
        
        flash('Berhasil menambah data buah')
        return redirect(url_for('fruits'))

@app.route('/fruit/edit/<id>', methods=['GET', 'POST'])
def edit_fruit(id):
    if request.method == 'GET':
        fruit = db.fruits.find_one({'_id': ObjectId(id)})
        return render_template('edit-fruit.html', fruit=fruit)
    else:
        name = request.form.get('name')
        price = int(request.form.get('price'))
        description = request.form.get('description')
        image = request.files['image']
        
        fruit = db.fruits.find_one({'_id': ObjectId(id)})
        target = f"static/uploads/{fruit['image']}" 
        
        if image:
            filename = save_image(image)
            delete_image(target)
            db.fruits.update_one({'_id': ObjectId(id)}, {'$set': {'image': filename}})
        
        db.fruits.update_one({'_id': ObjectId(id)}, {'$set': {'name': name, 'price': price, 'description': description}})
        
        flash('Berhasil mengubah data buah')
        return redirect(url_for('fruits'))

@app.route('/fruit/delete/<id>', methods=['POST'])
def delete_fruit(id):
    fruit = db.fruits.find_one({'_id': ObjectId(id)})
    target = f"static/uploads/{fruit['image']}" 
    delete_image(target)
    
    db.fruits.delete_one({'_id': ObjectId(id)})
    
    flash('Berhasil menghapus data buah!')
    return redirect(url_for('fruits'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)