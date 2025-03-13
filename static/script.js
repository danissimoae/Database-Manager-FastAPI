// Получить все источники
function getAllSources() {
    fetch("/sources/")
        .then(response => response.json())
        .then(data => {
            let resultsDiv = document.getElementById("allSources");
            resultsDiv.innerHTML = "<h3>Все источники:</h3>";
            data.forEach(source => {
                resultsDiv.innerHTML += `
                    <div class="source-entry">
                        <p><strong>ID:</strong> ${source.source_id}</p>
                        <p><strong>URL:</strong> <a href="${source.url}" target="_blank">${source.url}</a></p>
                        <p><strong>Описание:</strong> ${source.description}</p>
                        <p><strong>Информационная система:</strong> ${source.search_system_name}</p>
                    </div>
                    <hr>
                `;
            });
        });
}

// Получить источник по ID
// Получить источник по ID
function getSourceByID() {
    let sourceID = document.getElementById("getSourceID").value;
    fetch(`/sources/${sourceID}`)
        .then(response => response.json())
        .then(data => {
            let resultDiv = document.getElementById("singleSource");
            resultDiv.innerHTML = "<h3>Источник:</h3>";
            resultDiv.innerHTML += `
                <p>
                    <span>ID: ${data.source_id}</span> | 
                    <span>URL: ${data.url}</span> | 
                    Описание: ${data.description}
                </p>
            `;
        })
        .catch(() => {
            let resultDiv = document.getElementById("singleSource");
            resultDiv.innerHTML = "<h3>Источник не найден</h3>";
        });
}

// Поиск источников
function searchSources() {
    let query = document.getElementById("searchQuery").value;
    fetch(`/sources/search/?query=${query}`)
        .then(response => response.json())
        .then(data => {
            let resultsDiv = document.getElementById("searchResults");
            resultsDiv.innerHTML = "<h3>Результаты:</h3>";
            data.forEach(source => {
                resultsDiv.innerHTML += `
                    <div class="source-entry">
                        <p><strong>ID:</strong> ${source.source_id}</p>
                        <p><strong>URL:</strong> <a href="${source.url}" target="_blank">${source.url}</a></p>
                        <p><strong>Описание:</strong> ${source.description}</p>
                        <p><strong>Информационная система:</strong> ${source.search_system_name}</p>
                    </div>
                    <hr>
                `;
            });
        });
}

// Добавление поисковой системы
function addSearchSystem() {
    let name = document.getElementById("searchSystemName").value;
    let url = document.getElementById("searchSystemURL").value;
    fetch("/search-systems/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, url })
    }).then(response => response.json())
      .then(data => alert("Добавлена система: " + JSON.stringify(data)));
}

// Добавление источника
function addSource() {
    let searchSystemID = document.getElementById("sourceSearchSystemID").value;
    let url = document.getElementById("sourceURL").value;
    let description = document.getElementById("sourceDescription").value;

    // Подготавливаем данные в формат JSON
    const data = {
        search_system_id: searchSystemID,
        url: url,
        description: description
    };

    // Отправляем запрос
    fetch("/sources/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)  // Send the data as JSON
    })
    .then(response => response.json())
    .then(data => {
        alert("Добавлен источник: " + JSON.stringify(data));
    })
    .catch(error => {
        alert("Ошибка при добавлении источника: " + error.message);
    });
}

// Удаление источника
function deleteSource() {
    let sourceID = document.getElementById("deleteSourceID").value;
    fetch(`/sources/${sourceID}`, {
        method: "DELETE"
    }).then(response => {
        if (response.ok) {
            alert("Источник удален");
        } else {
            alert("Ошибка при удалении");
        }
    });
}

// Функция для загрузки полезной информации
function loadDashboardInfo() {
    // получаем число инф систем
    fetch("/search-systems/")
        .then(response => response.json())
        .then(data => {
            document.getElementById("searchSystemCount").textContent = data.length;
        });

    // получаем число источников
    fetch("/sources/")
        .then(response => response.json())
        .then(data => {
            document.getElementById("sourceCount").textContent = data.length;
        });
}

// Вызываем функцию чтобы получить данные
window.onload = loadDashboardInfo;

