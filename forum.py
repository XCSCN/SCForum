from flask import Flask, render_template, request, redirect, session, abort
from math import ceil

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 存储用户信息的字典
users = {'xiaocai_mua': 'admin'}

# 存储帖子的列表
posts = []

# 创建帖子的函数
def create_post(title, content, author, is_pinned=False):
    post = {'title': title, 'content': content, 'author': author, 'is_pinned': is_pinned}
    posts.append(post)

# 获取帖子对象
def get_post_by_id(post_id):
    if post_id < len(posts):
        return posts[post_id]
    else:
        return None

@app.route('/')
def index():
    page = request.args.get('page', default=1, type=int)  # 获取当前页码，默认为 1
    posts_per_page = 5  # 每页显示的帖子数量
    total_pages = ceil(len(posts) / posts_per_page)  # 计算总页数

    # 根据当前页码和每页显示的帖子数量计算出帖子的范围
    start = (page - 1) * posts_per_page
    end = start + posts_per_page
    paginated_posts = posts[start:end]

    # 在渲染模板时传递分页相关的数据
    username = session.get('username')  # 获取当前登录的用户名
    return render_template('index.html', posts=paginated_posts, username=username,
                           current_page=page, total_pages=total_pages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        
        if username in users:
            session['username'] = username
            return redirect('/')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/create_user', methods=['POST'])
def create_user():
    if 'username' in session and session['username'] == 'xiaocai_mua':
        username = request.form['username']
        password = request.form['password']

        if username not in users:
            users[username] = password

    return redirect('/admin')

@app.route('/create_post', methods=['GET', 'POST'])
def handle_create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = session['username']
        is_pinned = False  # 默认不置顶

        if session['username'] == 'xiaocai_mua' and 'is_pinned' in request.form:
            is_pinned = True

        create_post(title, content, author, is_pinned)
        return redirect('/')

    return render_template('create_post.html')

@app.route('/admin')
def admin():
    if 'username' in session:
        if session['username'] == 'xiaocai_mua':
            return render_template('admin.html', posts=posts)

    return abort(403)

@app.route('/pin_post/<int:post_id>')
def pin_post(post_id):
    # 通过 post_id 获取帖子对象
    post = get_post_by_id(post_id)

    if post:
        # 更新帖子的置顶属性
        post['is_pinned'] = True

        # 将置顶帖子移到帖子列表的第一个位置
        posts.remove(post)
        posts.insert(0, post)

    return redirect('/admin')

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'username' in session:
        if session['username'] == 'xiaocai_mua':
            if post_id < len(posts):
                posts.pop(post_id)

    return redirect('/admin')

if __name__ == '__main__':
    app.run()
