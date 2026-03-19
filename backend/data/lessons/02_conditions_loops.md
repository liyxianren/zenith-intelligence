# 条件分支与循环

## 学习目标

- 会使用 `if / elif / else`
- 理解比较运算符和逻辑运算符
- 会使用 `for` 和 `while` 重复执行任务

## 条件判断

```python
score = 85

if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("需要继续练习")
```

## 比较与逻辑运算

- 比较运算：`> >= < <= == !=`
- 逻辑运算：`and or not`

```python
age = 13
has_ticket = True

if age < 18 and has_ticket:
    print("可以入场")
```

## for 循环

```python
for i in range(5):
    print("第", i, "次练习")
```

`range(5)` 会得到 `0, 1, 2, 3, 4`。

## while 循环

```python
count = 3

while count > 0:
    print(count)
    count -= 1
```

`while` 适合“满足条件就继续”的场景。

## break 与 continue

```python
for i in range(1, 6):
    if i == 3:
        continue
    if i == 5:
        break
    print(i)
```

- `continue`：跳过本次循环
- `break`：直接结束整个循环

## 练习

1. 输入一个整数，判断它是正数、负数还是 0。
2. 使用 `for` 输出 1 到 10。
3. 使用 `while` 计算 1 到 100 的和。

## 小结

判断用于做选择，循环用于做重复工作。很多程序都是“先判断，再循环，再继续判断”的组合。
