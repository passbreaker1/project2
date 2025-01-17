from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import re

client = MongoClient('mongodb+srv://sparta:test@cluster0.a0mnxnt.mongodb.net/?retryWrites=true&w=majority')

db = client.dbsparta
application = app = Flask(__name__)
app.secret_key = 'any random string'

 

# 홈화면
@app.route('/')
def home():
    return render_template('index.html')


# 전체글 목록조회(list) 
@app.route("/bucket", methods=["GET"])
def bucket_get():
    all_buckets = list(db.bucket.find({}, {'_id': False}))
    return jsonify({'result': all_buckets})


# 좋아요, 싫어요 카운팅-미완성-index.html 함께 변경중
@app.route('/update', methods=['POST'])
def update_like_dislike():
    item_id = request.form['itemId']
    type = request.form['type']  # likeCount, dislikeCount로 전달됨
    new_count = int(request.form['count'])  # 변경된 카운트 값

    # MongoDB의 해당 아이템 업데이트
    # $inc 연산자를 사용하여 변경된 값을 기존 값에 더함
    db.bucket.update_one({'_id': ObjectId(item_id)}, {'$inc': {type: new_count}})

    return jsonify({'msg': '업데이트 완료!'})


# 내 방명록 쓰기 및 보기페이지
@app.route('/writeAndMyview')
def write():
    # return render_template('writeAndMyview.html')
    if 'email' in session:
        email = session['email']
        logged_in = True
        return render_template('writeAndMyview.html', email=email, logged_in=logged_in)
    else:
        return redirect(url_for('login'))

    # if 'id' in session:
    #     id= session.get('email',None)
    #     return render_template('writeAndMyview.html',email=email, logged_in=logged_in)
    # return render_template('login.html')


# 내 방명록 쓰기, 보기-id별 식별 필요함
@app.route("/bucket", methods=["POST"])
def bucket_post():
    bucket_receive = request.form['bucket_give']
    like_receive = int(request.form['likeCount'])
    dislike_receive = int(request.form['dislikeCount'])
    doc = {
        'bucket' : bucket_receive,
        'likeCount' : like_receive,
        'dislikeCount': dislike_receive
    }
    db.bucket.insert_one(doc)
    return jsonify({'msg': '저장 완료!'})


#### 회원가입 로그인 로그아웃

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SESSION_TYPE'] = 'filesystem'

users_collection = db['users']

# 회원가입
@app.route('/join', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = users_collection.find_one({'email': email})

        if not isValidEmail(email):
            flash('올바른 이메일 형식이 아닙니다')
            return render_template('join.html')
        
        if not isValidPassword(password):
            flash('올바른 암호 형식이 아닙니다.')
            return render_template('join.html')

        if existing_user:
            flash('이미 사용중인 아이디 입니다')
            return render_template('join.html')

        new_user = {'email': email, 'password': password}
        users_collection.insert_one(new_user)

        flash('회원가입성공! 로그인해주세요')
        return redirect(url_for('login'))

    return render_template('join.html')

def isValidEmail(email):
    emailRegex = re.compile(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$')
    return emailRegex.match(email)

def isValidPassword(password):
    passwordRegex = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')
    return passwordRegex.match(password)



# 로그인
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email})

        if user and user['password'] == password:
            session['email'] = email
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다')
            return redirect(url_for('login'))

    return render_template('login.html')


# 로그아웃
@app.route('/logout', methods=["GET"])
def logout():
    session.pop('email', None)
    return render_template('login.html')



if __name__ == '__main__':
    app.run()
