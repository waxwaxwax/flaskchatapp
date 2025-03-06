from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from datetime import timedelta
from utils.ask_ai import generate_response  # Azure OpenAIの呼び出し (独自実装)
from models import db, Thread, Message, User  # DB定義
from flask_migrate import Migrate
from flask_mail import Mail, Message as MailMessage
from models import db, Thread, Message, User


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_default_secret_key_for_development")
app.permanent_session_lifetime = timedelta(days=7)
bcrypt = Bcrypt(app)

# Flask-Mail 設定
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", "587"))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == 'True'
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "")
app.config['GMAIL'] = os.getenv("GMAIL", "")

mail = Mail(app)

# MySQL 設定
# Use SQLite as fallback if MySQL environment variables are not set
if not all([os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASSWORD'), os.getenv('MYSQL_HOST'), 
            os.getenv('MYSQL_PORT'), os.getenv('MYSQL_DB')]):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
else:
    mysql_user = os.getenv('MYSQL_USER')
    mysql_password = os.getenv('MYSQL_PASSWORD')
    mysql_host = os.getenv('MYSQL_HOST')
    mysql_port = os.getenv('MYSQL_PORT')
    mysql_db = os.getenv('MYSQL_DB')
    mysql_ssl_ca = os.getenv('MYSQL_SSL_CA', '')
    
    ssl_config = f"?ssl_ca={mysql_ssl_ca}" if mysql_ssl_ca else ""
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{mysql_user}:{mysql_password}@"
        f"{mysql_host}:{mysql_port}/{mysql_db}{ssl_config}"
    )

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html', title="Home Page", message="Welcome to Flask!")

@app.route('/about')
def about():
    return render_template('about.html', title="About Page", message="This is the about page.")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        msg = MailMessage("お問い合わせがありました",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[app.config['GMAIL']])
        msg.body = f"名前: {name}\nメール: {email}\nメッセージ: {message}"
        try:
            mail.send(msg)
            flash("メッセージが送信されました！", "success")
        except Exception as e:
            flash(f"エラーが発生しました: {str(e)}", "danger")
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('chat'))
        else:
            flash("メールアドレスまたはパスワードが間違っています。", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("ログインしてください。", "warning")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/chat', methods=['GET'])
def chat():
    if 'user_id' not in session:
        flash("ログインしてください。", "warning")
        return redirect(url_for('login'))
    user_id = session['user_id']
    threads = Thread.query.filter_by(user_id=user_id).all()
    return render_template('chat.html', threads=threads, thread=None, messages=[])

@app.route('/chat/new_thread', methods=['POST'])
def new_thread():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 403

    user_id = session['user_id']
    new_thread = Thread(user_id=user_id, name="New Chat")
    db.session.add(new_thread)
    db.session.commit()

    return jsonify({
        'success': True,
        'thread_id': new_thread.id,
        'thread_name': new_thread.name
    })
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # 既存ユーザーの確認
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("このメールアドレスは既に登録されています。", "danger")
            return redirect(url_for('register'))

        # パスワードのハッシュ化とユーザー作成
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("登録が完了しました！ログインしてください。", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/chat/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'reply': 'Error: Not logged in'}), 403

    user_id = session['user_id']
    data = request.json
    user_message = data.get('message', '').strip()
    thread_id = data.get('thread_id', None)

    if not user_message:
        return jsonify({'reply': 'Error: No message provided'}), 400

    # スレッドが指定されていない or 見つからない場合 → エラー
    thread = Thread.query.filter_by(id=thread_id, user_id=user_id).first()
    if not thread:
        return jsonify({'reply': 'Error: No active thread'}), 400

    # 最初のメッセージならスレッド名を変更
    existing_messages = Message.query.filter_by(thread_id=thread.id).count()
    if existing_messages == 0:
        thread.name = user_message[:30]  # 30文字以内に制限
        db.session.commit()

    # メッセージをDBに保存
    user_msg = Message(thread_id=thread.id, sender='user', content=user_message)
    db.session.add(user_msg)
    db.session.commit()

    # AIへのメッセージ履歴を準備
    messages = Message.query.filter_by(thread_id=thread.id).order_by(Message.created_at).all()
    conversation_history = [
        {"role": "user" if msg.sender == "user" else "assistant", "content": msg.content}
        for msg in messages
    ]
    # OpenAI から応答を取得
    ai_reply = generate_response(conversation_history)

    # AIのメッセージをDBに保存
    ai_msg = Message(thread_id=thread.id, sender='ai', content=ai_reply)
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        'reply': ai_reply,
        'thread_id': thread.id,
        'thread_name': thread.name
    })

@app.route('/chat/delete/<int:thread_id>', methods=['POST'])
def delete_thread(thread_id):
    if 'user_id' not in session:
        flash("ログインしてください。", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    thread = Thread.query.filter_by(id=thread_id, user_id=user_id).first()
    if not thread:
        flash("このスレッドを削除する権限がありません。", "danger")
        return redirect(url_for('chat'))

    Message.query.filter_by(thread_id=thread.id).delete()
    db.session.delete(thread)
    db.session.commit()
    return redirect(url_for('chat'))

@app.route('/chat/<int:thread_id>')
def chat_thread(thread_id):
    if 'user_id' not in session:
        flash("ログインしてください。", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    thread = Thread.query.filter_by(id=thread_id, user_id=user_id).first()
    if not thread:
        return redirect(url_for('chat'))

    messages = Message.query.filter_by(thread_id=thread_id).order_by(Message.created_at).all()
    threads = Thread.query.filter_by(user_id=user_id).all()

    return render_template('chat.html', threads=threads, thread=thread, messages=messages)

@app.route("/chat/<int:thread_id>/messages")
def get_thread_messages(thread_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = session["user_id"]
    thread = Thread.query.filter_by(id=thread_id, user_id=user_id).first()

    if not thread:
        return jsonify({"error": "Thread not found"}), 404

    messages = Message.query.filter_by(thread_id=thread.id).order_by(Message.created_at).all()
    data = []
    for msg in messages:
        data.append({
            "sender": msg.sender,
            "content": msg.content,
            "timestamp": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({"messages": data})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
