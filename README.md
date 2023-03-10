* TRPGなどに便利な六角タイルのマップ画像をJSONで定義して描画するツール
* `./HEXMAP_IN/` 配下のJSONファイルを読み込む
* `./HEXMAP_OUT/` 配下にJPEG形式で出力

フォントファイル([CascadiaPL.ttf](https://github.com/microsoft/cascadia-code))をリポジトリに含む

# セットアップ

```
docker-compose up -d --build
```

# 使い方


## すべてのJSONを読み込んで描画

```
python hexmap.py
```

## 特定のJSONファイルだけ読み込んで描画

```
python hexmap.py ./HEXMAP_IN/use_this_file_only.json
```

# サンプル

![](./opt/sample_map_20230116_175831.jpg)

* `hex` キーの配列で後に定義したタイル・ラベルほど優先して描画します

```json
{
  "hex": [
    {
      "_":         "wall. ... this key is ignored.",
      "h1":        0,
      "h2":        6,
      "v1":        0,
      "v2":        5,
      "color":     "dimgray",
      "decorates": [
        "*"
      ],
      "label":     "Wall"
    },
    {
      "h1":        1,
      "h2":        5,
      "v1":        1,
      "v2":        4,
      "color":     "white",
      "decorates": [],
      "label":     ""
    },
    {
      "h1":        2,
      "h2":        3,
      "v1":        3,
      "v2":        4,
      "color":     "lightblue",
      "decorates": [
        "*"
      ],
      "label":     "water"
    },
    {
      "h1":        3,
      "h2":        4,
      "v1":        1,
      "v2":        1,
      "color":     "lightblue",
      "decorates": [
        "*"
      ],
      "label":     "water"
    },
    {
      "h1":        3,
      "h2":        4,
      "v1":        2,
      "v2":        2,
      "color":     "888844",
      "decorates": [],
      "label":     "bridge"
    },
    {
      "h1":        0,
      "h2":        0,
      "v1":        2,
      "v2":        2,
      "color":     "orange",
      "decorates": [],
      "label":     "door"
    },
    {
      "h1":        5,
      "h2":        5,
      "v1":        4,
      "v2":        4,
      "color":     "white",
      "decorates": [
        "||"
      ],
      "label":     "start"
    }
  ]
}
```



# 参考サイト

[Hexagonal Grids](https://www.redblobgames.com/grids/hexagons/)