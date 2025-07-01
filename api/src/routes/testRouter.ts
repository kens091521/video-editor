import { Router, Request, Response } from "express";
const router = Router();

// Get a book by ID
router.get("/token", (req: Request, res: Response) => {
    // 這裡示範如何在 Express 路由中呼叫其他 API
    // 由於無法在這裡 import axios 或 node-fetch，直接用原生 fetch（Node 18+ 支援）
    // 假設要呼叫一個外部 API，例如 https://jsonplaceholder.typicode.com/todos/1

    fetch("https://jsonplaceholder.typicode.com/todos/1")
        .then(response => response.json())
        .then(data => {
            res.json({
                message: "成功呼叫外部 API",
                data: data
            });
        })
        .catch(error => {
            res.status(500).json({
                message: "呼叫外部 API 發生錯誤",
                error: error.toString()
            });
        });
});

// 檔案上傳 API，使用 express 原生的 req.files 需配合 middleware，例如 multer
// 這裡假設已經安裝並設定 multer，但因為不能 import，所以僅示範 API 路由結構
// 實際使用時，請在主程式引入 multer 並將 middleware 傳入

// 範例：
// import multer from "multer";
// const upload = multer({ dest: "uploads/" });

// 修正：Express 處理檔案上傳時，需配合 multer middleware，否則 req.file/req.files 會是 undefined
// 這裡僅示範結構，實際應在主程式引入並使用 upload.single("file") 或 upload.array("files")
router.post("/upload", (req: Request, res: Response) => {
    // @ts-ignore
    const hasFile = req.file || (req.files && Object.keys(req.files).length > 0);
    if (!hasFile) {
        return res.status(400).json({ message: "沒有上傳任何檔案" });
    }
    }

    // @ts-ignore
    const file = req.file || (req.files && req.files.file);

    // 回傳檔案資訊
    res.json({
        message: "檔案上傳成功",
        file: {
            originalname: file?.originalname,
            filename: file?.filename,
            mimetype: file?.mimetype,
            size: file?.size
        }
    });
});

export default router;