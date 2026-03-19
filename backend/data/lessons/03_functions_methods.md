# 函数与方法

## 学习目标

- 理解为什么要把代码封装成函数
- 会定义参数与返回值
- 认识常见内置函数和 lambda 表达式

## 什么是函数

函数就是“可以重复调用的一段代码”。

```python
def greet(name):
    print("你好，" + name)

greet("小明")
```

## 参数与返回值

```python
def add(a, b):
    return a + b

result = add(3, 5)
print(result)
```

- 参数：函数输入
- 返回值：函数输出

## 默认参数

```python
def power(base, exp=2):
    return base ** exp

print(power(3))
print(power(3, 3))
```

## 可变参数

```python
def total(*numbers):
    s = 0
    for n in numbers:
        s += n
    return s
```

## 常见内置函数

- `len()`：长度
- `range()`：生成整数序列
- `sorted()`：排序
- `sum()`：求和

## lambda 表达式

```python
square = lambda x: x * x
print(square(4))
```

`lambda` 适合写很短的小函数。

## 方法

方法是“对象自带的函数”。

```python
text = "python"
print(text.upper())
```

## 练习

1. 写一个函数，返回两个数中的较大值。
2. 写一个函数，接收若干成绩，返回平均分。
3. 用 `sorted()` 把列表从小到大排序。

## 小结

函数让代码更清晰、可复用，也更容易测试。后面写类和对象时，方法会变得更重要。
