# 数据类型与变量

## 学习目标

- 认识常见基本数据类型
- 会声明、初始化变量
- 会使用 `printf` 和 `scanf`

## 常见数据类型

```c
int age = 12;
float score = 95.5f;
char grade = 'A';
```

- `int`：整数
- `float`：单精度浮点数
- `char`：字符

## 变量声明与初始化

```c
int count;
count = 10;
```

也可以合并写：

```c
int count = 10;
```

## 输出

```c
printf("age = %d\n", age);
printf("score = %.1f\n", score);
printf("grade = %c\n", grade);
```

## 输入

```c
int number;
scanf("%d", &number);
```

`scanf` 读取变量时通常需要传入地址，所以要写 `&number`。

## 格式控制符

- `%d`：整数
- `%f`：浮点数
- `%c`：字符
- `%s`：字符串

## 小结

变量是程序中保存数据的位置，数据类型决定了变量能存什么，以及编译器如何解释它。
