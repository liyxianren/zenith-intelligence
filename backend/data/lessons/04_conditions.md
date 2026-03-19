# 条件语句

## 学习目标

- 会写 `if / else if / else`
- 会写 `switch / case`
- 能根据需求选择合适的分支结构

## if 语句

```c
int score = 88;

if (score >= 90) {
    printf("优秀\n");
} else if (score >= 60) {
    printf("及格\n");
} else {
    printf("继续努力\n");
}
```

## switch 语句

```c
int day = 2;

switch (day) {
    case 1:
        printf("周一\n");
        break;
    case 2:
        printf("周二\n");
        break;
    default:
        printf("其他\n");
}
```

## 使用建议

- 范围判断更适合 `if`
- 固定离散值更适合 `switch`

## 常见错误

- 忘记在 `switch` 分支里写 `break`
- 条件表达式写成赋值表达式

## 小结

分支结构的核心是“根据条件选择不同路径”。先把条件写清楚，再决定使用哪种语法。
