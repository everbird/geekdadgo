# Geek Dad Go

帮助父母从 Procare 下载宝宝的数据（包括但不限于照片、视频、Note、Meal等）

## Why?

我家宝宝所在的 daycare 用 Procare 每天发照片/Note 等宝宝的每日活动记录，可惜 Procare 没有提供专门的导出功能，设计上对导出数据也并不算友好，对于想要自己保留一份数据的父母困难重重，具体来讲：
1. 用浏览器访问的 Web 页面，仅能得到最近3个月的活动数据，不过照片和视频倒是有单独的页面，可以按指定的日/周/月提供下载（没有提供批量下载，想下载要一个一个点）
2. 用手机访问的 App，可以按活动类别展示指定日期内的数据（目测一次最多选85天），但无法从 App 上复制粘贴文字信息（要保存只能截屏）
3. 就算是手工下载或截屏的照片，照片的拍摄日期信息也没法一并保存（在按拍摄时间排序的照片流里，可能会用下载时间代替拍摄时间，或者显示为 NODATE，会显得很凌乱）

因此想找到一个拿到这些数据的办法，以便按自己的喜欢的方式管理（例如照片/图片放在 Amazon Photos，视频放在 Google Photos），摆脱只能在 Procare 中查看的境况。

## 思路

对于照片和视频，先通过 userscript 把下载文件的url和元信息保存到一个 csv 文件，再通过命令行根据 csv 文件并行下载文件，并更新其元信息；
对于 Note、Meal 或其他，先在手机 App 上录制成 MP4 视频，再通过 python 脚本提取成按日聚合的图片；

## Highlights

- 从 mp4 视频中逐帧分析，提取每日 Note/Meal 等

- OCR 识别日期和时间，更新 [EXIF original date](https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif/datetimeoriginal.html) 信息

- 按日将长图和多个图片缝合（stitch）成一张图片

- 可通过更改 config 微调对 mp4 视频的分析细节

## 如何安装？

## 如何导出照片/视频？

### Step 1. 导出照片/视频索引 csv 文件

1. 安装 [GreaseMonkey](https://addons.mozilla.org/en-US/firefox/addon/greasemonkey/) (Firfox) 或 [Tampermonkey](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo) (Chrome )
2. 安装 geek-dad-go_exporter.user.js userscript 脚本 (点击 Greasemonkey/Tampermonkey 按钮，选 “New user script ...“，将文件内容复制粘贴后保存 )
3. 打开或刷新 Procare Web 页面，例如 [Dashboard](https://schools.procareconnect.com/dashboard)
4. 点击页面右下角 "Export photo/video links" 按钮
5. 在弹出对话框中填写 起始时间 和 结束时间
6. 等待生成并下载 csv 文件，你可以通过浏览器自带的 Web Developer Tools 在 Console 中查看进度

### Step 2. 使用索引 csv 文件下载照片/视频

打开命令行终端（Terminal 或 iTerm2 之类），用 wget 并行下载 csv 文件中 url 对应的数据。

> ~/Downloads/procare
> ❯ time cat procare-photos-csv-2022-07-12_to_2023-05-24.csv | awk -F, '{ gsub(":", "-", $2); gsub(/\..*$/, "", $2); print $1,$2,$3}' | xargs -n3 -P8 sh -c 'wget -q -O photos_2022-07-12_to_2023-05-24/$0_$1.jpg $2'
> cat procare-photos-csv-2022-07-12_to_2023-05-24.csv  0.00s user 0.00s system 0% cpu 2:07.15 total
> awk -F, '{ gsub(":", "-", $2); gsub(/\..*$/, "", $2); print $1,$2,$3}'  0.04s user 0.01s system 0% cpu 2:53.29 total
> xargs -n3 -P8 sh -c 'wget -q -O photos_2022-07-12_to_2023-05-24/$0_$1.jpg $2'  85.71s user 31.48s system 60% cpu 3:12.35 total
> 
> ~/Downloads/procare 3m 12s
> ❯ cat procare-photos-csv-2022-07-12_to_2023-05-24.csv | wc -l
>     2114

### Step 3. 更新照片的 EXIF original date (视频不需要此步骤)

> ~/playground/geekdadgo main* ⇣
> html2pdf ❯ time geekdadgo update-dto -i ~/Downloads/procare/photos_2022-07-12_to_2023-05-24
> geekdadgo update-dto -i ~/Downloads/procare/photos_2022-07-12_to_2023-05-24  13.23s user 4.67s system 73% cpu 24.420 total

## 如何导出 Note / Meal 等？
