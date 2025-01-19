const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const box = 20; // Size of each grid cell
const rows = canvas.height / box;
const cols = canvas.width / box;

let snake = [{ x: 5 * box, y: 5 * box }];
let direction = 'RIGHT';
let nextDirection = 'RIGHT'; // To avoid quick reverse input
let bloodDrop = spawnBloodDrop();
let healthBarWidth = 0;
const healthBar = document.getElementById('health-bar');
const winMessage = document.getElementById('winMessage');

document.addEventListener('keydown', changeDirection);

function drawGrid() {
    ctx.fillStyle = '#f4f4f4';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#d9534f';
    for (let x = 0; x <= cols; x++) {
        ctx.moveTo(x * box, 0);
        ctx.lineTo(x * box, canvas.height);
    }
    for (let y = 0; y <= rows; y++) {
        ctx.moveTo(0, y * box);
        ctx.lineTo(canvas.width, y * box);
    }
    ctx.stroke();
}

function drawSnake() {
    for (let segment of snake) {
        ctx.fillStyle = '#d9534f';
        ctx.fillRect(segment.x, segment.y, box, box);
        ctx.strokeStyle = '#333';
        ctx.strokeRect(segment.x, segment.y, box, box);
    }
}

function spawnBloodDrop() {
    return {
        x: Math.floor(Math.random() * cols) * box,
        y: Math.floor(Math.random() * rows) * box
    };
}

function drawBloodDrop() {
    ctx.fillStyle = '#ff0000';
    ctx.beginPath();
    ctx.arc(bloodDrop.x + box / 2, bloodDrop.y + box / 2, box / 3, 0, 2 * Math.PI);
    ctx.fill();
}

function changeDirection(event) {
    const key = event.key;
    if (key === 'ArrowUp' && direction !== 'DOWN') nextDirection = 'UP';
    if (key === 'ArrowDown' && direction !== 'UP') nextDirection = 'DOWN';
    if (key === 'ArrowLeft' && direction !== 'RIGHT') nextDirection = 'LEFT';
    if (key === 'ArrowRight' && direction !== 'LEFT') nextDirection = 'RIGHT';
}

function moveSnake() {
    direction = nextDirection; // Apply the buffered direction change
    const head = { ...snake[0] };
    if (direction === 'UP') head.y -= box;
    if (direction === 'DOWN') head.y += box;
    if (direction === 'LEFT') head.x -= box;
    if (direction === 'RIGHT') head.x += box;

    // Check for collisions
    if (head.x < 0 || head.y < 0 || head.x >= canvas.width || head.y >= canvas.height || collision(head)) {
        resetGame();
        return;
    }

    snake.unshift(head);

    if (head.x === bloodDrop.x && head.y === bloodDrop.y) {
        // Increase health bar
        healthBarWidth += 10; // Increment bar width by 10%
        healthBar.style.width = `${healthBarWidth}%`;

        // Check if the player wins
        if (healthBarWidth >= 100) {
            winGame();
            return;
        }

        bloodDrop = spawnBloodDrop();
    } else {
        snake.pop(); // Remove the tail if no blood drop is collected
    }
}

function collision(head) {
    for (let segment of snake) {
        if (segment.x === head.x && segment.y === head.y) return true;
    }
    return false;
}

function winGame() {
    clearInterval(game);
    winMessage.style.display = 'block';

    // Send win to backend
    fetch('/win-badge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: "{{ session['user_id'] }}" })
    }).then(() => {
        console.log('Badge awarded!');
    });
}

function resetGame() {
    clearInterval(game);
    alert('Game Over! Try again.');
    location.reload();
}

// Main game loop
function gameLoop() {
    drawGrid();
    drawSnake();
    drawBloodDrop();
    moveSnake();
}

const game = setInterval(gameLoop, 100);
