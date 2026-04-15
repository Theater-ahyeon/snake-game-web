"""
Snake Game Pro - Flask Backend
提供用户认证、游戏存档、排行榜等功能
"""

import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_sock import Sock
import threading
import json
import hashlib
import secrets

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# Connected WebSocket clients for real-time leaderboard
connected_clients = []
client_lock = threading.Lock()

def broadcast_leaderboard_update(game_mode='all'):
    """Broadcast leaderboard update to all connected WebSocket clients"""
    with client_lock:
        for client in connected_clients:
            try:
                leaderboard = get_leaderboard_data(game_mode)
                client.send(json.dumps({
                    'type': 'leaderboard_update',
                    'data': leaderboard
                }))
            except:
                pass

def get_leaderboard_data(game_mode='all', limit=20):
    """Get leaderboard data"""
    db = get_db()
    if game_mode == 'all':
        scores = db.execute('''
            SELECT u.username, l.score, l.level, l.game_mode, l.achieved_at
            FROM leaderboard l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.score DESC
            LIMIT ?
        ''', (limit,)).fetchall()
    else:
        scores = db.execute('''
            SELECT u.username, l.score, l.level, l.game_mode, l.achieved_at
            FROM leaderboard l
            JOIN users u ON l.user_id = u.id
            WHERE l.game_mode = ?
            ORDER BY l.score DESC
            LIMIT ?
        ''', (game_mode, limit)).fetchall()
    return [dict(s) for s in scores]

# WebSocket endpoint
@sock.route('/ws')
def websocket(ws):
    """WebSocket endpoint for real-time updates"""
    with client_lock:
        connected_clients.append(ws)
    try:
        while True:
            data = ws.receive()
            try:
                msg = json.loads(data)
                if msg.get('type') == 'subscribe':
                    game_mode = msg.get('game_mode', 'all')
                    leaderboard = get_leaderboard_data(game_mode)
                    ws.send(json.dumps({'type': 'leaderboard', 'data': leaderboard}))
            except json.JSONDecodeError:
                pass
    except:
        pass
    finally:
        with client_lock:
            if ws in connected_clients:
                connected_clients.remove(ws)

# 配置
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['DATABASE'] = 'snake_game.db'

# 获取数据库连接
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 初始化数据库
def init_db():
    db = get_db()
    db.executescript('''
        -- 用户表
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );

        -- 游戏存档表
        CREATE TABLE IF NOT EXISTS game_saves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            save_name TEXT NOT NULL,
            game_mode TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            score INTEGER DEFAULT 0,
            snake_length INTEGER DEFAULT 3,
            game_state TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- 用户进度表
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            total_score INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            max_level INTEGER DEFAULT 1,
            max_length INTEGER DEFAULT 3,
            total_food_eaten INTEGER DEFAULT 0,
            total_time_played INTEGER DEFAULT 0,
            achievements TEXT DEFAULT '[]',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- 排行榜表
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_mode TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- 无尽模式记录
        CREATE TABLE IF NOT EXISTS endless_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            length INTEGER DEFAULT 0,
            time_alive INTEGER DEFAULT 0,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    db.commit()

# 密码哈希
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 验证密码
def verify_password(password, password_hash):
    return hash_password(password) == password_hash

# 获取当前用户（简化版，实际应使用JWT）
def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    try:
        token = auth_header.split(' ')[1]
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (token,)).fetchone()
        return dict(user) if user else None
    except:
        return None

# ==================== 认证路由 ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': '用户名长度应为3-20个字符'}), 400

    if len(password) < 6:
        return jsonify({'error': '密码长度至少6个字符'}), 400

    db = get_db()

    # 检查用户名是否存在
    existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        return jsonify({'error': '用户名已存在'}), 409

    # 创建用户
    cursor = db.execute(
        'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
        (username, hash_password(password), email)
    )
    db.commit()
    user_id = cursor.lastrowid

    # 初始化用户进度
    db.execute(
        'INSERT INTO user_progress (user_id) VALUES (?)',
        (user_id,)
    )
    db.commit()

    return jsonify({
        'message': '注册成功',
        'user_id': user_id,
        'username': username
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if not user or not verify_password(password, user['password_hash']):
        return jsonify({'error': '用户名或密码错误'}), 401

    # 更新最后登录时间
    db.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
    db.commit()

    return jsonify({
        'message': '登录成功',
        'user_id': user['id'],
        'username': user['username'],
        'token': str(user['id'])  # 简化版，实际应使用JWT
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    return jsonify({'message': '登出成功'})

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """获取用户资料"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    db = get_db()
    progress = db.execute('SELECT * FROM user_progress WHERE user_id = ?', (user['id'],)).fetchone()

    return jsonify({
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user.get('email'),
            'created_at': user['created_at'],
            'last_login': user['last_login']
        },
        'progress': dict(progress) if progress else None
    })

# ==================== 游戏存档路由 ====================

@app.route('/api/saves', methods=['GET'])
def get_saves():
    """获取用户所有存档"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    db = get_db()
    saves = db.execute(
        'SELECT * FROM game_saves WHERE user_id = ? ORDER BY updated_at DESC',
        (user['id'],)
    ).fetchall()

    return jsonify({
        'saves': [dict(save) for save in saves]
    })

@app.route('/api/saves', methods=['POST'])
def create_save():
    """创建新存档"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    data = request.get_json()
    save_name = data.get('save_name', '').strip()
    game_mode = data.get('game_mode', 'classic')
    difficulty = data.get('difficulty', 'normal')
    level = data.get('level', 1)
    score = data.get('score', 0)
    snake_length = data.get('snake_length', 3)
    game_state = data.get('game_state', '{}')

    if not save_name:
        save_name = f"存档_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    db = get_db()
    cursor = db.execute('''
        INSERT INTO game_saves (user_id, save_name, game_mode, difficulty, level, score, snake_length, game_state)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user['id'], save_name, game_mode, difficulty, level, score, snake_length, game_state))
    db.commit()

    return jsonify({
        'message': '存档成功',
        'save_id': cursor.lastrowid
    }), 201

