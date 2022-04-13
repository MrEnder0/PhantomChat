from flask import Flask, request, render_template, redirect, send_file
from better_profanity import profanity
from captcha.image import ImageCaptcha
import random, string, time, os

start_time = time.time()
letters = string.ascii_lowercase
app = Flask(__name__, static_folder="static/css")
profanity.load_censor_words()

@app.route('/')
def main_page():
    return render_template('home.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat_page_post():
    chat_name = request.form['text']
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
    try:
        chatfile = open(f'chats/{chatid}.txt', 'r')
        chat = chatfile.read()
        return render_template('chatroom.html')  + chat
    except:
        return render_template('404.html')

@app.route('/chat/<chatid>', methods=['POST'])
def chat_post(chatid):
    answer = request.form['text']
    answer = profanity.censor(answer)
    answer = answer.replace('\n', '<br>')
    answer = answer.replace('<script>', '')
    answer = answer.replace('</script>', '')
    
    if answer.startswith('!'):
        chatfile = open(f'chats/{chatid}.txt', 'a')
        answer = answer[1:]

        if answer == 'clearchat':
            chatfile.close()
            chatfile = open(f'chats/{chatid}.txt', 'w')
            chatfile.write('Command: Chat has been cleared.<br>\n')
            chatfile.close()

        if answer == 'delchat':
            if chatid != "main":
                chatfile.close()
                os.remove(f'chats/{chatid}.txt')
                return redirect('/')
            else:
                pass
        if answer == 'uptime':
            chatfile.close()
            chatfile = open(f'chats/{chatid}.txt', 'a')
            chatfile.write('Command: Uptime in mins '+str(round(time.time()-start_time)/60)+"<br>\n")
            chatfile.close()
        if answer.startswith('image'):
            answer = answer[6:]
            chatfile.close()
            chatfile = open(f'chats/{chatid}.txt', 'a')
            chatfile.write("<img src='"+answer+"' style='width:300px;height:250px'>"+"<br>\n")
            chatfile.close()
        if answer == 'credit':
            chatfile.write("Command: All code is written by MrEnder0001<br>\n")
            chatfile.close()
        if answer == 'exit':
            chatfile.close()
            return redirect('/')
    else:
        chatfile = open(f'chats/{chatid}.txt', 'a')
        chatfile.write(answer+"<br>\n")
        chatfile.close()

    return redirect(f'/chat/{chatid}')

@app.route('/captcha')
def captcha():
    image = ImageCaptcha(width = 280, height = 90)
    captcha_text = ''.join(random.choice(letters) for i in range(5))
    image.write(captcha_text, 'CAPTCHA.png')
    return send_file("CAPTCHA.png", mimetype='image/gif')


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