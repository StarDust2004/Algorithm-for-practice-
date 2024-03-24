# 对1.0/2.0版本的改进，考虑回头路的情况
# 将状态的定义修改为，考虑“马”所在位置和目前为止吃掉的棋子列表，
# 从而允许马走到之前走过的位置（只要有其他棋子位置发生了变化）

# 导入队列库（搜索算法可能需要）
import queue
# 导入随机数库
import random
import datetime

# 导入队列库（搜索算法可能需要）
import queue
# 导入随机数库
import random
import datetime

class ChessBoard:
    def __init__(self, size=8):
        '''
        初始化棋盘
        :param size: 正方形棋盘的边长尺寸，默认为8
        '''
        self.size = size
        self.board = [[' ' for _ in range(size)] for _ in range(size)]
        self.start = None
        self.end = None
        self.obstacles = []
        # self.deleted = [] # added by hry,用于记录当前节点删除的红色棋子

    def set_start(self, x, y):
        '''
        设置起始点
        :param x: 起始点x坐标
        :param y: 起始点y坐标
        :return: None
        '''
        self.start = (x, y)
        self.board[x][y] = 'S'

    def set_end(self, x, y):
        '''
        设置终止点
        :param x: 终止点x坐标
        :param y: 终止点y坐标
        :return: None
        '''
        self.end = (x, y)
        self.board[x][y] = 'E'

    def add_obstacle(self, x, y):
        '''
        添加障碍点
        :param x: 障碍点x坐标
        :param y: 障碍点y坐标
        :return: None
        '''
        self.obstacles.append((x, y))

    def is_valid_move(self, x, y, prev_x, prev_y, node_deleted = []):
        '''
        判断当前移动是否有效
        :param x: 移动后点的x坐标
        :param y: 移动后点的y坐标
        :param prev_x: 移动前点的x坐标
        :param prev_y: 移动前点的y坐标
        :return: True或False
        '''
        # TODO 1:请在这里补全判断当前移动是否合法的的代码
        if (x < 0 or x >= size) or (y < 0 or y >= size):
            return False
        if self.board[x][y] == 'B': # 目标位置有己方棋子
            return False
        if abs(x - prev_x) == 2: # 别马脚情况
            if (self.board[int((x + prev_x) / 2)][prev_y] == 'B' or # 障碍黑子
                (self.board[int((x + prev_x) / 2)][prev_y] == 'R' and
                (int((x + prev_x) / 2), prev_y) not in node_deleted)):# 障碍红子未被吃掉
                return False
        else:
            if (self.board[prev_x][int((y + prev_y) / 2)] == 'B' or # 障碍黑子
                (self.board[prev_x][int((y + prev_y) / 2)] == 'R' and
                (prev_x, int((y + prev_y) / 2)) not in node_deleted)):# 障碍红子未被吃掉
                return False
        return True

    def is_goal_reached(self, x, y):
        '''
        判断当前是否抵达终点
        :param x: 当前位置的x坐标
        :param y: 当前位置的x坐标
        :return: True或False
        '''
        return (x, y) == self.end

    def get_possible_moves(self, x, y, node_deleted = []):
        '''
        获取可能的下一步的坐标
        :param x: 当前点的x坐标
        :param y: 当前点的y坐标
        :return: 所有能移动到的有效点坐标的列表
        '''
        possible_moves = [
            (x + 1, y + 2), (x + 2, y + 1),
            (x + 2, y - 1), (x + 1, y - 2),
            (x - 1, y - 2), (x - 2, y - 1),
            (x - 2, y + 1), (x - 1, y + 2)
        ]

        return [(nx, ny) for nx, ny in possible_moves if self.is_valid_move(nx, ny, x, y, node_deleted)]

    def print_board(self):
        '''
        打印当前的棋盘
        :return: None
        '''
        print("+" + "---+" * self.size)
        for row in self.board:
            print("|", end="")
            for cell in row:
                print(f" {cell} |", end="")
            print("\n+" + "---+" * self.size)

    def generate_random_obstacles(self, obstacles_ratio=0.3, seed=0):
        '''
        在棋盘上随机生成一定比例的障碍
        :param obstacles_ratio: 障碍棋子占棋盘位置总数的比例
        :param seed: 随机数种子，控制生成相同的障碍位置
        :return: None
        '''
        num_obstacles = int(obstacles_ratio * self.size * self.size)
        random.seed(seed)
        available_positions = [(x, y) for x in range(self.size) for y in range(self.size)]

        if self.start:
            available_positions.remove(self.start)
        if self.end:
            available_positions.remove(self.end)

        if num_obstacles > len(available_positions):
            print("生成的障碍物数量大于可用位置数量。")
            return

        self.obstacles = random.sample(available_positions, num_obstacles)
        
        for x, y in self.obstacles:
            prob = random.random()
            if prob < 0.5:
                # 红方
                self.board[x][y] = 'R'
            else:
                # 黑方
                self.board[x][y] = 'B'

    def solve(self):
        # TODO 2: 请你在此处补全搜索算法
        node = Node(self.start, [], None) # 初始节点
        search_num = 0 # 搜索次数
        if self.is_goal_reached(node.position[0], node.position[1]):
            return node, search_num
        open_queue = queue.Queue()
        closed_set = set()
        open_queue.put(node)
        while not open_queue.empty():
            node = open_queue.get()
            closed_set.add(node)
            possible_next = self.get_possible_moves(node.x, node.y, node.deleted)
            search_num += 1
            # random.shuffle(possible_next)
            for next in possible_next:
                if self.board[next[0]][next[1]] == 'R':
                    new_node = Node(next, node.deleted + [next], node)
                else:
                    new_node = Node(next, node.deleted, node)
                if not ((is_in_the_queue(new_node, open_queue)) or (is_in_set(new_node, closed_set))): #
                    if self.is_goal_reached(next[0], next[1]): #
                        return new_node, search_num
                    open_queue.put(new_node)

        return None, search_num


        