@app.route('/api/saves/<int:save_id>', methods=['GET'])
def load_save(save_id):
    """加载存档"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    db = get_db()
    save = db.execute(
        'SELECT * FROM game_saves WHERE id = ? AND user_id = ?',
        (save_id, user['id'])
    ).fetchone()

    if not save:
        return jsonify({'error': '存档不存在'}), 404

    return jsonify({'save': dict(save)})

@app.route('/api/saves/<int:save_id>', methods=['PUT'])
def update_save(save_id):
    """更新存档"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    data = request.get_json()

    db = get_db()
    save = db.execute(
        'SELECT * FROM game_saves WHERE id = ? AND user_id = ?',
        (save_id, user['id'])
    ).fetchone()

    if not save:
        return jsonify({'error': '存档不存在'}), 404

    db.execute('''
        UPDATE game_saves
        SET save_name = ?, game_mode = ?, difficulty = ?, level = ?,
            score = ?, snake_length = ?, game_state = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        data.get('save_name', save['save_name']),
        data.get('game_mode', save['game_mode']),
        data.get('difficulty', save['difficulty']),
        data.get('level', save['level']),
        data.get('score', save['score']),
        data.get('snake_length', save['snake_length']),
        data.get('game_state', save['game_state']),
        save_id
    ))
    db.commit()

    return jsonify({'message': '存档更新成功'})

@app.route('/api/saves/<int:save_id>', methods=['DELETE'])
def delete_save(save_id):
    """删除存档"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    db = get_db()
    result = db.execute(
        'DELETE FROM game_saves WHERE id = ? AND user_id = ?',
        (save_id, user['id'])
    )
    db.commit()

    if result.rowcount == 0:
        return jsonify({'error': '存档不存在'}), 404

    return jsonify({'message': '存档删除成功'})

# ==================== 排行榜路由 ====================

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """获取排行榜"""
    game_mode = request.args.get('game_mode', 'all')
    limit = request.args.get('limit', 20, type=int)

    db = get_db()

    if game_mode == 'all':
        scores = db.execute('''
            SELECT u.username, l.score, l.level, l.game_mode, l.achieved_at
            FROM leaderboard l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.score DESC
            LIMIT ?
        ''', (limit,)).fetchall()
    else:
        scores = db.execute('''
            SELECT u.username, l.score, l.level, l.game_mode, l.achieved_at
            FROM leaderboard l
            JOIN users u ON l.user_id = u.id
            WHERE l.game_mode = ?
            ORDER BY l.score DESC
            LIMIT ?
        ''', (game_mode, limit)).fetchall()

    return jsonify({
        'leaderboard': [dict(score) for score in scores]
    })

@app.route('/api/leaderboard', methods=['POST'])
def add_score():
    """提交分数"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    data = request.get_json()
    score = data.get('score', 0)
    game_mode = data.get('game_mode', 'classic')
    level = data.get('level', 1)

    db = get_db()

    # 添加到排行榜
    db.execute(
        'INSERT INTO leaderboard (user_id, game_mode, score, level) VALUES (?, ?, ?, ?)',
        (user['id'], game_mode, score, level)
    )

    db.commit()

    # Broadcast update via WebSocket
    broadcast_leaderboard_update(game_mode)

    return jsonify({'message': '分数提交成功'})

@app.route('/api/endless', methods=['POST'])
def submit_endless():
    """提交无尽模式记录"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    data = request.get_json()
    score = data.get('score', 0)
    length = data.get('length', 0)
    time_alive = data.get('time_alive', 0)

    db = get_db()

    # 添加无尽模式记录
    db.execute(
        'INSERT INTO endless_records (user_id, score, length, time_alive) VALUES (?, ?, ?, ?)',
        (user['id'], score, length, time_alive)
    )

    # 更新用户进度
    progress = db.execute('SELECT * FROM user_progress WHERE user_id = ?', (user['id'],)).fetchone()
    if progress:
        db.execute('''
            UPDATE user_progress
            SET total_score = total_score + ?,
                games_played = games_played + 1,
                max_length = MAX(max_length, ?),
                total_time_played = total_time_played + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (score, length, time_alive, user['id']))
    else:
        db.execute(
            'INSERT INTO user_progress (user_id, total_score, games_played, max_length, total_time_played) VALUES (?, ?, ?, ?, ?)',
            (user['id'], score, 1, length, time_alive)
        )

    db.commit()

    # 获取用户的最佳无尽记录
    best = db.execute(
        'SELECT MAX(score) as best_score FROM endless_records WHERE user_id = ?',
        (user['id'],)
    ).fetchone()

    return jsonify({
        'message': '记录提交成功',
        'best_score': best['best_score'] if best else 0
    })

