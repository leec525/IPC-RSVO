import cv2
import os

# 图像序列所在的文件夹
folder_path = 'office/rgb_gs'

# 获取所有图像文件的路径
image_files = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))])

# 检查是否有图像文件
if not image_files:
    print("No images found in the specified folder.")
    exit()

# 播放图像序列
index = 0
while True:
    # 读取当前图像
    image = cv2.imread(image_files[index])
    if image is None:
        print(f"Error reading image: {image_files[index]}")
        break
    
    # 在图像上显示当前图片编号
    cv2.putText(image, f'Frame: {index+1}/{len(image_files)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # 显示图像
    cv2.imshow('Image Sequence', image)
    
    # 等待指定时间后显示下一帧（例如，延迟100毫秒，即每秒10帧）
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break
    
    # 更新索引，循环播放
    index = (index + 1) % len(image_files)

# 关闭所有窗口
cv2.destroyAllWindows()