class Node():
    def __init__(self, position, deleted = [], parent = None):
        self.position = position # 元组？ 
        self.x = position[0]
        self.y = position[1]
        self.deleted = deleted # 列表？
        self.parent = parent # 另一个节点
        # self.parents = [parent] # 用于有多个父节点的情况（多次经过该节点）

    def is_equal(self, anotherNode): # 判断两个状态是否相同（不考虑父节点）
        if self.position == anotherNode.position and self.deleted == anotherNode.deleted:
            return True
        return False
    
def is_in_the_queue(target, my_queue):
    index = 0
    for i in range(my_queue.qsize()):
        item = my_queue.get()
        if item.is_equal(target):
            index = index + 1
        my_queue.put(item)
    if index > 0:
        return True
    else:
        return False

def is_in_set(target, my_set):
    for item in my_set:
          if target.is_equal(item):
            return True
    return False

def path(node, start = (0,0)): # 寻找当前马位置到初始位置的路径
        # 它会遍历节点的父节点链，将所有节点添加到一个列表中.
        path_back = []
        num = 0
        while node.position != start:
            path_back.append(node.position)
            node = node.parent
            num += 1
        path_back.append(node.position)
        return reversed(list(path_back)), num


# 示例用法
if __name__ == "__main__":
    size = 20

    # 实例化一个大小为size的棋盘
    chessboard = ChessBoard(size=size)
    # 设置初始点为(0,0)
    chessboard.set_start(0, 0)
    # 设置终止点为(n-1,n-1)
    chessboard.set_end(size-1, size-1)
    # 随机生成20%的障碍棋子
    chessboard.generate_random_obstacles(obstacles_ratio=0.3, seed=4)
    # 打印初始棋盘
    if size <= 10:
        print("初始棋盘：")
        chessboard.print_board()

    start_time = datetime.datetime.now()
    # 搜索算法求解
    node, search_num = chessboard.solve()
    end_time = datetime.datetime.now() # 记录搜索算法用时


    if node == None:
        print("未能找到解决方法!")
    else:
        final_path, num= path(node)
        print("找到一条最佳可行路径！")
        print("马跳跃的步数:", num)
        print("搜索次数：", search_num)
        print("马跳跃的路径: ")
        for i in final_path:
            print(i)
    # chessboard.print_board()
            
    print('无信息搜索用时', end='')
    if (end_time - start_time).seconds > 0:
        print((end_time - start_time).seconds, end='')
        print('秒')
    else:
        print((end_time - start_time).microseconds / 1000, end='')
        print('毫秒')