@app.route('/api/endless/stats', methods=['GET'])
def get_endless_stats():
    """获取无尽模式统计"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    db = get_db()
    stats = db.execute('''
        SELECT
            COUNT(*) as total_games,
            MAX(score) as best_score,
            MAX(length) as max_length,
            SUM(time_alive) as total_time
        FROM endless_records
        WHERE user_id = ?
    ''', (user['id'],)).fetchone()

    # 获取全球排名
    rank = db.execute('''
        SELECT COUNT(*) + 1 as rank
        FROM endless_records
        WHERE score > (
            SELECT COALESCE(MAX(score), 0) FROM endless_records WHERE user_id = ?
        )
    ''', (user['id'],)).fetchone()

    return jsonify({
        'stats': dict(stats),
        'rank': rank['rank'] if rank else 0
    })

# ==================== 关卡路由 ====================

@app.route('/api/levels', methods=['GET'])
def get_levels():
    """获取关卡配置"""
    levels = [
        {
            'level': 1,
            'name': '初出茅庐',
            'description': '经典模式，热身关卡',
            'map_size': 20,
            'obstacle_count': 0,
            'food_count': 1,
            'speed': 150,
            'unlock_score': 0
        },
        {
            'level': 2,
            'name': '小试牛刀',
            'description': '开始出现障碍物',
            'map_size': 20,
            'obstacle_count': 5,
            'food_count': 1,
            'speed': 140,
            'unlock_score': 100
        },
        {
            'level': 3,
            'name': '稳步提升',
            'description': '障碍物增多',
            'map_size': 20,
            'obstacle_count': 10,
            'food_count': 1,
            'speed': 130,
            'unlock_score': 300
        },
        {
            'level': 4,
            'name': '身手不凡',
            'description': '挑战升级',
            'map_size': 25,
            'obstacle_count': 15,
            'food_count': 2,
            'speed': 120,
            'unlock_score': 600
        },
        {
            'level': 5,
            'name': '炉火纯青',
            'description': '大师级别',
            'map_size': 25,
            'obstacle_count': 20,
            'food_count': 2,
            'speed': 110,
            'unlock_score': 1000
        },
        {
            'level': 6,
            'name': '出神入化',
            'description': '接近巅峰',
            'map_size': 30,
            'obstacle_count': 25,
            'food_count': 3,
            'speed': 100,
            'unlock_score': 1500
        },
        {
            'level': 7,
            'name': '登峰造极',
            'description': '最高难度',
            'map_size': 30,
            'obstacle_count': 35,
            'food_count': 3,
            'speed': 90,
            'unlock_score': 2500
        },
        {
            'level': 8,
            'name': '独孤求败',
            'description': '极限挑战',
            'map_size': 35,
            'obstacle_count': 45,
            'food_count': 4,
            'speed': 80,
            'unlock_score': 4000
        }
    ]
    return jsonify({'levels': levels})

@app.route('/api/levels/<int:level>/unlock', methods=['POST'])
def check_level_unlock(level):
    """检查关卡是否解锁"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录', 'unlocked': False}), 401

    db = get_db()
    progress = db.execute('SELECT total_score, max_level FROM user_progress WHERE user_id = ?', (user['id'],)).fetchone()

    if not progress:
        return jsonify({'unlocked': level == 1})

    levels = [
        0, 100, 300, 600, 1000, 1500, 2500, 4000
    ]

    if level < 1 or level > 8:
        return jsonify({'error': '关卡不存在'}), 404

    required_score = levels[level - 1]
    current_score = progress['total_score'] if progress else 0

    return jsonify({
        'unlocked': current_score >= required_score,
        'current_score': current_score,
        'required_score': required_score
    })

