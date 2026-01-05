import streamlit as st

from config.config import my_config, save_config, languages, audio_languages, transition_types, \
    fade_list, audio_types, load_session_state_from_yaml, save_session_state_to_yaml, app_title, GPT_soVITS_languages, CosyVoice_voice
from main import main_generate_video_content, main_generate_ai_video, main_generate_video_dubbing, \
    main_get_video_resource, main_generate_subtitle, main_try_test_audio, get_audio_voices, main_try_test_local_audio, \
    main_generate_ai_video_from_img, main_generate_images
from pages.common import common_ui
from services.sd.sd_service import SDService
from tools.tr_utils import tr

from services.llm.llm_provider import get_llm_provider

import os

from tools.utils import get_file_map_from_dir

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# print("当前脚本的绝对路径是:", script_path)

# 脚本所在的目录
script_dir = os.path.dirname(script_path)

default_bg_music_dir = os.path.join(script_dir, "../bgmusic")
default_bg_music_dir = os.path.abspath(default_bg_music_dir)

default_chattts_dir = os.path.join(script_dir, "../chattts")
default_chattts_dir = os.path.abspath(default_chattts_dir)

load_session_state_from_yaml('01_first_visit')


def save_to_config(region, key):
    value = st.session_state.get(key)
    if value:
        if not my_config[region]:
            my_config[region] = {}
        my_config[region][key] = value
        save_config()


common_ui()

def generate_images(image_generator):
    main_generate_images(image_generator)
def get_video_resource():
    main_get_video_resource()


def generate_subtitle():
    main_generate_subtitle()


def generate_video_content():
    main_generate_video_content()


def generate_video_dubbing():
    main_generate_video_dubbing()


def try_test_audio():
    main_try_test_audio()


def try_test_local_audio():
    main_try_test_local_audio()


def generate_video(video_generator):
    save_session_state_to_yaml()
    resource_provider = my_config['resource']['provider']
    if resource_provider == 'stableDiffusion':
        main_generate_ai_video_from_img(video_generator)
    else:
        main_generate_ai_video(video_generator)


# LLM区域
llm_container = st.container(border=True)
with llm_container:
    st.subheader(tr("LLM Video Subject generator"))
    st.info(tr("Please input video subject, then click the generate button to generate the video content"))
    st.text_input(label=tr("Video Subject"), placeholder=tr("Please input video subject"), key="video_subject")
    llm_columns = st.columns(3)
    video_length_options = {"60": "60字以内", "120": "120字以内", "300": "300字以内", "600": "600字以内"}
    # video_length_options = {"60": "60字以内", "120": "120字以内", "300": "300字以内"}
    with llm_columns[0]:
        st.selectbox(label=tr("Video content language"), options=languages, format_func=lambda x: languages.get(x),
                     key="video_language")
    with llm_columns[1]:
        st.selectbox(label=tr("Pic length"), options=video_length_options,
                     format_func=lambda x: video_length_options.get(x), key="video_length")
        # print(st.session_state.get("video_length"))
    with llm_columns[2]:
        st.button(label=tr("Generate Video Content"), type="primary", on_click=generate_video_content)
    # print(st.session_state.get("video_content"))
    st.text_area(label=tr("Video content"), key="video_content", height=200)
    st.text_input(label=tr("Video content keyword"), key="video_keyword")

# # 生成视频
# video_generator = st.container(border=True)
# with video_generator:
#     st.button(label=tr("Generate Video Button"), type="primary", on_click=generate_images, args=(video_generator,))
# result_video_file = st.session_state.get("result_video_file")
# if result_video_file:
#     st.video(result_video_file)

# 图片生成
image_generator = st.container(border=True)
with image_generator:
    st.button(label=tr("Generate Images"), type="primary", on_click=generate_images, args=(image_generator,))
generated_image = st.session_state.get("generated_image")
if generated_image is not None:
    st.image(generated_image, caption="Generated Image", use_column_width=True)
