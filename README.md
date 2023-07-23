# <p align="center">Masiroer</p>
## <p align="center">This is a SDK for API of [masiro](masiro.me)</p>
</br>

> 该项目的目的是为后续的开发APP做准备，因此处理成`解析程序`+`配置文件`，方便后续跨平台和跨语言。  
> 发现真白萌有官方的[`PWA`](https://flutter.masiro.me/flutter/)，估计很快也会上线官方的APP。  
> 本项目计划推迟，或仅仅作为一个第三方SDK。  

### 解析程序
- [x] python  
- [ ] kitlin  
- [x] JavaScript(Node.js version)

### 配置文件
#### auth
- [x] login
- [ ] ~get token~ (will not support)

#### novel
- [x] get novel menu
- [x] get novel info
- [ ] get novel comment
- [x] mark novel
- [x] unmark novel
- [x] get article
- [ ] get article comment
- [ ] tip article (may not support)
- [ ] reply novel comment
- [ ] reply article comment
- [ ] vote article
- [ ] report (may not support)

#### forum
- [x] load forum list
- [x] load homopage
- [x] load more post
- [x] search forum
- [ ] reply post
- [ ] vote post
- [ ] ......

#### lists
- [x] get random novel
- [x] get latest novel
- [x] search
- [ ] ......

#### self
- [x] check in
- [x] get my notice
- [ ] ~wish~ (will not support)
- [ ] ......

#### user
- [x] get user info box
- [ ] ......

### 目前已知的问题
> - novel.get_info中，返回值 mark_status 有歧义
> - novel.get_menu中，章节的 url 不能正常获取