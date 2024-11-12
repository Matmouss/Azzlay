let selecting_piece = false;

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('message', data => {
    console.log(data);
});


socket.on('game_won', data => {
    const victoryScreen = document.getElementById('victory-screen');
    const turnCounterElement = document.getElementById('turn-counter');
    turnCounterElement.textContent = data["nb_moves"];
    const bestElement = document.getElementById('best-score');
    bestElement.textContent = data["best"];
    victoryScreen.classList.add('show');
    document.getElementById('restart-button').addEventListener('click', () => {
        victoryScreen.classList.remove('show');
        location.reload();
    });
});

socket.on('game_state', data => {
    const gameState = data.state;
    updateGameState(gameState);
});

socket.on('restart', () => {
    location.reload();
});

socket.on('game_start', data => {
    updateGameState(data.state);
    const victoryScreen = document.getElementById('victory-screen');
    victoryScreen.classList.add('hidden');
    socket.emit('loop');
})

socket.on('piece_selection', data => {
    highlightSelection(data);      
});

function updateGameState(state) {
    const gameBoard = document.getElementById('game-board');
    gameBoard.innerHTML = renderGrid(state.grid, state.overlay);
    adjustCellSize();
    updateRules(state.rules);
    updateObjectives(state.goals);
    updateLevelText(state.extra_text);
    updateInventory(state.inventory);
    updateNbMoves(state.moves)
}

function updateGameStart(state) {
    const gameBoard = document.getElementById('game-board');
    gameBoard.innerHTML = renderGrid(state.grid, state.overlay);
    adjustCellSize();
    updateRules(state.rules);
    updateObjectives(state.goals);
    updateLevelText(state.extra_text);
    updateInventory(state.inventory);
}

function updateNbMoves(moves){
    const turnCounterElement = document.getElementById('turn-counter-ingame');
    turnCounterElement.textContent = moves;
}

function highlightItem(index) {
    const inventoryList = document.getElementById('inventory-list');
    const items = inventoryList.getElementsByTagName('li');
    if (index >= 0 && index < items.length) {
        // Remove highlight from all items
        Array.from(items).forEach(item => item.classList.remove('highlight'));
        // Add highlight to the specified item
        items[index].classList.add('highlight');
    }
}    

function highlightSelection(data) {
    const inventoryList = document.getElementById('inventory-list');
    let currentIndex = 0;
    selecting_piece = true;
    highlightItem(currentIndex);
    
    function handleKeyDown(event) {
        const key = event.key.toLowerCase(); // Normalise la touche en minuscule
        const items = inventoryList.getElementsByTagName('li');
        if (items.length === 0) return;

        switch (key) {
            case 'arrowup':
            case 'z':
            case 'w':
                currentIndex = (currentIndex > 0) ? currentIndex - 1 : items.length - 1;
                highlightItem(currentIndex);
                break;
            case 'arrowdown':
            case 's':
                currentIndex = (currentIndex < items.length - 1) ? currentIndex + 1 : 0;
                highlightItem(currentIndex);
                break;
            case 'enter':
                document.removeEventListener('keydown', handleKeyDown);
                socket.emit('selected_piece', {index: currentIndex });
                selecting_piece = false;
                break;
            default:
                document.removeEventListener('keydown', handleKeyDown);
                socket.emit('selected_piece', { index: '-1' });
                selecting_piece = false;
                break;
        }
    }

    document.addEventListener('keydown', handleKeyDown);
}



