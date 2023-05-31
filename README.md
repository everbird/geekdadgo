# Procare 照片索引csv导出

1. 安装 GreaseMonkey
2. 安装 geek-dad-go_exporter.js 脚本
3. 打开 Procare
4. 点击页面右下角 "Export photo links" 按钮
5. 填写 起始时间和结束时间
6. 等待生成 csv
7. 检查下载的 csv 文件

# 使用照片索引csv下载照片

```bash
~/Downloads/procare
❯ time cat procare-photos-csv-2022-07-12_to_2023-05-24.csv | awk -F, '{ gsub(":", "-", $2); gsub(/\..*$/, "", $2); print $1,$2,$3}' | xargs -n3 -P8 sh -c 'wget -q -O photos_2022-07-12_to_2023-05-24/$0_$1.jpg $2'
cat procare-photos-csv-2022-07-12_to_2023-05-24.csv  0.00s user 0.00s system 0% cpu 2:07.15 total
awk -F, '{ gsub(":", "-", $2); gsub(/\..*$/, "", $2); print $1,$2,$3}'  0.04s user 0.01s system 0% cpu 2:53.29 total
xargs -n3 -P8 sh -c 'wget -q -O photos_2022-07-12_to_2023-05-24/$0_$1.jpg $2'  85.71s user 31.48s system 60% cpu 3:12.35 total

~/Downloads/procare 3m 12s
❯ cat procare-photos-csv-2022-07-12_to_2023-05-24.csv | wc -l
    2114
```

# 更新下载图片的 Date/Time Original EXIF tag

```bash
~/playground/geekdadgo main* ⇣
html2pdf ❯ time geekdadgo update-dto -i ~/Downloads/procare/photos_2022-07-12_to_2023-05-24
geekdadgo update-dto -i ~/Downloads/procare/photos_2022-07-12_to_2023-05-24  13.23s user 4.67s system 73% cpu 24.420 total

```

# Upload 到你的照片管理存储


# 视频下载部分同照片，不用改时间
