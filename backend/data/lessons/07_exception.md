# 异常处理

## 学习目标

- 理解什么是异常
- 会使用 `try / except / finally`
- 会用 `raise` 和 `assert`

## 什么是异常

异常就是程序运行时出现的错误，例如除以 0、文件不存在、类型不匹配。

```python
print(10 / 0)
```

## 捕获异常

```python
try:
    num = int(input("请输入一个整数："))
    print(10 / num)
except ValueError:
    print("输入的不是整数")
except ZeroDivisionError:
    print("不能除以 0")
```

## finally

`finally` 中的代码无论是否报错都会执行。

```python
try:
    f = open("demo.txt", "r", encoding="utf-8")
finally:
    print("操作结束")
```

## 主动抛出异常

```python
def set_age(age):
    if age < 0:
        raise ValueError("年龄不能小于 0")
```

## 断言

```python
score = 90
assert score >= 0
```

断言适合检查“本来就应该成立”的条件。

## 练习

1. 输入两个数，处理除数为 0 的情况。
2. 自定义一个函数，输入年龄，非法时抛出异常。
3. 思考：什么时候应该捕获异常，什么时候应该让异常继续抛出？

## 小结

异常处理的目标不是“隐藏所有错误”，而是让程序在错误发生时给出清晰反馈并安全结束。
