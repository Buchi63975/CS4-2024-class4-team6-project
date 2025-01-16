document.addEventListener("DOMContentLoaded", function () {
  const messagesContainer = document.getElementById("message-area");
  const messageForm = document.getElementById("dm-form");
  const messageInput = document.getElementById("message-input");
  const receiver = document.getElementById("receiver").value; // 受信者のusername

  function loadMessages() {
    fetch(`/api/messages/${receiver}/`)
      .then((response) => response.json())
      .then((data) => {
        console.log("Received data:", data); // デバッグ用
        messagesContainer.innerHTML = "";

        if (data.messages && Array.isArray(data.messages)) {
          data.messages.forEach((message) => {
            const messageDiv = document.createElement("div");
            messageDiv.classList.add("message");

            // 送信者が自分の場合とそうでない場合でスタイルを変える
            if (
              message.sender === document.getElementById("current-user").value
            ) {
              messageDiv.classList.add("sent");
            } else {
              messageDiv.classList.add("received");
            }

            messageDiv.innerHTML = `
                            <strong>${message.sender}</strong>
                            <p>${message.content}</p>
                            <small>${new Date(
                              message.created_at
                            ).toLocaleString()}</small>
                        `;
            messagesContainer.appendChild(messageDiv);
          });

          // スクロールを最下部に
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } else {
          console.error("Invalid message format:", data);
        }
      })
      .catch((error) => {
        console.error("Error loading messages:", error);
        messagesContainer.innerHTML =
          "<p>メッセージの読み込みに失敗しました。</p>";
      });
  }

  messageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const message = messageInput.value.trim();

    if (!message) {
      alert("メッセージを入力してください。");
      return;
    }

    fetch(`/api/messages/${receiver}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
      body: JSON.stringify({
        content: message,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Send response:", data); // デバッグ用
        messageInput.value = "";
        loadMessages(); // メッセージを再読み込み
      })
      .catch((error) => {
        console.error("Error sending message:", error);
        alert("メッセージの送信に失敗しました。");
      });
  });

  // 初回メッセージ読み込み
  loadMessages();

  // 定期的な更新（オプション）
  setInterval(loadMessages, 5000); // 5秒ごとに更新
});

// 会話リストのクリックイベント
conversationList.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("conversation")) {
    selectedUsername = e.target.dataset.username;
    document.getElementById("receiver").value = selectedUsername; // 追加
    loadMessages(selectedUsername);
    document.getElementById("dm-form").style.display = "flex";
  }
});

// メッセージを取得する関数
function fetchMessages() {
  fetch(`/api/messages/${recipientUsername}/`)
    .then((response) => response.json())
    .then((data) => {
      console.log("Received messages:", data); // デバッグ用
      // メッセージの表示処理
    })
    .catch((error) => console.error("Error:", error));
}
