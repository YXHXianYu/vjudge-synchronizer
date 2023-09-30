# vjudge synchronizer

## 1. 功能

* 可以将board.xcpcio.com的榜同步至vjudge
* 为什么不用vjudge自带的历史排名功能呢？
  * 因为vjudge会直接使用非现场赛的榜，需要每支队伍自己在settings里打勾，很麻烦
* 演示
  * [Bilibili](https://www.bilibili.com/video/BV1Tw411e7Sg)


## 2. 依赖

* Python
* Selenium
* PyYaml
* ChromeDriver
  * 请下载符合自己Chrome浏览器版本的驱动
  * 目录下自带的驱动为 117 版本


## 3. 如何使用

* 安装依赖
* 将 `config.yml.template` 重命名为 `config.yml`
  * 在 `config.yml` 中修改配置信息（vjudge比赛链接、board链接、vjudge管理员账号与密码）

* 运行 `vjudge_synchronizer.py`

