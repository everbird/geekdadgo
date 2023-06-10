# Geek Dad Go

帮助家长从 Procare 下载自家宝宝的数据（包括但不限于照片、视频、Note、Meal等）

## Why?

我家宝宝所在的 daycare 用 Procare 每天发照片/Note 等宝宝的每日活动记录，可惜 Procare 没有提供专门的导出功能，设计上对导出数据也并不算友好，对于想要自己保留一份数据的父母困难重重，具体来讲：
1. 用浏览器访问的 Web 页面，仅能得到最近3个月的活动数据，不过照片和视频倒是有单独的页面，可以按指定的日/周/月提供下载（没有提供批量下载，想下载要一个一个点）
2. 用手机访问的 App，可以按活动类别展示指定日期内的数据（目测一次最多选85天），但无法从 App 上复制粘贴文字信息（要保存只能截屏）
3. 就算是手工下载或截屏的照片，照片的拍摄日期信息也没法一并保存（在按拍摄时间排序的照片流里，可能会用下载时间代替拍摄时间，或者显示为 NODATE，会显得很凌乱）

因此想找到一个拿到这些数据的办法，以便按自己的喜欢的方式管理（例如照片/图片放在 Amazon Photos，视频放在 Google Photos），摆脱只能在 Procare 中查看的囧境。

## 思路

对于照片和视频，先通过 userscript 把下载文件的url和元信息保存到一个 csv 文件，再通过命令行根据 csv 文件并行下载文件，并更新其元信息；
对于 Note、Meal 或其他，先在手机 App 上录制成 MP4 视频，再通过 python 脚本提取成按日聚合的图片；

## Highlight Features

- 从 mp4 视频中逐帧分析，提取每日 Note/Meal 等

- OCR 识别日期和时间，更新 [EXIF original date](https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif/datetimeoriginal.html) 信息(这样该照片在照片流按拍摄时间排序时，才会被放到对应那一天)

- 按日将长图和多个图片缝合（stitch）成一张图片

- 可通过更改 config 微调对 mp4 视频的分析细节(仅测试过 iPhone X Max，其他厂商或型号手机录制的 mp4 可能需要调整参数，例如调整 OCR 识别日期、时间的正确位置，提高识别准确率)

## 如何安装？

