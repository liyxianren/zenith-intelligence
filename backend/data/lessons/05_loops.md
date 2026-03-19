# 循环结构

## 学习目标

- 会使用 `for`、`while`、`do while`
- 理解循环条件和循环变量
- 会使用 `break` 和 `continue`

## for 循环

```c
for (int i = 1; i <= 5; i++) {
    printf("%d\n", i);
}
```

适合已知循环次数的情况。

## while 循环

```c
int n = 3;
while (n > 0) {
    printf("%d\n", n);
    n--;
}
```

## do while 循环

```c
int n = 0;
do {
    printf("至少执行一次\n");
} while (n > 0);
```

## break 与 continue

```c
for (int i = 1; i <= 10; i++) {
    if (i == 3) continue;
    if (i == 8) break;
    printf("%d\n", i);
}
```

## 小结

循环让程序可以批量处理重复任务。写循环时最重要的是确认“什么时候开始、什么时候结束、每次怎么变化”。
