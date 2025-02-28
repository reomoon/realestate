// 아파트 이름 필터
function filterByArticleName() {
    var selectedValue = document.getElementById("articleNameFilter").value;
    var rows = document.getElementById("articlesTable").getElementsByTagName("tr");

    let showGroup = false;
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        if (row.classList.contains("group-header")) {
            var articleName = row.innerText.trim();
            showGroup = (selectedValue === "" || articleName === selectedValue);
        }
        row.style.display = showGroup ? "" : "none";
    }
}

// 검색 필터 추가
function filterTable() {
    var input = document.getElementById("searchInput");
    var filter = input.value.trim().toLowerCase();
    var rows = document.getElementById("articlesTable").getElementsByTagName("tr");

     // x 버튼을 숨기거나 나타내는 로직
     var clearBtn = document.getElementById("clearBtn");
     if (filter !== "") {
         clearBtn.style.display = "block"; // 텍스트가 있으면 버튼을 보이게 함
     } else {
         clearBtn.style.display = "none"; // 텍스트가 없으면 버튼을 숨김
     }

    
    for (var i = 0; i < rows.length; i++) { // i = 1 → i = 0 으로 수정
        var row = rows[i];
        var textContent = row.innerText.toLowerCase(); // 여기서 textContent 정의

        if (filter === "") {
            row.style.display = "";
            removeHighlights(row);
        } else if (textContent.includes(filter)) {
            row.style.display = "";
            highlightText(row, filter);
        } else {
            row.style.display = "none";
        }
    }
}

// 검색어 삭제 기능
function clearSearch() {
    var input = document.getElementById("searchInput");
    input.value = "";  // 입력 필드 비우기
    filterTable();     // 테이블 필터링 재실행
}

// 검색 텍스트 하이라이트 
function highlightText(row, keyword) {
    if (!keyword) return;

    var regex = new RegExp(`(${keyword})`, "gi");
    removeHighlights(row);

    function wrapMatch(node) {
        if (node.nodeType === 3) {
            var match = node.nodeValue.match(regex);
            if (match) {
                var replacedText = node.nodeValue.replace(regex, '<span class="highlight">$1</span>');
                var tempDiv = document.createElement("div");
                tempDiv.innerHTML = replacedText;

                var fragment = document.createDocumentFragment();
                while (tempDiv.firstChild) {
                    fragment.appendChild(tempDiv.firstChild);
                }
                node.parentNode.replaceChild(fragment, node);
            }
        } else if (node.nodeType === 1) {
            for (var i = node.childNodes.length - 1; i >= 0; i--) {
                wrapMatch(node.childNodes[i]);
            }
        }
    }

    wrapMatch(row);
}


function removeHighlights(row) {
    var spans = row.querySelectorAll(".highlight");
    spans.forEach(span => {
        span.outerHTML = span.innerHTML; // span 태그만 제거하고 내용 유지
    });
}
