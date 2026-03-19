# 列表与字典

## 学习目标

- 会创建和操作列表
- 会使用字典保存键值对数据
- 理解切片与推导式的基本写法

## 列表

```python
scores = [95, 88, 76]
print(scores[0])
scores.append(100)
```

列表适合保存“一组有顺序的数据”。

## 切片

```python
nums = [1, 2, 3, 4, 5]
print(nums[1:4])
print(nums[:3])
print(nums[-2:])
```

## 常用列表方法

- `append()`：追加
- `insert()`：插入
- `pop()`：删除并返回
- `sort()`：原地排序

## 字典

```python
student = {
    "name": "Alice",
    "age": 12,
    "city": "Shanghai"
}

print(student["name"])
student["grade"] = "7年级"
```

字典适合保存“有字段名称的数据”。

## 遍历

```python
for key, value in student.items():
    print(key, value)
```

## 推导式

```python
squares = [x * x for x in range(1, 6)]
even_map = {x: x * 2 for x in range(1, 6)}
```

## 练习

1. 创建一个购物清单列表并添加两个商品。
2. 用字典保存一本书的信息：书名、作者、价格。
3. 用列表推导式生成 1 到 10 的平方。

## 小结

列表强调顺序，字典强调字段名。它们是 Python 中最常用的两种容器类型。
