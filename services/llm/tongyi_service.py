#  Copyright © [2024] 程序那些事
#
#  All rights reserved. This software and associated documentation files (the "Software") are provided for personal and educational use only. Commercial use of the Software is strictly prohibited unless explicit permission is obtained from the author.
#
#  Permission is hereby granted to any person to use, copy, and modify the Software for non-commercial purposes, provided that the following conditions are met:
#
#  1. The original copyright notice and this permission notice must be included in all copies or substantial portions of the Software.
#  2. Modifications, if any, must retain the original copyright information and must not imply that the modified version is an official version of the Software.
#  3. Any distribution of the Software or its modifications must retain the original copyright notice and include this permission notice.
#
#  For commercial use, including but not limited to selling, distributing, or using the Software as part of any commercial product or service, you must obtain explicit authorization from the author.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Author: 程序那些事
#  email: flydean@163.com
#  Website: [www.flydean.com](http://www.flydean.com)
#  GitHub: [https://github.com/ddean2009/MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus)
#
#  All rights reserved.
#
#

# 设置 tongyi API 的基础 URL 和 API 密钥
import os
import requests

from langchain_community.llms.tongyi import Tongyi
from langchain_core.prompts import PromptTemplate
from urllib.parse import quote

from config.config import my_config
from services.llm.llm_service import MyLLMService
from tools.utils import must_have_value

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 脚本所在的目录
script_dir = os.path.dirname(script_path)

# workdir
workdir = os.path.join(script_dir, "../../resource")
workdir = os.path.abspath(workdir)


def download_image(image_url, save_path):
    """下载图片到本地"""
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Image downloaded successfully: {save_path}")
        return True
    else:
        print(f"Failed to download image: {response.status_code}")
        return False



class MyTongyiService(MyLLMService):
    def __init__(self):
        super().__init__()  # 调用父类的构造函数来初始化父类的属性
        # DASHSCOPE_API_KEY = getpass()
        self.TONGYI_API_KEY = my_config['llm']['Tongyi']['api_key']  # 替换为您的 tongyi API 密钥
        self.TONGYI_MODEL_NAME = my_config['llm']['Tongyi']['model_name']  # 替换为 tongyi API 的model
        must_have_value(self.TONGYI_API_KEY, "请设置tongyi API 密钥")
        must_have_value(self.TONGYI_MODEL_NAME, "请设置tongyi API model")
        os.environ["DASHSCOPE_API_KEY"] = self.TONGYI_API_KEY

    def generate_content(self, topic: str, prompt_template: PromptTemplate, language: str = None, length: str = None):
        # 创建 Kimi 的 LLM 实例
        llm = Tongyi(model=self.TONGYI_MODEL_NAME)

        description = llm.invoke(prompt_template.format(topic=topic, language=language, length=length))

        return description.strip()

    def generate_image_with_wanxiang(self, prompt: str, width: int = 1024, height: int = 1024, n: int = 1):
        """
        使用通义万相API生成图片
        :param prompt: 图片生成的提示词
        :param width: 图片宽度
        :param height: 图片高度
        :param n: 生成图片数量
        :return: 生成的图片信息
        """
        try:
            import dashscope
            from dashscope import ImageSynthesis

            # 设置API密钥
            dashscope.api_key = self.TONGYI_API_KEY

            # 使用通义万相进行图像生成
            response = ImageSynthesis.call(
                model=ImageSynthesis.Models.wanx_v1,  # 通义万相模型
                prompt=prompt,
                n=n,
                size=f'{width}*{height}'
            )

            if response.status_code == 200:
                # 返回生成的图片URL列表
                image_urls = []
                for result in response.output.results:
                    image_urls.append(result.url)
                return image_urls
            else:
                print(f"Image generation failed: {response.code}, {response.message}")
                return None
        except ImportError:
            print("Please install dashscope: pip install dashscope")
            return None
        except Exception as e:
            print(f"Error in image generation: {str(e)}")
            return None

    def generate_image_prompt_from_topic(self, topic: str):
        """
        使用通义千问生成适合图片生成的提示词
        :param topic: 主题
        :return: 适合图片生成的提示词
        """
        # 创建一个专门用于生成图片提示词的模板
        image_prompt_template = PromptTemplate.from_template(
            "根据以下主题生成详细、具体的图片生成提示词，使用英文描述：{topic}。要求包含画面构图、风格、颜色、光线、主体等详细描述。"
        )

        # 使用通义千问生成图片提示词
        image_prompt = self.generate_content(topic, image_prompt_template)
        return image_prompt

    def generate_and_save_image(self, topic: str, width: int = 1024, height: int = 1024, n: int = 1):
        """
        从主题生成图片并保存到本地
        :param topic: 主题
        :param width: 图片宽度
        :param height: 图片高度
        :param n: 生成图片数量
        :return: 本地保存的图片路径列表
        """
        # 首先生成图片提示词
        image_prompt = self.generate_image_prompt_from_topic(topic)
        print(f"Generated image prompt: {image_prompt}")

        # 使用通义万相生成图片
        image_urls = self.generate_image_with_wanxiang(image_prompt, width, height, n)
        if not image_urls:
            print("Failed to generate image from Tongyi Wanxiang")
            return None

        # 下载生成的图片到本地
        saved_paths = []
        for i, image_url in enumerate(image_urls):
            # 创建保存路径
            image_name = f"tongyi-image-{quote(topic)[:50]}-{i}.jpg"  # 限制文件名长度
            save_path = os.path.join(workdir, image_name)
            save_path = os.path.abspath(save_path)

            # 下载图片
            if download_image(image_url, save_path):
                saved_paths.append(save_path)
            else:
                print(f"Failed to save image {image_url} to {save_path}")

        return saved_paths