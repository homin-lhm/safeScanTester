# safeScanTester
可自定扫描策略的安全扫描工具

# ===========问题背景===========
## 背景
    在服务端测试工作中，安全测试是非常重要的一环，如果不进行安全测试存在服务被攻击的风险、隐私数据暴露的风险、服务宕机的风险，但安全测试的成本相对来说较高，需要对每一个接口进行安全用例设计和依赖工具进行自动化的扫描，而这些安全测试用例绝大部分在我们团队中都是可通用的，比方说sql注入的检测要模拟的注入方式几乎都是一样的，除了处理数据的不同其他完全一样。

## 痛点
- 安全测试成本高
- 安全测试用例通用性高
- 安全测试质量过程不可保障
- 当前测试团队缺少安全测试规范

## 解决方案
经测试团队对齐并和开发团队进行讨论，最终得到的落地方案是实现一个接口安全自动扫描服务（apiSafeScanSever），可解决的问题包括安全测试手段规范性、减少测试团队在安全测试过程中的人力成本、可自定义安全扫描策略以及校验机制等。
    
# ===========具体的流程设计===========
为满足apiSafeScanSever的交互诉求，服务需提供2个能力，一个是面向开发人员添加扫描任务，一个是面向开发人员提供扫描结果的获取方式。

- 添加扫描任务流程
- 获取扫描结果流程
    
# ===========db设计===========

数据库地址：xxx.xxx.xx.xx:3306
数据访问账号信息：
****
****

status表创建
```mysql
CREATE TABLE `status` (
    `scan_id` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_unicode_ci',
    `status` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_unicode_ci',
    PRIMARY KEY (`scan_id`) USING BTREE
)
COMMENT='获取扫描状态'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
;
```

results表创建
```mysql
CREATE TABLE `results` (
    `scan_id` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_unicode_ci',
    `result` VARCHAR(50) NOT NULL DEFAULT '0' COMMENT '0-未发现安全问题 1-存在安全问题' COLLATE 'utf8mb4_unicode_ci',
    `status` VARCHAR(50) NOT NULL DEFAULT '' COLLATE 'utf8mb4_unicode_ci',
    `scan_strategy` JSON NOT NULL,
    `fail_data` JSON NOT NULL,
    PRIMARY KEY (`scan_id`) USING BTREE
)
COMMENT='存储扫描结果'
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
;
```
# ===========扫描策略设计===========
## sql注入扫描
怎么模拟攻击行为：
- 定义sql注入字典集（存储在XX配置文件中）
- 遍历接口请求参数的每一个字段，读取字典集的数据不断替换字段值，发送接口请求

怎么判断是否存在sql注入的风险问题：
- 如果返回体存在<html>标签，说明可能是未被处理的异常场景
- 遍历返回体的所有字段，如果字段中存在列表类型，并且长度>1，可能存在注入风险，需要人工分析
- 如果返回体包含mysql报错的相关字段，说明被替换的参数值可能被数据库执行


# ===========接口文档设计===========
新建扫描任务
![image](https://github.com/user-attachments/assets/26ef55ee-be1d-4203-b4a0-509451f38a79)

获取扫描结果
![image](https://github.com/user-attachments/assets/6e27dad6-c423-4c10-aa45-98be701d4cf4)
