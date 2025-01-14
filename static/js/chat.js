const express = require("express");
const app = express();
const http = require("http").Server(app);
const io = require("socket.io")(http);
const nunjucks = require("nunjucks");

// ユーザーのソケットIDを管理するオブジェクト
const userSockets = new Map();

// 接続時の処理
io.on("connection", (socket) => {
  console.log("ユーザーが接続しました");

  // ユーザーが接続した際にユーザー名を取得
  socket.on("setUserName", (userName) => {
    if (!userName) userName = "匿名"; // ユーザー名が未入力の場合は「匿名」を設定
    socket.userName = userName; // ユーザー名をソケットに格納
  });

  // ユーザーが接続したときの処理
  socket.on("user connected", (userId) => {
    userSockets.set(userId, socket.id);
  });

  // DMメッセージの処理
  socket.on("private message", async (data) => {
    const { to, message, from } = data;

    // メッセージをデータベースに保存
    try {
      await db.query(
        "INSERT INTO direct_messages (from_user, to_user, message, created_at) VALUES ($1, $2, $3, NOW())",
        [from, to, message]
      );

      // 受信者のソケットIDを取得
      const recipientSocket = userSockets.get(to);
      if (recipientSocket) {
        // オンラインの場合、リアルタイムで送信
        io.to(recipientSocket).emit("private message", {
          from,
          message,
          timestamp: new Date(),
        });
      }

      // 送信者にも送信完了を通知
      socket.emit("message sent", {
        to,
        message,
        timestamp: new Date(),
      });
    } catch (error) {
      console.error("Message save error:", error);
      socket.emit("message error", { error: "メッセージの送信に失敗しました" });
    }
  });

  // ユーザーの切断処理
  socket.on("disconnect", () => {
    // ユーザーのソケットIDを削除
    for (const [userId, socketId] of userSockets.entries()) {
      if (socketId === socket.id) {
        userSockets.delete(userId);
        break;
      }
    }
  });

  // チャットメッセージの処理（全員にメッセージを配信）
  socket.on("chat", (msg) => {
    if (socket.userName) {
      // ユーザー名が設定されていれば、その名前をメッセージに付加
      io.emit("chat", `${socket.userName}: ${msg}`);
    } else {
      // ユーザー名が設定されていない場合は、匿名で送信
      io.emit("chat", `匿名: ${msg}`);
    }
  });
});

// DMページの表示
app.get("/messages/:userId", async (req, res) => {
  try {
    // 相手ユーザーの情報を取得
    const recipient = await db.query("SELECT * FROM users WHERE id = $1", [
      req.params.userId,
    ]);

    res.render("dm.html", {
      request: {
        user: req.user,
      },
      recipient: recipient.rows[0],
    });
  } catch (error) {
    res.status(500).send("Error loading messages");
  }
});

// 過去のメッセージを取得するAPI
app.get("/api/messages/:userId", async (req, res) => {
  try {
    const messages = await db.query(
      `SELECT * FROM direct_messages 
            WHERE (from_user = $1 AND to_user = $2)
            OR (from_user = $2 AND to_user = $1)
            ORDER BY created_at ASC`,
      [req.user.id, req.params.userId]
    );

    res.json(messages.rows);
  } catch (error) {
    res.status(500).json({ error: "Error loading messages" });
  }
});

// サーバー起動
http.listen(3000, () => {
  console.log("Server is running on http://localhost:3000");
});
