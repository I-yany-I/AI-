import pygame
import random
from queue import PriorityQueue
import time
import threading



#定义全局变量
#全局变量
BACKGROUND_COLOR = (232,232,232) #主窗口背景颜色
SCORE_TEXT_COLOR = (192,192,192) #分数文字颜色
TIP_TEXT_COLOR = (64,64,64)      #提示文字颜色
SCREEN_RECT = (0,0,640,480)      #窗口大小
CELL_SIZE = 20                   #单元格大小
USEREVENT = 24                   #自定义事件
FOOD_UPDATE_EVENT = pygame.USEREVENT + 1 #食物更新标志
SNAKE_UPDATE_EVENT = pygame.USEREVENT + 2 #蛇更新标志


class Label(object):
    """标签文本类"""
    
    def __init__(self,size = 48,is_score = True):
        """初始化
        :param size: 字体大小
        :param is_score: 是否是显示得分的对象
        """
        self.font = pygame.font.SysFont("SimHei",size)#黑体字
        self.is_score = is_score
        
    def draw(self,window,txt):
        """"绘制当前对象的内容"""
        color = SCORE_TEXT_COLOR if self.is_score else TIP_TEXT_COLOR
        text_surface = self.font.render(txt,True,color)
        
        #获取文本内容的矩形
        text_rect = text_surface.get_rect()
        #获取窗口的矩形
        window_rect = window.get_rect()
        #修改显示的坐标
        if self.is_score:
            #游戏得分，显示在窗口左下角
            text_rect.bottomleft = window_rect.bottomleft
        else:
            #提示信息，显示在窗口中间
            text_rect.center = window_rect.center
        #绘制文本内容到窗口
        window.blit(text_surface,text_rect)
        
