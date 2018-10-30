# UCAS-kits
UCAS(University of Chinese Academy of Sciences) website and life kits.

# Preface
```
在配置文件中填写个人信息
```


# 配置文件
routecode 说明
* `0001`，雁栖湖—玉泉路7:00
* `0003`，雁栖湖—玉泉路13:00
* `0004`，雁栖湖—玉泉路15:40
* `0005`，玉泉路—雁栖湖6:30
* `0006`，玉泉路—雁栖湖10:00
* `0007`，玉泉路—雁栖湖15:00

# Usage
* 预订班车
```
python kits.py
返回一个支付界面URL，在浏览器中打开，需要在浏览器中登录，选择支付方式即可。
```

- [ ] 定时预约
- [x] 验证码识别
- [ ] argparser
- [ ] 多线程