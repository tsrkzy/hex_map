import sys
import json
import os.path
from datetime import datetime
import math

from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter

IN_DIR = "HEXMAP_IN"
OUT_DIR = "HEXMAP_OUT"

CANVAS_BACKGROUND_1 = '000000'
CANVAS_BACKGROUND_2 = '111111'

HEX_SIZE = 80  # = 六角形を6つの正三角形に分割した際の1辺の長さ
HEX_GUTTER = 10
HEX_WIDTH = HEX_SIZE * math.sqrt(3)
HEX_HEIGHT = HEX_SIZE * 2
HEX_SLIT = 2

LABEL_PADDING = 4


def load_json(path: str):
    txt = None
    with open(path) as f:
        txt = f.read()

    return txt


def generate_image(json_dict: dict):
    hex_list = json_dict.get('hex', [])
    hex_data_list, (x_min
                    , y_min
                    , x_max
                    , y_max) = calculate_size(hex_list)

    if (not x_min) or (not y_min) or x_min < 0 or y_min < 0:
        raise Exception("try to draw hex into out-bound")
    canvas_width = math.ceil(x_max + HEX_WIDTH)
    canvas_height = math.ceil(y_max + HEX_HEIGHT)
    size = (
        canvas_width
        , canvas_height
    )
    img = Image.new(mode="RGB", size=size, color=rgb_hex_str_to_tuple(CANVAS_BACKGROUND_1))

    draw_background(img, canvas_width, canvas_height)

    draw_hexagonal(img, hex_data_list)

    img = apply_gaussian_blur(img)

    draw_label(img, hex_data_list)

    return img


def apply_gaussian_blur(img):
    # return img.filter(ImageFilter.BLUR)
    return img.filter(ImageFilter.GaussianBlur(radius=0.5))


def draw_background(img, width, height):
    d = ImageDraw.Draw(img)
    L = 20
    x_range = range(0, width, L)
    y_range = range(0, height, L)
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            if odd(i + j):
                d.rectangle((x, y, x + L, y + L), fill=rgb_hex_str_to_tuple(CANVAS_BACKGROUND_2))


def calculate_size(_hex_list):
    x_min = None
    y_min = None
    x_max = None
    y_max = None

    hex_list = []

    for _hex in _hex_list:
        h1 = _hex["h1"] * 2
        h2 = _hex["h2"] * 2
        v1 = _hex["v1"]
        v2 = _hex["v2"]
        hex_color = _hex.get("color", "white")
        decorates = _hex.get("decorates", [])
        label = _hex.get("label", None)
        # print(f"h{h1}-{h2}\nv{v1}-{v2}, color: {hex_color}, label: {label}")

        color_tuple = rgb_hex_str_to_tuple(hex_color)

        h_range = range(h1, h2 + 1, 2)
        v_range = range(v1, v2 + 1, 1)
        for h in h_range:
            for v in v_range:
                # hex座標(h,v) で v がodd(奇数)なら右に並べる
                # https://www.redblobgames.com/grids/hexagons/#size-and-spacing
                x_offset = (1 if odd(v) else 0.5) * HEX_WIDTH
                x_spacing = (0.5 * h) * HEX_WIDTH

                y_offset = 0.5 * HEX_HEIGHT
                y_spacing = (0.75 * v) * HEX_HEIGHT

                x = x_offset + x_spacing
                y = y_offset + y_spacing

                x_min = min(x, x_min) if x_min is not None else x
                y_min = min(y, y_min) if y_min is not None else y
                x_max = max(x, x_max) if x_max is not None else x
                y_max = max(y, y_max) if y_max is not None else y

                d = {
                    "x": x,
                    "y": y,
                    "h": h,
                    "v": v,
                    "color_tuple": color_tuple,
                    "decorates": decorates,
                    "label": label
                }
                hex_list.append(d)
    return hex_list, (x_min
                      , y_min
                      , x_max
                      , y_max)


def draw_hexagonal(img, hex_list=[]):
    d = ImageDraw.Draw(img)

    for _hex in hex_list:
        x = _hex["x"]
        y = _hex["y"]
        color_tuple = _hex["color_tuple"]
        decorates = _hex["decorates"]

        # 六角形
        _draw_hexagonal(draw=d
                        , x=x
                        , y=y
                        , decorates=decorates
                        , color_tuple=color_tuple)


def draw_label(img, hex_list=[]):
    d = ImageDraw.Draw(img)

    # 逆順で実行し、hv基準で先勝ち(JSONで最後に定義したラベルのみ描画する)
    hv_dict = {}
    _hex_list = hex_list[:]
    _hex_list.reverse()
    for _hex in _hex_list:
        x = _hex["x"]
        y = _hex["y"]
        h = _hex["h"]
        v = _hex["v"]
        key = f"{h}_{v}"
        if hv_dict.get(key):
            continue
        hv_dict[key] = True

        label = _hex["label"]

        # ラベル
        _draw_label(draw=d
                    , h=h
                    , v=v
                    , x=x
                    , y=y
                    , label=label)


