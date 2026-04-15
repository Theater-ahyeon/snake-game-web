/**
 * 贪吃蛇 OJ 版 - C语言实现
 *
 * 编译: gcc -o snake src/snake.c
 * 运行: ./snake < input.txt
 *
 * OJ交互流程:
 * 1. 程序读取20行地图 + N值
 * 2. 循环:
 *    - 读取一个字符(方向) from stdin
 *    - 输出方向和当前分数 to stdout
 *    - 读取两个整数(新食物位置或结束信号) from stdin
 *    - 如果是结束信号(100 100)，输出最终地图和分数，退出
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAP_SIZE 20
#define MAX_SNAKE_LENGTH (MAP_SIZE * MAP_SIZE)

// 地图元素
#define WALL '#'
#define EMPTY '.'
#define SNAKE_HEAD 'H'
#define SNAKE_BODY 'B'
#define FOOD 'F'
#define OBSTACLE 'O'

// 方向
#define DIR_UP 'W'
#define DIR_LEFT 'A'
#define DIR_DOWN 'S'
#define DIR_RIGHT 'D'

// 方向增量
typedef struct {
    int dr;
    int dc;
} Direction;

// 蛇的位置
typedef struct {
    int row;
    int col;
} Position;

// 蛇
typedef struct {
    Position body[MAX_SNAKE_LENGTH];
    int length;
    char direction;  // 当前方向
} Snake;

// 全局变量
char map[MAP_SIZE][MAP_SIZE + 1];  // +1 for null terminator
Snake snake;
int score = 0;
int inputCount = 0;  // 累计输入次数（用于N次后增长）
int N;               // 每N次输入蛇身增长一节

// 方向映射
Direction dirs[256];

// 初始化方向映射
void init_dirs(void) {
    memset(dirs, 0, sizeof(dirs));
    dirs[(int)DIR_UP].dr = -1;
    dirs[(int)DIR_UP].dc = 0;
    dirs[(int)DIR_DOWN].dr = 1;
    dirs[(int)DIR_DOWN].dc = 0;
    dirs[(int)DIR_LEFT].dr = 0;
    dirs[(int)DIR_LEFT].dc = -1;
    dirs[(int)DIR_RIGHT].dr = 0;
    dirs[(int)DIR_RIGHT].dc = 1;
}

// 读取地图
void read_map(void) {
    for (int i = 0; i < MAP_SIZE; i++) {
        scanf("%s", map[i]);
    }
    scanf("%d", &N);

    // 解析蛇的初始位置
    snake.length = 0;
    snake.direction = DIR_UP;

    // 先找到蛇头
    for (int i = 0; i < MAP_SIZE; i++) {
        for (int j = 0; j < MAP_SIZE; j++) {
            if (map[i][j] == SNAKE_HEAD) {
                snake.body[snake.length].row = i;
                snake.body[snake.length].col = j;
                snake.length++;
            }
        }
    }
    // 再找到蛇身
    for (int i = 0; i < MAP_SIZE; i++) {
        for (int j = 0; j < MAP_SIZE; j++) {
            if (map[i][j] == SNAKE_BODY) {
                snake.body[snake.length].row = i;
                snake.body[snake.length].col = j;
                snake.length++;
            }
        }
    }
}

// 检查方向是否有效（不能反向）
int is_valid_direction(char new_dir) {
    char current = snake.direction;

    // 不能直接反向
    if (current == DIR_UP && new_dir == DIR_DOWN) return 0;
    if (current == DIR_DOWN && new_dir == DIR_UP) return 0;
    if (current == DIR_LEFT && new_dir == DIR_RIGHT) return 0;
    if (current == DIR_RIGHT && new_dir == DIR_LEFT) return 0;

    return 1;
}

// 移动蛇
// 返回值: 1=继续游戏, 0=游戏结束
int move_snake(char new_dir) {
    Direction dir = dirs[(int)new_dir];

    int head_row = snake.body[0].row;
    int head_col = snake.body[0].col;

    // 计算新蛇头位置
    int new_head_row = head_row + dir.dr;
    int new_head_col = head_col + dir.dc;

    // 检查是否撞墙
    if (new_head_row < 0 || new_head_row >= MAP_SIZE ||
        new_head_col < 0 || new_head_col >= MAP_SIZE) {
        return 0;
    }

    // 检查是否撞障碍物
    if (map[new_head_row][new_head_col] == OBSTACLE) {
        return 0;
    }

    // 检查是否撞自身（不包括尾巴，因为尾巴会移动）
    // 移动后，蛇头的位置不应该与身体任何部分重叠（除了旧尾巴位置）
    for (int i = 1; i < snake.length - 1; i++) {
        if (snake.body[i].row == new_head_row &&
            snake.body[i].col == new_head_col) {
            return 0;
        }
    }

    // 更新方向
    snake.direction = new_dir;

    // 记录旧尾巴位置（用于增长）
    Position old_tail = snake.body[snake.length - 1];

    // 检查是否吃到食物
    int ate_food = 0;
    if (map[new_head_row][new_head_col] == FOOD) {
        ate_food = 1;
        score += 10;
        // 清除食物
        map[new_head_row][new_head_col] = EMPTY;
    }

    // 移动蛇身（从后往前）
    for (int i = snake.length - 1; i > 0; i--) {
        snake.body[i] = snake.body[i - 1];
    }
    snake.body[0].row = new_head_row;
    snake.body[0].col = new_head_col;

    // 如果吃食物了，增长一节
    if (ate_food) {
        // 尾巴位置保持（因为吃食物后长度增加）
        snake.body[snake.length] = old_tail;
        snake.length++;
    } else {
        // 每N次输入增长一节
        inputCount++;
        if (inputCount >= N) {
            inputCount = 0;
            // 在尾巴位置增长
            snake.body[snake.length] = old_tail;
            snake.length++;
        }
    }

    // 更新地图 - 先清除旧蛇位置
    for (int i = 0; i < MAP_SIZE; i++) {
        for (int j = 0; j < MAP_SIZE; j++) {
            if (map[i][j] == SNAKE_HEAD || map[i][j] == SNAKE_BODY) {
                map[i][j] = EMPTY;
            }
        }
    }

    // 标记新的蛇头和蛇身
    map[snake.body[0].row][snake.body[0].col] = SNAKE_HEAD;
    for (int i = 1; i < snake.length; i++) {
        map[snake.body[i].row][snake.body[i].col] = SNAKE_BODY;
    }

    return 1;
}

// 输出当前地图和分数
void output_result(void) {
    for (int i = 0; i < MAP_SIZE; i++) {
        printf("%s\n", map[i]);
    }
    printf("%d\n", score);
    fflush(stdout);
}

int main(void) {
    // 初始化
    init_dirs();

    // 读取地图和N值
    read_map();

    // 主循环
    while (1) {
        char dir;
        int new_food_row, new_food_col;

        // 读取移动方向
        scanf(" %c", &dir);

        // 检查方向是否有效
        if (!is_valid_direction(dir)) {
            // 无效方向，游戏结束
            output_result();
            break;
        }

        // 先输出方向
        printf("%c\n", dir);
        fflush(stdout);

        // 输出当前分数（移动前的分数）
        printf("%d\n", score);
        fflush(stdout);

        // 移动蛇
        int alive = move_snake(dir);
        if (!alive) {
            // 撞到东西，游戏结束
            output_result();
            break;
        }

        // 读取交互程序的响应
        scanf("%d %d", &new_food_row, &new_food_col);

        // 检查结束信号
        if (new_food_row == 100 && new_food_col == 100) {
            // 游戏结束，输出最终地图
            output_result();
            break;
        }

        // 生成新食物
        if (new_food_row >= 0 && new_food_row < MAP_SIZE &&
            new_food_col >= 0 && new_food_col < MAP_SIZE) {
            // 放置新食物
            map[new_food_row][new_food_col] = FOOD;
        }
    }

    return 0;
}
