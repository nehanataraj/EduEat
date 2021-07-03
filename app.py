import os

from flask import Flask, request, render_template, jsonify
from google.cloud import vision
from flask_cors import CORS
import redis
import json
r = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

app.config["IMAGE_UPLOADS"] = os.getcwd()


@app.route("/")
def home():
    return render_template("index.html")


# Route to upload image
@app.route('/upload-image', methods=['GET', 'POST'])
def upload_image():

    if request.method == "POST":
        if request.files:
            dairy = False
            grains = False
            protein = False
            veggies = False
            fruits = False
            junk = False
            stars = 2

            contained = []
            notcontained = []

            grainfoods = ['Noodle', 'Pasta', 'Al dente', 'Sliced bread', 'Whole wheat bread', 'White bread', 'Bread', 'Bun', 'Hamburger', 'Stringozzi']
            proteinfoods = ['Hamburger', 'Meat', 'Patty', 'Seed', 'Nut', 'Cashew family', 'Ventricina']
            veggiefoods = ['Produce', 'Leaf vegetable', 'Vegetable', 'Root vegetable', 'Artichoke', 'Broccoli', 'Carrot', 'Carrots', 'Bean', 'Beans', 'Salad']
            fruitfoods = ['Fruit', 'Fruits', 'Apple', 'Apples', 'Orange', 'Produce', 'Salad']
            dairyfoods = ['Milk', 'milk', 'Lowfat milk', 'Yogurt', 'Butter', 'Ice cream', 'Cheese']
            junkfoods = ['French fries', 'Junk food', 'Fried food']

            im = request.files["image"]
            # print(image + "Uploaded to Faces")
            # flash('Image successfully Uploaded to Faces.')
            im.save(os.path.join(app.config["IMAGE_UPLOADS"], im.filename))

            # Instantiates a client
            client = vision.ImageAnnotatorClient()

            # The name of the image file to annotate
            file_name = os.path.abspath(im.filename)
            # Loads the image into memory
            with open(file_name, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            # Performs label detection on the image file
            response = client.label_detection(image=image)
            labels = response.label_annotations

            # Performs object detection on the image file
            objects = client.object_localization(image=image).localized_object_annotations

            # Performs text detection on the image file
            response1 = client.text_detection(image=image)
            texts = response1.text_annotations

            for label in labels:
                if label.description in grainfoods:
                    grains = True
                elif label.description in proteinfoods:
                    protein = True
                elif label.description in veggiefoods:
                    veggies = True
                elif label.description in dairyfoods:
                    dairy = True
                elif label.description in fruitfoods:
                    fruits = True
                elif label.description in junkfoods:
                    junk = True
            for text in texts:
                if text.description in grainfoods:
                    grains = True
                elif text.description in proteinfoods:
                    protein = True
                elif text.description in veggiefoods:
                    veggies = True
                elif text.description in dairyfoods:
                    dairy = True
                elif text.description in fruitfoods:
                    fruits = True
                elif text.description in junkfoods:
                    junk = True
            for object in objects:
                if object.name in grainfoods:
                    grains = True
                elif object.name in proteinfoods:
                    protein = True
                elif object.name in veggiefoods:
                    veggies = True
                elif object.name in dairyfoods:
                    dairy = True
                elif object.name in fruitfoods:
                    fruits = True
                elif object.name in junkfoods:
                    junk = True

            if fruits is True:
                contained.append('Fruits')
                stars += 1
            else:
                notcontained.append('Fruits')
            if grains is True:
                contained.append('Grains')
                stars += 1.5
            else:
                notcontained.append('Grains')
            if protein is True:
                contained.append('Protein')
                stars += 1
            else:
                notcontained.append('Protein')
            if veggies is True:
                contained.append('Vegetables')
                stars += 1
            else:
                notcontained.append('Vegetables')
            if dairy is True:
                contained.append('Dairy')
                stars += .5
            else:
                notcontained.append('Dairy')
            if junk is True:
                stars -= 1.5
                contained.append('Junk Food')
            else:
                notcontained.append('Junk Food')
            if stars < 0:
                stars = 0
            return jsonify(contained, notcontained, stars)


@app.route('/uploads/<filename>')
def send_uploaded_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
