import os
from PIL import Image
import shutil

# 定义文件路径
input_folder = "rgb_rs/sliced"
output_folder = "rgb_rs/t1_fast_cam1"
output_folder_gs = "rgb_gs"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(output_folder_gs, exist_ok=True)

# 获取所有帧数
frame_numbers = sorted(set(int(f.split('_')[2]) for f in os.listdir(input_folder) if f.startswith('t1_fast_') and f.endswith('.png')))

# 图像尺寸
image_width = 640
image_height = 480

for frame_number in frame_numbers:
    # 提取全局图像
    # 构建原始文件名和路径
    part_filename_gs = f't1_fast_{frame_number:06d}_part_0000.png'
    part_path_gs = os.path.join(input_folder, part_filename_gs)
    
    if os.path.exists(part_path_gs):
        # 构建新的文件名和路径
        new_filename = f't1_fast_frame_{frame_number:04d}.png'
        new_path = os.path.join(output_folder_gs, new_filename)
        
        # 复制并重命名文件
        shutil.copy(part_path_gs, new_path)
        print(f'Copied and renamed {part_path_gs} to {new_path}')
    else:
        print(f"Warning: {part_path_gs} does not exist.")

    # 拼接卷帘图像
    # 创建一个空白的卷帘图像
    combined_image = Image.new('RGB', (image_width, image_height))
    
    for row in range(image_height):
        part_filename = f't1_fast_{frame_number:06d}_part_{row:04d}.png'
        part_path = os.path.join(input_folder, part_filename)
        
        if os.path.exists(part_path):
            part_image = Image.open(part_path)
            combined_image.paste(part_image, (0, row))
        else:
            print(f"Warning: {part_path} does not exist.")
    
    # 保存拼接后的图像
    combined_image.save(os.path.join(output_folder, f't1_fast_{frame_number:06d}.png'))
    print(f'Frame {frame_number} has been combined and saved.')

print("所有全局图像帧保存完成！")
print("所有卷帘图像帧拼接完成！")
