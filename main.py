import sqlite3, random, string, time, os

try:
    from flask import Flask, request, render_template, redirect, send_file
    from better_profanity import profanity
    from captcha.image import ImageCaptcha
except ImportError:
    print("[!] Error: Missing dependencies...\n[#] Installing dependencies...")
    os.system('python3 pip install flask better_profanity captcha')
    print("[#] Dependencies installed, to apply reopen the server.")
    exit()
    
start_time = time.time()
profanity.load_censor_words()
letters = string.ascii_lowercase
disallowedchars = [':', '"', '/', '\\', '.']

connection = sqlite3.connect('data.db', check_same_thread=False)
cursor = connection.cursor()

app = Flask(__name__, static_folder="static")

def generate_captcha():
    global captcha_text
    image = ImageCaptcha(width = 280, height = 90)
    captcha_text = ''.join(random.choice(letters) for i in range(5))
    image.write(captcha_text, 'static/CAPTCHA.png')

def new_user(ip):
    nickname = "Ghost " + ''.join(random.choices(string.digits, k=6))
    cursor.execute("INSERT INTO 'users'(username, userip, captcha, admin) VALUES(?, ?, ?, ?)", (nickname, ip, False, False))
    connection.commit()

def get_nickname(ip):
    cursor.execute("SELECT username FROM 'users' WHERE userip = ?", (ip,))
    nickname = cursor.fetchone()
    return nickname[1]

