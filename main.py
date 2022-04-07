from flask import Flask, request, render_template, redirect
from better_profanity import profanity
import time

start_time = time.time()
app = Flask(__name__, static_folder="static/css")
profanity.load_censor_words()

@app.route('/')
def main_page():
    return render_template('home.html')

@app.route('/chat')
def chat_page():
    return 'Enter chat name:\n' + render_template('text.html')

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
        return 'Enter secret message:\n' + render_template('text.html')  + chat
    except:
        return render_template('404.html')

@app.route('/chat/<chatid>', methods=['POST'])
def chat_post(chatid):
    answer = request.form['text']
    answer = profanity.censor(answer)
    
    if answer.startswith('!'):
        chatfile = open(f'chats/{chatid}.txt', 'a')
        answer = answer[1:]
        if answer == 'credit':
            chatfile.write("<p>"+"Command: All code is written by MrEnder0001"+"</p>"+'\n')
            chatfile.close()
        if answer == 'clearchat':
            chatfile.close()
            chatfile = open(f'chats/{chatid}.txt', 'w')
            chatfile.write("<p>"+'Command: Chat has been cleared.'+"</p>"+'\n')
            chatfile.close()
        if answer == 'exit':
            chatfile.close()
            return redirect('/')
        if answer == 'uptime':
            chatfile.close()
            chatfile = open(f'chats/{chatid}.txt', 'a')
            chatfile.write("<p>"+'Command: Uptime in mins '+str(round(time.time()-start_time)/60)+"</p>"+'\n')
            chatfile.close()
        if answer.startswith('image'):
            answer = answer[6:]
            chatfile.close()
            chatfile = open(f'chats/{chatid}.txt', 'a')
            chatfile.write("<img src='"+answer+"' style='width:300px;height:250px'>"+'\n<p></p>\n')
            chatfile.close()
    else:
        chatfile = open(f'chats/{chatid}.txt', 'a')
        chatfile.write("<p>"+answer+"</p>"+'\n')
        chatfile.close()

    return redirect(f'/chat/{chatid}')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=80, debug=False)
