
# 设置火山引擎API的基础URL和API密钥
import os
import requests

from langchain_core.prompts import PromptTemplate
from urllib.parse import quote

from config.config import my_config
from services.llm.llm_service import MyLLMService
from tools.utils import must_have_value
import tools.utils as utils
from tools.utils import random_with_system_time, get_must_session_option, extent_audio, get_session_option

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


class MyVolcEngineService(MyLLMService):
    def __init__(self):
        super().__init__()  # 调用父类的构造函数来初始化父类的属性
        # 从配置文件获取火山引擎API密钥信息
        self.VOLCENGINE_ACCESS_KEY = my_config['llm']['VolcEngine']['access_key_id']  # 替换为您的火山引擎AK
        self.VOLCENGINE_SECRET_KEY = my_config['llm']['VolcEngine']['access_key_secret']  # 替换为您的火山引擎SK
        self.VOLCENGINE_MODEL_NAME = my_config.get('llm', {}).get('VolcEngine', {}).get('model_name', 'jimeng_high_aes_general_v21_L')
        must_have_value(self.VOLCENGINE_ACCESS_KEY, "请设置火山引擎Access Key")
        must_have_value(self.VOLCENGINE_SECRET_KEY, "请设置火山引擎Secret Key")

    def generate_content(self, topic: str, prompt_template: PromptTemplate, language: str = None, length: str = None):
        # 火山引擎API不支持文本生成，这里只是继承父类方法
        raise NotImplementedError("火山引擎图像生成API不支持文本内容生成")
    
    def generate_image_with_volcengine_from_image(self, prompt: str, width: int = 1024, height: int = 1024,seed: int = 0, 
                                                  upload_pic_name: str = None, scale: float = 0.5):
        """
        使用火山引擎即梦AI API生成图片
        :param prompt: 图片生成的提示词
        :param width: 图片宽度
        :param height: 图片高度
        :param n: 生成图片数量
        :return: 生成的图片信息
        """
        try:
            # 导入火山引擎SDK
            from volcengine.visual.VisualService import VisualService

            print("VisualService导入成功")


            # 创建视觉服务实例
            visual_service = VisualService()
            visual_service.set_ak(self.VOLCENGINE_ACCESS_KEY)   # 设置AK
            visual_service.set_sk(self.VOLCENGINE_SECRET_KEY)   # 设置SK

            # 暂时用固定地址
            # ip = utils.get_local_ip()

            ip = "193.112.106.176"
            # 构建url
            image_urls = f"{ip}:8502/{upload_pic_name}"

            # 构建请求参数
            form = {
                "req_key": "jimeng_i2i_v30",  # 使用固定的模型名称
                "image_urls": image_urls,
                "prompt": prompt,  # 提示词
                "seed": seed, # 随机种子
                "scale": scale, # 文字影响程度
                "width": width,  # 图片宽度
                "height": height,  # 图片高度
                "return_url": True  # 返回图片URL
            }

            print(f"Request parameters: {form}")

            # 调用API生成图片
            resp = visual_service.cv_process(form)

            print(f"Image generation response: {resp}")

            # 解析返回结果
            if resp.get('code') == 10000:  # 假设0表示成功
                image_urls = resp.get('data', {}).get('image_urls', [])
                print(f"Generated image URLs: {image_urls}")
                return image_urls
            else:
                print(f"Image generation failed: {resp.get('message', 'Unknown error')}")
                return None

        except ImportError as e:
            print(f"Please install volcengine: pip install volcengine: {str(e)}")
            return None
        except Exception as e:
            print(f"Error in image generation: {str(e)}")
            return None

    def generate_image_with_volcengine(self, prompt: str, width: int = 1024, height: int = 1024, llmPre: bool = False, n: int = 1):
        """
        使用火山引擎即梦AI API生成图片
        :param prompt: 图片生成的提示词
        :param width: 图片宽度
        :param height: 图片高度
        :param n: 生成图片数量
        :return: 生成的图片信息
        """
        try:
            # 导入火山引擎SDK
            from volcengine.visual.VisualService import VisualService

            print("VisualService导入成功")


            # 创建视觉服务实例
            visual_service = VisualService()
            visual_service.set_ak(self.VOLCENGINE_ACCESS_KEY)   # 设置AK
            visual_service.set_sk(self.VOLCENGINE_SECRET_KEY)   # 设置SK

            # 构建请求参数
            form = {
                "req_key": "jimeng_t2i_v31",  # 使用固定的模型名称
                "prompt": prompt,  # 提示词
                "use_pre_llm": llmPre, #文本扩写
                "width": width,  # 图片宽度
                "height": height,  # 图片高度
                "n": n,  # 生成图片数量
                "return_url": True  # 返回图片URL
            }

            print(f"Request parameters: {form}")

            # 调用API生成图片
            resp = visual_service.cv_process(form)

            print(f"Image generation response: {resp}")

            # 解析返回结果
            if resp.get('code') == 10000:  # 假设0表示成功
                image_urls = resp.get('data', {}).get('image_urls', [])
                print(f"Generated image URLs: {image_urls}")
                return image_urls
            else:
                print(f"Image generation failed: {resp.get('message', 'Unknown error')}")
                return None

        except ImportError as e:
            print(f"Please install volcengine: pip install volcengine: {str(e)}")
            return None
        except Exception as e:
            print(f"Error in image generation: {str(e)}")
            return None

    def generate_image_prompt_from_topic(self, topic: str):
        """
        生成适合火山引擎图片生成的提示词
        :param topic: 主题
        :return: 适合图片生成的提示词
        """
        # 创建一个专门用于生成图片提示词的模板
        image_prompt_template = PromptTemplate.from_template(
            "根据以下主题生成详细、具体的图片生成提示词，使用英文描述：{topic}。要求包含画面构图、风格、颜色、光线、主体等详细描述。长度在500字以内"
        )

        # 使用其他LLM服务生成图片提示词（这里可以使用通义千问或其他支持的服务）
        from services.llm.openai_service import MyOpenAIService
        llm_service = MyOpenAIService()  # 假设使用OpenAI服务生成提示词
        image_prompt = llm_service.generate_content(topic, image_prompt_template)
        return image_prompt

    def generate_and_save_image(self, image_generator):
        """
        从主题生成图片并保存到本地
        :param topic: 主题
        :param width: 图片宽度
        :param height: 图片高度
        :param n: 生成图片数量
        :return: 本地保存的图片路径列表
        """
        with image_generator:
            topic = get_must_session_option('video_subject', "请输入要生成的主题")
            if topic is None:
                return
            
            content = get_must_session_option('video_content', "请输入要生成的内容")
            if content is None:
                return

            llm_provider = my_config['llm']['provider']
            print("llm_provider:", llm_provider)
            width = get_session_option("Width") or 1024
            print("Width:", width)
            height = get_session_option("Height") or 1024
            print("Height:", height)
            llmPre = get_session_option("usePreLlm")
            print("usePreLlm:", llmPre)
            # 首先生成图片提示词
            # image_prompt = self.generate_image_prompt_from_topic(topic)
            image_prompt = topic
            print(f"Generated image prompt: {image_prompt}")

            seed = get_session_option("Seed")
            print("Seed:", seed)
            scale = get_session_option("Scale")
            print("Scale:", scale)
            upload_pic_name = get_session_option("upload_pic_name")
            print("upload_pic_name:", upload_pic_name)

            # 使用火山引擎即梦AI生成图片
            if upload_pic_name is None:
                image_urls = self.generate_image_with_volcengine(image_prompt, width, height, llmPre, n)
            else:
                image_urls = self.generate_image_with_volcengine_from_image(image_prompt, width, height, seed, upload_pic_name, scale)
            
            
            if not image_urls:
                print("Failed to generate image from VolcEngine Jimeng AI")
                return None

            # 下载生成的图片到本地
            saved_paths = []
            for i, image_url in enumerate(image_urls):
                # 创建保存路径
                image_name = f"volcengine-image-{(topic)[:10]}-{i}.jpg"  # 限制文件名长度
                save_path = os.path.join(workdir, image_name)
                save_path = os.path.abspath(save_path)

                # 下载图片
                if download_image(image_url, save_path):
                    saved_paths.append(save_path)
                else:
                    print(f"Failed to save image {image_url} to {save_path}")

            return saved_paths