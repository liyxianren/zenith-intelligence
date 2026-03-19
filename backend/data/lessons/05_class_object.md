# 类与对象

## 学习目标

- 理解类与对象的关系
- 会用 `class` 定义简单类
- 会写构造函数和实例方法

## 类和对象是什么

- 类：模板
- 对象：根据模板创建出来的具体实例

比如“学生”是类，“小明”是对象。

## 定义类

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        print(f"我是{self.name}，今年{self.age}岁")
```

## 创建对象

```python
s1 = Student("小明", 12)
s1.introduce()
```

## `__init__` 的作用

`__init__` 是构造函数，用来在对象创建时完成初始化。

## 实例属性与类属性

```python
class Dog:
    species = "犬类"

    def __init__(self, name):
        self.name = name
```

- `species` 是类属性
- `name` 是实例属性

## 练习

1. 定义一个 `Book` 类，包含书名和作者。
2. 给它添加一个 `show_info()` 方法。
3. 创建两个对象并输出信息。

## 小结

类用于描述一类事物，对象则是实际的数据载体。后面继续学习继承和多态时，会在这个基础上扩展。
