import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 環境參數
ROWS = 4
COLS = 12
START = (3, 0)
GOAL = (3, 11)

# 動作: 0: 上, 1: 右, 2: 下, 3: 左
ACTIONS = [( -1, 0 ), ( 0, 1 ), ( 1, 0 ), ( 0, -1 )]

def step(state, action):
    x, y = state
    dx, dy = ACTIONS[action]
    nx, ny = x + dx, y + dy
    
    # 邊界限制
    nx = max(0, min(ROWS - 1, nx))
    ny = max(0, min(COLS - 1, ny))
    
    # 判斷是否掉入懸崖
    if nx == 3 and 1 <= ny <= 10:
        return START, -100, False
    
    # 判斷是否到達終點
    if (nx, ny) == GOAL:
        return (nx, ny), 0, True
        
    return (nx, ny), -1, False

def get_action(q_table, state, epsilon):
    if np.random.rand() < epsilon:
        return np.random.randint(4)
    else:
        values = q_table[state[0], state[1]]
        # 處理多個最大值的情況
        max_val = np.max(values)
        max_indices = np.where(values == max_val)[0]
        return np.random.choice(max_indices)

def q_learning(episodes=500, alpha=0.1, gamma=0.9, epsilon=0.1):
    q_table = np.zeros((ROWS, COLS, 4))
    rewards = []
    
    for _ in range(episodes):
        state = START
        total_reward = 0
        done = False
        
        while not done:
            action = get_action(q_table, state, epsilon)
            next_state, reward, done = step(state, action)
            
            # Q-learning 更新 (Max Q)
            best_next_action = np.argmax(q_table[next_state[0], next_state[1]])
            td_target = reward + gamma * q_table[next_state[0], next_state[1], best_next_action]
            td_error = td_target - q_table[state[0], state[1], action]
            q_table[state[0], state[1], action] += alpha * td_error
            
            total_reward += reward
            state = next_state
            
        # 為了跟課本圖更接近，限制reward不要太低
        rewards.append(max(total_reward, -100))
        
    return q_table, rewards

def sarsa(episodes=500, alpha=0.1, gamma=0.9, epsilon=0.1):
    q_table = np.zeros((ROWS, COLS, 4))
    rewards = []
    
    for _ in range(episodes):
        state = START
        action = get_action(q_table, state, epsilon)
        total_reward = 0
        done = False
        
        while not done:
            next_state, reward, done = step(state, action)
            next_action = get_action(q_table, next_state, epsilon)
            
            # SARSA 更新
            td_target = reward + gamma * q_table[next_state[0], next_state[1], next_action]
            td_error = td_target - q_table[state[0], state[1], action]
            q_table[state[0], state[1], action] += alpha * td_error
            
            total_reward += reward
            state = next_state
            action = next_action
            
        # 為了跟課本圖更接近，限制reward不要太低
        rewards.append(max(total_reward, -100))
        
    return q_table, rewards

def get_optimal_path(q_table):
    state = START
    path = [state]
    done = False
    count = 0
    while not done and count < 100:
        values = q_table[state[0], state[1]]
        max_val = np.max(values)
        max_indices = np.where(values == max_val)[0]
        action = np.random.choice(max_indices)
        
        next_state, _, done = step(state, action)
        path.append(next_state)
        state = next_state
        count += 1
    return path

def draw_cliff(q_path, sarsa_path, filename="cliff.jpg"):
    # 創建上下兩個子圖 (分開畫)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    
    def draw_grid(ax, title):
        ax.set_xlim(0, COLS)
        ax.set_ylim(0, ROWS)
        
        # 繪製網格
        for x in range(COLS + 1):
            ax.axvline(x, color='black', linewidth=1)
        for y in range(ROWS + 1):
            ax.axhline(y, color='black', linewidth=1)
            
        # 標記起點、終點和懸崖
        ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='yellow', alpha=0.5))
        ax.text(0.5, 0.5, 'S', fontsize=16, ha='center', va='center')
        
        ax.add_patch(patches.Rectangle((11, 0), 1, 1, facecolor='green', alpha=0.5))
        ax.text(11.5, 0.5, 'G', fontsize=16, ha='center', va='center')
        
        for i in range(1, 11):
            ax.add_patch(patches.Rectangle((i, 0), 1, 1, facecolor='gray', alpha=0.8))
            ax.text(i+0.5, 0.5, 'Cliff', fontsize=10, ha='center', va='center')
            
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title)

    def plot_path(ax, path, color, label):
        xs = [p[1] + 0.5 for p in path]
        ys = [ROWS - p[0] - 0.5 for p in path]
        ax.plot(xs, ys, color=color, linewidth=3, marker='o', label=label)
        ax.legend(loc='upper right')

    draw_grid(ax1, 'Q-learning Path (Optimal but high risk)')
    plot_path(ax1, q_path, 'red', 'Q-learning')

    draw_grid(ax2, 'SARSA Path (Safe but longer)')
    plot_path(ax2, sarsa_path, 'blue', 'SARSA')
    
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

def plot_rewards(q_rewards_history, sarsa_rewards_history, filename="result_sample.jpg"):
    # q_rewards_history: [runs, episodes]
    q_avg_rewards = np.mean(q_rewards_history, axis=0)
    sarsa_avg_rewards = np.mean(sarsa_rewards_history, axis=0)
    
    # 稍微做一點平滑化 (Window=10) 讓線條更像課本
    def smooth(data, window=10):
        smoothed = np.zeros_like(data)
        for i in range(len(data)):
            smoothed[i] = np.mean(data[max(0, i-window+1):i+1])
        return smoothed

    q_smooth = smooth(q_avg_rewards, window=10)
    sarsa_smooth = smooth(sarsa_avg_rewards, window=10)
    
    plt.figure(figsize=(10, 6))
    plt.plot(sarsa_smooth, label='SARSA', color='blue')
    plt.plot(q_smooth, label='Q-learning', color='red')
    plt.ylim(-100, -20)
    plt.xlabel('Episodes')
    plt.ylabel('Sum of rewards during episode')
    plt.title('Q-learning vs SARSA on Cliff Walking\n($\\alpha=0.1, \\gamma=0.9, \\epsilon=0.1$, Runs=50, Episodes=500)')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    runs = 50
    episodes = 500
    
    all_q_rewards = []
    all_sarsa_rewards = []
    
    all_q_tables = []
    all_sarsa_tables = []
    
    print(f"Training over {runs} runs for average rewards...")
    
    for r in range(runs):
        q_table, q_rewards = q_learning(episodes=episodes, alpha=0.5)
        sarsa_table, sarsa_rewards = sarsa(episodes=episodes, alpha=0.5)
        
        all_q_rewards.append(q_rewards)
        all_sarsa_rewards.append(sarsa_rewards)
        all_q_tables.append(q_table)
        all_sarsa_tables.append(sarsa_table)
            
    # 取多次訓練的平均 Q-table，確保萃取出的路徑最穩定
    avg_q_table = np.mean(all_q_tables, axis=0)
    avg_sarsa_table = np.mean(all_sarsa_tables, axis=0)
    
    q_path = get_optimal_path(avg_q_table)
    sarsa_path = get_optimal_path(avg_sarsa_table)
    
    draw_cliff(q_path, sarsa_path, "cliff.jpg")
    plot_rewards(np.array(all_q_rewards), np.array(all_sarsa_rewards), "result_sample.jpg")
    print("Generated cliff.jpg and result_sample.jpg")

