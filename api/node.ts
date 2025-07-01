import express from 'express';

const app = express();
const port = 3001;

app.get('/hello', (req, res) => {
  res.json({ message: '你好，這是來自 node.ts 的簡單 API！' });
});

app.listen(port, () => {
  console.log(`API 伺服器運行於 http://localhost:${port}`);
}); 