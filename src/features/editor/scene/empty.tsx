import useStore from "../store/use-store";
import { useEffect, useRef, useState } from "react";
import { Droppable } from "@/components/ui/droppable";
import { PlusIcon } from "lucide-react";
import { DroppableArea } from "./droppable";

const SceneEmpty = () => {
  const [isLoading, setIsLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const [desiredSize, setDesiredSize] = useState({ width: 0, height: 0 });
  const { size } = useStore();

  useEffect(() => {
    const container = containerRef.current!;
    const PADDING = 96;
    const containerHeight = container.clientHeight - PADDING;
    const containerWidth = container.clientWidth - PADDING;
    const { width, height } = size;

    const desiredZoom = Math.min(
      containerWidth / width,
      containerHeight / height,
    );
    setDesiredSize({
      width: width * desiredZoom,
      height: height * desiredZoom,
    });
    setIsLoading(false);
  }, [size]);

  // 彈出選擇檔案視窗並上傳檔案
  const onSelectFiles = async () => {
    // 建立一個隱藏的 input 元素
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = true;
    input.accept = "*/*"; // 可根據需求限制檔案類型
    input.onchange = async (event: any) => {
      const files: FileList = event.target.files;
      if (!files || files.length === 0) return;

      const formData = new FormData();
      Array.from(files).forEach((file) => {
        formData.append("files", file);
      });

      try {
        const response = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("檔案上傳失敗");
        }

        const result = await response.json();
        console.log("上傳成功：", result);
        // 這裡可以根據需要進一步處理上傳結果
      } catch (error) {
        console.error("上傳錯誤：", error);
      }
    };
    // 觸發點擊，顯示選擇檔案視窗
    input.click();
  };

  return (
    <div ref={containerRef} className="absolute z-50 flex h-full w-full flex-1">
      {!isLoading ? (
        <Droppable
          maxFileCount={4}
          maxSize={4 * 1024 * 1024}
          disabled={false}
          onValueChange={onSelectFiles}
          className="h-full w-full flex-1 bg-background"
        >
          <DroppableArea
            onDragStateChange={setIsDraggingOver}
            className={`absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 transform items-center justify-center border border-dashed text-center transition-colors duration-200 ease-in-out ${
              isDraggingOver ? "border-white bg-white/10" : "border-white/15"
            }`}
            style={{
              width: desiredSize.width,
              height: desiredSize.height,
            }}
          >
            <div className="flex flex-col items-center justify-center gap-4 pb-12">
              <div className="hover:bg-primary-dark cursor-pointer rounded-md border bg-primary p-2 text-secondary transition-colors duration-200">
                <PlusIcon className="h-5 w-5" aria-hidden="true" />
              </div>
              <div className="flex flex-col gap-px">
                <p className="text-sm text-muted-foreground">Click to upload</p>
                <p className="text-xs text-muted-foreground/70">
                  Or drag and drop files here
                </p>
              </div>
            </div>
          </DroppableArea>
        </Droppable>
      ) : (
        <div className="flex flex-1 items-center justify-center bg-background-subtle text-sm text-muted-foreground">
          Loading...
        </div>
      )}
    </div>
  );
};

export default SceneEmpty;
