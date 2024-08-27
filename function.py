import io
import requests
import base64
from utils.AuthV3Util import addAuthParams
import os
import shutil
import json
from PIL import Image
import cv2
import pdf2image


poppler_path = r'./poppler-24.07.0/Library/bin'

def createRequest(img_path, APP_KEY, APP_SECRET, render, lang_from, lang_to):
    '''
    note: 将下列变量替换为需要请求的参数
    取值参考文档: https://ai.youdao.com/DOCSIRMA/html/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E7%BF%BB%E8%AF%91/API%E6%96%87%E6%A1%A3/%E5%9B%BE%E7%89%87%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1/%E5%9B%BE%E7%89%87%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1-API%E6%96%87%E6%A1%A3.html
    '''
    lang_from = lang_from
    lang_to = lang_to
    render = render
    type = '1'

    # 数据的base64编码
    q = readFileAsBase64(img_path)
    data = {'q': q, 'from': lang_from, 'to': lang_to, 'render': render, 'type': type}

    addAuthParams(APP_KEY, APP_SECRET, data)

    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = doCall('https://openapi.youdao.com/ocrtransapi', header, data, 'post')
#     print(str(res.content, 'utf-8'))
    return res


def doCall(url, header, params, method):
    if 'get' == method:
        return requests.get(url, params)
    elif 'post' == method:
        return requests.post(url, params, header)


def readFileAsBase64(path):
    f = open(path, 'rb')
    data = f.read()
    return str(base64.b64encode(data), 'utf-8')


def img_translation(pdf_path, pdf_name, APP_KEY, APP_SECRET, lang_from, lang_to):
    image_list = pdf2image.convert_from_path(pdf_path = pdf_path + f'/{pdf_name}', poppler_path = poppler_path)
    for i in range(len(image_list)):
        # PDF -> jpg形式
        image_list[i].save(f'{pdf_path}/img_data/img{i+1}.jpg')
        # jpg path
        path = f'{pdf_path}/img_data/img{i+1}.jpg'
        # 链接API进行翻译
        res = createRequest( f'{pdf_path}/img_data/img{i+1}.jpg', APP_KEY, APP_SECRET, 1, lang_from, lang_to)
        # json加载api翻译后的结果（base64格式）
        res = json.loads(str(res.content, 'utf-8'))

        # base64重新转换成image
        image_base64 = base64.b64decode(res['render_image'])
        image = Image.open(io.BytesIO(image_base64))
        image.save(f'{pdf_path}/trans_img_data/trans_img{i+1}.jpg')


def img_to_pdf(pdf_path, pdf_name):
    img_list = []
    for img_name in os.listdir(f'{pdf_path}/trans_img_data'):
        img = cv2.imread(f'{pdf_path}/trans_img_data/{img_name}')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_list.append(Image.fromarray(img))
    img_1 = img_list[0]
    # 把img1保存为PDF文件,将另外的图片添加进来，列表需删除第一张图片，不然会重复
    img_list = img_list[1:]
    img_1.save(f'{pdf_path}/fanyi_result_folder/trans_{pdf_name}', "PDF", resolution=100.0, save_all=True,
               append_images=img_list)

    # 清空img文件夹
    shutil.rmtree(f'{pdf_path}/img_data/')
    shutil.rmtree(f'{pdf_path}/trans_img_data/')
    os.mkdir(f'{pdf_path}/img_data/')
    os.mkdir(f'{pdf_path}/trans_img_data/')


def trans_run(pdf_path, APP_KEY, APP_SECRET, lang_from, lang_to):
    if not os.path.exists(f'{pdf_path}/img_data/'):
        os.mkdir(f'{pdf_path}/img_data/')
    if not os.path.exists(f'{pdf_path}/trans_img_data/'):
        os.mkdir(f'{pdf_path}/trans_img_data/')
    if not os.path.exists(f'{pdf_path}/fanyi_result_folder/'):
        os.mkdir(f'{pdf_path}/fanyi_result_folder/')

    pdf_list = [f for f in os.listdir(pdf_path) if f.endswith('.pdf')]
    for pdf_name in pdf_list:
        img_translation(pdf_path, pdf_name, APP_KEY, APP_SECRET, lang_from, lang_to)
        img_to_pdf(pdf_path, pdf_name)