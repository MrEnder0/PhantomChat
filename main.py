from flask import Flask, request, render_template, redirect, send_file
from better_profanity import profanity
from captcha.image import ImageCaptcha
import random, string, time, os

start_time = time.time()
profanity.load_censor_words()
letters = string.ascii_lowercase
disallowedchars = [':', '"', '/', '\\', '.']
app = Flask(__name__, static_folder="static")

def generate_captcha():
    global captcha_text
    image = ImageCaptcha(width = 280, height = 90)
    captcha_text = ''.join(random.choice(letters) for i in range(5))
    image.write(captcha_text, 'static/CAPTCHA.png')

def asign_username(ip, username):
    usernamefile = open('usernames.txt', 'a')
    if "|" or "=" or "." in username:
        username = username.replace("|", "")
        username = username.replace("=", "")
        username = username.replace(".", "")

    if username == '':
        NewUsername = "Ghost " + ''.join(random.choices(string.digits, k=6))
        usernamefile.write(f'{ip}={NewUsername}|')
    else:
        usernamefile.write(f'{ip}={username}|')

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
    captchaRequire = open('captcha_require.txt', 'r')
    usernamefile = open('usernames.txt', 'r')

    if not userip in captchaRequire.read():
        try:
            chatfile = open(f'chats/{chatid}.txt', 'r')
            chat = chatfile.read()
            if not userip in usernamefile.read():
                asign_username(userip, '')
            return render_template('chatroom.html')  + chat
        except:
            if not userip in usernamefile.read():
                asign_username(userip, '')
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
    captchaRequire = open('captcha_require.txt', 'r')

    if not userip in captchaRequire.read():
        chatroom_message = request.form['text']
        chatroom_message = profanity.censor(chatroom_message)
        chatroom_message = chatroom_message.replace('\n', '<br>')
        chatroom_message = chatroom_message.replace('<script>', '')
        chatroom_message = chatroom_message.replace('</script>', '')
    
        if chatroom_message.startswith('!'):
            chatfile = open(f'chats/{chatid}.txt', 'a')
            chatroom_message = chatroom_message[1:]

            if chatroom_message == 'clearchat':
                chatfile.close()
                chatfile = open(f'chats/{chatid}.txt', 'w')
                chatfile.write('Command: Chat has been cleared.<br>\n')
                chatfile.close()

            if chatroom_message == 'delchat':
                if chatid != "main":
                    chatfile.close()
                    os.remove(f'chats/{chatid}.txt')
                    return redirect('/')
                else:
                    pass

            if chatroom_message == 'uptime':
                chatfile.close()
                chatfile = open(f'chats/{chatid}.txt', 'a')
                chatfile.write('Command: Uptime in mins '+str(round(time.time()-start_time)/60)+"<br>\n")
                chatfile.close()

            if chatroom_message.startswith('image'):
                chatroom_message = chatroom_message[6:]
                chatfile.close()
                chatfile = open(f'chats/{chatid}.txt', 'a')
                chatfile.write("<img src='"+chatroom_message+"' style='width:300px;height:250px'>"+"<br>\n")
                chatfile.close()

            if chatroom_message == 'credit':
                chatfile.write("Command: All code is written by MrEnder0001<br>\n")
                chatfile.close()
            
            if chatroom_message == 'exit':
                chatfile.close()
                return redirect('/')
            if random.randint(0,100) < 20:
                captchaRequire = open('captcha_require.txt', 'a')
                captchaRequire.write(userip+'|')
                captchaRequire.close()
        else:
            chatfile = open(f'chats/{chatid}.txt', 'a')
            chatfile.write(chatroom_message+"<br>\n")
            chatfile.close()
            if random.randint(0,100) < 20:
                captchaRequire = open('captcha_require.txt', 'a')
                captchaRequire.write(userip+'|')
                captchaRequire.close()
    else:
        captcha_answer = request.form['captcha']
        if captcha_answer == captcha_text:
            captchaRequire = open('captcha_require.txt', 'r')
            required_captcha = captchaRequire.read()
            captchaRequire.close()
            captchaRequire = open('captcha_require.txt', 'w')
            captchaRequire.write(required_captcha.replace(userip+"|", ''))
            captchaRequire.close()
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
