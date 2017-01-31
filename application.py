import wsgiref.simple_server
import urllib.parse
import sqlite3
import http.cookies
import cgi

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE if not exists users(username varchar(255), password varchar(255))')
registerform = '''
    <html>
        <form action="register" method="POST">
            <div class="container">
                <label><b>USERNAME</b></label>
                <input type="text" placeholder="New Username" name="username" required>
                <label><b>PASSWORD</b></label>
                <input type="password" placeholder="New Password" name="password" required>
                <label><b>REPEAT PASSWORD</b></label>
                <input type="password" placeholder="Repeat Password" name="repeatpassword" required
                <div class="clearfix">
                    <button type="button" class="cancelbtn">Cancel</button>
                    <button type="submit" class="signupbtn">Sign Up</button>
                </div>
            </div>
        </form>
    </html>
    '''
loginform = '''
    <html>
        <form action="login" method="POST">
            <div class="container">
            <label><b>USERNAME></b></label>
            <input type="text" placeholder="Username" name="name" required>
            <label><b>PASSWORD</b></label>
            <input type="password" placeholder="Password" name="pass" required>
            <button type="submit">Login</button>
        </form>
    </html>
    '''

def application(environ, start_response):
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    path = environ['PATH_INFO']
    post_env = environ.copy()
    post_env['QUERY_STRING'] = ''
    post = cgi.FieldStorage(
        fp=environ['wsgi.input'],
        environ=post_env,
        keep_blank_values=True
    )
    #print('hello loser 2.0')
    un = post['username'].value if 'username' in post else None
    pw = post['password'].value if 'password' in post else None
    print(un,pw)
    if path == '/register' and un and pw:
        print('hello loser')
        user = cursor.execute('SELECT * FROM users WHERE username = ?', [un]).fetchall()
        if user:
            start_response('200 OK', headers)
            return ['Sorry, username {} is taken'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            cursor.execute('INSERT INTO users (username,password) VALUES(?,?)', (un,pw))
            connection.commit()
            connection.close()
            return ['User created successfully'.encode()]
        ### insert code here###

    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',[un,pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un,pw)))
            start_response('200 OK', headers)
            return ['User {} successfully logged in. <a href="/account"> Account </a>'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password'.encode()]
    elif path == '/logout':
        headers.append(('Set-Cookie', 'session=0; expires=Thu, 01 Jan 1970 00:00:00 GMT'))
        start_response('200 OK', headers)
        return ['Logged out. <a href="/">Login</a>'.encode()]

    elif path == '/account':
        start_response('200 OK', headers)
        if 'HTTP_COOKIE' not in environ:
            return ['Not logged in <a href="/">Login</a>'.encode()]
        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        if 'session' not in cookies:
            return ['Not logged in <a href="/">Login</a>'.encode()]
        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute ('SELECT * FROM users WHERE username = ? AND password = ?' [un,pw]).fetchall()
        if user:
            return ['Logged in: {}. <a href="/">Logout</a>'.formar(un).encode()]

        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]

    elif path == '/':

        start_response('200 OK', headers)
        page = [b"<html>", registerform.encode(), b"</html>"]
        headers = [('content-type', 'text/html')]
        return page



    else:

        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]

httpd = wsgiref.simple_server.make_server('', 8000, application)

httpd.serve_forever()
