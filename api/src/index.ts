import express from "express";
import bookRoutes from "./routes/bookRoutes";
import testRouter from "./routes/testRouter";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use("/api", bookRoutes);
app.use("/api", testRouter);

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});