@app.route('/')
def main_page():
    return render_template('home.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat_page_post():
    chat_name = request.form['text']
    for word in disallowedchars:
        if word in chat_name:
            return redirect('/chat')
    try:
        chat_file = open(f'chats/{chat_name}.txt', 'r')
        chat_file.close()
        return redirect(f'/chat/{chat_name}')
    except FileNotFoundError:
        chat_file = open(f'chats/{chat_name}.txt', 'w')
        chat_file.close()
        return redirect(f'/chat/{chat_name}')

@app.route('/chat/<chatid>')
def chat(chatid):
    for word in disallowedchars:
        if word in chatid:
            return redirect('/chat/' + chatid)

    userip = request.remote_addr
    cursor.execute("Select * FROM 'users' WHERE userip=?", (userip,))
    userInfo = cursor.fetchone()

    try:
        if not len(userInfo)==0:pass
    except:
        new_user(userip)
        chatfile = open(f'chats/{chatid}.txt', 'r')
        chat = chatfile.read()
        return render_template('chatroom.html')  + chat

    captcha = userInfo[3]

    if not captcha:
        try:
            chatfile = open(f'chats/{chatid}.txt', 'r')
            chat = chatfile.read()
            return render_template('chatroom.html')  + chat
        except:
            return render_template('404.html')
    else:
        generate_captcha()
        return render_template('captcha.html')

@app.route('/chat/<chatid>', methods=['POST'])
def chat_post(chatid):
    for word in disallowedchars:
        if word in chatid:
            return redirect('/chat/' + chatid)

    userip = request.remote_addr
    cursor.execute("Select * FROM 'users' WHERE userip=?", (userip,))
    userInfo = cursor.fetchone()
    captcha = userInfo[3]

    if not captcha:
        chatroom_message = request.form['text']
        chatroom_message = profanity.censor(chatroom_message)
        chatroom_message = chatroom_message.replace('\n', '<br>')
        chatroom_message = chatroom_message.replace('<script>', '')
        chatroom_message = chatroom_message.replace('</script>', '')
        chatroom_message = chatroom_message.replace('<script src', '')
        chatroom_message = chatroom_message.replace('<script type="text/javascript" src', '')
        chatroom_message = chatroom_message.replace('javascript="', '')
        chatroom_message = chatroom_message.replace('<iframe>', '')
        chatroom_message = chatroom_message.replace('</iframe>', '')
        chatroom_message = chatroom_message.replace('<portal>', '')
        chatroom_message = chatroom_message.replace('</portal>', '')

        if random.randint(0,10) < 2:
                cursor.execute("UPDATE 'users' SET captcha = ? WHERE userip = ?", (True, userip))
                connection.commit()
    
        if chatroom_message.startswith('!'):
            chatfile = open(f'chats/{chatid}.txt', 'a')
            chatroom_message = chatroom_message[1:]

            if chatroom_message == 'uptime':
                chatfile.close()
                chatfile = open(f'chats/{chatid}.txt', 'a')
                chatfile.write('<p style="font-size: 32px;font-family: KoHo;">*[Command] Uptime in mins '+str(round((time.time()-start_time)/60, 2))+"</p>\n")
                chatfile.close()

            if chatroom_message.startswith('image'):
                chatroom_message = chatroom_message[6:]
                chatfile.close()
                chatfile = open(f'chats/{chatid}.txt', 'a')
                chatfile.write("<img src='"+chatroom_message+"' style='width:300px;height:250px'>"+"<br>\n")
                chatfile.close()
            
            if chatroom_message.startswith('garticphone'):
                chatroom_message = chatroom_message[12:]
                chatfile.close()
                if chatroom_message.startswith('https://garticphone.com/'):
                    chatfile = open(f'chats/{chatid}.txt', 'a')
                    chatfile.write(f'<div style="background-color: whitesmoke;width: 550px;border: 7px solid black;padding: 5px;margin: 20px;border-radius: 25px;line-height: 450%;font-family: KoHo;"><h1 style="vertical-align: super;vertical-align: text-top;vertical-align: top;text-align: center;"><strong>GarticPhone Party</strong></h1><button onclick="location.href = \'{chatroom_message}\'" class="gatricphone_join" style="background-color: black;border: none;color: white;padding: 18px 200px;text-align: center;font-size: 24px;margin: 4px 2px;border-radius: 25px;opacity: 0.8;text-align: center;"><h3>Join Party</h3></button></div>')

            if chatroom_message == 'credit':
                chatfile.write('<p style="font-size: 32px;font-family: KoHo;">*[Command] All code is written by MrEnder0001</p>\n')
                chatfile.close()

            if chatroom_message.startswith('nickname'):
                nickname = chatroom_message[9:]
                cursor.execute("UPDATE 'users' SET username = ? WHERE userip = ?", (nickname, userip))
                connection.commit()
            
            if chatroom_message == 'exit':
                chatfile.close()
                return redirect('/')

            if chatroom_message.startswith('admin.'):
                cursor.execute("Select * FROM 'users' WHERE userip=?", (userip,))
                userInfo = cursor.fetchone()
                isadmin = userInfo[4]
                if isadmin:
                    if chatroom_message == 'admin.clearchat':
                        chatfile.close()
                        chatfile = open(f'chats/{chatid}.txt', 'w')
                        chatfile.write('<p style="font-size: 32px;font-family: KoHo;">*[Command] Chat has been cleared.</p>\n')
                        chatfile.close()
                    if chatroom_message == 'admin.delchat':
                        chatfile.close()
                        os.remove(f'chats/{chatid}.txt')
                        return redirect('/')
                    if chatroom_message.startswith('admin.announce'):
                        chatfile.close()
                        message = chatroom_message[14:]
                        for chat in os.listdir('chats'):
                            chatfile = open(f'chats/{chat}', 'a')
                            chatfile.write(f'<strong><p style="font-size: 32px;font-family: KoHo;">*[Anouncement] {message}</p></strong>\n')
                            chatfile.close()

            if chatroom_message == 'test.forcecaptcha':
                chatfile.close()
                cursor.execute("UPDATE 'users' SET captcha = ? WHERE userip = ?", (True, userip))
                connection.commit()
                return redirect('/chat/'+chatid)
        else:
            cursor.execute("Select * FROM 'users' WHERE userip=?", (userip,))
            userInfo = cursor.fetchone()
            username = userInfo[1]
            chatfile = open(f'chats/{chatid}.txt', 'a')
            chatfile.write(f'<p style="font-size: 32px;font-family: KoHo;">[{username}] {chatroom_message}</p>\n')
            chatfile.close()
    else:
        captcha_answer = request.form['captcha']
        if captcha_answer == captcha_text:
            cursor.execute("UPDATE 'users' SET captcha = ? WHERE userip = ?", (False, userip))
            connection.commit()
        else:
            return redirect(f'/chat/{chatid}')

    return redirect(f'/chat/{chatid}')

@app.route('/captcha')
def captcha():
    generate_captcha()
    return send_file("static/css/CAPTCHA.png", mimetype='image/gif')

@app.route('/robots.txt')
def robots():
    robots_txt = open('static/robots.txt', 'r')
    return robots_txt.read()

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
    
