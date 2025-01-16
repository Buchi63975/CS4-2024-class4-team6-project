// -- 変数を用意（true： 自分が送信/false： 相手が送信） --
// 送信者が自分かどうか保存する変数
let isMyself = true;
// ---------- 送信ボタンの取得 ----------
// idをもとに送信ボタン取得
let sendBtn = document.getElementById("sendBtn");

// ---- 送信ボタンがクリックされたときの処理 ----
sendBtn.addEventListener("click", function () {
  // ---------- 入力欄を取得 ----------
  // idをもとにinputタグを保存
  let inputMessage = document.getElementById("inputMessage");
  // ---------- 入力値を取得 ------------
  // inputタグがもつ画面の入力値を変数に保存
  let messageText = inputMessage.value;
  // --- 入力値が空の場合に処理を中断 ---
  // 入力値が空かチェックする
  if (messageText == "") {
    // 以降の処理実行されない
    return;
  }

  // ------- メッセージ用のdivタグを作成する  -------
  // messageBoxにdivを入れる
  let messageBox = createMessageBox();
  // ------- メッセージ用のpタグを作成する  -------
  let message = createMessage(messageText);
  // ------- divにpタグを追加する -------
  // messageBoxの子要素として追加するためappendChildを使用
  messageBox.appendChild(message);

  // ---- チャット画面のdivタグを取得する ----
  let room = document.getElementById("room");
  // -- チャット画面のdivに新規メッセージのdivを追加する --
  // 動作確認時Safariだとうまくいかず、Chromeで確認
  room.appendChild(messageBox);

  // -- 送信ボタンが押された時に、入力欄の入力値をリセットする --
  // 入力欄が持っている値を空文字で上書き
  inputMessage.value = "";

  // ------- 送信されるたびに送信者を変更 -------
  if (isMyself) {
    // 自分が送信者の場合、次の送信者を相手にする
    isMyself = false;
  } else {
    // 相手が送信者の場合、次の送信者を自分にする
    isMyself = true;
  }

  // ------- メッセージ用のdivタグを作成する  -------
  function createMessageBox() {
    // ---------- divを作成 ----------
    let messageBox = document.createElement("div");
    // 誰が送信者かチェック
    if (isMyself) {
      // 自分が送信者の場合
      // 「box-right」というクラスをdivに追加（要素に対してクラスを設定）
      messageBox.classList.add("box-right");
    } else {
      // 相手が送信者の場合
      // 「box-left」というクラスをdivに追加（要素に対してクラスを設定）
      messageBox.classList.add("box-left");
    }

    return messageBox;
  }

  // ------- メッセージ用のpタグを作成する  -------
  // pタグ作るとき文字の設定が必要
  function createMessage(messageText) {
    // ---------- pタグを作成 ----------
    let message = document.createElement("p");
    // pタグのテキストに画面の入力値を設定
    // 文字設定する時はtextContent使用
    message.textContent = messageText;
    // pタグに「message-box」というクラスを追加
    message.classList.add("message-box");
    // 誰が送信者かチェック
    if (isMyself) {
      // 自分が送信者の場合
      // pタグに「green」というクラスを追加
      message.classList.add("green");
    } else {
      // 相手が送信者の場合
      // pタグに「white」というクラスを追加
      message.classList.add("white");
    }

    return message;
  }
});
