from Config.config import * 

@app.route("/mail")
def mail():
    msg = Message('Hello', sender='yourId@gmail.com',
                  recipients=['pongsirichatkaew@gmail.com'])
    msg.body = "Hello Flask message sent from Flask-Mail"
    mail.send(msg)
    return "Sent"