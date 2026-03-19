# 面向对象编程

## 学习目标

- 理解封装、继承、多态
- 会使用 `super()`
- 初步认识魔术方法

## 封装

封装就是把数据和操作数据的方法放在一起，对外暴露清晰接口。

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
```

## 继承

```python
class Animal:
    def speak(self):
        print("动物发出声音")

class Dog(Animal):
    def speak(self):
        print("汪汪")
```

子类可以复用父类的能力，并按需要重写方法。

## super()

```python
class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    def __init__(self, name, grade):
        super().__init__(name)
        self.grade = grade
```

## 多态

同一个方法名，在不同对象上表现不同。

```python
animals = [Dog(), Animal()]
for item in animals:
    item.speak()
```

## 魔术方法

常见魔术方法：

- `__init__`：初始化
- `__str__`：字符串展示
- `__len__`：长度

```python
class Box:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Box({self.value})"
```

## 小结

面向对象的重点不是“语法有多复杂”，而是让程序更容易扩展、复用和维护。