# ==================== 成就路由 ====================

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """获取所有成就"""
    achievements = [
        {'id': 'first_game', 'name': '初次见面', 'description': '完成第一局游戏', 'icon': '🎮'},
        {'id': 'score_100', 'name': '百分达成', 'description': '单局得分超过100', 'icon': '💯'},
        {'id': 'score_500', 'name': '五百辉煌', 'description': '单局得分超过500', 'icon': '🏆'},
        {'id': 'score_1000', 'name': '千分传奇', 'description': '单局得分超过1000', 'icon': '👑'},
        {'id': 'length_10', 'name': '长蛇之姿', 'description': '蛇身长度达到10', 'icon': '🐍'},
        {'id': 'length_20', 'name': '巨蟒之力', 'description': '蛇身长度达到20', 'icon': '🦎'},
        {'id': 'level_5', 'name': '五关勇士', 'description': '通关第5关', 'icon': '⭐'},
        {'id': 'level_8', 'name': '八关大师', 'description': '通关第8关', 'icon': '🌟'},
        {'id': 'endless_1000', 'name': '无尽一千', 'description': '无尽模式得分超过1000', 'icon': '♾️'},
        {'id': 'endless_5000', 'name': '无尽五千', 'description': '无尽模式得分超过5000', 'icon': '🔥'},
        {'id': 'games_10', 'name': '十局老手', 'description': '累计完成10局游戏', 'icon': '🎯'},
        {'id': 'games_50', 'name': '五十局高手', 'description': '累计完成50局游戏', 'icon': '💫'},
        {'id': 'time_60', 'name': '坚持一分钟', 'description': '单局存活超过60秒', 'icon': '⏱️'},
        {'id': 'perfect_level', 'name': '完美通关', 'description': '一命通关任意关卡', 'icon': '💎'}
    ]
    return jsonify({'achievements': achievements})

@app.route('/api/achievements/unlock', methods=['POST'])
def unlock_achievement():
    """解锁成就"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    data = request.get_json()
    achievement_id = data.get('achievement_id')

    if not achievement_id:
        return jsonify({'error': '成就ID不能为空'}), 400

    db = get_db()
    progress = db.execute('SELECT achievements FROM user_progress WHERE user_id = ?', (user['id'],)).fetchone()

    if not progress:
        return jsonify({'error': '用户进度不存在'}), 404

    import json
    achievements = json.loads(progress['achievements'] or '[]')

    if achievement_id not in achievements:
        achievements.append(achievement_id)
        db.execute(
            'UPDATE user_progress SET achievements = ? WHERE user_id = ?',
            (json.dumps(achievements), user['id'])
        )
        db.commit()
        return jsonify({'message': '成就解锁成功', 'new_achievement': True})
    else:
        return jsonify({'message': '成就已解锁', 'new_achievement': False})

# ==================== 统计路由 ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取用户统计"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401

    db = get_db()
    progress = db.execute('SELECT * FROM user_progress WHERE user_id = ?', (user['id'],)).fetchone()

    if not progress:
        return jsonify({
            'total_score': 0,
            'games_played': 0,
            'games_won': 0,
            'max_level': 0,
            'max_length': 0,
            'total_food_eaten': 0,
            'total_time_played': 0
        })

    return jsonify(dict(progress))

# ==================== 健康检查 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# 初始化数据库
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
