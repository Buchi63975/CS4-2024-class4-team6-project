from flask_socketio import SocketIO, emit
from flask import request

socketio = SocketIO()


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("private message")
def handle_private_message(data):
    to_user = data.get("to")
    from_user = data.get("from")
    message = data.get("message")

    # メッセージをデータベースに保存
    # SQLiteを使用している場合の例
    try:
        with db.connect() as con:
            con.execute(
                'INSERT INTO direct_messages (from_user, to_user, message, created_at) VALUES (?, ?, ?, datetime("now"))',
                [from_user, to_user, message],
            )

        # 受信者にメッセージを送信
        emit(
            "private message",
            {
                "from": from_user,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            },
            room=to_user,
        )

        # 送信者に確認を送信
        emit(
            "message sent",
            {
                "to": to_user,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        print("Error:", e)
        emit("message error", {"error": "Failed to send message"})
