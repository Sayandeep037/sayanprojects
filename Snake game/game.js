class Snake {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = 200;
        this.y = 200;
        this.dx = 20;
        this.dy = 0;
        this.cells = [{x: this.x, y: this.y}];
        this.maxCells = 4;
    }

    update() {
        this.x += this.dx;
        this.y += this.dy;

        this.cells.unshift({x: this.x, y: this.y});
        if (this.cells.length > this.maxCells) {
            this.cells.pop();
        }
    }
}

class Game {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.snake = new Snake();
        this.food = this.getRandomFood();
        this.score = 0;
        this.highScore = parseInt(localStorage.getItem('snakeHighScore')) || 0;
        this.gameOver = false;

        this.bindEvents();
        this.updateHighScoreDisplay();
        this.start();
    }

    bindEvents() {
        document.addEventListener('keydown', this.handleKeyPress.bind(this));
        document.getElementById('restart-btn').addEventListener('click', () => this.restart());
    }

    handleKeyPress(e) {
        if (this.gameOver) return;

        // Prevent reverse direction
        switch(e.key) {
            case 'ArrowLeft':
                if (this.snake.dx === 0) {
                    this.snake.dx = -20;
                    this.snake.dy = 0;
                }
                break;
            case 'ArrowRight':
                if (this.snake.dx === 0) {
                    this.snake.dx = 20;
                    this.snake.dy = 0;
                }
                break;
            case 'ArrowUp':
                if (this.snake.dy === 0) {
                    this.snake.dx = 0;
                    this.snake.dy = -20;
                }
                break;
            case 'ArrowDown':
                if (this.snake.dy === 0) {
                    this.snake.dx = 0;
                    this.snake.dy = 20;
                }
                break;
        }
    }

    getRandomFood() {
        return {
            x: Math.floor(Math.random() * 20) * 20,
            y: Math.floor(Math.random() * 20) * 20
        };
    }

    checkCollision() {
        // Wall collision
        if (this.snake.x < 0 || this.snake.x >= this.canvas.width ||
            this.snake.y < 0 || this.snake.y >= this.canvas.height) {
            return true;
        }

        // Self collision
        for (let i = 1; i < this.snake.cells.length; i++) {
            if (this.snake.x === this.snake.cells[i].x && 
                this.snake.y === this.snake.cells[i].y) {
                return true;
            }
        }

        return false;
    }

    update() {
        if (this.gameOver) return;

        this.snake.update();

        // Check food collision
        if (this.snake.x === this.food.x && this.snake.y === this.food.y) {
            this.snake.maxCells++;
            this.score += 10;
            document.getElementById('score').textContent = `Score: ${this.score}`;
            if (this.score > this.highScore) {
                this.highScore = this.score;
                localStorage.setItem('snakeHighScore', this.highScore);
                this.updateHighScoreDisplay();
            }
            this.food = this.getRandomFood();
        }

        // Check game over
        if (this.checkCollision()) {
            this.gameOver = true;
            document.getElementById('game-over').style.display = 'block';
            document.getElementById('final-score').textContent = this.score;
            return;
        }

        this.draw();
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw snake
        this.ctx.fillStyle = '#4CAF50';
        this.snake.cells.forEach((cell, index) => {
            this.ctx.fillRect(cell.x, cell.y, 18, 18);
        });

        // Draw food
        this.ctx.fillStyle = '#ff0000';
        this.ctx.fillRect(this.food.x, this.food.y, 18, 18);
    }

    start() {
        if (!this.gameOver) {
            this.update();
            setTimeout(() => requestAnimationFrame(() => this.start()), 200);
        }
    }

    updateHighScoreDisplay() {
        document.getElementById('high-score').textContent = `High Score: ${this.highScore}`;
    }

    restart() {
        this.snake.reset();
        this.food = this.getRandomFood();
        this.score = 0;
        this.gameOver = false;
        document.getElementById('score').textContent = 'Score: 0';
        document.getElementById('game-over').style.display = 'none';
        this.start();
    }
}

// Start the game when the page loads
window.onload = () => new Game();