def _draw_label(draw, h, v, x, y, label=None):
    font_label = ImageFont.truetype("./fonts/CascadiaPL.ttf", 15)
    font_pos = ImageFont.truetype("./fonts/CascadiaPL.ttf", 14)

    # 表示順は↓
    # label
    #  pos

    # 座標
    pos_label = f"({int(h / 2)},{v})"
    left, top, right, bottom = font_pos.getbbox(pos_label)
    pos_l = left
    pos_t = top
    pos_r = right
    pos_b = bottom
    pos_width = (pos_r - pos_l)
    pos_height = (pos_b - pos_t)
    pos_label_pos = (int(x - pos_width / 2), int(y - (0 if label else (pos_height / 2))))

    # label(任意)
    label_l = pos_l
    label_r = pos_r
    label_height = 0
    if label:
        left, top, right, bottom = font_label.getbbox(label)
        label_l = left
        label_t = top
        label_r = right
        label_b = bottom
        label_width = (label_r - label_l)
        label_height = (label_b - label_t + LABEL_PADDING)
        label_pos = (int(x - label_width / 2), int(y - label_height - LABEL_PADDING))

    rect_l = min(label_l, pos_l)
    rect_r = max(label_r, pos_r)
    rect_w = rect_r - rect_l
    padding = LABEL_PADDING if label else 0

    rect_pos = [
        x - rect_w / 2
        , y - ((label_height + padding) if label else (pos_height / 2))
        , x + rect_w / 2
        , y + (pos_height if label else pos_height / 2)
    ]

    # ラベル台
    draw.rounded_rectangle(rect_pos
                           , radius=3
                           , fill=rgb_hex_str_to_tuple("whitesmoke")
                           , width=0)

    # 座標ラベル
    draw.text(pos_label_pos
              , text=pos_label
              , fill=rgb_hex_str_to_tuple("gray")
              , font=font_pos)

    # labelで指定した文字列ラベル
    if label:
        draw.text(label_pos
                  , text=label
                  , fill=rgb_hex_str_to_tuple("dimgray")
                  , font=font_label)


def _draw_hexagonal(x, y, decorates, draw, color_tuple):
    # 六角形の描画
    hex_pos = [x, y, HEX_SIZE - HEX_SLIT]
    draw.regular_polygon(hex_pos
                         , n_sides=6
                         , rotation=90
                         , fill=color_tuple
                         , outline=rgb_hex_str_to_tuple("black"))
    if "||" in decorates:
        inner_pos_1 = [x, y, HEX_SIZE - HEX_GUTTER]
        draw.regular_polygon(inner_pos_1
                             , n_sides=6
                             , rotation=90
                             , fill=color_tuple
                             , outline=rgb_hex_str_to_tuple("blue"))
        inner_pos_2 = [x, y, HEX_SIZE - HEX_GUTTER * 2]
        draw.regular_polygon(inner_pos_2
                             , n_sides=6
                             , rotation=90
                             , fill=color_tuple
                             , outline=rgb_hex_str_to_tuple("blue"))
    if "*" in decorates:
        step = range(0, 3, 1)
        for s in step:
            _x1 = x + HEX_SIZE * math.cos(math.radians(90 + 60 * s))
            _y1 = y + HEX_SIZE * math.sin(math.radians(90 + 60 * s))
            _x2 = x + HEX_SIZE * math.cos(math.radians(90 + 60 * (s + 3)))
            _y2 = y + HEX_SIZE * math.sin(math.radians(90 + 60 * (s + 3)))
            draw.line([(_x1, _y1), (_x2, _y2)], width=1, fill=rgb_hex_str_to_tuple("black"))


def odd(n: int):
    """
    is 奇数
    :param n:
    :return:
    """
    return n % 2 == 1


def rgb_hex_str_to_tuple(hexstr: str):
    try:
        return color_name_to_tuple(hexstr)
    except Exception as e:
        r_hex = hexstr[0:2]
        g_hex = hexstr[2:4]
        b_hex = hexstr[4:6]
        r_int = int(r_hex, 16)
        g_int = int(g_hex, 16)
        b_int = int(b_hex, 16)

        return r_int, g_int, b_int


def color_name_to_tuple(color_name: str):
    return ImageColor.getrgb(color_name)


def save_image(img, map_name: str):
    out_abs_dir = os.path.abspath(f"./{OUT_DIR}")
    os.makedirs(out_abs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    img.save(f"{out_abs_dir}/{map_name}_{timestamp}.jpg", quality=95)


if __name__ == '__main__':
    input_list = sys.argv[1:]
    path_list = []
    if input_list:
        path_list.extend(input_list)
    elif os.path.isdir(f"./{IN_DIR}"):
        files = os.listdir(os.path.abspath(f"./{IN_DIR}"))
        if files:
            path_list.extend([
                f"./{IN_DIR}/{f}"
                for f in files
                if os.path.isfile(f"./{IN_DIR}/{f}") and os.path.splitext(f"./{IN_DIR}/{f}")[1] == '.json'])
        else:
            path_list.append("input.json")
    else:
        path_list.append("input.json")

    for i, path in enumerate(path_list):
        print(f"[({i}/{len(path_list)})generate: {path}]")
        json_str = load_json(path)
        json_dict = json.loads(json_str)

        img = generate_image(json_dict)

        map_name = os.path.splitext(os.path.basename(path))[0]

        save_image(img, map_name)
        print("  -> saved.")