class Food():
    """食物类"""
    def __init__(self):
        self.color = (255,0,0)#颜色初始为红色
        self.score = 10#得分
        self.rect = pygame.Rect(0,0,CELL_SIZE,CELL_SIZE)#食物的位置
        self.random_rect()
        
    def draw(self,window):
        """绘制食物"""
        if self.rect.width < CELL_SIZE:
            #食物矩形的宽度小于单元格大小，增加食物的大小
            self.rect.inflate_ip(4,4)
        pygame.draw.ellipse(window,self.color,self.rect)
        
    def random_rect(self,existing_positions = [],snake_body = []):
        """随机生成食物的位置"""
        """随机生成食物位置，并避免与已有位置重叠"""
        while True:
            x = random.randint(0, SCREEN_RECT[2] // CELL_SIZE - 1) * CELL_SIZE
            y = random.randint(0, SCREEN_RECT[3] // CELL_SIZE - 1) * CELL_SIZE
            new_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if new_rect.topleft not in existing_positions and not any(new_rect.colliderect(body) for body in snake_body):
                self.rect.topleft = (x, y)
                break
        #把创建好的食物矩形大小修改为0
        self.rect.inflate_ip(-CELL_SIZE,-CELL_SIZE)
        
        #设置定时器，每隔一段时间更新食物的位置
        pygame.time.set_timer(FOOD_UPDATE_EVENT,30000)
        
class Snake():
    """蛇类"""
    def __init__(self):
        self.color = (64,64,64)        #身体颜色
        self.head_color = (0,0,0)
        self.direction = pygame.K_RIGHT        #默认方向
        self.body_list = []            #蛇的身体列表
        self.time_interval = 100       #蛇移动的时间间隔
        self.score = 0                 #得分
        self.next_direction = self.direction  
        self.reset_snake()
        
        for _ in range(3):
            self.add_body()
    
    def reset_snake(self):
        """重置蛇的数据"""
        self.direction = pygame.K_RIGHT
        self.score = 0
        self.time_interval = 100
        self.body_list.clear()
        
        for _ in range(3):
            self.add_body()
        
    def add_body(self):
        """增加蛇的身体"""
        if len(self.body_list) == 0:
            #没有身体
            head = pygame.Rect(-CELL_SIZE,0,CELL_SIZE,CELL_SIZE)
        else:
            #有身体
            head = self.body_list[0].copy()
        #根据方向移动蛇头
        if self.direction == pygame.K_UP:
            head.y -= CELL_SIZE
        elif self.direction == pygame.K_DOWN:
            head.y += CELL_SIZE
        elif self.direction == pygame.K_LEFT:
            head.x -= CELL_SIZE
        elif self.direction == pygame.K_RIGHT:
            head.x += CELL_SIZE
            
        #把蛇头插入到列表的第一个位置
        self.body_list.insert(0,head)
        
        #定时器，每隔一段时间移动蛇
        pygame.time.set_timer(SNAKE_UPDATE_EVENT,self.time_interval)
    
    def draw(self,window):
        for idx,rect in enumerate(self.body_list):
            pygame.draw.rect(window,self.color,rect.inflate(-2,-2),idx == 0)
            
    def move(self):
        """移动蛇"""
        self.direction = self.next_direction
        self.add_body()
        self.body_list.pop()
        
    def ai_move(self, path):
        """根据路径移动蛇"""
        if path is None:
            return
        next_cell = path[1]
        head = self.body_list[0]
        if next_cell.x < head.x:
            self.direction = pygame.K_LEFT
        elif next_cell.x > head.x:
            self.direction = pygame.K_RIGHT
        elif next_cell.y < head.y:
            self.direction = pygame.K_UP
        elif next_cell.y > head.y:
            self.direction = pygame.K_DOWN
        self.add_body()
        self.body_list.pop()                         

    def change_direction(self,direction):
        """改变蛇的移动方向"""
        SHUIPING_DIRECTION = [pygame.K_LEFT,pygame.K_RIGHT]
        CHUIZHI_DIRECTION = [pygame.K_UP,pygame.K_DOWN]
        if direction in SHUIPING_DIRECTION and self.direction in CHUIZHI_DIRECTION:
            self.next_direction = direction
        elif direction in CHUIZHI_DIRECTION and self.direction in SHUIPING_DIRECTION:
            self.next_direction = direction
        # 添加延迟，单位为秒
        time.sleep(0.05)
            
    def check_collision(self):
        """检测蛇是否碰撞"""
        head = self.body_list[0]
        if head.x < 0 or head.x >= SCREEN_RECT[2] or head.y < 0 or head.y >= SCREEN_RECT[3]:
            return True
        for rect in self.body_list[1:]:
            if head == rect:
                return True
        return False
    
    def check_eat(self,food_rect):
        """检测蛇是否吃到食物"""
        head = self.body_list[0]
        if head == food_rect:
            self.score += 1
            self.body_list.append(pygame.Rect(-CELL_SIZE, 0, -CELL_SIZE, -CELL_SIZE))
            #修改移动的时间间隔
            if self.time_interval > 100:
                self.time_interval -= 10
            return True
        return False
    
    def find_path(self, food, obstacles):
        """使用A*算法找到从蛇头到食物的路径"""
        # 创建一个优先队列来存储待检查的节点，初始节点为蛇头
        open_list = PriorityQueue()
        open_list.put((0, (self.body_list[0].x, self.body_list[0].y)))

        # 创建两个字典来存储每个节点的从起点到该节点的代价和该节点的父节点
        g_score = {(self.body_list[0].x, self.body_list[0].y): 0}
        came_from = {(self.body_list[0].x, self.body_list[0].y): None}

        while not open_list.empty():
            # 获取当前代价最小的节点
            current = open_list.get()[1]

            # 如果当前节点就是食物，那么我们已经找到了路径
            if current == (food.rect.x, food.rect.y):
                path = []
                while current is not None:
                    path.append(pygame.Rect(current[0], current[1], CELL_SIZE, CELL_SIZE))
                    current = came_from[current]
                path.reverse()
                return path

            # 检查当前节点的所有邻居
            for neighbor in [(current[0], current[1] - CELL_SIZE), (current[0], current[1] + CELL_SIZE),
                             (current[0] - CELL_SIZE, current[1]), (current[0] + CELL_SIZE, current[1])]:
                neighbor_rect = pygame.Rect(neighbor[0], neighbor[1], CELL_SIZE, CELL_SIZE)

                # 如果邻居是障碍物或者在蛇的身体中，那么跳过这个邻居
                if any(neighbor_rect.colliderect(obstacle.rect) for obstacle in obstacles) or \
                   any(neighbor_rect == body for body in self.body_list):
                    continue

                # 计算从起点到邻居的代价
                tentative_g_score = g_score[current] + 1

                # 如果这个邻居还没有被检查过，或者我们找到了一条到这个邻居更短的路径，那么更新这个邻居的信息
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + abs(food.rect.x - neighbor[0]) + abs(food.rect.y - neighbor[1])
                    open_list.put((f_score, neighbor))
                    came_from[neighbor] = current

        # 如果没有找到路径，返回None
        return None 
    

class Obstacle():
    """障碍物类"""
    def __init__(self):
        self.color = (0,0,0) # 障碍物颜色
        self.rect = pygame.Rect(0,0,CELL_SIZE,CELL_SIZE)
        
    def draw(self,window):
        """绘制障碍物"""
        pygame.draw.rect(window,self.color,self.rect)
    
    def randomize_position(self, existing_positions):
        """随机生成障碍物位置，并避免与已有位置重叠"""
        while True:
            x = random.randint(0, SCREEN_RECT[2] // CELL_SIZE - 1) * CELL_SIZE
            y = random.randint(0, SCREEN_RECT[3] // CELL_SIZE - 1) * CELL_SIZE
            new_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if new_rect.topleft not in existing_positions:
                self.rect.topleft = (x, y)
                break
        
    def check_collision_with_obstacle(self, snake_rect):
        """检测蛇是否碰撞到障碍物"""
        if snake_rect.colliderect(self.rect):
            return True
        return False
    

        
class Game():
    def __init__(self):
        self.main_window = pygame.display.set_mode((640,480))
        
        pygame.display.set_caption("贪吃蛇")
        
        self.score_Label = Label()
        self.score = 0
        
        self.tip_Label = Label(24,False)#暂停的标签
        
        self.is_game_over = False #游戏是否结束的标记，如果为True则游戏结束
        self.is_pause = False
        
        self.food = Food()
        self.existing_positions = []  # 存储已有位置的列表，初始为空
        
        self.snake = Snake()
        
        self.obstacles = []  # 存储障碍物的列表
        
        
        
        # 初始化障碍物
        for _ in range(5):  # 假设生成5个障碍物
            obstacle = Obstacle()
            obstacle.randomize_position(self.existing_positions)
            self.obstacles.append(obstacle)
            
            # 将障碍物的位置添加到existing_positions列表中
            self.existing_positions.append(obstacle.rect.topleft)
            
    
    
    def start(self,player_control):
        """启动并控制游戏//玩家模式"""
        self.player_control = player_control
        clock = pygame.time.Clock()
        
        
        running = True
        while running:
            # 事件监听
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_SPACE:
                        if self.is_game_over:
                            self.reset_game()
                        else:
                            self.is_pause = not self.is_pause

                    # 只有在玩家模式下处理方向改变事件
                    elif self.player_control == "player" and event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        if not self.is_pause and not self.is_game_over:
                            self.snake.change_direction(event.key)

                elif event.type == FOOD_UPDATE_EVENT:
                    # 更新食物位置
                    self.food.random_rect(self.existing_positions, self.snake.body_list)  # 食物位置更新
                elif event.type == SNAKE_UPDATE_EVENT:
                    # 蛇移动
                    # 玩家控制模式，移动蛇
                    if player_control == "player" and not self.is_pause and not self.is_game_over:       
                        if not self.is_pause and not self.is_game_over:
                            self.snake.move()

                    # AI 控制模式下寻找最短路径并移动蛇
                    elif player_control == "AI" and not self.is_pause and not self.is_game_over:
                        path = self.snake.find_path(self.food, self.obstacles)
                        self.snake.ai_move(path)
                        if path:
                            next_cell = path[1]
                            head = self.snake.body_list[0]
                            if next_cell.x < head.x:
                                self.snake.change_direction(pygame.K_LEFT)
                            elif next_cell.x > head.x:
                                self.snake.change_direction(pygame.K_RIGHT)
                            elif next_cell.y < head.y:
                                self.snake.change_direction(pygame.K_UP)
                            elif next_cell.y > head.y:
                                self.snake.change_direction(pygame.K_DOWN)
                        else:
                            # 如果没有找到路径，则随机选择一个方向移动蛇
                            direction = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
                            self.snake.change_direction(direction)
                            
                        
                    
                            
            # 设置窗口背景颜色
            self.main_window.fill(BACKGROUND_COLOR)
            
            #绘制得分
            self.score_Label.draw(self.main_window,"得分：%d" % self.snake.score)
            
            #绘制暂停标志
            if self.is_game_over:
                self.tip_Label.draw(self.main_window,"游戏结束，按空格键重新开始...")
            elif self.is_pause:
                self.tip_Label.draw(self.main_window,"游戏暂停，按空格键继续...")
            else:
                for obstacle in self.obstacles:
                    if self.snake.check_collision() or obstacle.check_collision_with_obstacle(self.snake.body_list[0]):
                        self.is_game_over = True
                        self.tip_Label.draw(self.main_window, "游戏结束，按空格键重新开始...")
                        break  # 一旦发生碰撞，跳出循环
                    else:
                        if self.snake.check_eat(self.food.rect):
                            self.food.random_rect(self.existing_positions, self.snake.body_list)
                
            #绘制食物
            self.food.draw(self.main_window)
            
            #绘制蛇
            self.snake.draw(self.main_window)
            
            # 绘制障碍物
            for obstacle in self.obstacles:
                obstacle.draw(self.main_window)
            
            #更新显示
            pygame.display.flip()
            
            #设置帧率
            clock.tick(60)
    
    def find_path(self):
        self.path = self.snake.find_path(self.food, self.obstacles)   
        
    def reset_game(self):   
        """重置游戏"""
        self.score = 0
        self.is_game_over = False
        self.is_pause = False   
        
        self.snake.reset_snake()
        
        self.food.random_rect()
            


pygame.init() #初始化pygame
    
#游戏代码
while True:
    print("请选择游戏模式：1/玩家模式 2/AI模式")
    player_control = input()
    if player_control == "1":
        player_control = "player"
        Game().start(player_control) #创建游戏对象
        break
    elif player_control == "2":
        player_control = "AI"
        Game().start(player_control)
        break
    else:
        print("无效的输入，请输入1或2")


pygame.quit() #退出pygame