function renderGrid(grid, overlayGrid) {
    let html = "<table>";
    // Parcourir chaque ligne de la grille principale
    grid.forEach((row, rowIndex) => {
        html += "<tr>";
        // Parcourir chaque cellule dans la ligne
        row.forEach((cell, colIndex) => {
            let imgSrc = '';
            let overlaySrc = ''; // Image d'overlay

            // Gestion des images de la grille principale
            switch(cell) {
                case 'normal':
                    imgSrc = '/static/images/player.png';
                    break;
                case 'strong':
                    imgSrc = '/static/images/strong.png';
                    break;
                case 'core':
                    imgSrc = '/static/images/core.png';
                    break;
                case 'circle':
                    imgSrc = '/static/images/circle.png';
                    break;
                case 'triangle':
                    imgSrc = '/static/images/triangle.png';
                    break;
                case 'square':
                    imgSrc = '/static/images/square.png';
                    break;
                case 'quantum':
                    imgSrc = '/static/images/quantum.png';
                    break;
                case 'cross':
                    imgSrc = '/static/images/cross.png';
                    break;
                case 'dollar':
                    imgSrc = '/static/images/dollar.png';
                    break;
                case null:
                    imgSrc = '/static/images/wall.png';
                    break;
                default:
                    imgSrc = '/static/images/void.png';
                    break;
            }

            // Vérifier s'il y a un overlay à cet emplacement dans overlayGrid
            let overlayType = overlayGrid[rowIndex][colIndex];
            if (Array.isArray(overlayType)) {
                overlaySrc = overlayType[0];  // Première image de l'animation (par exemple)
            }
            

            // Ajouter les images de base et d'overlay dans un container
            html += `<td>
                        <div class="cell-container">
                            ${imgSrc ? `<img src="${imgSrc}" alt="${cell}" class="base-image">` : ''}
                            ${overlaySrc ? `<img src="${overlaySrc}" alt="overlay" class="overlay-image">` : ''}
                        </div>
                     </td>`;
        });
        html += "</tr>";
    });
    html += "</table>";
    return html;
}

function adjustCellSize() {
    const gameBoard = document.getElementById('game-board');
    const cells = gameBoard.getElementsByTagName('td');
    if (cells.length > 0) {
        const gridWidth = gameBoard.offsetWidth;
        const gridHeight = gameBoard.offsetHeight;
        const cellSize = Math.max(gridHeight / gameBoard.getElementsByTagName('tr').length, gridHeight / gameBoard.getElementsByTagName('tr').length)/2.5;
        for (let cell of cells) {
            cell.style.width = `${cellSize}px`;
            cell.style.height = `${cellSize}px`;
        }
        const imgs = gameBoard.getElementsByTagName('img');
        for (let img of imgs) {
            img.style.width = `${cellSize}px`; // Adjust the image size slightly smaller than the cell
            img.style.height = `${cellSize}px`;
        }
    }
}

function updateRules(rules) {
    const rulesList = document.getElementById('rules-list');
    rulesList.innerHTML = '';
    if (rules && Array.isArray(rules)) {
        rules.forEach(rule => {
            const li = document.createElement('li');
            li.textContent = rule;
            rulesList.appendChild(li);
        });
    }
}

function updateObjectives(goals) {
    const objectivesList = document.getElementById('objectives-list');
    objectivesList.innerHTML = '';
    if (goals && Array.isArray(goals)) {
        goals.forEach(objective => {
            const li = document.createElement('li');
            li.textContent = objective;
            objectivesList.appendChild(li);
        });
    }
}

function updateLevelText(text) {
    const levelText = document.getElementById('level-text');
    levelText.textContent = text || "";
}

function updateInventory(inventory) {
    const inventoryList = document.getElementById('inventory-list');

    if (!selecting_piece){
        inventoryList.innerHTML = '';

        li = document.createElement('li');
        li.textContent = "circle: " + String(inventory["circle"]);
        inventoryList.appendChild(li);
    
        li = document.createElement('li');
        li.textContent = "triangle: " + String(inventory["triangle"]);
        inventoryList.appendChild(li);
    
        li = document.createElement('li');
        li.textContent = "square: " + String(inventory["square"]);
        inventoryList.appendChild(li);
    
        li = document.createElement('li');
        li.textContent = "quantum: " + String(inventory["quantum"]);
        inventoryList.appendChild(li);
    
    }
    
}

function backToHome() {
    window.location.href = "/";
}

document.addEventListener('keydown', function(event) {
    const action = handleArrows(event.key);
    if (action !== 'nothing' && !selecting_piece) {
        socket.emit('game_action', { action: action});
    }
});

function handleArrows(key) {
    const keyMap = {
        "arrowup": "up",
        "z": "up",
        "w": "up",
        "arrowdown": "down",
        "s": "down",
        "arrowright": "right",
        "d": "right",
        "arrowleft": "left",
        "q": "left",
        "a": "left",
        "enter": "enter",
        " ": "space",
        "r": "restart",
        "e": "restart" 
    };
    return keyMap[key.toLowerCase()] || "nothing";
}

// Adjust cell size on window resize
window.addEventListener('resize', adjustCellSize);
