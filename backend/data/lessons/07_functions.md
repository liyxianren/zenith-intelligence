# 函数

## 学习目标

- 会声明和定义函数
- 理解参数与返回值
- 了解递归和作用域

## 函数定义

```c
int add(int a, int b) {
    return a + b;
}
```

## 函数调用

```c
int result = add(3, 5);
printf("%d\n", result);
```

## 函数声明

当函数定义写在 `main` 后面时，通常要先声明：

```c
int add(int a, int b);
```

## 递归

```c
int factorial(int n) {
    if (n == 1) return 1;
    return n * factorial(n - 1);
}
```

## 变量作用域

- 局部变量：函数内部定义，只在函数内有效
- 全局变量：定义在函数外，整个文件中可访问

## 小结

函数的价值在于拆分问题、减少重复代码。一个函数最好只做一件清晰的事情。
