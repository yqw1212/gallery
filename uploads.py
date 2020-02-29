from flask import Flask, request, render_template, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, patch_request_class, IMAGES, AUDIO, DATA, DOCUMENTS, TEXT, secure_filename
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from pypinyin import lazy_pinyin
from PIL import Image
import os
import PIL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()+'/files/'
app.config['THUMBNAIL_FOLDER'] = os.getcwd()+'/thumbnail/'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'只能上传图片'), FileRequired(u'文件未选择')])
    submit = SubmitField(u'上传')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form1 = UploadForm()
    file_list = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
    pic_list = os.listdir(app.config['THUMBNAIL_FOLDER'])
    if form1.validate_on_submit():
        if chinese(form1.photo.data.filename):
            new = new_name(form1.photo.data.filename)
            photos.save(form1.photo.data, name=new)
        else:
            photos.save(form1.photo.data)
    return render_template("index.html", form1=form1, photos=photos, file_list=file_list, pic_list=pic_list)


@app.route('/delete/<file>')
def delete(file):
    file_path = photos.path(file)
    os.remove(file_path)
    return redirect(url_for('upload_file'))


def create_picture(image):
    base_width = 80
    img = Image.open(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], image))
    w_percent = (base_width/float(img.size[0]))
    h_size = int((float(img.size[1])*w_percent))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))


def chinese(filename):
    name = filename.split('.')[0]
    for ch in name:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def new_name(filename):
    name = filename.split('.')[0]
    ext = filename.split('.')[1]
    fname = '_'.join(lazy_pinyin(name))+'.'+ext
    return fname


if __name__ == '__main__':
    app.run()
