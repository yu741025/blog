# Code Style Suggestions

## 1. 善用 `Annotated`，嚴格定義 typing

- 使用 [Enum](https://github.com/ShuChenAI/teamsync-backend/blob/cd94f425826de3e4316ae7f2c23e37135a07051f/src/schemas/__init__.py#L13) 取代字串常數。
- 使用 [Regex pattern](https://github.com/ShuChenAI/teamsync-backend/blob/cd94f425826de3e4316ae7f2c23e37135a07051f/src/schemas/cyber_accounts.py#L12) 取代原始字串驗證。Ex.startAt, editAt
- 優先使用閉區間（Closed interval）而非開區間（Open interval）。

## 2. 明確定義 API 參數類別

- 對於 `Query`、`Path`、`Form` 等 API 參數，需明確定義其類別（explicitly define），以增強程式碼的可讀性與維護性。

## 3. 統整輔助函數

- 建議將輔助函數統整至 `src/utils/` 等資料夾，以維持 API Router 的可讀性和模組化。

## 4. API 文件撰寫

- API 相關的說明應撰寫在對應 function 的 `description` 中，這樣程式碼與文件的共同維護可以更加流暢。

  - 範例 API：[Chatroom: Chat APIs](https://api.scfg.io/docs#/Chatroom%3A%20Chat%20APIs/submit_ai_chat_private_chatrooms_chat_ai__chatroom_id__post)
  - 範例程式碼：[chat.py](https://github.com/ShuChenAI/teamsync-backend/blob/cd94f425826de3e4316ae7f2c23e37135a07051f/src/routers/private/chatrooms/chat.py#L523)

---

## 💬 Review Comment

> 整體來說完成度非常高，看的出來是有設計過系統的，在沒有提到需要使用 Category，能夠自行設計 `many-to-many ORM relationship`，讓人相當驚艷！

---