``` bash
# Dependencies of pytesseract and PyExifTool package used in python
brew install tesseract exiftool

```
推荐使用 [pyenv](https://github.com/pyenv/pyenv#installation) 和 virtualenv 避免影响系统 python 

``` bash
# Use 3.9.2 for example, you can use whatever version >= 3
pyenv install 3.9.2

# Setup and activate a virtual environment
pyenv virtualenv 3.9.2 geekdadgo-runtime
pyenv activate geekdadgo-runtime

# Upgrade pip to avoid troubles
python -m pip install --upgrade pip

# Install geekdadgo
pip install git+https://github.com/everbird/geekdadgo.git@v0.1.0

# Download config file
wget -O ~/.geekdadgo.conf https://raw.githubusercontent.com/everbird/geekdadgo/main/config/.geekdadgo.conf
geekdadgo --help
```

## 如何导出照片/视频？

下面均以手机用 iPhone X Max，桌面系统用 macOS，浏览器用 Firefox 为例，不再做特殊说明。若使用不同，请自行做相应调整。

### Step 1. 导出照片/视频索引 csv 文件

1. 安装 [GreaseMonkey](https://addons.mozilla.org/en-US/firefox/addon/greasemonkey/) (Firfox) 或 [Tampermonkey](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo) (Chrome )
2. 安装 [geek-dad-go_exporter.user.js](https://raw.githubusercontent.com/everbird/geekdadgo/main/geek-dad-go_exporter.user.js) userscript 脚本 (点击链接即可提示安装，或者自己手工安装：点击 Greasemonkey/Tampermonkey 按钮，选 “New user script ...“，将文件内容复制粘贴后保存 )
3. 打开或刷新 Procare Web 页面，例如 [School Dashboard](https://schools.procareconnect.com/dashboard)
4. 点击页面右下角新出现的 "Export photo/video links" 按钮
5. 在弹出对话框中分别填写 起始时间 和 结束时间，格式为 YYYY-MM-DD，例如 2023-07-12
6. 等待生成并下载 csv 文件，你可以通过浏览器自带的 Web Developer Tools 在 Console 中查看进度

### Step 2. 使用索引 csv 文件下载照片/视频

打开命令行终端（Terminal 或 iTerm2 之类），执行以下命令：

``` bash
cat procare-photos-csv-2022-07-12_to_2023-05-24.csv | awk -F, '{ gsub(":", "-", $2); gsub(/\..*$/, "", $2); print $1,$2,$3}' | xargs -n3 -P8 sh -c 'wget -q -O photos_2022-07-12_to_2023-05-24/$0_$1.jpg $2'
```
该命令用 wget 并行下载 csv 文件中 url 对应的数据，所以执行前请确保 wget 已安装。下载时间跟网速和图片数量有关，附上例子如下：

> ~/Downloads/procare\
> ❯ time cat procare-photos-csv-2022-07-12_to_2023-05-24.csv | awk -F, '{ gsub(":", "-", $2); gsub(/\..*$/, "", $2); print $1,$2,$3}' | xargs -n3 -P8 sh -c 'wget -q -O photos_2022-07-12_to_2023-05-24/$0_$1.jpg $2'\
> cat procare-photos-csv-2022-07-12_to_2023-05-24.csv  0.00s user 0.00s system 0% cpu 2:07.15 total\
> awk -F, '{ gsub(":", "-", $2); gsub(/\..*$/, "", $2); print $1,$2,$3}'  0.04s user 0.01s system 0% cpu 2:53.29 total\
> xargs -n3 -P8 sh -c 'wget -q -O photos_2022-07-12_to_2023-05-24/$0_$1.jpg $2'  85.71s user 31.48s system 60% cpu 3:12.35 total
> 
> ~/Downloads/procare 3m 12s\
> ❯ cat procare-photos-csv-2022-07-12_to_2023-05-24.csv | wc -l\
>     2114

### Step 3. 更新照片的 EXIF original date (视频不需要此步骤)

执行以下命令：

``` bash
geekdadgo update-dto -i ~/Downloads/procare/photos_2022-07-12_to_2023-05-24
```
所有 -i 参数对应目录中的 png, jpg, jpeg 文件都会被遍历，按文件名以下划线(_)分隔后末尾的时间来更新该图片的 EXIF original date。附上例子如下：

> ~/playground/geekdadgo main* ⇣\
> ❯ time geekdadgo update-dto -i ~/Downloads/procare/photos_2022-07-12_to_2023-05-24\
> geekdadgo update-dto -i ~/Downloads/procare/photos_2022-07-12_to_2023-05-24  13.23s user 4.67s system 73% cpu 24.420 total

## 如何导出 Note / Meal 等？

开始之前，先准备好屏幕录制功能。在 Settings -> Control Center 中加入 Screen Recording，这样从屏幕右上角下划时，会有屏幕录制按钮。

<img width="256" alt="screen recording settings" src="https://github.com/everbird/geekdadgo/assets/142570/7eb414be-4b47-4227-aaea-ca0dcdd7138f">
<img width="256" alt="screen recording button" src="https://github.com/everbird/geekdadgo/assets/142570/0e35fe86-920f-40e2-a2eb-36082c2d4f75">

打开 Procare 移动端 App，在 Activity 标签中点击宝宝名字右下方的漏斗图标，在 Activity Filter 页面，将默认的 "All Activities" 改为你想要保存的活动类型，例如 Note 或 Meals 等。再依次选择起始时间和结束时间后，点击 APPLY 按钮得到你所选择类别和时间范围的列表。注意 App 中时间范围目测一次最多选 85 天，所以推荐按月操作。

开始录制之前，先将屏幕一直划到底部，让所有需要加载的新数据全都显示出来，直到看到底部"This is the end of your activities"。

双击顶部状态栏回到页面最顶部，从屏幕右上角下划，选择屏幕录制按钮，在开始倒计时时回到 Procare 页面，屏幕左上角出现红色按钮时，开始录制屏幕。

尽量匀速上划，直到再次看到底部。然后点击左上角红色按钮结束录制。请保障所录制的内容不包含切换程序、加载、通知条等影响画面的元素，必要时可开启 Do Not Disturb 模式。

附上例子视频仅供参考：

https://github.com/everbird/geekdadgo/assets/142570/a18b2244-5cb9-40ed-8cbe-8e49fb979a47

将录制好的 mp4 文件传输到电脑上(例如我直接用的 AirDrop)

用以下命令将 mp4 文件按日提取成图片，放在 images 目录内：
``` bash
geekdadgo run -o images -i procare-note-20230301-20230331.MP4 
```
注意你可以用 `-o` 指定自己的输出目录，用 `--config-path` 指定自定义配置，用 `-vvvv` 开启更多日志。

从上述例子视频提取出的文件如下：

<img width="528" alt="notes output" src="https://github.com/everbird/geekdadgo/assets/142570/619521de-60fc-432a-b109-c4ed45a4165b">

附上具体图片：

<img width="384" alt="img_procare-note-20221201-20221231_frame0065_s_2022-12-08T14-45-00" src="https://github.com/everbird/geekdadgo/assets/142570/50a20325-2358-4692-81fb-b69ac7cceac9">
<img width="384" alt="img_procare-note-20221201-20221231_frame0198_n_2022-12-07T14-20-00" src="https://github.com/everbird/geekdadgo/assets/142570/0bbde590-d0ae-4a25-b3e1-8d42097b6d08">
<img width="384" alt="img_procare-note-20221201-20221231_frame0229_n_2022-12-06T19-40-00" src="https://github.com/everbird/geekdadgo/assets/142570/626dbc32-f63d-4bc8-823c-d2e4f2825932">
<img width="384" alt="img_procare-note-20221201-20221231_frame0309_n_2022-12-05T20-22-00" src="https://github.com/everbird/geekdadgo/assets/142570/20ebe557-cbdb-4a32-aabd-17fa1477dbd6">
<img width="384" alt="img_procare-note-20221201-20221231_frame0403_m0_2022-12-02T13-56-00" src="https://github.com/everbird/geekdadgo/assets/142570/16519b46-a2d6-4c8b-98ae-a7590a47fb10">

提取后请自行验收一遍图片，若出现严重遗漏、OCR偏差、缝合错位等，可以调整配置文件中的相应参数来适应你的情况

用以下命令更新图片的 EXIF original date

``` bash
geekdadgo update-dto -i images
```

如有必要，可以考虑用不同的配置文件，将同一个 mp4 文件的图片提取到不同目录，然后从中挑选出每日较好的那张。




