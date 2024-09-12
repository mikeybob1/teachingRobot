import requests
import base64
import json
from PIL import Image
import os

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def generate_output_filename(input_path, output_dir):
    base_name = os.path.basename(input_path)  # 获取原始文件名
    name, ext = os.path.splitext(base_name)  # 分离文件名和扩展名
    output_filename = f"{name}_generated{ext}"  # 添加 "_generated" 后缀
    return os.path.join(output_dir, output_filename)

def generate_image(pic_url, output_dir):
    # 检查图片是否存在
    if not os.path.exists(pic_url):
        return {"error": "Invalid image path"}, 400

    image = Image.open(pic_url)
    width, height = image.size

    init_image_base64 = image_to_base64(pic_url)

    # 构建请求体
    api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"
    payload = {
        "prompt": "a person with larger abdominal muscles",  # 提示词
        "negative_prompt": "no changes to face",  # 负面提示
        "styles": [],  # 样式
        "seed": -1,  # 随机种子
        "sampler_name": "DPM++ 2M",  # 采样器
        "scheduler": "Karras",
        "batch_size": 1,  # 一次生成的图像数量
        "n_iter": 1,  # 迭代次数
        "steps": 40,  # 生成图像的步数
        "cfg_scale": 7,  # 引导尺度
        "width": width,  # 原始图像的宽度
        "height": height,  # 原始图像的高度
        "restore_faces": True,  # 是否修复面部
        "denoising_strength": 0.2,  # 去噪强度
        "init_images": [init_image_base64],  # 替换为 base64 编码的图片
        "send_images": True,  # 返回生成的图像
        "save_images": False,  # 是否保存图像
        "checkpoint": "epicrealism_naturalSinRC1VAE.safetensors"  # 使用的模型 checkpoints
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        if "images" in result:
            image_data = result["images"][0]
            image_bytes = base64.b64decode(image_data)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            output_filename = generate_output_filename(pic_url, output_dir)
            with open(output_filename, "wb") as output_file:
                output_file.write(image_bytes)

            return {"url": f"{os.path.basename(output_filename)}"}, 200
        else:
            return {"error": "No image generated"}, 500
    else:
        return {"error": f"Failed to process image. Status code: {response.status_code}"}, 500
